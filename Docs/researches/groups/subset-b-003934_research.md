# subset-b-003934 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_main.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_main.c

## Purpose
`hns_roce_main.c` is the top-level HNS RoCE verbs-device and HCA lifecycle layer. It registers common `ib_device_ops`, exposes device and port attributes, handles RoCE netdev events, user context mmap setup, optional stats/resource tracking hooks, hardware-entry-memory setup, HCA bring-up/teardown, and device-error CQ notification.

## Important APIs, Types, And Functions
The file centers on `struct hns_roce_dev`, `struct hns_roce_ib_iboe`, `struct hns_roce_ucontext`, `struct hns_user_mmap_entry`, `struct hns_roce_bond_group`, and `struct ib_device_ops`. Key verbs callbacks are `hns_roce_query_device()`, `hns_roce_query_port()`, `hns_roce_alloc_ucontext()`, `hns_roce_dealloc_ucontext()`, `hns_roce_mmap()`, `hns_roce_modify_device()`, and `hns_roce_port_immutable()`. Device lifecycle is driven by `hns_roce_init()`, `hns_roce_exit()`, `hns_roce_register_device()`, `hns_roce_unregister_device()`, `hns_roce_init_hem()`, and `hns_roce_setup_hca()`. Netdev integration uses `hns_roce_netdev_event()`, `handle_en_event()`, and `hns_roce_set_mac()`. `hns_roce_handle_device_err()` scans QPs and signals armed CQs during device failure.

## Control Flow
Initialization allocates debug counters, initializes optional command queues, reads hardware profile data, initializes command/EQ infrastructure, optionally switches command completion to event mode, initializes HEM tables, sets up HCA-side allocators, calls hardware init, registers the RDMA device, and registers debugfs. Registration composes base, hardware-specific, and capability-specific `ib_device_ops`; binds netdevs or bond devices; registers the IB device; programs initial MTU/MAC state; registers a netdevice notifier; then marks the device active. User context allocation validates udata, negotiates feature flags, allocates a UAR, creates a DB mmap entry, initializes record-doorbell bookkeeping when supported, and returns ABI capabilities. Teardown unwinds in reverse: debugfs, device unregister/notifier removal, hardware exit, HCA/HEM cleanup, command polling restore, EQ and command cleanup, optional CMQ exit, and counter free.

## State And Persistence
State is in memory and hardware tables only. `hr_dev->active` gates user context allocation and is cleared before unregister. `hr_dev->dev_addr[]`, `ib_dev->port_data[].cache.last_port_state`, UAR IDA state, QP/CQ lists, page-directory list, HEM tables, and DFX counters are runtime state. Node description changes are copied into `ib_dev->node_desc` under `sm_lock`; no nonvolatile persistence is used. Netdev events update hardware MAC on older revisions and dispatch IB port active/error events for LAG master state transitions. Device-error handling builds a temporary list of armed CQs needing completion notification.

## Dependencies And Integration Points
The file integrates RDMA core uverbs, mmap entries, netdev notifiers, RoCE GID cache operations, bonding helpers from `hns_roce_bond.h`, hardware methods in `hr_dev->hw`, HEM table management, debugfs, EQ/command infrastructure, and optional resource tracking and hardware stats. It relies on PCI revision checks for HIP08/HIP09 behavior and capability flags for FRMR, SRQ, XRC, flow control, stats, bonding, and record doorbells.

## Risks
The registration path has many capability-dependent partial states; failures after bond group allocation or bond init must not leak bond resources. `hns_roce_setup_mtu_mac()` dereferences `get_hr_netdev()` without a local NULL check, so probe correctness depends on prior netdev population. Ucontext cleanup frees the UAR ID directly through IDA rather than a paired helper, so allocation-index invariants must remain stable. Device-error CQ notification runs while holding `qp_list_lock` and calls completion handling after building the list; locking order against CQ locks and completions is important. Netdev notifier returns `NOTIFY_DONE` even on handled events, so external notifier semantics rely only on side effects.

## Test Signals
Useful signals include probe failure injection at every lifecycle step, register/unregister with and without bonding, HIP08/HIP09 MAC programming, user context ABI negotiation and mmap of DB/DWQE regions, invalid mmap pgoff and `dis_db` behavior, port query with missing netdev, netdev up/down/changeaddr events, hardware stats query bounds, FRMR/SRQ/XRC operation availability by capability flag, device-error flushing of armed CQs, and full teardown after partial initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_mr.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_mr.c

## Purpose
`hns_roce_mr.c` implements HNS memory registration and the reusable memory-translation-region layer used by MRs and queue buffers. It allocates MR keys, builds MPT hardware contexts, pins or allocates backing buffers, chooses page size and hop depth, builds base-address/MTT tables, maps SG lists for fast registration, and exposes MTT lookup helpers.

## Important APIs, Types, And Functions
Important types include `struct hns_roce_mr`, `struct hns_roce_mtr`, `struct hns_roce_buf_attr`, `struct hns_roce_hem_cfg`, and `struct hns_roce_buf_region`. Verbs entry points are `hns_roce_get_dma_mr()`, `hns_roce_reg_user_mr()`, `hns_roce_rereg_user_mr()`, `hns_roce_dereg_mr()`, `hns_roce_alloc_mr()`, and `hns_roce_map_mr_sg()`. MTR helpers include `hns_roce_mtr_create()`, `hns_roce_mtr_destroy()`, `hns_roce_mtr_map()`, and `hns_roce_mtr_find()`. Key internal helpers are `alloc_mr_key()`, `alloc_mr_pbl()`, `hns_roce_mr_enable()`, `mtr_alloc_bufs()`, `get_best_page_shift()`, `get_best_hop_num()`, `mtr_init_buf_cfg()`, and `mtr_alloc_mtt()`.

## Control Flow
Normal user MR registration allocates a software MR, obtains an MTPT ID/key, creates a PBL MTR over user memory, writes the MTPT through hardware callbacks, creates the MPT hardware context, and returns the key as both lkey and rkey. DMA MRs allocate only a key and enable an MPT without a PBL. Reregistration queries the current MPT, destroys it, updates IOVA/size/PD/access, optionally rebuilds the PBL, writes a replacement MTPT, and recreates the hardware context. Fast MRs allocate an MTT-only PBL at creation, then `hns_roce_map_mr_sg()` converts scatterlists into page addresses and maps them into the MTR. MTR creation optionally pins user memory or allocates kernel buffers, adapts page shift and hop count, initializes HEM config, allocates MTT tables, and maps DMA addresses unless the caller will map later.

## State And Persistence
MR state is runtime only: key, PD, access flags, IOVA, length, PBL hop count, page count, enable state, optional page list, and embedded MTR. MTR state records user or kernel backing memory, direct-vs-multihop layout, root base address, base-address page size, buffer page size, regions, and HEM list state. IDA state in `mr_table.mtpt_ida` owns key indexes. No persistent storage is used; hardware MPT and MTT contents are reconstructed from software state during creation/reregistration.

## Dependencies And Integration Points
The file depends on RDMA core MR and umem APIs, scatterlist page conversion, HNS command mailboxes, hardware MTPT writer callbacks, HEM table/list APIs, buffer allocation helpers, page-size capabilities from `hr_dev->caps`, and tracepoints from `hns_roce_trace.h`. The MTR abstraction is shared by QP and SRQ code for WQE, index, and queue buffers.

## Risks
`alloc_mr_key()` maps any negative ID allocation failure to `-ENOMEM`, which can hide `-ENOSPC`-style exhaustion details. Reregistration destroys the hardware MPT before all replacement work is guaranteed to succeed; if later steps fail the MR remains disabled and partially updated. `hns_roce_mtr_map()` assumes `pages[0]` is valid for direct mode, so callers must never pass zero pages. Adaptive page-size and hop calculations are sensitive to device page capability masks and umem alignment. The fast-MR page list is transient, so error paths must always free it. Direct-mode multi-region splitting requires physically contiguous small pages and can fail for otherwise valid allocations.

## Test Signals
Test DMA MR, user MR, FRMR allocation, invalid `dmah`, MTPT exhaustion, MPT create/destroy failure, reregistration by PD/access/translation combinations, failed reregistration recovery expectations, SG mapping alignment and page-size bounds, SG overrun returning zero, direct and multihop MTR creation, MTT-only MTRs, `hns_roce_mtr_find()` for direct and multihop offsets, adaptive page-size selection, hop-count overflow, and cleanup after every injected allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_mr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_pd.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_pd.c

## Purpose
`hns_roce_pd.c` manages simple ID-backed protection domains, user access regions, and XRC domains for HNS RoCE. It provides the RDMA-core PD/XRCD verbs callbacks and initializes the per-device IDA ranges used by those objects.

## Important APIs, Types, And Functions
The main exported functions are `hns_roce_init_pd_table()`, `hns_roce_alloc_pd()`, `hns_roce_dealloc_pd()`, `hns_roce_uar_alloc()`, `hns_roce_init_uar_table()`, `hns_roce_init_xrcd_table()`, `hns_roce_alloc_xrcd()`, and `hns_roce_dealloc_xrcd()`. It manipulates `struct hns_roce_ida`, `struct hns_roce_pd`, `struct hns_roce_uar`, and `struct hns_roce_xrcd`.

## Control Flow
Table initialization sets IDA ranges from capability limits and reserved counts. PD allocation obtains an ID from the PD IDA, stores it in `pdn`, and returns the PD number to userspace when udata is present. PD deallocation returns the ID to the IDA. UAR allocation obtains a logical index, maps it to a physical UAR index modulo available physical UARs, sets the BAR2 page frame number for doorbells, and records the direct-WQE BAR4 base when supported. XRCD allocation checks the XRC capability flag before allocating an XRC domain number; deallocation frees the ID.

## State And Persistence
All state is volatile IDA allocation state plus object fields (`pdn`, `logic_idx`, `index`, `pfn`, `xrcdn`). UAR physical mapping is derived from PCI BAR addresses and capability flags at allocation time. No hardware context is created here and there is no nonvolatile persistence.

## Dependencies And Integration Points
This file is called by `hns_roce_main.c` during HCA setup and through the registered `ib_device_ops`. UAR allocation is consumed by user-context setup and kernel doorbell paths. PD numbers are embedded in MR, AH, QP, and SRQ hardware contexts. XRCDs are only exposed when `HNS_ROCE_CAP_FLAG_XRC` is enabled.

## Risks
Negative IDA allocation results are collapsed to `-ENOMEM`, losing exhaustion versus interruption detail. `hns_roce_uar_alloc()` sets `hr_dev->dwqe_page` as a device-wide side effect on every allocation when direct WQE is supported. UAR cleanup is done by callers using raw `ida_free()`, so the logical index must remain valid through all failure paths. PD userspace response failure frees the ID but leaves no additional object state to clear.

## Test Signals
Test PD allocation/deallocation across reserved ranges, userspace response copy failure, PD ID exhaustion, UAR physical index mapping with one and many physical UARs, direct-WQE BAR address selection, XRCD allocation when capability is absent/present, XRCD ID exhaustion, and repeated init/destroy cycles for IDA state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_pd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_qp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_qp.c

## Purpose
`hns_roce_qp.c` implements HNS queue-pair allocation, destruction, state modification, event delivery, WQE-buffer layout, doorbell mapping, QPN bank selection, and work-queue overflow checks. It translates RDMA-core QP creation and modification requests into HNS queue memory, context-table, and hardware-callback operations.

## Important APIs, Types, And Functions
Important types are `struct hns_roce_qp`, `struct hns_roce_qp_table`, `struct hns_roce_wq`, `struct hns_roce_bank`, `struct hns_roce_work`, and HNS uAPI create/modify structures. Entry points include `hns_roce_create_qp()`, `hns_roce_qp_destroy()`, `hns_roce_modify_qp()`, `hns_roce_qp_event()`, `hns_roce_flush_cqe()`, `hns_roce_get_send_wqe()`, `hns_roce_get_recv_wqe()`, `hns_roce_get_extend_sge()`, `hns_roce_wq_overflow()`, `hns_roce_init_qp_table()`, and `hns_roce_cleanup_qp_table()`. Major helpers include `alloc_qpn()`, `alloc_qpc()`, `hns_roce_qp_store()`, `set_rq_size()`, `set_ext_sge_param()`, `set_qp_param()`, `alloc_qp_buf()`, `alloc_qp_db()`, `alloc_kernel_wrid()`, and `hns_roce_lock_cqs()`.

## Control Flow
QP creation validates type support, records GSI/XRC details, initializes locks and deferred flush work, computes SQ/RQ sizing from kernel or userspace inputs, allocates kernel WRID arrays when needed, builds an MTR-backed WQE buffer, allocates a QPN from a bank selected by CQ affinity and load, maps user or kernel doorbells, allocates QPC/IRRL/TRRL/SCCC HEM entries, inserts the QP into the xarray and CQ/device lists, copies userspace response data, initializes optional flow control, and initializes the refcount/completion. Modification serializes on the QP mutex, checks current-state expectations and RDMA state-transition legality, validates port/pkey/MTU/atomic limits, invokes the hardware `modify_qp()` callback, and may copy response traffic-class data to userspace. Async event paths look up QPs through the xarray with a temporary refcount and translate HNS events to IB events. HIP08 CQE flush uses deferred work to move a QP to error state because mailbox operations may sleep.

## State And Persistence
QP state includes QPN, QP type, port, SQ/RQ producer-consumer counters, WQE sizes/counts, extended-SGE layout, inline data, congestion type, doorbell records/registers, MTR buffer, CQ list nodes, xarray membership, refcount/completion, and flush flags. QPN allocation is distributed across eight banks with per-bank IDAs, `next` counters, and in-use counts. State is runtime only; hardware QP context and flow-control context are recreated during creation and changed by modify callbacks.

## Dependencies And Integration Points
This file depends on RDMA core QP state validation, uverbs udata copy helpers, HNS MTR helpers from `hns_roce_mr.c`, HEM table APIs, CQ locking/list contracts, HNS database mapping helpers, congestion/flow-control hardware callbacks, the device IRQ workqueue, and capability/revision flags. CQ and QP event handling integrates with async event queues outside this file.

## Risks
`free_qpc()` releases TRRL and IRRL but does not visibly put the QPC table or SCCC table allocated by `alloc_qpc()`, which is a high-value resource-lifetime point to verify against hardware-specific cleanup. Error labels after userspace response failure remove a QP from lists/xarray before refcount initialization, so ordering is delicate. `hns_roce_modify_qp()` returns `-EINVAL` for a no-op RESET-to-RESET path because it jumps to `out` before setting `ret = 0`, which may be intentional avoidance or a surprising behavior. User error-state flush depends on record doorbells; without SQ record DB it warns and rejects. Bank selection assumes a nonzero valid bank mask. CQ lock ordering is custom and must stay consistent across QP list, CQ poll, and flush paths.

## Test Signals
Test all supported and unsupported QP types, GSI fixed QPN, XRC with/without capability, userspace and kernel SQ/RQ sizing bounds, HIP08 reserved RQ SGE behavior, extended SGE and inline-data negotiation, QPN bank distribution and exhaustion, direct-WQE mmap response, user/kernel record DB mapping, every creation error label, flow-control init failure, valid and invalid modify transitions, MTU and atomic-limit validation, userspace error-state flush with/without record DBs, async event refcount races, deferred flush work during destroy, WQE accessors, overflow checks under CQ polling, and QP table cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_qp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_restrack.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_restrack.c

## Purpose
`hns_roce_restrack.c` provides RDMA netlink resource-tracking detail for HNS CQ, QP, MR, and SRQ objects. It exposes driver-specific summary attributes and optional raw hardware context dumps for diagnostics.

## Important APIs, Types, And Functions
The exported callbacks are `hns_roce_fill_res_cq_entry()`, `hns_roce_fill_res_cq_entry_raw()`, `hns_roce_fill_res_qp_entry()`, `hns_roce_fill_res_qp_entry_raw()`, `hns_roce_fill_res_mr_entry()`, `hns_roce_fill_res_mr_entry_raw()`, `hns_roce_fill_res_srq_entry()`, and `hns_roce_fill_res_srq_entry_raw()`. They use RDMA netlink helpers such as `nla_nest_start()`, `rdma_nl_put_driver_u32()`, `rdma_nl_put_driver_u32_hex()`, and `nla_put()`.

## Control Flow
Summary callbacks open a `RDMA_NLDEV_ATTR_DRIVER` nest, append selected software fields, close the nest, and cancel it on size errors. Raw callbacks check that the corresponding hardware query callback exists, issue a query for the CQC/QPC/SCCC/MPT/SRQC context, and put the raw context blob under `RDMA_NLDEV_ATTR_RES_RAW`. QP raw output combines QPC with optional SCCC data; DIP congestion uses the DIP index when present.

## State And Persistence
The file does not own persistent state. It snapshots live object fields such as CQ depth/consumer index, QP WQE counts, MR PBL layout, and SRQ identifiers. Raw dumps reflect hardware context at query time. Failed SCCC queries are rate-limited warnings and leave the SCCC part zeroed.

## Dependencies And Integration Points
These callbacks are installed in `hns_roce_main.c` through `hns_roce_dev_restrack_ops`. They depend on RDMA netlink resource tracking, HNS object conversion helpers, hardware query callbacks from the selected HNS generation, and context structures from the v2 hardware header.

## Risks
Raw context layout is driver/kernel ABI diagnostic data; structure-size changes can affect user tooling that expects exact blobs. Summary fields are read without object-local locks, so rapidly changing indices or QP attributes may be slightly stale. `hns_roce_fill_res_mr_entry_raw()` passes `hr_mr->key` to `query_mpt()` while other paths often use hardware indexes, so query callback expectations are important. Optional SCCC failure is nonfatal, which can hide flow-control diagnostic gaps.

## Test Signals
Test netlink dump size exhaustion, summary and raw dumps for CQ/QP/MR/SRQ, missing hardware query callbacks returning `-EINVAL`, QP raw dumps with and without flow control, DIP congestion with missing/present DIP object, SCCC query failure warning behavior, and concurrent destroy/dump races under RDMA restrack references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_restrack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_srq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_srq.c

## Purpose
`hns_roce_srq.c` implements shared receive queue creation, destruction, event delivery, buffer allocation, index queues, record doorbells, and SRQ context programming for HNS RoCE.

## Important APIs, Types, And Functions
The main entry points are `hns_roce_create_srq()`, `hns_roce_destroy_srq()`, `hns_roce_srq_event()`, and `hns_roce_init_srq_table()`. Important helpers include `alloc_srqn()`, `alloc_srqc()`, `hns_roce_create_srqc()`, `alloc_srq_idx()`, `alloc_srq_wqe_buf()`, `alloc_srq_db()`, `set_srq_param()`, `proc_srq_sge()`, `free_srqc()`, `free_srq_buf()`, and `free_srq_db()`. It uses `struct hns_roce_srq`, `struct hns_roce_srq_table`, `struct hns_roce_idx_que`, and HNS SRQ uAPI create/response structures.

## Control Flow
Creation initializes SRQ locks, validates and rounds attributes, fills XRC/CQ extension fields, copies userspace queue addresses when present, allocates an MTR-backed index queue, allocates an MTR-backed WQE buffer, optionally allocates kernel WRID storage, maps or allocates record doorbells, allocates an SRQN, allocates SRQC HEM and stores the SRQ in an xarray, writes the SRQC into a command mailbox, creates the hardware SRQ context, initializes event/refcount state, and returns SRQN/capability flags to userspace. Destruction destroys the hardware SRQ context, erases xarray membership, waits for outstanding event references, frees the SRQN, unmaps doorbells, frees buffers, and destroys the mutex. Async SRQ events xarray-lookup the SRQ, take a refcount, translate limit/error events to IB events, and drop the refcount.

## State And Persistence
SRQ state is runtime only: SRQN, WQE count and SGE count, reserved SGE count, SRQ limit, xrcdn/cqn, index queue head/tail and optional bitmap, WQE MTR, optional WRID array, record doorbell mapping, xarray membership, refcount/completion, and callback pointer. Hardware SRQC state is created and destroyed through command mailboxes; no configuration is persisted across device reset or reload.

## Dependencies And Integration Points
The file depends on RDMA SRQ/XRC/CQ helpers, uverbs udata validation/copy, HNS MTR creation from `hns_roce_mr.c`, HEM table APIs, command mailbox helpers, doorbell mapping helpers, and hardware `write_srqc()` support. It is enabled by SRQ capability wiring in `hns_roce_main.c`.

## Risks
Userspace creation validates only through `ib_copy_validate_udata_in(..., que_addr)`, so ABI layout compatibility around optional DB fields must be preserved. `free_srqc()` waits for event references after xarray erase, making refcount initialization and all error paths important. HIP08 reserved-SGE adjustment differs for kernel and userspace and can surprise capacity reporting. Kernel SRQ DB register uses a fixed `SRQ_DB_REG` offset. Attribute validation rejects zero max_sge but permits max_wr to be raised to the minimum, so callers should observe modified caps.

## Test Signals
Test SRQ creation with kernel and userspace queues, minimum-depth rounding, max WR/SGE rejection, HIP08 reserved-SGE behavior, XRC and CQ extension fields, index/WQE MTR allocation failures, record DB capability negotiation, userspace response copy failure after hardware creation, async limit/error event delivery, bogus SRQN events, destroy waiting for event refs, and table init range handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_srq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_trace.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_trace.h

## Purpose
`hns_roce_trace.h` defines ftrace tracepoints for HNS RoCE diagnostics. It captures CQE flush heads, SQ/RQ/SRQ WQE contents, async event queue entries, MR metadata, MTR buffer attributes, and command queue requests/responses.

## Important APIs, Types, And Functions
The file uses `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, and `TRACE_EVENT` to define `hns_sq_flush_cqe`, `hns_rq_flush_cqe`, `hns_sq_wqe`, `hns_rq_wqe`, `hns_srq_wqe`, `hns_ae_info`, `hns_mr`, `hns_buf_attr`, `hns_cmdq_req`, and `hns_cmdq_resp`. It references `enum hns_roce_trace_type`, `struct hns_roce_mr`, `struct hns_roce_buf_attr`, `struct hns_roce_cmq_desc`, HNS SGE sizes, and v2 EQE size constants.

## Control Flow
Trace events are passive instrumentation compiled through `trace/define_trace.h`. WQE and AEQE tracepoints copy little-endian 32-bit words into trace entries before printing arrays. MR and buffer-attribute tracepoints snapshot key fields from software structures. Command queue tracepoints record opcode, flags, return value, and six data words with the device name.

## State And Persistence
There is no owned driver state. Trace records are transient kernel tracing data controlled by ftrace/perf infrastructure. The tracepoint arrays impose fixed maximum captured sizes: WQE capture is capped by `MAX_WQE_SIZE`, and AEQE capture by `HNS_ROCE_V3_EQE_SIZE`.

## Dependencies And Integration Points
The header depends on Linux tracepoint infrastructure, `string_choices.h`, HNS device and v2 hardware headers, and the build convention that `TRACE_INCLUDE_FILE` and `TRACE_INCLUDE_PATH` match this header. It is included by MR and command paths that emit diagnostics.

## Risks
`wqe_template` stores `len / sizeof(__le32)` words into a fixed array without an explicit clamp in the trace assignment; callers must pass lengths no larger than `MAX_WQE_SIZE`. `hns_buf_attr` unconditionally reads `region[0..2]`, which is safe only if the array has at least three entries. Trace format strings become user-visible ABI for tracing tools. High-rate WQE/command tracing can expose traffic metadata and impose overhead.

## Test Signals
Test tracepoint compilation with `CREATE_TRACE_POINTS`, enabling each event through ftrace, WQE length boundaries, AEQE dump length, MR and buffer-attribute output during MR/QP/SRQ creation, command request/response output, and trace parsing compatibility after structure or enum changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/Kconfig

## Purpose
`Kconfig` adds the build-time configuration symbol for the AMD Pensando DSC RDMA/RoCE provider.

## Important APIs, Types, And Functions
The only symbol is `CONFIG_INFINIBAND_IONIC`, a tristate named "AMD Pensando DSC RDMA/RoCE Support". It depends on `NETDEVICES`, `ETHERNET`, `PCI`, `INET`, and the Pensando Ethernet driver symbol `IONIC`.

## Control Flow
Kconfig selection controls whether the `ionic_rdma` provider is built in, built as a module, or omitted. The help text describes DSC RoCE support and the module name.

## State And Persistence
This file has no runtime state. It influences kernel configuration state and therefore which objects are compiled.

## Dependencies And Integration Points
The dependency on `IONIC` ties the RDMA driver to the Ethernet/LIF infrastructure that supplies PCI, lif configuration, doorbell, interrupt, and device-command services. The symbol is consumed by the Ionic RDMA `Makefile`.

## Risks
Missing dependencies on RDMA core symbols may be covered by menu placement outside this file; if moved, the symbol could become visible without the expected InfiniBand core context. The strict `IONIC` dependency prevents building the RDMA provider without the net driver, which is correct for shared lif resources but affects modular packaging.

## Test Signals
Test `allyesconfig`, `allmodconfig`, and minimal configs with `IONIC=n/m/y`, verify `ionic_rdma` module visibility only when dependencies are met, and confirm module naming matches the help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/Makefile

## Purpose
`Makefile` builds the Ionic RDMA provider object and gives it access to shared Pensando Ionic Ethernet headers.

## Important APIs, Types, And Functions
The file sets `ccflags-y` to include `drivers/net/ethernet/pensando/ionic`, builds `ionic_rdma.o` when `CONFIG_INFINIBAND_IONIC` is enabled, and composes the module from `ionic_ibdev.o`, `ionic_lif_cfg.o`, `ionic_queue.o`, `ionic_pgtbl.o`, `ionic_admin.o`, `ionic_controlpath.o`, `ionic_datapath.o`, and `ionic_hw_stats.o`.

## Control Flow
Kbuild compiles each listed translation unit into the composite `ionic_rdma` module or built-in object. The include path makes shared `ionic_api.h` and firmware definitions visible to the RDMA files.

## State And Persistence
There is no runtime state. The file defines build composition and compile-time include search behavior.

## Dependencies And Integration Points
It is paired with `Kconfig` and integrates RDMA-specific files with shared Ionic net-driver headers. `ionic_admin.c` and `ionic_controlpath.c` rely on symbols and structures from the other objects listed here, especially lif config, queue helpers, page-table helpers, datapath completions, and hardware stats.

## Risks
The relative include path couples the RDMA driver to the net-driver source tree layout. Missing an object in `ionic_rdma-y` can produce link-time failures or incomplete `ib_device_ops`. Header name collisions are possible because the net-driver include directory is injected globally for this directory.

## Test Signals
Test module and built-in builds, clean rebuilds after touching shared Ionic headers, link coverage for all `ionic_*` symbols used by admin/controlpath/datapath files, and out-of-tree or alternate source-root builds where `$(srctree)` include paths matter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_admin.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_admin.c

## Purpose
`ionic_admin.c` implements the Ionic RDMA admin/event queue infrastructure. It creates RDMA event queues, admin completion queues, and admin queues; posts and completes firmware admin WQEs; handles watchdog timeouts and LIF reset/kill; polls EQs and dispatches CQ/QP events into RDMA core callbacks.

## Important APIs, Types, And Functions
The central global is `ionic_evt_workq`. Key functions are `ionic_admin_post()`, `ionic_admin_wait()`, `ionic_create_rdma_admin()`, `ionic_destroy_rdma_admin()`, `ionic_kill_rdma_admin()`, and `ionic_rdma_reset_devcmd()`. Admin internals include `ionic_admin_poll_locked()`, `ionic_admin_dwork()`, `ionic_admin_work()`, `ionic_admin_busy_wait()`, and `ionic_admin_cancel()`. Queue construction uses `ionic_create_rdma_admincq()`, `ionic_create_rdma_adminq()`, `ionic_create_eq()`, and their destroy helpers. Event handling uses `ionic_poll_eq()`, `ionic_poll_eq_isr()`, `ionic_poll_eq_work()`, `ionic_cq_event()`, and `ionic_qp_event()`.

## Control Flow
Admin creation clamps requested EQ/AQ counts, requires minimum event/admin queues, creates EQs with interrupts and device queue commands, creates one admin CQ per admin queue, creates admin queues backed by host queue memory, attaches CQ context to AQ, and marks queues active. Posting selects an admin queue by CPU, queues a work request, and immediately polls if the queue was idle. Polling first completes CQEs, validates type/qid/command index, copies completion state to matching WQEs, consumes admin queue strides, rings CQ credits, arms CQ interrupts, then posts pending WQEs into available admin queue space and rings the admin doorbell. Waiting supports busy-wait, interruptible wait, uninterruptible wait, and teardown semantics. The delayed watchdog polls missed completions, warns after a threshold, and kills/resets RDMA on timeout. EQ ISR/work polling reads events with color bits, dispatches CQ notifications/errors and QP events, then re-arms interrupts or continues work.

## State And Persistence
Runtime state includes per-device `admin_state`, per-AQ `admin_state`, pending/posted WR lists, queue producer/consumer indexes, CQ color and arm state, watchdog stamp, interrupt masks/credits, xarray-backed QP/CQ lookup state owned elsewhere, and reset/admin delayed work. Admin kill transitions active queues through paused/killed states, completes pending admin WQEs locally as killed, flushes QPs/CQs, and may dispatch `IB_EVENT_DEVICE_FATAL`. There is no nonvolatile persistence.

## Dependencies And Integration Points
The file depends on shared Ionic net-driver device commands (`ionic_adminq_post_wait`, `ionic_intr_*`, LIF reset helpers), RDMA CQ/QP object helpers from `ionic_controlpath.c`, queue helpers, page-table/CQ creation helpers, workqueues, interrupts, DMA ordering barriers, and RDMA core event callbacks. Admin opcodes are consumed by the controlpath verbs operations for AH/MR/CQ/QP creation and modification.

## Risks
Admin timeout kills all admin queues and flushes QPs, so false timeouts or missed completions are disruptive. `ionic_admin_busy_wait()` can hold CPU with IRQs disabled for up to the configured retry window. Admin CQ validation drops malformed completions but still advances CQ producer/color, so hardware/software index mismatch handling is critical. Kill/reset uses local IRQ disabling and spin locks while flushing objects; lock ordering against CQ/QP datapath locks must be stable. Destroy assumes callers already killed/canceled work before freeing queues. Partial EQ/AQ creation is allowed above minimums, so later vector arithmetic must tolerate reduced counts.

## Test Signals
Test admin queue creation at min/max/partial counts, admin WQE stride splitting, CQE validation failures, missed event polling, watchdog warning and timeout reset, busy-wait AH paths, interruptible wait cancellation, teardown wait semantics after killed admin, EQ ISR budget overflow and work continuation, CQ notify/error events, QP event translations, LIF reset failure fallback, destroy after partial creation, and lockdep under kill/reset with active QPs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_admin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_controlpath.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_controlpath.c

## Purpose
`ionic_controlpath.c` implements most Ionic RDMA verbs control-plane operations: user contexts and mmap, PDs, AHs, MRs/MWs, CQs, QPs, CMB-backed queues, QP state transitions, query paths, flushing, and resource-ID allocation. It translates RDMA-core objects into Ionic admin commands and shared queue/page-table resources.

## Important APIs, Types, And Functions
Important entry points include `ionic_alloc_ucontext()`, `ionic_dealloc_ucontext()`, `ionic_mmap()`, `ionic_mmap_free()`, `ionic_alloc_pd()`, `ionic_dealloc_pd()`, `ionic_create_ah()`, `ionic_query_ah()`, `ionic_destroy_ah()`, `ionic_get_dma_mr()`, `ionic_reg_user_mr()`, `ionic_reg_user_mr_dmabuf()`, `ionic_dereg_mr()`, `ionic_alloc_mr()`, `ionic_map_mr_sg()`, `ionic_alloc_mw()`, `ionic_dealloc_mw()`, `ionic_create_cq()`, `ionic_destroy_cq()`, `ionic_create_qp()`, `ionic_modify_qp()`, `ionic_query_qp()`, `ionic_destroy_qp()`, `ionic_flush_qp()`, and `ionic_notify_flush_cq()`. Core helpers include resource allocators `ionic_get_*id()`, `ionic_mmap_entry_insert()`, AH header builders, admin command wrappers for AH/MR/CQ/QP, SQ/RQ init/destroy helpers, CMB mapping helpers, `ionic_clean_cq()`, and `ionic_reset_qp()`.

## Control Flow
User context allocation validates ABI input, allocates a doorbell ID, inserts a doorbell mmap entry, and returns device capabilities, queue types, opcode support, UDMA count, and EXPDB support. AH creation builds an Ethernet/VLAN/IPv4-or-IPv6/UDP RoCE header template, DMA maps it, posts a create-AH admin command, and returns the AH ID. MR registration pins umem or dmabuf, picks a supported page size, initializes a page table, creates the MR through admin, and frees the temporary page-table buffer while retaining object/umem state. CQ creation may create one CQ per selected UDMA, validates user qdescs or allocates kernel queues, initializes page tables, posts create-CQ admin commands, and returns CQ IDs. QP creation intersects UDMA masks from CQs and userspace, allocates a QPID and optional AH ID/header for RC, initializes SQ/RQ from user qdescs or kernel queues, optionally places queues in CMB/EXPDB memory, posts create-QP admin command, creates user mmap entries for CMB queues, copies response data, stores the QP in the device xarray, and updates returned caps. Modify-QP validates RDMA state transitions and privileged qkey use, posts modify-QP admin command, then locally flushes or resets queues for ERR/RESET transitions.

## State And Persistence
State is volatile and split across resource bitmaps, RDMA objects, xarrays, queues, page-table buffers, CMB allocations, mmap entries, and admin-created device state. `ionic_ctx` owns a DBID and mmap entry. PDs own PD IDs and flags. AHs store AH ID, SGID index, and packed header. MRs/MWs own MR IDs, keys, flags, umem, page-table metadata, and a `created` flag. CQs store queue state, CQID/EQID, lock, flush lists, color/credit, kref/completion, optional umem, and xarray membership. QPs store QPID/UDMA, SQ/RQ queue metadata, CMB placement state, mmap entries, AH header/ID for RC, CQ IDs, flush/reset flags, state, kref/completion, and metadata arrays. No state persists across driver reload or LIF reset.

## Dependencies And Integration Points
The file depends on `ionic_admin.c` for command posting/waiting, Ionic queue and page-table helpers, shared net-driver LIF configuration, CMB allocation APIs, RDMA core uverbs and mmap APIs, umem/dmabuf APIs, GID/GRH/UD header helpers, CQ/QP datapath completion functions, and resource-ID helpers. It is one of the main providers of `ib_device_ops` for the Ionic RDMA device.

## Risks
`ionic_create_qp()` stores the QP in the xarray after copying the userspace response; if xarray insertion fails, the `err_resp` path removes user mmap entries that may not have been initialized for all CMB combinations, so NULL-safe assumptions should be verified. Query-QP allocates `hdr_buf` and DMA maps it but later reconstructs AV from `qp->hdr`, not the just-filled `hdr_buf`, suggesting either firmware writes are unused or the intended copy-back is missing. Query-QP unmaps DMA buffers with `sizeof(*query_*)` rather than the mapped `PAGE_SIZE`, which deserves DMA-debug testing. `ionic_get_qpid()` toggles `next_qpid_udma_idx` with XOR against `udma_count - 1`, which assumes power-of-two UDMA counts. Destroy paths return early on failed destroy admin commands, leaving host resources intact for safety but possibly leaking until reset. CMB required-vs-best-effort fallback is subtle, especially with EXPDB and WC/UC mmap flags. `ionic_dereg_mr()` calls `ionic_pgtbl_unbuf()` both after successful registration and again at deregistration; helper idempotence is important.

## Test Signals
Test ucontext DB mmap and response ABI, invalid qdesc validation, mmap WC/noncached selection, PD ID exhaustion, AH IPv4/IPv6/VLAN/ECN header construction, AH busy-wait non-sleepable paths, user MR and dmabuf MR registration, page-size negotiation failures, FRMR SG mapping and DMA sync, MW type 1/2 creation, CQ multi-UDMA creation and unwind, CQ destroy partial admin failures, QP UDMA mask intersection, GSI and RC QP creation, CMB required/best-effort/EXPDB paths, userspace mmap response failures, xarray insertion failure, modify state validation and privileged qkey rejection, ERR flushing and RESET cleaning, query-QP AV/cap extraction, destroy with active CQ entries, and reset/kill behavior interacting with controlpath objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_controlpath.c -->
