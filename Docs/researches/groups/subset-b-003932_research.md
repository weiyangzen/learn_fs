# subset-b-003932 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/verbs_txreq.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/verbs_txreq.h

Purpose: Defines the HFI1 verbs transmit request wrapper that bridges RDMA verbs send state to the HFI1 SDMA transmit machinery. `struct verbs_txreq` embeds an `hfi1_sdma_header` and `sdma_txreq`, then carries the owning `rvt_qp`, active WQE, optional memory region, SGE state, selected SDMA engine, send context, header dword count, and current send size.

Important APIs/types/functions: `get_txreq()` is the fast path allocator from `dev->verbs_txreq_cache` with `GFP_ATOMIC | __GFP_NOWARN`, requiring `qp->slock`; it falls back to `__get_txreq()` when the cache allocation fails. `get_waiting_verbs_txreq()` converts an `iowait_work` queue head from `sdma_txreq` back to `verbs_txreq`; `verbs_txreq_queued()` delegates queue-state checks to `iowait_packet_queued()`. The file declares `hfi1_put_txreq()`, `verbs_txreq_init()`, and `verbs_txreq_exit()` for lifecycle management.

Control flow: Callers under the QP send lock request a txreq, get initialized QP/private context pointers, zero descriptor count for later descriptor-existence tests, set header type from QP private state, and clear SDMA flags before filling the packet. Queued txreqs are recovered through the embedded `sdma_txreq`.

State and persistence: State is transient per-send kernel memory. Persistent resources are the driver kmem cache initialized and destroyed by the declared init/exit helpers. The txreq references QP, WQE, MR, and SGE state but does not own them except through the later `hfi1_put_txreq()` release path.

Dependencies and integration: Depends on HFI1 verbs, SDMA, and iowait internals plus RDMA core `rvt_qp`/`rvt_swqe` data. It integrates with HFI1 QP private fields `s_sde`, `s_sendcontext`, and `hdr_type`.

Risks: Allocation is atomic and can fail under pressure; slow-path locking must avoid deadlock with `qp->slock`. Stale embedded pointers would be dangerous if a txreq outlives its QP/WQE lifetime, so release and iowait queue ownership are critical. Test signals include stress sends under memory pressure, iowait wakeups, SDMA descriptor accounting, and lockdep around QP send locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/verbs_txreq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/Kconfig

Purpose: Adds the kernel configuration switch for the Hisilicon Hip08 family RoCE driver. `CONFIG_INFINIBAND_HNS_HIP08` is a tristate option that builds the HNS RoCE hardware v2 module.

Important APIs/types/functions: This is Kconfig metadata rather than C code. The key symbol is `INFINIBAND_HNS_HIP08`, presented as "Hisilicon Hip08 Family RoCE support"; its module name is documented as `hns-roce-hw-v2`.

Control flow: Kernel configuration exposes the option only when architecture and bus prerequisites are met. Enabling it selects compilation through the adjacent Makefile.

State and persistence: Build-time state only. No runtime state is stored here, but the choice determines whether the driver is absent, built-in, or loadable as a module.

Dependencies and integration: Requires `ARM64` or `(COMPILE_TEST && 64BIT)`, plus `PCI` and `HNS3`. The explicit `HNS3` dependency ties the RDMA driver to the Hisilicon Ethernet stack used for RoCE netdev and hardware-service integration.

Risks: Incorrect dependency constraints could allow builds on unsupported platforms or hide valid compile-test coverage. Test signals include `allyesconfig`/`allmodconfig` on ARM64 and 64-bit compile-test targets, module name verification, and ensuring HNS3 symbols are available whenever this driver is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/Makefile

Purpose: Defines how the Hisilicon HNS RoCE hardware v2 driver is built and which source objects make up the module.

Important APIs/types/functions: The Makefile sets include paths into the HNS3 Ethernet driver directories and local source directory, then lists `hns-roce-hw-v2-objs`: main, command, PD, AH, HEM, MR, QP, CQ, allocation, doorbell, SRQ, restrack, debugfs, hardware v2, and bonding objects. `obj-$(CONFIG_INFINIBAND_HNS_HIP08)` binds the object aggregate to the Kconfig symbol.

Control flow: Kbuild compiles the listed objects into `hns-roce-hw-v2.o` when the config symbol is enabled. Include flags make HNS3 private headers visible to the RDMA driver.

State and persistence: Build metadata only. The object list is the persistence contract for which subsystems are linked into the module.

Dependencies and integration: Integrates directly with `drivers/net/ethernet/hisilicon/hns3`, `hns3pf`, and `hns3_common`. This reflects the driver coupling to HNAE3 handles, netdev state, and hardware mailbox/provider interfaces.

Risks: Missing object entries silently drop functionality at link time; stale include paths break cross-subsystem builds. Test signals include module build, modpost unresolved symbol checks, and verifying new features such as bonding/debugfs are included in the object aggregate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_ah.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_ah.c

Purpose: Implements address handle creation and query for HNS RoCE, translating RDMA core AH attributes into the driver's hardware address vector.

Important APIs/types/functions: `hns_roce_create_ah()` fills `struct hns_roce_ah.av`; `hns_roce_query_ah()` reconstructs `rdma_ah_attr` from that vector. `get_ah_udp_sport()` derives a RoCE UDP source port from the GRH flow label or a valid random port when no flow label is supplied.

Control flow: Creation reads GRH, port, SGID index, static rate, hop limit, flow label, UDP source port, traffic class, and SL. For RoCEv2 GIDs it asks hardware for DSCP-to-priority mapping and may replace SL with the mapped priority when the NIC uses DSCP TC mapping. It validates SL, copies destination GID and DMAC, records HIP08 VLAN fields, and optionally returns priority, TC mode, and DMAC to userspace.

State and persistence: AH state is stored in the in-memory `hns_roce_av` embedded in the AH. There is no firmware context allocation in this file; AH destruction is inline no-op in the header.

Dependencies and integration: Uses RDMA core AH/GRH helpers, `rdma_read_gid_l2_fields()`, HNS hardware `get_dscp`, `check_sl_valid()`, PCI revision checks, and DFX error counters. It depends on `hns_roce_hw_v2.h` ABI structures for userspace response shape.

Risks: HIP08 rejects userspace AH creation, so ABI behavior differs by revision. DSCP priority mapping failures other than `-EOPNOTSUPP` abort creation. VLAN extraction, SGID attributes, and SL validation are correctness-critical for packet routing. Test signals include RoCEv1/RoCEv2 AH creation, DSCP mode mapping, HIP08 VLAN cases, invalid SL rejection, and userspace response compatibility by `udata->outlen`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_ah.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_alloc.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_alloc.c

Purpose: Provides shared DMA buffer allocation helpers and global ID/table cleanup for HNS RoCE resources.

Important APIs/types/functions: `hns_roce_buf_alloc()` allocates a `struct hns_roce_buf` made of one or more coherent DMA trunks. `hns_roce_buf_free()` releases those trunks. `hns_roce_get_kmem_bufs()` exports kernel buffer DMA page addresses; `hns_roce_get_umem_bufs()` exports user umem DMA blocks. `hns_roce_cleanup_bitmap()` tears down ID allocators and xarrays for XRC, SRQ, QP, CQ, MR, PD, and UAR resources.

Control flow: Allocation validates that the requested page shift is at least hardware page size. Direct mode requests one contiguous trunk aligned to page size; non-direct mode allocates one trunk per hardware page-sized unit. `NOFAIL` mode accepts partial allocation as long as at least one trunk was allocated; otherwise all trunks must be allocated. On failure it frees all allocated trunks.

State and persistence: Buffer objects persist until explicit free and own coherent DMA mappings in `trunk_list`. ID allocator cleanup is device-lifetime teardown state and must happen after resource users are gone.

Dependencies and integration: Uses coherent DMA APIs, RDMA umem block iteration, IDA, xarray cleanup, and table cleanup functions implemented by QP/CQ code. The buffer layout is consumed by MTR/MR/CQ/QP creation through `hns_roce_buf_dma_addr()`.

Risks: Partial `NOFAIL` buffers require consumers to honor `npages` and allocated size. `page_shift > trunk_shift` in `hns_roce_get_kmem_bufs()` is rejected because it would skip beyond trunk granularity. Test signals include direct/non-direct allocation, atomic allocation flags, partial allocation handling, DMA address enumeration, and teardown under all optional caps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_bond.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_bond.c

Purpose: Implements RoCE bonding support over Linux bonding/LAG netdevices for HNS RoCE PFs. It tracks bond groups per PCI bus, reacts to netdev notifier events, switches RDMA client instances between normal and bonded modes, and programs hardware bond state.

Important APIs/types/functions: `hns_roce_alloc_bond_grp()` creates up to two bond groups per bus and registers netdevice notifiers. `hns_roce_dealloc_bond_grp()` tears them down. `hns_roce_bond_init()` recovers or sets netdev binding during client init. `hns_roce_bond_suspend()`/`hns_roce_bond_resume()` unregister and restore notifiers across reset. Internal helpers include `hns_roce_set_bond()`, `hns_roce_clear_bond()`, `hns_roce_slave_changestate()`, `hns_roce_slave_change_num()`, and `hns_roce_set_bond_netdev()`.

Control flow: A global xarray maps bus numbers to `hns_roce_die_info`. CHANGEUPPER and CHANGELOWERSTATE events are filtered to supported bond masters and known slaves. Work is deferred by one second. The worker recomputes support and slave maps, clears unsupported bonds, creates a new bond from `NOT_BONDED`, or sends change commands for active-state and slave-count changes. Active-backup mode follows the active slave; hash mode picks active RDMA ports and supports only hash types through L23.

State and persistence: `hns_roce_bond_group` persists across events and carries upper netdev, main RoCE device, slave maps, active maps, bus/bond IDs, TX/hash mode, ready flag, state machine value, mutex, notifier, and delayed work. `hns_roce_die_info` persists per bus with bond slots and suspend nesting count.

Dependencies and integration: Depends on Linux bonding/LAG APIs, RDMA netdev lookup, HNS3 `hnae3_handle`, hardware v2 bond commands, and external helpers such as `hns_roce_bond_init_client()`, `hns_roce_bond_uninit_client()`, `hns_roce_cmd_bond()`, `roce_del_all_netdev_gids()`, and `rdma_roce_rescan_port()`.

Risks: The code assumes `netdev_master_upper_dev_get_rcu()` returns a device before `dev_hold()`, so null handling depends on notifier context. State transitions mix mutex-protected and unprotected assignments; reset/suspend paths must avoid notifier races. Main-device switching can temporarily uninit clients. Test signals include bond create/delete, active-backup failover, hash mode slave changes, netdev unregister, PF reset recovery, SR-IOV/VF rejection, same-bus enforcement, and concurrent notifier storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_bond.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_bond.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_bond.h

Purpose: Declares the RoCE bonding data model, state machine enums, constants, and public hooks used by the HNS RoCE driver and HNS3 client glue.

Important APIs/types/functions: Constants limit a bond to four functions and two groups per bus. `struct hns_roce_bond_group` stores upper netdev, main device, active/slave maps, bond ID, bus, per-function netdev/handle pairs, readiness, bond state, LAG TX/hash mode, mutex, notifier, and delayed work. `struct hns_roce_die_info` stores per-bus groups, ID mask, mutex, and suspend count. Public functions cover lookup, allocation, cleanup, active-state check, init, suspend, and resume.

Control flow: The header supports the implementation's state machine: not attached, not bonded, bonded, slave-number change, and slave-state change. Command types distinguish set, change, and clear bond hardware operations.

State and persistence: All persistent bonding state is represented by the two structs here and is keyed by bus in the C file's global xarray.

Dependencies and integration: Includes `linux/netdevice.h` and `net/bonding.h`, and references HNS RoCE and HNAE3 handles through forward-visible structs from included headers. It is consumed by main/HNS3 lifecycle code and the bond implementation.

Risks: Constant limits are hardware policy; exceeding function or group counts produces unsupported behavior. Public hooks must be called in the right device/reset ordering. Test signals include compile coverage with bonding enabled, state enum handling in switch statements, and matching command enum values with firmware expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_bond.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_cmd.c

Purpose: Implements mailbox command submission for HNS RoCE hardware, supporting both polling and event-driven completion modes plus DMA mailbox allocation helpers.

Important APIs/types/functions: `hns_roce_cmd_mbox()` is the main command entry point. `hns_roce_cmd_event()` handles asynchronous command completion events by token. `hns_roce_cmd_init()`/`cleanup()` manage the DMA pool. `hns_roce_cmd_use_events()` allocates command contexts and switches to event mode; `hns_roce_cmd_use_polling()` frees them. Mailbox helpers allocate/free command buffers and create/destroy hardware contexts.

Control flow: Before posting, `chk_mbox_avail()` may short-circuit with `-EBUSY` or success. Poll mode serializes on `poll_sem`, posts via `hw->post_mbox`, waits using `hw->poll_mbox_done`, and uses token `0xffff`. Event mode serializes capacity through `event_sem`, takes a context from a circular free list, increments its token generation, posts with event enable, waits up to `HNS_ROCE_CMD_TIMEOUT_MSECS`, and reads the event result.

State and persistence: `hr_dev->cmd` owns the DMA pool, semaphores, event contexts, free-head index, and mode flag. DFX counters persist posted, polled, and event completions. Mailbox buffers are coherent DMA blocks from a 4 KiB pool.

Dependencies and integration: Depends on hardware callbacks `post_mbox`, `poll_mbox_done`, and optional `chk_mbox_avail`. CQ/QP/MR/HEM creation paths use `hns_roce_create_hw_ctx()` and `hns_roce_destroy_hw_ctx()`.

Risks: Event context free-list handling does not put contexts back onto a conventional free list; correctness relies on bounded semaphore and token modulo indexing. Timeout leaves the hardware command status uncertain. Test signals include command storm in event mode, token mismatch AEQs, mailbox timeout/failure injection, polling-to-event transition during init, and DMA pool allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_cmd.h

Purpose: Defines mailbox size/timeout constants, hardware command opcodes, and command helper prototypes for HNS RoCE.

Important APIs/types/functions: `HNS_ROCE_MAILBOX_SIZE` is 4096 bytes and `HNS_ROCE_CMD_TIMEOUT_MSECS` is 10000. The opcode enums cover base-address table operations for QPC/CQC/MPT/SRQC/SCCC/timer contexts, EQ context commands, query/modify commands, and object lifecycle commands for MPT, CQ, QP, and SRQ. Prototypes expose mailbox command submission and command mailbox allocation.

Control flow: Callers pass an opcode plus input/output DMA parameters and tag to `hns_roce_cmd_mbox()`. Higher-level wrappers create or destroy hardware contexts by combining a mailbox DMA address with a command and object index.

State and persistence: No runtime state is stored here. The opcode definitions are a stable hardware ABI contract.

Dependencies and integration: Included by command implementation and object-management files such as CQ, MR, QP, SRQ, and HEM users. The enum values must match firmware/hardware mailbox definitions.

Risks: Wrong opcode values can corrupt hardware context tables. The file has two anonymous enums with potentially overlapping values by command domain, so call sites must use the correct command for the firmware path. Test signals include firmware command compatibility, create/destroy/query coverage for each object type, and build checks for all prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_common.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_common.h

Purpose: Provides low-level MMIO access helpers, endian-safe register/descriptor field macros, and register offset definitions used by HNS RoCE hardware code.

Important APIs/types/functions: `roce_write()`, `roce_read()`, and `roce_raw_write()` wrap MMIO. `roce_get_field()`, `roce_set_field()`, `roce_get_bit()`, and `roce_set_bit()` operate on little-endian 32-bit values. `FIELD_LOC` plus `hr_reg_*` macros encode typed bitfield locations and perform compile-time checks where fields must stay inside one dword.

Control flow: Hardware-specific code uses these macros while building context descriptors and touching MMIO registers. Register definitions include vendor/GUID/GID/SMAC, mailbox, doorbell, EQ, ECC, CMQ, VF interrupt, and extended doorbell registers.

State and persistence: No independent runtime state. The constants define the persistent hardware register map assumed by the driver.

Dependencies and integration: Depends on Linux bitfield helpers and MMIO APIs. Included by command, CQ, HEM, and hardware v2 code.

Risks: Field macros use pointer casting to `__le32 *`; callers must pass correctly laid-out packed hardware descriptors. Cross-dword field misuse is intentionally caught in some helpers. Register offset drift against hardware revisions is high risk. Test signals include compile-time field checks, hardware init/readback tests, sparse/endian analysis, and register-level failure injection around mailbox and EQ paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_cq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_cq.c

Purpose: Implements completion queue allocation, hardware context creation/destruction, event delivery, and CQ table initialization for HNS RoCE.

Important APIs/types/functions: Public APIs include `hns_roce_create_cq()`, `hns_roce_destroy_cq()`, `hns_roce_cq_completion()`, `hns_roce_cq_event()`, `hns_roce_init_cq_table()`, `hns_roce_cleanup_cq_table()`, and HIP09 user-context bank helpers. Internal helpers allocate CQN IDs, MTR-backed CQ buffers, optional record doorbells, CQC HEM contexts, and firmware CQC objects.

Control flow: Creation rejects unsupported flags, validates CQE count and vector, copies userspace command data, rounds entries to a power of two with a minimum, chooses CQE size, creates an MTR, maps or allocates doorbell records if supported, allocates a banked CQN, gets CQC HEM, stores the CQ in an xarray, writes CQC data into a command mailbox, sends CREATE_CQC, and copies response to userspace. Error paths unwind in reverse. Destruction sends DESTROY_CQC, erases the xarray entry, synchronizes IRQ, waits for event references, returns HEM, frees ID/DB/buffer.

State and persistence: `hns_roce_cq` owns MTR, DB, CQN, vector, counters, refcount, completion, QP linkage lists, and flags. `hns_roce_cq_table` owns the lookup xarray and bank IDAs/load counters. HIP09 user contexts reserve a CQ bank for all CQs in that context.

Dependencies and integration: Uses RDMA uverbs, user/kernel doorbell helpers, HEM table management, command mailbox, hardware `write_cqc`, EQ IRQs, xarray, IDA, and DFX counters. Completion events call RDMA core CQ handlers.

Risks: CQN lower bits encode bank ID and lookup masks with `num_cqs - 1`; sizing must match hardware power-of-two assumptions. IRQ synchronization and refcount completion prevent use-after-free during async events. Test signals include userspace/kernel CQ creation, CQ record DB capability negotiation, bank balancing, invalid vector/count rejection, async error events, destroy under interrupt load, and mailbox failure unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_cq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_db.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_db.c

Purpose: Manages doorbell record memory for user and kernel consumers. Doorbell records are small DMA-visible words used by hardware to observe queue producer/consumer indexes.

Important APIs/types/functions: `hns_roce_db_map_user()` pins and maps a user page containing DB records. `hns_roce_db_unmap_user()` releases references. `hns_roce_alloc_db()` allocates a kernel DB record from coherent per-page pgdirs. `hns_roce_free_db()` returns it and frees empty pgdirs.

Control flow: User mapping serializes on the ucontext page mutex, reuses an existing pinned page for the same page-aligned virtual address or pins a new page with `ib_umem_get()`, then computes DMA and CPU virtual offsets. Kernel allocation searches existing pgdirs with a simple buddy-like bitmap for order 0 or order 1 records, allocating a new coherent page if needed. Free coalesces order-0 buddies into order 1 and releases pgdir pages when fully free.

State and persistence: User DB pages are cached in `hns_roce_ucontext.page_list` with refcounts. Kernel DB pages live in `hr_dev->pgdir_list`, protected by `pgdir_mutex`, and persist until all records are freed.

Dependencies and integration: Used by CQ/QP/SRQ creation paths. Depends on RDMA umem internals, scatterlist DMA addresses, coherent DMA, mutexes, bitmaps, and refcount helpers.

Risks: `hns_roce_db_map_user()` initializes refcount to one and increments again on first use; unmap decrements then conditionally decrements if one, which is a non-obvious lifetime pattern that deserves stress testing. User page assumptions depend on a single-page umem and valid SG mappings. Test signals include repeated DBs on one user page, concurrent ucontext map/unmap, kernel order-0/order-1 fragmentation, pgdir full/free transitions, and CQ/QP teardown leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_db.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_debugfs.c

Purpose: Exposes lightweight debugfs diagnostics for HNS RoCE, currently software DFX counters per device.

Important APIs/types/functions: `hns_roce_init_debugfs()` creates the module root `hns_roce`; `hns_roce_cleanup_debugfs()` removes it. `hns_roce_register_debugfs()` creates a device directory named by PCI device and a `sw_stat/sw_stat` seqfile. `hns_roce_unregister_debugfs()` removes the device tree. `sw_stat_debugfs_show()` prints all software DFX counters.

Control flow: Registration builds nested debugfs dentries and initializes a seqfile wrapper whose open method calls `single_open()` with the stored read function and data pointer. Reads iterate `HNS_ROCE_DFX_CNT_TOTAL` and print names plus atomic64 counter values.

State and persistence: Global root dentry persists for module lifetime. Per-device dentries persist between device register/unregister. Counter values live in `hr_dev->dfx_cnt`.

Dependencies and integration: Depends on Linux debugfs, seq_file, PCI naming, and the DFX counter enum in `hns_roce_device.h`. AH, CQ, command, MR, QP, SRQ, mmap, and ucontext paths increment these counters.

Risks: Debugfs creation failures are ignored, which is typical but means diagnostics may be absent without hard failure. The counter-name array must stay aligned with the enum. Test signals include debugfs mount/read checks, device hotplug removal, counter increment visibility after induced errors, and enum/name coverage when new counters are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_debugfs.h

Purpose: Declares debugfs wrapper structures and lifecycle functions for HNS RoCE diagnostics.

Important APIs/types/functions: `struct hns_debugfs_seqfile` stores a seq read callback and data pointer. `struct hns_sw_stat_debugfs` groups the software-stat root and seqfile. `struct hns_roce_dev_debugfs` is embedded in `hns_roce_dev` and stores the per-device root plus software-stat subtree. Public functions initialize/cleanup module debugfs and register/unregister a device.

Control flow: The header does not implement flow; it provides the device-embedded state consumed by `hns_roce_debugfs.c` and main device lifecycle code.

State and persistence: The structures model debugfs dentries that persist for device/module lifetime and are removed recursively on cleanup.

Dependencies and integration: Forward declares `struct hns_roce_dev` and relies on Linux debugfs/seq_file types through implementation includes. It is included by `hns_roce_device.h`.

Risks: Dentry lifetime must match device lifetime to avoid dangling private data in seqfile callbacks. Test signals include build coverage, open/read while device removal is serialized, and cleanup idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_device.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_device.h

Purpose: Central HNS RoCE driver interface header. It defines hardware constants, capability flags, resource structs, device state, hardware callback tables, inline conversions/helpers, and prototypes shared across the driver.

Important APIs/types/functions: Major structs include `hns_roce_dev`, `hns_roce_caps`, `hns_roce_hw`, `hns_roce_qp`, `hns_roce_cq`, `hns_roce_srq`, `hns_roce_mr`, `hns_roce_mtr`, `hns_roce_hem_table`, `hns_roce_cmdq`, `hns_roce_ucontext`, DB/page structs, EQ structs, and resource tables. Inline helpers convert RDMA core objects to driver objects, compute buffer DMA offsets, convert page sizes to hardware units, map traffic class/DSCP, and fetch netdev/bus data.

Control flow: This header establishes contracts used by object lifecycle files. `hns_roce_dev` aggregates PCI/device handles, MMIO bases, caps, command state, ID allocators, MR/CQ/SRQ/QP/EQ/HEM tables, workqueues, private hardware data, debugfs state, and DFX counters. `hns_roce_hw` is the hardware abstraction vtable used by generic code for mailbox, context programming, HEM set/clear, QP modification, EQ init, queries, counters, and DSCP mapping.

State and persistence: Most persistent runtime state is declared here: per-device caps, resource tables, xarrays, IDAs, doorbell page directories, MTR/HEM lists, QP/CQ/SRQ refcounts and completions, reset/device states, and debug counters.

Dependencies and integration: Includes PCI, RDMA verbs, HNS ABI, and debugfs declarations. It exposes prototypes implemented across allocation, command, AH, MR, CQ, DB, QP, SRQ, restrack, main, and HEM files. It also binds to netdevs for RoCE, congestion control, reset handling, and optional bonding through caps/helpers.

Risks: Because this is the shared contract header, layout or enum changes have broad ABI and hardware effects. Capability flags gate optional resource cleanup and creation behavior. Inline object conversions rely on embedding layout. Test signals include full driver build, sparse/lockdep, uverbs ABI compatibility, hardware capability profile validation, reset teardown coverage, optional cap matrix testing, and resource leak checks across all object types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_hem.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_hem.c

Purpose: Implements Hardware Entry Memory management for HNS RoCE. It allocates refcounted coherent memory chunks for hardware context tables and constructs multi-hop base-address trees for MTR/MTT style buffers.

Important APIs/types/functions: Public table APIs are `hns_roce_table_get()`, `hns_roce_table_put()`, `hns_roce_table_find()`, `hns_roce_init_hem_table()`, `hns_roce_cleanup_hem_table()`, `hns_roce_cleanup_hem()`, `hns_roce_calc_hem_mhop()`, and `hns_roce_check_whether_mhop()`. HEM-list APIs are `hns_roce_hem_list_init()`, `hns_roce_hem_list_request()`, `hns_roce_hem_list_release()`, `hns_roce_hem_list_calc_root_ba()`, and `hns_roce_hem_list_find_mtt()`.

Control flow: Table get determines whether the table is direct or multi-hop. Direct mode indexes a chunk by object number, allocates a coherent HEM chunk, calls hardware `set_hem`, and sets refcount. Multi-hop mode calculates L0/L1/L2 indexes from caps, lazily allocates BA pages and buffer pages, wires DMA addresses through parent BA pages, then programs the relevant hardware steps for context tables. Put decrements refcount, clears hardware entries, frees buffer and now-empty BA pages. Init preallocates pointer arrays for HEM and BA levels based on object count and cap-derived chunk sizes.

State and persistence: `hns_roce_hem_table` owns arrays of `hns_roce_hem` chunks plus optional L0/L1 BA page arrays and DMA addresses. Each allocated HEM has coherent DMA memory and a refcount. HEM lists own root, middle, and bottom `hns_roce_hem_item` lists and a root BA for a specific MTR.

Dependencies and integration: Uses device caps for hop counts/page sizes, hardware `set_hem`/`clear_hem`, coherent DMA, mutex/refcount/list helpers, and context users such as CQ/QP/MR/SRQ/timer/GMV tables. HEM-list output is consumed by MTR creation and MR/CQ/QP buffer mapping.

Risks: Multi-hop index math must match firmware exactly; off-by-one errors corrupt BA trees. Cleanup conditionally frees parent BA pages only when sibling chunks are absent. Large MR construction can be long-running, so the loop calls `cond_resched()` after a 4K-page threshold. Test signals include direct and 1/2/3-hop tables, refcount sharing, hardware set/clear failures, large MRs, mixed-region MTRs, cleanup after partial allocation failure, and `hns_roce_table_find()` DMA offset correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_hem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_hem.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_hem.h

Purpose: Declares HNS RoCE HEM table/list types, HEM type identifiers, hop-count classification macros, and public HEM APIs.

Important APIs/types/functions: HEM types identify mapped context tables (`QPC`, `MTPT`, `CQC`, `SRQC`, `SCCC`, timers, `GMV`) and unmapped address/resource tables (`MTT`, `CQE`, `SRQWQE`, `IDX`, `IRRL`, `TRRL`). `struct hns_roce_hem` holds a coherent buffer, DMA address, size, and refcount. `struct hns_roce_hem_mhop` carries cap-derived hop configuration and calculated indexes. Macros classify whether a type/hop combination needs one, two, or three BA table chunks.

Control flow: Callers initialize HEM tables during device setup, get/put table chunks during object creation/destruction, find CPU/DMA addresses for existing entries, and use HEM lists to build MTR root/middle/bottom BA chains.

State and persistence: This header defines the in-memory shape for refcounted HEM chunks and multi-hop index calculation, but state is stored in `hns_roce_hem_table` from `hns_roce_device.h` and list structs embedded in MTRs.

Dependencies and integration: Consumed by CQ, MR, QP, SRQ, EQ, and main teardown code. It relies on device caps and `HNS_ROCE_HOP_NUM_0` constants from `hns_roce_device.h`.

Risks: Type ordering matters because macros treat values below `HEM_TYPE_MTT` as mapped context HEM and values at/above it as unmapped buffer/address tables. Reordering or adding types without updating the classification logic is risky. Test signals include compile coverage for all HEM users, cap combinations for hop 0/1/2/3, and cleanup coverage for every type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_hem.h -->
