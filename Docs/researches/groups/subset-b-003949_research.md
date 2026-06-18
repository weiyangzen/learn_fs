# subset-b-003949 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_hw.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_hw.c

Purpose: hardware command, interrupt, and resource-management implementation for the Emulex/OneConnect OCRDMA RoCE driver. It translates RDMA core and driver-internal requests into SLI mailbox commands, creates the control queues that carry those commands, manages EQ/CQ interrupt dispatch, and allocates firmware-visible resources such as PDs, CQs, QPs, SRQs, memory keys, address-vector tables, DCBX service-level state, and RDMA statistics.

Important APIs/types/functions: exported entry points include `ocrdma_init_hw()`, `ocrdma_cleanup_hw()`, `ocrdma_ring_cq_db()`, `ocrdma_get_irq()`, QP state conversion through `get_ibqp_state()`, mailbox verbs such as `ocrdma_mbx_alloc_pd()`, `ocrdma_mbx_create_cq()`, `ocrdma_mbx_create_qp()`, `ocrdma_mbx_modify_qp()`, `ocrdma_mbx_destroy_qp()`, SRQ and MR/lkey helpers, `ocrdma_mbx_rdma_stats()`, address-vector allocation, `ocrdma_init_service_level()`, and flush-list helpers. Internally, the key state is `dev->mq`, `dev->mqe_ctx`, `dev->eq_tbl`, `dev->pd_mgr`, `dev->av_tbl`, `dev->cq_tbl`, `dev->qp_tbl`, and firmware attribute fields under `dev->attr`, `dev->phy`, and model/port metadata.

Control flow: initialization creates event queues, requests IRQs, creates the mailbox completion queue and mailbox queue, queries firmware configuration, device limits, firmware version, PHY details, controller attributes, and creates the address-handle table. Mailbox submission is serialized by `mqe_ctx.lock`: `ocrdma_post_mqe()` copies a command into the coherent MQ slot, writes a memory barrier, advances the head, and rings the MQ doorbell; the IRQ path consumes EQEs, dispatches the MQ CQ, marks matching command completions by tag, wakes the waiter, and lets `ocrdma_mbx_cmd()` copy the response back and convert CQE or mailbox status to Linux errors. Data CQs are dispatched to the registered RDMA completion handler and then to buddy CQs for flushed error CQEs.

State and persistence: most persistent state is runtime-only and mirrored between firmware IDs and host objects. EQ, MQ, CQ, QP, SRQ, AV, and MR queues use DMA-coherent memory whose physical pages are passed to firmware. PD pools may be preallocated as normal and DPP bitmaps with usage and threshold counters. QP state is guarded by `q_lock`; transitions to INIT reset queue pointers and remove flush-list entries, while transitions to ERR add the QP to CQ flush lists under `flush_q_lock`. The mailbox context can enter `fw_error_state` after a 30-second timeout, causing later mailbox commands to fail early. `ocrdma_eqd_set_task()` persists adaptive interrupt moderation state in each EQ's `aic_obj` and reschedules itself every second until cleanup cancels it.

Dependencies/integration: depends on the BE RoCE/NIC provider for MCC commands, PCI coherent DMA, BAR doorbells, MSI-X or INTx interrupts, Linux RDMA core types, GID and address helpers, DCBX firmware command formats, and SLI bit layouts from `ocrdma_sli.h`. It is called from `ocrdma_main.c` during device add/remove and from verbs, AH, MR, CQ, QP, MAD, and stats code throughout the OCRDMA driver.

Risks and test signals: mailbox timeout handling is coarse and globally poisons the command context; test firmware reset/non-response paths and cleanup after timeout. Error unwinds for QP creation, CQ binding, stats allocation, and AH table creation should be checked for leaked coherent memory, stale EQ `cq_cnt`, and DPP PD credit restoration. Interrupt dispatch depends on correct valid-bit clearing, budget accounting, and doorbell ordering; test INTx and MSI-X, stale EQEs after CQ teardown, MQ async events, CQ overflow/fatal QP events, and buddy CQ flush callbacks. QP modify packs GRH, VLAN, PFC service level, IPv4-mapped GIDs, and MAC resolution into firmware fields; test RoCE v1/v2, VLAN absent with PFC, DCBX update events, all QP state transitions, SRQ-backed QPs, and big-endian conversion paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_hw.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_hw.h

Purpose: internal hardware interface header for OCRDMA. It exposes the mailbox, queue, key, CQ, QP, SRQ, address-vector, stats, and link/service-level functions implemented by `ocrdma_hw.c`, plus byte-order helpers and a doorbell-address helper used by other driver modules.

Important APIs/types/functions: `ocrdma_cpu_to_le32()`, `ocrdma_le32_to_cpu()`, `ocrdma_copy_cpu_to_le32()`, and `ocrdma_copy_le32_to_cpu()` centralize 32-bit word conversion for firmware command and completion buffers, becoming no-ops or `memcpy()` on little-endian builds. `ocrdma_get_db_addr()` derives a user/kernel doorbell page address from PD ID and NIC doorbell page size. The prototypes cover hardware lifecycle, CQ doorbells, link speed/config queries, PD/lkey/MR allocation, CQ/QP/SRQ mailbox commands, address-vector allocation, QP flush and state handling, stats fetch, service-level initialization, PD pool allocation, and link-state dispatch.

Control flow: this header defines the cross-module call graph boundary. Module add in `ocrdma_main.c` calls `ocrdma_init_hw()` before resource allocation and `ocrdma_cleanup_hw()` during removal. Verbs implementations call the mailbox create/modify/query/destroy helpers, poll/arm paths call `ocrdma_ring_cq_db()`, stats code calls `ocrdma_mbx_rdma_stats()`, and MAD/link code calls the link and PMA-related helpers.

State and persistence: no standalone state is allocated here. It documents how external modules interact with persistent runtime state inside `struct ocrdma_dev`, `struct ocrdma_qp`, `struct ocrdma_cq`, `struct ocrdma_srq`, `struct ocrdma_pd`, and `struct ocrdma_hw_mr`. The byte-order helpers mutate buffers in place on big-endian systems, so callers must pass firmware-layout buffers whose length is a multiple of 32-bit words.

Dependencies/integration: includes `ocrdma_sli.h`, so all command structure definitions and bit fields are visible to callers. It depends on core OCRDMA types declared elsewhere in the driver and bridges RDMA core types such as `enum ib_qp_state`, `struct ib_qp_attr`, `struct ib_qp_init_attr`, `struct ib_srq_attr`, and `struct ib_mad`.

Risks and test signals: the header is a high-blast-radius contract; signature drift must be compiled against all OCRDMA objects. Test big-endian builds or static analysis for every conversion helper call, especially paths that convert strings or byte arrays as 32-bit words. Validate doorbell address calculations for PD IDs, DPP pages, and user mmap paths, and compile with SRQ-capable and non-SRQ ASIC code paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_main.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_main.c

Purpose: top-level module and RDMA core integration for the OCRDMA RoCE driver. It registers the driver with the BE RoCE provider, allocates and registers an `ib_device`, installs RDMA verbs operations, exposes small device sysfs attributes, initializes hardware/resources/stats, handles link events, and tears everything down on device removal or shutdown.

Important APIs/types/functions: `ocrdma_dev_ops` maps RDMA core operations to OCRDMA verbs implementations for PD, MR, CQ, QP, AH, user context, mmap, MAD, posting, polling, querying, and notification. `ocrdma_dev_srq_ops` conditionally adds SRQ methods for SKH-R ASICs. `ocrdma_register_device()` fills node GUID/description, port count, completion vectors, parent device, netdev binding, DMA max segment size, and calls `ib_register_device()`. `ocrdma_add()` and `ocrdma_remove()` are the provider-facing lifecycle hooks, while `ocrdma_update_link_state()` dispatches RDMA port events.

Control flow: module init creates the OCRDMA debugfs root and registers `ocrdma_drv` with `be_roce_register_driver()`. On add, the driver allocates an `ib_device`, allocates a mailbox command buffer, copies NIC provider info, initializes hardware, allocates software tables/stat resources, initializes DCBX service level, registers with RDMA core, queries current link state, creates port stats debugfs files, and schedules the EQ delay work. Removal cancels EQ delay work, unregisters from RDMA core first to stop clients, removes stats, frees resources, cleans hardware queues, and deallocates the RDMA device. Shutdown dispatches a port error before removal.

State and persistence: per-device state lives for the provider add/remove lifetime. `dev->id` is derived from PCI function, `nic_info` is copied from the BE provider, `mbx_cmd` is a shared embedded mailbox command scratch buffer, and software tables include CQ/QP/STag arrays, PD pool, stats memory, AV table lock, and flush queue lock. Link-status initialization is tracked by `OCRDMA_FLAGS_LINK_STATUS_INIT`, suppressing the first down notification until an initial up state is known.

Dependencies/integration: integrates with Linux module infrastructure, RDMA core registration and object sizing, netdev-to-IB binding, IPv6 EUI-48 GUID generation, BE RoCE provider callbacks and ABI version, PCI DMA constraints, debugfs/stats support, and OCRDMA verbs/AH/HW/MAD helper modules. The sysfs group exposes `hw_rev` and `hca_type` through the RDMA device.

Risks and test signals: lifecycle ordering is important because clients must be stopped before hardware queues and stats memory disappear. Test add failure at each step, remove after partial initialization, provider shutdown event, link up/down notification suppression on first down state, SRQ operation installation only on SKH-R ASICs, debugfs root cleanup after provider registration failure, and concurrent delayed EQ moderation work during removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_sli.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_sli.h

Purpose: firmware/SLI protocol contract for the OCRDMA driver. It defines ASIC IDs, mailbox subsystem opcodes, doorbell offsets and bit layouts, queue geometry, mailbox entry formats, async event and completion formats, resource command request/response structures, QP/SRQ/MR/CQ/AH encodings, WQE/CQE layouts, stats response layouts, controller attributes, and DCBX configuration structures.

Important APIs/types/functions: the central structures are `ocrdma_mbx_hdr`, `ocrdma_mbx_rsp`, `ocrdma_mqe`, `ocrdma_mcqe`, `ocrdma_eqe`, `ocrdma_cqe`, `ocrdma_hdr_wqe`, `ocrdma_sge`, `ocrdma_av`, `ocrdma_mbx_query_config`, QP command structs (`ocrdma_create_qp_req`, `ocrdma_modify_qp`, `ocrdma_qp_params`), SRQ/MR/PD/lkey commands, AH table commands, `ocrdma_rdma_stats_req/resp`, `mgmt_hba_attribs`, and `ocrdma_dcbx_cfg`. Constants define firmware command IDs for RoCE/common/DCBX subsystems, maximum QP/CQ/STag counts, EQ/MQ lengths, page-count limits, CQE status values, WQE opcodes, QP states, and async event codes.

Control flow: the file is declarative but drives every hardware control path. `ocrdma_hw.c` uses these definitions to initialize mailbox headers, build page lists, choose embedded versus non-embedded commands, ring doorbells, decode EQEs and MQ CQEs, map firmware async events to RDMA events, query device limits, and pack QP path parameters. Verbs and completion paths interpret WQEs/CQEs according to this layout, while stats/debugfs interpret the RDMA stats response structures.

State and persistence: this header does not own runtime state, but it defines the firmware-visible persistent state layout: queue IDs, PD IDs, QP IDs, SRQ IDs, lkeys/rkeys, AH table entries, CQ/EQ/MQ ring entries, WQE/CQE contents, stats counters, and DCBX state snapshots. Structure packing and field widths are part of the device ABI and must stay stable relative to firmware.

Dependencies/integration: included by `ocrdma_hw.h` and indirectly by most OCRDMA modules. It relies on kernel integer types, `BIT()`, endian annotations for Ethernet/GRH fields, and firmware behavior documented only through these constants. It is the shared vocabulary between RDMA core-facing code and the BE/RoCE firmware mailbox interface.

Risks and test signals: any wrong mask, shift, structure size, or endian assumption can corrupt firmware commands or misdecode completions. Notable sharp edges include many overlapping bit fields, mixed embedded/non-embedded response headers, packed network headers, a typo-like `OCRDMA_MAX_WQE_MEM_SIZE` reference to `OCRDMA_MIN_HQ_PAGE_SIZE`, and separate Lancer/SKH-R queue/CQ conventions. Test by building all OCRDMA objects, checking `sizeof()`/offset expectations against firmware documentation where available, exercising mailbox commands across ASIC generations, validating big-endian command buffers, and decoding real CQE/async/stats samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_sli.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_stats.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_stats.c

Purpose: debugfs and PMA statistics support for OCRDMA. It allocates the firmware stats mailbox buffer and a text scratch buffer, fetches RDMA statistics through `ocrdma_mbx_rdma_stats()`, formats groups of counters for debugfs files, provides a reset control file, and populates IB PMA port counters from firmware TX/RX stats.

Important APIs/types/functions: exported functions are `ocrdma_alloc_stats_resources()`, `ocrdma_release_stats_resources()`, `ocrdma_add_port_stats()`, `ocrdma_rem_port_stats()`, `ocrdma_init_debugfs()`, `ocrdma_rem_debugfs()`, and `ocrdma_pma_counters()`. Internal formatters include resource, RX, TX, WQE, doorbell error, RX/TX QP error, TX/RX debug word dumps, and driver debug stats. `ocrdma_dbgfs_ops_read()` and `ocrdma_dbgfs_ops_write()` implement the debugfs ABI, while `ocrdma_update_stats()` throttles firmware stats refreshes to once per elapsed second.

Control flow: device resource allocation initializes `stats_lock`, allocates a coherent mailbox payload sized for request or response, and allocates a 4 KiB debugfs text buffer. `ocrdma_add_port_stats()` creates a per-PCI-device debugfs directory under `ocrdma` and one file per stats type, each with an `ocrdma_stats` descriptor as private data. A read locks `stats_lock`, refreshes stats if enough time elapsed, chooses the formatter by type, and uses `simple_read_from_buffer()` with no partial-read support. Writing nonzero to `reset_stats` issues the stats mailbox command with reset set. PMA counter generation calls the same refresh path and writes big-endian packet/data counters into the MAD.

State and persistence: `dev->stats_mem.va` stores the latest firmware stats response and is reused as the request buffer for mailbox fetches. `dev->stats_mem.debugfs_mem` is a shared per-device scratch buffer protected by `stats_lock`. `dev->last_stats_time` controls refresh throttling. Resource counters for PDs are patched from the software PD manager after firmware stats fetches when preallocation is active. Debugfs dentries are rooted globally in `ocrdma_dbgfs_dir` and per device in `dev->dir`.

Dependencies/integration: depends on debugfs, user copy helpers, jiffies, RDMA PMA MAD structures, OCRDMA hardware mailbox stats command, SLI stats layouts, and software counters maintained by CQE/async handling and PD allocation code. It is initialized from module init and device add in `ocrdma_main.c`, and PMA consumers reach it through MAD processing.

Risks and test signals: `ocrdma_alloc_stats_resources()` leaks the coherent stats buffer if debugfs scratch allocation fails because it returns false without freeing `mem->va`; test allocation-failure unwind. The 4 KiB text buffer can truncate large stat groups, with `ocrdma_add_stat()` logging and silently skipping entries after overflow. Reads require the user buffer to be at least `strlen(data)` and reject partial reads with `-ENOSPC`, which can surprise standard tools with small buffers. Test concurrent debugfs reads, reset while reads occur, once-per-second refresh behavior, PMA counters after mailbox failure, stats fallback preservation in `ocrdma_mbx_rdma_stats()`, and debugfs cleanup when the root directory is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_stats.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_stats.h

Purpose: internal stats/debugfs header for OCRDMA. It declares the debugfs text-buffer size, enumerates all debugfs stats file types, and exposes stats lifecycle, per-port debugfs, and PMA counter functions to the rest of the driver.

Important APIs/types/functions: `OCRDMA_MAX_DBGFS_MEM` fixes each device's debugfs formatting buffer at 4096 bytes. `enum OCRDMA_STATS_TYPE` assigns identifiers for resource, RX, WQE, TX, doorbell error, RX/TX QP error, TX/RX debug, driver debug, and reset stats. Prototypes cover global debugfs root creation/removal, per-device stats memory allocation/release, per-port stats file add/remove, and `ocrdma_pma_counters()`.

Control flow: `ocrdma_main.c` calls `ocrdma_init_debugfs()` at module init and `ocrdma_rem_debugfs()` at exit. Device add calls `ocrdma_alloc_stats_resources()` before registration and `ocrdma_add_port_stats()` after link query; removal reverses this through `ocrdma_rem_port_stats()` and `ocrdma_release_stats_resources()`. MAD handling calls `ocrdma_pma_counters()` to fill standard port counters.

State and persistence: no data is defined directly in this header, but the enum values are stored in per-device `struct ocrdma_stats` instances and used as dispatch keys by `ocrdma_stats.c`. The buffer size constant constrains persistent debugfs scratch memory allocated in `dev->stats_mem`.

Dependencies/integration: includes `linux/debugfs.h`, `ocrdma.h`, and `ocrdma_hw.h`, creating a dependency cycle where stats declarations also see hardware mailbox prototypes and SLI layouts. It exposes `struct ib_mad` usage through the PMA prototype.

Risks and test signals: adding a new enum value requires matching debugfs descriptor initialization and read dispatch or reads will fail with `-EFAULT`. Changing `OCRDMA_MAX_DBGFS_MEM` affects stackless formatting assumptions and user-visible debugfs output length. Test compile coverage for include cycles, debugfs file creation for every enum type, PMA counter calls with stats disabled or allocation failed, and cleanup paths when debugfs root creation returns NULL or an error dentry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_stats.h -->
