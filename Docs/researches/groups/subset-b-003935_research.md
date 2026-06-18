# subset-b-003935 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_datapath.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_datapath.c

Purpose: Ionic RoCE datapath verbs implementation. It posts send and receive work requests, prepares firmware WQEs, polls completion queues, translates device completion status into `ib_wc`, handles CQ notification arming, and drains flushed QPs after error or destroy transitions.

Important APIs/functions: exported verbs hooks are `ionic_post_send()`, `ionic_post_recv()`, `ionic_poll_cq()`, and `ionic_req_notify_cq()`. Internal helpers include `ionic_next_cqe()`, `ionic_poll_recv()`, `ionic_poll_send()`, `ionic_comp_msn()`, `ionic_comp_npg()`, `ionic_flush_send_many()`, `ionic_flush_recv_many()`, WQE preparation helpers for send, UD send, RDMA, atomic, local invalidate, fast register MR, and receive posting.

Control flow: CQ polling alternates across per-UDMA CQs in a `struct ionic_vcq`, first emits send completions already made visible by earlier CQEs, then consumes device CQEs while color matches, then drains flush lists. Receive CQEs validate QP lookup, queue state, WQE ID, and posted metadata before filling `ib_wc`. Send completions are split between MSN completions for remote progression and NPG completions for local progression; `ionic_poll_send()` emits only signaled or error completions. Posting validates QP state and queue capacity, prepares WQEs by opcode, advances producer indices, reserves CQ credits, and rings SQ/RQ doorbells.

State and persistence: state is in `struct ionic_qp` queue producers/consumers, SQ metadata, RQ free-list metadata, MSN sequence arrays, flush flags, and CQ lists. `struct ionic_cq` tracks color, credit, arm producer counters, and pending poll/flush lists. The file does not persist to disk; hardware-visible state is coherent queue memory and doorbell writes.

Dependencies and integration: depends on `ionic_fw.h` ABI layouts/opcodes, `ionic_queue.h` ring helpers, `ionic_ibdev.h` object containers, RDMA core work request/completion structures, xarray QP lookup, DMA barriers, and Ionic doorbell registers from the Ethernet device integration.

Risks: queue ownership relies on color bits, producer/consumer arithmetic, and CQ credit accounting. Error CQEs move QPs to flush lists, so missed list transitions can stall completions. `ionic_prep_atomic()` calls `ionic_prep_common()` after filling the atomic body, which reuses common SGL preparation and must remain layout-compatible. Inline posting copies from user-provided virtual addresses already accepted by RDMA core, so opcode and size validation are the main guardrails. Several invalid device completion cases return `-EIO` after warnings.

Test signals: RDMA send/recv, RDMA read/write, immediate data, invalidation, atomics, fast-reg MR, UD/GSI receive metadata, CQ arming with `IB_CQ_REPORT_MISSED_EVENTS`, queue-full posting, signaled versus unsignaled sends, and QP error flush behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_datapath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_fw.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_fw.h

Purpose: firmware ABI contract for the Ionic RDMA driver. It defines memory key encoding, MR/QP flag translations, device status translation, WQE/CQE/EQE layouts, admin command payloads, opcodes, stat descriptors, and layout helper functions consumed by control path, datapath, and stats code.

Important APIs/types: `struct ionic_sge`, `union ionic_v1_pld`, `struct ionic_v1_wqe`, `struct ionic_v1_cqe`, `struct ionic_v1_admin_wqe`, admin command structs for AH/MR/CQ/QP/stat operations, `struct ionic_v1_eqe`, and `struct ionic_v1_stat`. Helpers include `ionic_mrid()`, `ionic_mrid_index()`, `to_ionic_mr_flags()`, `to_ionic_qp_flags()`, `from_ionic_qp_flags()`, `ionic_to_ib_status()`, QP type/state translators, CQE/EQE field extractors, and WQE stride capacity helpers.

Control flow: higher layers translate RDMA core state into ABI values with the inline helpers, fill packed admin or data WQEs, and decode CQEs/EQEs by bitfields. Datapath code selects v1 or v2 opcodes via the RDMA version, computes maximum SGE/inline capacities from queue stride, and uses CQE status/type/QID helpers during polling. Stats code normalizes and reads `ionic_v1_stat` descriptors.

State and persistence: no mutable runtime state is stored here. The header defines persistent wire and DMA memory formats shared with firmware. `static_assert()` guards admin payload sizes against accidental ABI drift.

Dependencies and integration: includes Linux kernel helpers and RDMA verbs definitions. It is included by Ionic RDMA object, datapath, page-table, and stats files and must match firmware, device identity capabilities, and RDMA core status semantics.

Risks: packed structures, endian annotations, and bit shifts are hardware ABI. Any change can silently break WQE/CQE interpretation. `to_ionic_qp_state()` returns `0` for unsupported states, which maps to reset-like behavior if caller validation is weak. Capacity helpers use pointer arithmetic from synthetic base addresses, so stride and expanded-doorbell assumptions must stay aligned with hardware.

Test signals: compile-time size assertions, admin command success for create/query/modify/destroy paths, datapath opcode coverage on RDMA version 1 and 2 devices, CQE status translation tests, and stats descriptor decoding with all endian/type variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_hw_stats.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_hw_stats.c

Purpose: RDMA hardware statistics and RDMA counter support for Ionic. It discovers firmware-provided statistic descriptors, exposes global port stats through RDMA core, and supports per-counter QP aggregation by issuing admin commands for each bound QP.

Important APIs/functions: public entry points are `ionic_stats_init()` and `ionic_stats_cleanup()`. RDMA device ops installed from this file include `alloc_hw_port_stats`, `get_hw_stats`, `counter_alloc_stats`, `counter_dealloc`, `counter_bind_qp`, `counter_unbind_qp`, and `counter_update_stats`. Internal helpers normalize `struct ionic_v1_stat`, fill `rdma_stat_desc`, decode typed values, and issue stats admin WQEs.

Control flow: initialization checks `lif_cfg.stats_type`. Global stats allocate a descriptor buffer and value buffer, DMA-map the descriptor page, send `IONIC_V1_ADMIN_STATS_HDRS`, normalize names/types/offsets, and install port stat ops. QP counters allocate a `struct ionic_counter_stats`, request `IONIC_V1_ADMIN_QP_STATS_HDRS`, initialize an xarray of counters, and install counter ops. A stats read DMA-maps the value page, sends a values command, then decodes each descriptor offset into RDMA counters. QP counter reads iterate all QPs bound to a counter and sum returned values.

State and persistence: device-level state lives in `dev->hw_stats`, `dev->hw_stats_buf`, `dev->hw_stats_hdrs`, and `dev->hw_stats_count`. Per-counter state is kept in `dev->counter_stats`, xarray entries, `struct ionic_counter` value pages, and QP list membership. No persistent storage exists beyond driver lifetime.

Dependencies and integration: uses Ionic admin queue submission/waiting, DMA mapping, RDMA hardware stats and counter APIs, xarray allocation, and QP list entries in `struct ionic_qp`.

Risks: descriptor offsets are firmware-provided; `ionic_v1_stat_val()` bounds and alignment checks invalid entries but returns all-ones on bad layout, which can look like a huge counter. Counter QP lists are updated without local locking in this file, so correctness depends on RDMA counter core serialization and QP teardown ordering. Admin opcode availability is checked against `lif_cfg.admin_opcodes`.

Test signals: devices advertising global stats, devices advertising QP stats, invalid port reads, counter bind/unbind/dealloc, aggregation across multiple QPs, admin timeout/error handling, and cleanup after partial initialization failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_hw_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_ibdev.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_ibdev.c

Purpose: Ionic RDMA ib_device registration and device lifecycle glue. This file binds an Ethernet Ionic LIF to the RDMA core, fills device attributes and ops, initializes resource allocators and tables, creates admin/event infrastructure, registers with ib_core, and tears everything down on remove/reset.

Important APIs/functions: the file provides the driver-facing add/remove/reset hooks for the Ionic RDMA device and wires the `ib_device_ops` table to control-path, datapath, mmap, MR/MW, AH, CQ, QP, ucontext, PD, query, port, and stats helpers declared in `ionic_ibdev.h`.

Control flow: probe-style setup obtains LIF configuration via `ionic_fill_lif_cfg()`, allocates and initializes `struct ionic_ibdev`, seeds xarrays and ID allocators, creates admin queues/EQs, sets RDMA core attributes, registers verbs ops, initializes optional stats, then registers the ib_device. Teardown reverses registration, disables/cleans stats, destroys admin/EQ resources, drains reset/admin work, and frees ID/xarray state. Reset paths coordinate with admin state so in-flight work is paused or killed before objects are re-created or failed.

State and persistence: central state is `struct ionic_ibdev`: `lif_cfg`, QP/CQ xarrays, resource ID allocators, admin/EQ vectors, reset work, admin delayed work, stats pointers, and UDMA allocation cursors. State exists for the lifetime of the RDMA device and is rebuilt from LIF identity after reprobe/reset.

Dependencies and integration: integrates with Linux RDMA core, the Ionic Ethernet LIF/device identity, admin/control/datapath/stat modules, workqueues, xarrays, IDA allocators, and netdev/lif helper functions.

Risks: lifecycle ordering is the main risk: ib_device unregister must happen before freeing queues and resource tables visible to verbs callbacks. Reset/admin work needs clear state transitions to avoid completing commands against freed objects. Device limits must match firmware identity fields or user-visible caps can exceed allocatable resources.

Test signals: module probe/remove, RDMA device visibility in `ibv_devices`, uverbs context creation, reset during active QPs/CQs, admin queue failure injection, stats ops installation, and leak checks for xarrays/IDAs/workqueues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_ibdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_ibdev.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_ibdev.h

Purpose: central internal header for the Ionic RDMA driver. It defines driver limits, the main `struct ionic_ibdev`, object wrappers for RDMA core types, admin/EQ/CQ/QP/MR/AH state, helper conversions, and prototypes spanning admin, control path, datapath, stats, and page-table code.

Important APIs/types: key types are `struct ionic_ibdev`, `ionic_eq`, `ionic_aq`, `ionic_admin_wr`, `ionic_ctx`, `ionic_tbl_buf`, `ionic_pd`, `ionic_cq`, `ionic_vcq`, `ionic_qp`, `ionic_sq_meta`, `ionic_rq_meta`, `ionic_ah`, `ionic_mr`, `ionic_counter_stats`, and `ionic_counter`. Inline helpers convert RDMA core pointers back to Ionic containers, select user or kernel doorbell IDs, detect local-only opcodes, and complete QP/CQ krefs.

Control flow: every implementation file includes this header to share object layout and function contracts. RDMA core calls enter object wrappers, helpers recover Ionic private state, control path allocates resources and queues, datapath posts/polls them, stats binds counters to QPs, and page-table helpers fill MR/CQ/QP DMA mapping descriptors.

State and persistence: the header documents all runtime state ownership. `ionic_ibdev` owns global tables, ID allocators, admin/EQ vectors, reset state, and stats. `ionic_qp` owns SQ/RQ queues, metadata, flush state, CMB mappings, user umems, and addressing metadata. `ionic_cq` owns poll/flush queues, credits, color, arm counters, and optional umem.

Dependencies and integration: includes RDMA core headers, user ABI, Ionic Ethernet API/register headers, and local firmware/queue/resource/LIF config headers. It is the private ABI among all Ionic RDMA translation units.

Risks: broad sharing means layout changes can affect concurrency and teardown in multiple files. List heads embedded in QP/CQ objects must be initialized and removed consistently. The header repeats `IONIC_SPEC_HIGH`, which is harmless but signals the need for careful constants review. Conversion helpers assume RDMA core objects are always embedded in the declared wrappers.

Test signals: full driver build, sparse/lockdep checks, QP/CQ create/destroy with user and kernel queues, reset teardown, mmap lifecycle, and all verbs ops resolving to declared prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_ibdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_lif_cfg.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_lif_cfg.c

Purpose: adapter between the Ionic Ethernet LIF identity and the RDMA driver's compact LIF configuration. It extracts firmware identity limits, queue type identifiers, doorbell resources, stats support, UDMA layout, page-size capabilities, and expanded-doorbell support.

Important APIs/functions: `ionic_fill_lif_cfg()` is the main initializer. `ionic_lif_netdev()` returns a held netdev reference. `ionic_lif_fw_version()` copies the firmware version string. `ionic_lif_asic_rev()` exposes the ASIC revision. `ionic_get_expdb()` is an internal helper that converts physical CMB expanded-doorbell page availability into RDMA flags.

Control flow: `ionic_fill_lif_cfg()` reads `lif->ionic->ident.lif.rdma` and device identity, stores device and LIF pointers, kernel doorbell page, interrupt control base, physical doorbell BAR address, queue bases/counts/types, resource counts, RDMA/admin opcode limits, stats type, UDMA shift/count, maximum stride, and expanded-doorbell capability. For RDMA identity version at least 2.1 it trusts firmware `page_size_cap`; older identities use a hard-coded 4K/2M/1G mask.

State and persistence: the function populates caller-owned `struct ionic_lif_cfg`, which becomes part of `struct ionic_ibdev`. It snapshots firmware and LIF configuration at RDMA device setup time; it does not allocate long-lived resources except the netdev reference in `ionic_lif_netdev()`.

Dependencies and integration: depends on Ionic Ethernet driver internals (`ionic.h`, `ionic_lif.h`), PCI BAR/device identity fields, RDMA identity structures, and local config constants in `ionic_lif_cfg.h`.

Risks: values are trusted from device identity and must be validated by later resource creation. `udma_count` is currently forced to two, so hardware with a different future UDMA count would require updates. Callers of `ionic_lif_netdev()` must balance the `dev_hold()`.

Test signals: probe on older and newer firmware identity versions, page-size capability reporting, expanded-doorbell feature combinations, queue count clamping by admin setup, and netdev reference leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_lif_cfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_lif_cfg.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_lif_cfg.h

Purpose: LIF configuration data contract for Ionic RDMA. It defines version/page-size constants, expanded-doorbell capability bits, `struct ionic_lif_cfg`, and the small set of LIF helper prototypes used by the RDMA device setup path.

Important APIs/types: `IONIC_VERSION()` composes major/minor values for identity checks. `IONIC_PAGE_SIZE_SUPPORTED` is the fallback 4K/2M/1G page-size mask. `IONIC_EXPDB_*` bits describe supported expanded-doorbell WQE sizes. `struct ionic_lif_cfg` stores hardware device pointers, LIF indices, kernel doorbell ID/page, interrupt control MMIO, physical doorbell base, page/resource limits, queue bases/counts/types, UDMA grouping, RDMA/admin opcode counts, maximum stride, and expanded-doorbell flags.

Control flow: `ionic_fill_lif_cfg()` populates the structure from an Ethernet LIF before RDMA resources are created. Other Ionic RDMA files then use this immutable-ish configuration for DMA mapping device selection, doorbell ringing, queue ID allocation, stats/admin opcode checks, and user-visible capability decisions.

State and persistence: all fields are runtime configuration cached from firmware/LIF identity. The header itself has no code-managed storage. `dbpage`, `intr_ctrl`, and `db_phys` point into PCI/device resources owned by the Ethernet Ionic device.

Dependencies and integration: declares opaque `struct ionic_lif` use and returns `struct net_device`. The implementation includes Ethernet driver headers; RDMA callers include only this contract.

Risks: the include guard lacks a `#define _IONIC_LIF_CFG_H_`, so repeated inclusion in one translation unit would not be prevented by this file alone. The current source appears to rely on include graph behavior and should be fixed if touched. Hardware capability fields must stay synchronized with firmware identity definitions.

Test signals: clean build with repeated includes, RDMA probe using all queue/resource fields, stats opcode gating, and feature reporting for CMB/expanded-doorbell paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_lif_cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_pgtbl.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_pgtbl.c

Purpose: page-table buffer construction for Ionic RDMA objects. It converts either a single DMA address or an RDMA user memory object into the firmware page-table form used by MR, CQ, and QP creation and fast registration.

Important APIs/functions: `ionic_pgtbl_init()` initializes a `struct ionic_tbl_buf`; `ionic_pgtbl_page()` appends a DMA page; `ionic_pgtbl_dma()` returns either the page-table DMA address or direct DMA address plus VA offset; `ionic_pgtbl_off()` returns the offset for multi-page tables; `ionic_pgtbl_unbuf()` unmaps/frees the table buffer.

Control flow: initialization zeros the buffer, derives page count and page-size log from `ib_umem` when present, validates `limit`, allocates and DMA-maps an array of little-endian DMA entries only when more than one page is needed, then fills entries from `rdma_umem_for_each_dma_block()` or a single DMA address. Error paths unmap and clear the buffer.

State and persistence: `struct ionic_tbl_buf` records page count, limit, size, table virtual address, table DMA address, and page-size log. A one-page/direct mapping uses `tbl_dma` without allocating `tbl_buf`; multi-page mappings allocate a DMA-mapped table until `ionic_pgtbl_unbuf()`.

Dependencies and integration: uses RDMA umem block iterators, Linux DMA mapping, and Ionic firmware command fields that expect table DMA, map count, page-size log, and offsets. MR registration and queue creation consume this structure.

Risks: `order_base_2(page_size)` assumes valid power-of-two page sizes selected by callers. Single-page direct mode and multi-page table mode share `tbl_dma`, so callers must use `ionic_pgtbl_dma()`/`ionic_pgtbl_off()` rather than interpreting fields directly. `ionic_pgtbl_page()` enforces the limit but does not validate DMA alignment.

Test signals: user MR registration with one page and many pages, CQ/QP user queue mapping, fast-reg MR after `ib_map_mr_sg`, DMA mapping failure unwinds, and page sizes across supported 4K/2M/1G capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_pgtbl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_queue.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_queue.c

Purpose: coherent DMA ring allocation for Ionic RDMA queues. It initializes queue geometry, allocates queue memory, and frees it during teardown.

Important APIs/functions: `ionic_queue_init()` validates requested depth and stride, computes power-of-two depth/stride logs, enforces at least page-sized allocation, sets size and mask, allocates coherent DMA memory, checks page alignment, and initializes producer/consumer/doorbell state. `ionic_queue_destroy()` frees the coherent allocation.

Control flow: callers pass logical usable depth and element stride. The implementation adds one entry to preserve a hole for full/empty detection, rounds depth and stride up with `order_base_2()`, raises depth when necessary so the total queue is at least one page, rejects log values above 16, and allocates `BIT_ULL(depth_log2 + stride_log2)` bytes. The ring mask is `2^depth_log2 - 1`, so actual queue capacity is mask entries.

State and persistence: initialized state is stored in `struct ionic_queue`: size, DMA address, CPU pointer, producer, consumer, mask, depth/stride logs, and doorbell bits. Memory persists until explicit destroy and is visible to the device as coherent DMA.

Dependencies and integration: depends on Linux coherent DMA allocation and helper math. `ionic_queue.h` inline helpers perform all subsequent indexing, producer/consumer movement, and doorbell value construction.

Risks: destroy assumes `q->ptr`/`q->size` are valid from successful init. The requested stride is rounded up to a power of two, so firmware queue stride must be programmed with `stride_log2`, not the original byte stride. Capacity differs from raw allocation depth because one slot is reserved.

Test signals: queue creation for minimum depth, maximum depth/stride rejection, page-sized small queues, DMA allocation failure, and create/destroy of AQ/EQ/CQ/SQ/RQ paths under probe/remove and reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_queue.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_queue.h

Purpose: ring-buffer abstraction for Ionic RDMA driver/device queues. It defines queue geometry, doorbell constants, allocation prototypes, and inline helpers for queue occupancy, indexing, wrap/color tracking, and doorbell values.

Important APIs/types: `struct ionic_queue` stores coherent memory, DMA address, producer/consumer indices, ring mask, depth/stride logs, and doorbell bits. Helpers include `ionic_queue_empty()`, `ionic_queue_length()`, `ionic_queue_length_remaining()`, `ionic_queue_full()`, `ionic_color_wrap()`, `ionic_queue_at()`, `ionic_queue_at_prod()`, `ionic_queue_at_cons()`, `ionic_queue_next()`, producer/consumer increment helpers, `ionic_queue_dbell_init()`, and `ionic_queue_dbell_val()`.

Control flow: queue users initialize memory with `ionic_queue_init()`, prepare entries at `prod` or inspect entries at `cons`, advance indices with mask arithmetic, and ring doorbells using the qid-initialized doorbell value ORed with the producer index. CQ polling uses `ionic_color_wrap()` to track device-owned CQE wrap state.

State and persistence: queue state lives entirely in `struct ionic_queue`. Producer and consumer semantics are direction-specific; comments note several helpers are valid only for to-device queues. Doorbell state persists as a precomputed qid field plus current producer bits.

Dependencies and integration: includes MMIO and Ionic register macros for doorbells. Used by admin queues, event queues, CQs, SQs, RQs, and datapath completion logic.

Risks: helpers do not bounds-check entry indices or enforce full/empty preconditions. Pointer arithmetic on `void *` is a GNU C kernel extension. Misusing to-device helpers on from-device queues can corrupt CQ interpretation. Color wrap assumes producer advances exactly as CQEs are consumed.

Test signals: producer/consumer wrap tests, queue-full and queue-empty behavior at mask boundaries, doorbell values for expected QIDs, CQ color toggling across wrap, and static analysis for callers holding required locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_res.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_res.h

Purpose: resource ID allocation helpers for Ionic RDMA and mapping helpers for UDMA-aware queue IDs. It wraps Linux IDA allocation and defines transforms between compact bit IDs and firmware queue IDs.

Important APIs/types: `struct ionic_resid_bits` owns an `ida` and size limit. Inline helpers are `ionic_resid_init()`, `ionic_resid_destroy()`, `ionic_resid_get_shared()`, `ionic_resid_get()`, `ionic_resid_put()`, `ionic_bitid_to_qid()`, and `ionic_qid_to_bitid()`.

Control flow: resource users initialize an allocator with a capacity, allocate IDs either across the full range or a caller-specified shared range, free IDs on object destruction, and destroy the IDA at device teardown. Queue ID helpers rearrange the UDMA bit and queue group bits so allocation can scan UDMA-specific halves while firmware sees queue IDs in group order.

State and persistence: ID allocation state is held by the IDA in `struct ionic_resid_bits` for the RDMA device lifetime. Queue ID mapping is stateless bit manipulation based on `qgrp_shift` and `half_qid_shift` from LIF configuration.

Dependencies and integration: depends on Linux IDA/IDR and bit helpers. `struct ionic_ibdev` owns allocators for doorbell IDs, PDs, AHs, MRs, QPs, and CQs; QID transforms are used for CQ/QP allocation across UDMA queue groups.

Risks: `ionic_resid_put()` trusts the ID is currently allocated. Queue transforms assume valid shifts and queue counts that are powers of two in the expected layout. Incorrect `half_qid_shift` or `qgrp_shift` can allocate queues on the wrong UDMA and break CQ/QP affinity.

Test signals: ID exhaustion/reuse, shared-range allocation boundaries, destroy with no leaks, round-trip `qid -> bitid -> qid` for all supported queue IDs, and UDMA-balanced QP/CQ allocation under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_res.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/Kconfig

Purpose: Kconfig entry for the Intel Ethernet Protocol Driver for RDMA (`INFINIBAND_IRDMA`), covering Intel IPU E2000, E810, and X722 RDMA support.

Important symbols: `INFINIBAND_IRDMA` is a tristate option with help text describing RoCEv2 and iWARP device support. It depends on `INET`, `IPV6 || !IPV6`, `PCI`, and the Ethernet drivers `IDPF`, `ICE`, and `I40E`. It selects `GENERIC_ALLOCATOR`, `AUXILIARY_BUS`, and `CRC32`.

Control flow: kernel configuration determines whether the irdma driver is built in, built as a module, or omitted. Dependency selection ensures networking, PCI, auxiliary device support, allocator support, checksum helpers, and the required Intel Ethernet providers are available before compiling the RDMA driver.

State and persistence: no runtime state. This file controls build-time configuration and module availability.

Dependencies and integration: pairs with the irdma Makefile and parent InfiniBand Kconfig tree. The hard dependency on multiple Ethernet drivers reflects that irdma attaches through Intel networking devices and auxiliary bus plumbing.

Risks: depending on all listed Ethernet drivers may make the RDMA driver unavailable in configurations that only enable one supported NIC family. Kconfig dependency drift can surface as unresolved symbols or missing auxiliary devices during build/probe.

Test signals: `olddefconfig`, `allmodconfig`, module build with IPv6 enabled and disabled, and probe tests on IPU E2000/E810/X722 platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/Makefile

Purpose: build recipe for the Intel irdma RDMA driver. It maps `CONFIG_INFINIBAND_IRDMA` to the composite `irdma.o` module and lists all translation units that make up the driver.

Important entries: `obj-$(CONFIG_INFINIBAND_IRDMA) += irdma.o` controls inclusion. `irdma-objs` includes connection management (`cm.o`), control/HMC/hardware setup, generation-specific i40iw and ig3rdma/icrdma files, main device registration, PBLE, PUDA, trace, UDA, user/kernel verbs, utilities, virtchnl, and work scheduler code. `CFLAGS_trace.o = -I$(src)` ensures trace compilation can include local generated/header paths.

Control flow: Kbuild compiles each object in `irdma-objs` and links them into one built-in or module object according to Kconfig. The object order expresses broad dependencies but runtime initialization is still controlled by module/device code.

State and persistence: no runtime state; this file determines compile/link composition.

Dependencies and integration: integrates with Linux Kbuild and the RDMA hardware driver directory. Its object list must remain synchronized with internal headers and exported functions across irdma source files.

Risks: missing an object yields unresolved symbols or silently absent feature paths. Adding a new trace user may require CFLAGS/header updates. Whitespace alignment is mixed tabs/spaces but acceptable to make.

Test signals: incremental and clean kernel builds, `modpost` symbol checks, build with `INFINIBAND_IRDMA=m` and `=y`, and tracepoint compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/cm.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/cm.c

Purpose: Intel irdma iWARP connection manager. It implements the TCP-like handshake over ILQ/PUDA packets, MPA v1/v2 negotiation, active and passive iw_cm APIs, listener/qhash/APBVT management, ARP/neighbor resolution, retransmission/close timers, QP offload transition, disconnect processing, and interface-change teardown.

Important APIs/functions: public entry points include `irdma_accept()`, `irdma_reject()`, `irdma_connect()`, `irdma_create_listen()`, `irdma_destroy_listen()`, `irdma_receive_ilq()`, `irdma_setup_cm_core()`, `irdma_cleanup_cm_core()`, `irdma_cm_teardown_connections()`, `irdma_if_notify()`, `irdma_schedule_cm_timer()`, `irdma_send_ack()`, `irdma_send_reset()`, `irdma_rem_ref_cm_node()`, VLAN/loopback helpers, and connection qhash helpers. Internal clusters handle frame building, MPA parsing, TCP option parsing, node/listener creation, state transitions, timers, events, and disconnect workers.

Control flow: active connect builds a CM node from iw_cm addresses, resolves ARP/neighbor, adds established qhash/APBVT filters, creates an AH when needed, sends SYN, processes SYN/ACK, sends MPA request, parses MPA reply, offloads QP context, sends RTT/read0 as needed, moves QP to RTS, and reports `CONNECT_REPLY`. Passive listen installs SYN qhash filters, creates nodes on incoming SYN, replies SYN/ACK after AH setup, parses MPA request, reports `CONNECT_REQUEST`, then `irdma_accept()` builds an MPA reply LSMM, configures QP TCP/iWARP context, moves to RTS, and reports `ESTABLISHED`. RST/FIN/ACK handlers update TCP sequence state and drive close states. Events are posted to an ordered workqueue with a CM node reference.

State and persistence: CM state lives in `struct irdma_cm_core`, `struct irdma_cm_node`, `struct irdma_cm_listener`, APBVT entries, qhash filters, AHs, timers, and QP references. Nodes are RCU-hashed by port tuple and refcounted. Listeners maintain child wildcard listeners and pending-accept counts. No disk persistence exists; hardware state includes qhash filters, APBVT ports, AHs, ARP table entries, and QP offload context.

Dependencies and integration: depends on RDMA iw_cm, QP modify/offload paths, PUDA ILQ send/receive buffers, ARP table management, qhash management, APBVT port filters, Linux IPv4/IPv6 routing and neighbor APIs, VLAN/netdevice APIs, workqueues, timers, RCU, and tracepoints.

Risks: this is concurrency and state-machine sensitive. Refcounts span timers, event work, receive processing, QP references, and RCU hash removal. Retransmission entries hold PUDA buffers with their own refcounts. Passive accept/reject uses `passive_state` to suppress duplicate reset handling. Wildcard listeners create child qhash nodes per interface address, so interface notification must keep filters synchronized. Sequence/window validation is simplified for handshake traffic, so malformed packet tests matter. Error unwinds after QoS, qhash, APBVT, AH, and CM node allocation must leave hardware filters clean.

Test signals: active/passive iWARP connection establishment, MPA v1 fallback after reset, MPA v2 IRD/ORD negotiation including RDMA0 read/write, private-data length limits, SYN backlog drops, retransmission timeout, reject path, FIN simultaneous close, RST during each major state, IPv4/IPv6/VLAN/DCB priority behavior, wildcard listen interface up/down, reset teardown, and lockdep/KASAN under connect/disconnect stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/cm.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/cm.h

Purpose: public/internal declarations for the irdma iWARP connection manager. It defines MPA protocol constants, TCP option constants, CM node/listener/event states, timer and address structures, node/listener/core state containers, and prototypes used by other irdma modules.

Important APIs/types: protocol types include `struct ietf_mpa_v1`, `struct ietf_mpa_v2`, `struct ietf_rtr_msg`, TCP option structs, and `union all_known_options`. State enums include `irdma_cm_node_state`, `mpa_frame_ver`, `send_rdma0`, `irdma_tcpip_pkt_type`, `irdma_cm_listener_state`, and `irdma_cm_event_type`. Core runtime types are `irdma_timer_entry`, `irdma_cm_tcp_context`, `irdma_apbvt_entry`, `irdma_cm_listener`, `irdma_cm_node`, `irdma_cm_info`, `irdma_cm_event`, and `irdma_cm_core`.

Control flow: `cm.c` and neighboring modules use this header to schedule retransmit/close timers, create/listen/connect/accept/reject/destroy iw_cm sessions, process interface notifications, perform ARP table lookups, send ACKs, manage CM node references, and add established qhashes. `irdma_cm_core` function pointers select generation-specific frame formation and AH handling during CM setup.

State and persistence: the header lays out all in-memory CM state: listener lists, CM hash tables, APBVT hash table, TCP timer, event workqueue, stats counters, node TCP/MPA metadata, private-data buffers, AH/qhash/APBVT ownership flags, and refcounts. These persist while the device and individual CM sessions/listeners exist.

Dependencies and integration: relies on RDMA iw_cm IDs, irdma device/QP/PUDA/AH types from surrounding headers, Linux networking address types, workqueues, timers, hashtables, RCU, refcounts, and VLAN/Ethernet constants.

Risks: structure layout is shared across multiple files, so field ownership and locking rules must remain clear. Several constants encode wire limits such as 512-byte private data and MPA header sizes. `DECLARE_HASHTABLE(..., 8)` gives 256 buckets despite `IRDMA_CM_HASHTABLE_SIZE` being 1024, so readers should not assume that macro controls the declared tables. Function prototypes include `irdma_cm_start()`/`irdma_cm_stop()` even though this file's visible implementation uses setup/cleanup names, implying definitions or legacy declarations elsewhere must be checked during refactors.

Test signals: compile coverage from all irdma objects, state transition coverage for every enum value used in `cm.c`, hash/list teardown under RCU, timer entry lifecycle, and ABI checks for MPA frame sizes/private data limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/cm.h -->
