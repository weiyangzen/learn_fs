# subset-b-003946 research

Grouped research for mlx5 InfiniBand/RDMA queue-pair, shared-receive-queue, resource-tracking, UMR, and uverbs support under `sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/qp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/qp.c

## Purpose
`qp.c` is the mlx5 verbs-layer implementation for Queue Pairs, receive Work Queues, RSS indirection tables, XRC domains, and drain/counter helpers. It translates RDMA core QP/WQ create, modify, query, destroy, and drain operations into mlx5 command contexts and low-level send/receive queue state, while also handling raw Ethernet QPs that are represented as separate TIS/TIR/SQ/RQ hardware objects.

## Important APIs, types, and functions
- `mlx5_ib_create_qp()`, `mlx5_ib_modify_qp()`, `mlx5_ib_query_qp()`, and `mlx5_ib_destroy_qp()` are the main RDMA core QP entry points.
- `create_user_qp()`, `create_kernel_qp()`, `create_dci()`, `create_dct()`, and `create_xrc_tgt_qp()` implement type-specific creation for userspace, kernel, DCI, DCT, and XRC target QPs.
- Raw packet support is split through `create_raw_packet_qp_tis()`, `create_raw_packet_qp_sq()`, `create_raw_packet_qp_rq()`, `create_raw_packet_qp_tir()`, `create_raw_packet_qp()`, and matching destroy/modify helpers.
- `struct mlx5_create_qp_params` collects parsed userspace command metadata, response sizing, RSS mode, user index, and the RDMA init attributes.
- `set_rq_size()`, `calc_sq_size()`, `calc_send_wqe()`, `sq_overhead()`, and `get_send_sge()` size WQEs and queue buffers from verbs capabilities and mlx5 hardware limits.
- `process_vendor_flags()`, `process_create_flags()`, `check_qp_type()`, `check_valid_flow()`, `check_qp_attr()`, and `check_ucmd_data()` validate QP type, capability flags, user command layout, RSS constraints, and reserved fields.
- `__mlx5_ib_modify_qp()` is the central state-transition engine for non-DCT QPs. It builds QPC fields, address paths, counters, affinity, atomic capability, ECE response, and invokes either `mlx5_core_qp_modify()` or raw-packet SQ/RQ modification.
- `mlx5_ib_modify_dct()` handles the special two-step DCT lifecycle where create data is staged at QP creation and the hardware DCT is created on INIT-to-RTR.
- `mlx5_set_path()`, `mlx5r_ib_rate()`, and the rate mapping helpers translate RDMA address handles, RoCE Ethernet metadata, InfiniBand path fields, UDP source port entropy, and static rates into mlx5 address vector fields.
- `mlx5_ib_read_wqe_sq()`, `mlx5_ib_read_wqe_rq()`, and `mlx5_ib_read_wqe_srq()` support diagnostic reading of user/kernel WQEs, including wrapped SQ WQEs.
- `mlx5_ib_create_wq()`, `mlx5_ib_modify_wq()`, `mlx5_ib_destroy_wq()`, `mlx5_ib_create_rwq_ind_table()`, and `mlx5_ib_destroy_rwq_ind_table()` implement standalone receive WQs and RQT-backed RSS objects.
- `mlx5_ib_drain_sq()`, `mlx5_ib_drain_rq()`, and `handle_drain_completion()` provide RDMA drain support, including direct-poll and internal-error handling.
- `mlx5_ib_qp_set_counter()` binds QPs to RDMA counters immediately in RTS or defers until RTS if needed.

## Control flow
QP creation starts by initializing device SRQ resources, validating QP type and flow, parsing userspace command sizes, checking reserved fields, processing mlx5 vendor flags, deriving a user index, and validating standard create flags. `create_qp()` dispatches to RSS raw TIR creation, DCT staging, DCI creation, XRC target creation, GSI creation, or the common user/kernel QP path.

Common user QP creation allocates or accepts a UAR/BFREG, maps the user queue memory and doorbell record, computes PAS entries, fills QPC fields such as PD, queue sizes, CQs, SRQ/XRCD defaults, timestamp format, and user index, then calls `mlx5_qpc_create_qp()`. Kernel QP creation allocates mlx5 fragment buffers, doorbells, WRID arrays, send queue tracking arrays, and a kernel UAR, then creates the QP. Successful non-RSS QPs are added under `reset_flow_resource_lock` to the device QP list and CQ send/receive lists for reset cleanup.

Raw packet QPs use a different hardware topology. Send side creation creates a TIS and tracked SQ. Receive side creation creates a tracked RQ and direct TIR. RSS raw QPs create an indirect TIR pointing at an RWQ indirection table and validate Toeplitz hash fields and inner/outer tunnel hash requests.

Modify flow checks driver profile permissions, userspace modify command data, state transition legality through RDMA core or DCI-specific rules, port and P_Key bounds, and RDMA atomic depth limits. `__mlx5_ib_modify_qp()` then maps IB states to mlx5 command opcodes, builds a QPC, applies optional fields through an optparam mask, handles raw packet rate limit and vport SQ steering separately, updates software state, cleans CQs and queue indices on kernel RESET, and applies pending counter binding when a QP reaches RTS.

Destroy flow first transitions active QPs to RESET where possible, removes reset/CQ tracking list nodes under the CQ locks, cleans kernel CQ entries, destroys raw packet or transport hardware objects, and releases user mappings or kernel buffers. DCT and GSI use their own destroy helpers.

## State and persistence
The primary persistent state is hardware QP/SQ/RQ/TIS/TIR/RQT/DCT state in the mlx5 device. In-memory state includes `qp->state`, queue sizes and WQE shifts, BFREG ownership, doorbell mappings, raw packet SQ/RQ state, rate limit information, ECE data, enabled flags, counter-pending state, OOO datapath mode, list membership for reset handling, and per-QP mutex protection.

Userspace QPs persist mappings to user memory (`ib_umem`) and user doorbell records until destroy. Kernel QPs own mlx5 fragment buffers, doorbells, WRID arrays, and send-queue bookkeeping. Raw packet QPs own extra flow rules, TIS/TIR IDs, and optional packet pacing rate table entries. DCT creation data is stored in `qp->dct.in` until INIT-to-RTR creates the hardware DCT.

## Dependencies and integration points
This file integrates with the RDMA core QP/WQ/RSS/XRCD verbs, mlx5 command helpers from `qpc.c`, GSI support, counters, reset flow tracking, CQ cleanup, mlx5 flow steering, LAG affinity, RoCE/IB address-handle conversion, UAR/BFREG allocation, user memory pinning, DMA PAS population, and mlx5 capability tables. It also provides QP event workqueue initialization and cleanup used by the resource event path.

## Risks
- QP creation combines many capability flags and QP subtypes; a missed validation can expose unsupported hardware fields or reject valid userspace ABI combinations.
- Raw packet QPs have split SQ/RQ/TIS/TIR state; partial create or modify failures must unwind every created object and rate/flow steering resource in the right order.
- State transition masks are dense and type-specific. Changing `opt_mask`, `ib_nr_to_mlx5_nr()`, or DCI/DCT validation can silently break legal transitions or allow illegal ones.
- Userspace command compatibility relies on exact `inlen`, `outlen`, `comp_mask`, and reserved-field checks. ABI drift is a high-risk area.
- Queue sizing uses powers of two, shifts, and hardware maximums; overflow or off-by-one mistakes can corrupt WQE layout or PAS sizing.
- Reset and CQ cleanup are concurrency-sensitive because QPs are on device and CQ lists while asynchronous event/reset paths can inspect them.
- UAR/BFREG allocation differs for static, dynamic, and direct UAR index modes; leaks or double frees can affect other QPs in the same context.
- DCT lifecycle is unusual because the hardware object is not created until modify; destroy and query paths must respect staged versus live state.

## Test signals
- Build with mlx5 InfiniBand enabled and run sparse/smatch-style checks around shifts, enum conversions, and userspace struct bounds.
- RDMA verbs tests should cover RC, UC, UD, XRC INI/TGT, DCI, DCT, GSI/HW GSI, REG_UMR, raw packet, RSS raw, and source-QPN QP creation.
- Exercise user and kernel QP creation with invalid queue sizes, non-power-of-two SQ counts, invalid BFREG/UAR flags, unsupported create/vendor flags, and reserved udata bytes.
- Modify-state tests should cover every legal state transition and representative illegal masks, including DCI/DCT-specific paths, ECE input/output, OOO datapath enablement, atomics, and LAG affinity.
- Raw packet tests should cover SQ-only, RQ-only, bidirectional, RSS Toeplitz, tunnel hash, CVLAN stripping, scatter FCS, end padding, vport SQ steering, counter binding, and packet pacing changes/failures.
- Reset/drain tests should verify CQ cleanup, drain completion under direct/softirq/workqueue polling, and internal-error behavior.
- Counter tests should validate immediate RTS binding, deferred pre-RTS binding, default counter fallback, and firmware without counter-set modification support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/qp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/qp.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/qp.h

## Purpose
`qp.h` declares the mlx5 QP resource table and the core QP/DCT/SQ/RQ/XRCD helper interface shared by `qp.c`, `qpc.c`, UMR, and related mlx5 IB modules. It is the local contract between verbs-level queue-pair code and mlx5 command/resource tracking code.

## Important APIs, types, and functions
- `struct mlx5_qp_table` stores the mlx5 event notifier, DCT `xarray`, spinlock, and radix tree used for QP/SQ/RQ resource lookup.
- `mlx5_init_qp_table()` and `mlx5_cleanup_qp_table()` initialize and unregister the resource/event infrastructure.
- `mlx5_qpc_create_qp()`, `mlx5_core_qp_modify()`, `mlx5_core_destroy_qp()`, `mlx5_core_qp_query()`, `mlx5_core_create_dct()`, `mlx5_core_destroy_dct()`, and `mlx5_core_dct_query()` expose mlx5 command operations for transport QPs and DCTs.
- `mlx5_core_create_rq_tracked()`, `mlx5_core_destroy_rq_tracked()`, `mlx5_core_create_sq_tracked()`, and `mlx5_core_destroy_sq_tracked()` expose event-tracked raw RQ/SQ creation and destruction.
- `mlx5_core_res_hold()` and `mlx5_core_res_put()` provide refcounted lookup/release for event resources.
- `mlx5_core_set_delay_drop()` exposes the firmware command for delay-drop receive queues.
- `mlx5_core_xrcd_alloc()` and `mlx5_core_xrcd_dealloc()` manage XRCD numbers.
- `mlx5_ib_qp_set_counter()`, `mlx5_ib_qp_event_init()`, `mlx5_ib_qp_event_cleanup()`, and `mlx5r_ib_rate()` are exported helpers implemented in `qp.c`.

## Control flow
Other mlx5 IB files include this header when they need to create or destroy tracked QP-like resources, query or modify QPs, hold event resources during asynchronous callbacks, or allocate XRCDs. The table is initialized during device setup, used by resource creation paths to publish objects, and cleaned up on device teardown.

## State and persistence
The header itself stores no state, but it defines the structure that persists QP resource lookup state inside `struct mlx5_ib_dev`. The radix tree and DCT xarray back asynchronous event dispatch and protect resources with explicit refcounts and completions.

## Dependencies and integration points
It depends on `struct mlx5_ib_dev`, mlx5 core QP/DCT types, RDMA counter and QP types, xarray, radix tree, notifier blocks, and spinlocks. It is tightly coupled with `qpc.c` for implementation and with `qp.c` for verbs-level usage.

## Risks
- The resource table layout is consumed by asynchronous event code; changing it affects locking and lifetime rules.
- APIs mix QP, raw SQ/RQ, DCT, XRCD, and counter operations. Callers must choose the helper that matches the hardware object type.
- `mlx5_core_res_hold()`/`put()` require strict pairing because event handlers can otherwise race destroy paths.

## Test signals
- Compile coverage should ensure all prototypes remain consistent with `qp.c`, `qpc.c`, and UMR callers.
- Event-injection or fault tests should validate that QP/SQ/RQ/DCT resources can be looked up, refcounted, and released during destroy races.
- XRCD and delay-drop users should verify command wrappers still pass correct IDs and UID fields after signature changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/qp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/qpc.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/qpc.c

## Purpose
`qpc.c` is the mlx5 IB command and resource-tracking backend for QPs, DCTs, tracked raw SQ/RQ objects, XRCD allocation, delay-drop configuration, and QP-related asynchronous events. It provides the lower-level hardware command operations used by `qp.c`.

## Important APIs, types, and functions
- `mlx5_qpc_create_qp()`, `mlx5_core_qp_modify()`, `mlx5_core_destroy_qp()`, and `mlx5_core_qp_query()` wrap CREATE/MODIFY/DESTROY/QUERY QP firmware commands and resource registration.
- `mlx5_core_create_dct()`, `mlx5_core_destroy_dct()`, and `mlx5_core_dct_query()` manage DCT hardware objects, including drain-before-destroy.
- `mlx5_core_create_rq_tracked()`, `mlx5_core_destroy_rq_tracked()`, `mlx5_core_create_sq_tracked()`, and `mlx5_core_destroy_sq_tracked()` publish raw RQ/SQ resources into the QP table so mlx5 events can be delivered to their owners.
- `create_resource_common()`, `destroy_resource_common()`, `modify_resource_common_state()`, `mlx5_get_rsc()`, and `mlx5_core_put_rsc()` implement radix-tree resource lifetime, invalidation, refcounting, and completion-based teardown.
- `rsc_event_notifier()`, `dct_event_notifier()`, and `is_event_type_allowed()` translate mlx5 notifier events into resource callbacks while filtering unsupported event/resource-type combinations.
- `modify_qp_mbox_alloc()` and `get_ece_from_mbox()` allocate opcode-specific modify mailboxes, copy QPC data, set ECE inputs, and extract ECE outputs.
- `mlx5_core_xrcd_alloc()` and `mlx5_core_xrcd_dealloc()` wrap XRCD firmware commands.
- `mlx5_core_set_delay_drop()` programs the delay-drop timeout.

## Control flow
Device setup calls `mlx5_init_qp_table()`, which initializes the radix tree, DCT xarray, debugfs, and mlx5 notifier. QP/SQ/RQ creation executes the firmware command first, then inserts the resulting number into the resource table with a resource type encoded above `MLX5_USER_INDEX_LEN`. If resource insertion fails, the hardware object is destroyed.

Asynchronous events arrive through `rsc_event_notifier()`. DCT drained events are handled through the DCT xarray and complete the DCT's `drained` completion. QP/SQ/RQ events compute a resource number from event data plus queue type, hold the resource, validate the event type, and call the object's event handler. For QP/SQ/RQ events the handler is responsible for putting the resource.

Destroy removes or invalidates the resource from lookup before destroying hardware. RQ destroy marks the common resource invalid first because failed firmware destroy can be retried; successful destroy then removes and waits for the last event reference. DCT destroy drains the object, waits for drained completion, uses an `XA_ZERO_ENTRY` placeholder to avoid erasing a newly-created DCT that reuses the same number, and then destroys the hardware DCT.

## State and persistence
The QP table persists a radix-tree mapping from encoded QP/SQ/RQ numbers to `struct mlx5_core_rsc_common`, plus a DCT xarray. Each tracked resource owns a refcount, completion, resource type, invalid flag, UID, QPN, event callback, and creation PID. Hardware state persists in the device until destroy commands complete.

## Dependencies and integration points
This file integrates with the mlx5 command executor, mlx5 notifier events, debugfs QP tracking, xarray/radix-tree kernel containers, resource refcount completions, and RDMA device type checks. It is the implementation behind declarations in `qp.h` and is used by `qp.c` for all command-level QP operations.

## Risks
- Event delivery races with destroy; incorrect invalidation or refcount handling can cause use-after-free or lost completion.
- DCT/SRQ-number reuse is explicitly handled with `XA_ZERO_ENTRY`; changing the destroy sequence can erase a newly created object.
- `modify_qp_mbox_alloc()` has opcode-specific mailbox layouts. Missing ECE or QPC handling for a new opcode can break modify responses.
- Tracked RQ destroy can fail and be retried. Code must restore resource validity on firmware failure.
- Event type filtering depends on the encoded event queue type and resource type matching the radix-tree key.

## Test signals
- Fault-injection tests should force firmware create/destroy/modify failures and verify command unwind paths and resource-table cleanup.
- Event tests should inject or emulate path migration, communication established, SQ drained, SRQ last WQE, WQ fatal/access/request errors, and DCT drained events.
- Destroy-race tests should create/destroy QPs, RQs, SQs, and DCTs while events arrive, checking refcount completion and reuse behavior.
- ECE tests should exercise modify opcodes that return ECE values and confirm userspace sees updated options.
- Build tests should cover SMI and non-SMI RDMA device types to exercise debugfs gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/qpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/restrack.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/restrack.c

## Purpose
`restrack.c` registers mlx5-specific RDMA resource tracking callbacks. It enriches RDMA netlink resource dumps with raw mlx5 hardware resource data, ODP memory-region statistics, ODP mode labels, and mlx5 driver QP subtypes.

## Important APIs, types, and functions
- `mlx5_ib_restrack_init()` installs `restrack_ops` into the RDMA device.
- `dump_rsc()` drives mlx5 resource dump commands using `mlx5_rsc_dump_cmd_create()`, `mlx5_rsc_dump_next()`, and `mlx5_rsc_dump_cmd_destroy()`.
- `fill_res_raw()` allocates a bounded buffer, dumps raw mlx5 hardware resource data, and emits `RDMA_NLDEV_ATTR_RES_RAW`.
- `fill_stat_mr_entry()` emits ODP counters for page faults, handled faults, invalidations, handled invalidations, and prefetches.
- `fill_res_mr_entry()` labels ODP MRs as implicit or explicit under `RDMA_NLDEV_ATTR_DRIVER`.
- `fill_res_mr_entry_raw()`, `fill_res_cq_entry_raw()`, and `fill_res_qp_entry_raw()` dump raw MKEY, CQ, and QP PRM data.
- `fill_res_qp_entry()` exposes mlx5 driver QP subtypes `REG_UMR`, `DCT`, and `DCI` for `IB_QPT_DRIVER`-style resources.

## Control flow
Initialization calls `ib_set_device_ops()` with a static `ib_device_ops` containing only resource-tracking callbacks. When RDMA netlink requests resource data, RDMA core calls the relevant fill callback. Raw callbacks allocate up to `MAX_DUMP_SIZE`, ask mlx5 firmware to dump one object by type and index, copy each returned page chunk into the buffer, and append it as a netlink attribute. MR callbacks skip non-ODP resources and otherwise emit driver metadata or statistics.

## State and persistence
This file maintains no long-lived state beyond registered device ops. It reads live hardware resource state through mlx5 dump commands and reads live ODP atomic counters from `struct mlx5_ib_mr`. Temporary dump buffers and pages are freed after each request.

## Dependencies and integration points
It integrates with RDMA netlink resource tracking, mlx5 resource dump firmware APIs, ODP MR statistics, netlink attribute helpers, mlx5 CQ/QP/MKEY identifiers, and mlx5 private QP type definitions. It is initialized through the declaration in `restrack.h`.

## Risks
- `dump_rsc()` enforces `MAX_DUMP_SIZE` of 1024 bytes; larger firmware dumps fail instead of truncating, so new hardware dump formats may need a larger bound.
- Netlink attribute construction can fail with `-EMSGSIZE`; nested attributes must be cancelled on every error path.
- Raw dumps expose low-level hardware state and must use the correct segment type and object number to avoid misleading diagnostics.
- Only ODP MRs receive stats and driver labels; callers must not interpret missing attributes as an error for regular MRs.
- `fill_res_qp_entry()` only recognizes selected driver QP subtypes; newly added driver QP types need updates for useful netlink output.

## Test signals
- RDMA netlink resource dump tests should verify raw CQ/QP/MR attributes are present and bounded for mlx5 devices.
- ODP MR tests should create implicit and explicit ODP MRs and confirm mode labels and counter names/values are emitted.
- Driver QP tests should create REG_UMR, DCT, and DCI resources and check subtype and `IB_QPT_DRIVER` type reporting.
- Failure tests should force small netlink buffers, resource dump command errors, and allocation failures to validate cleanup and `-EMSGSIZE`/error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/restrack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/restrack.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/restrack.h

## Purpose
`restrack.h` is the local header for mlx5 RDMA resource tracking integration. It exposes the initialization hook that installs mlx5 resource dump callbacks into the RDMA device.

## Important APIs, types, and functions
- Includes `mlx5_ib.h` for `struct mlx5_ib_dev`.
- Declares `mlx5_ib_restrack_init(struct mlx5_ib_dev *dev)`.

## Control flow
Device initialization code includes this header and calls `mlx5_ib_restrack_init()` once the `mlx5_ib_dev` is ready to receive RDMA device ops. The implementation in `restrack.c` registers the static callback table.

## State and persistence
The header stores no state. The only persistent effect of its API is that the RDMA device receives mlx5-specific resource tracking callbacks.

## Dependencies and integration points
It depends on mlx5 IB device definitions and integrates with RDMA core device-ops registration through `restrack.c`.

## Risks
- The header is intentionally small; the main risk is signature drift between initialization callers and `restrack.c`.
- If initialization ordering changes, callers must still ensure resource-tracking ops are installed before userspace netlink queries are expected.

## Test signals
- Compile coverage catches prototype mismatches.
- Device initialization tests should verify mlx5 resource tracking callbacks are available through RDMA netlink after device registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/restrack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/srq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/srq.c

## Purpose
`srq.c` implements RDMA core shared receive queue verbs for mlx5. It creates, modifies, queries, destroys, and posts receives to basic, XRC, and tag-matching SRQs, handling both userspace-backed and kernel-backed SRQ buffers.

## Important APIs, types, and functions
- `mlx5_ib_create_srq()`, `mlx5_ib_modify_srq()`, `mlx5_ib_query_srq()`, and `mlx5_ib_destroy_srq()` are the RDMA core SRQ operations.
- `create_srq_user()` parses `struct mlx5_ib_create_srq`, validates reserved fields, obtains optional user index, pins user buffer memory, maps the user doorbell, and sets UID/user-index fields.
- `create_srq_kernel()` allocates a kernel doorbell, fragmented buffer, next-WQE ring, PAS array, and WRID array.
- `destroy_srq_user()` and `destroy_srq_kernel()` release the resources created by the two creation paths.
- `mlx5_ib_srq_event()` converts mlx5 SRQ limit and catastrophic events into RDMA `IB_EVENT_SRQ_LIMIT_REACHED` and `IB_EVENT_SRQ_ERR` callbacks.
- `mlx5_ib_post_srq_recv()` posts receive WRs to kernel SRQs by filling WQE data segments, maintaining the free-list head, and updating the doorbell record.
- `mlx5_ib_free_srq_wqe()` returns completed kernel SRQ WQEs to the free list.

## Control flow
Creation validates SRQ type (`BASIC`, `XRC`, or `TM`), max WR/SGE against device limits, initializes locks, rounds queue depth to a power of two with one spare entry, computes descriptor size and gather capacity, then builds either user or kernel backing resources. It fills `mlx5_srq_attr` with queue geometry, flags, XRC domain/default XRCD, tag-matching parameters, CQ number, PD, and doorbell DMA, then calls `mlx5_cmd_create_srq()`. On success it installs the event callback, returns the SRQN to userspace if needed, and normalizes reported max WR.

Modify rejects resizing and only supports arming the SRQ low-watermark limit through `mlx5_cmd_arm_srq()`. Query allocates an attribute object, calls `mlx5_cmd_query_srq()`, and reports SRQ limit/max WR/max SGE. Destroy calls `mlx5_cmd_destroy_srq()` before freeing user or kernel backing resources.

Kernel receive posting is protected by `srq->lock` with IRQ save. It rejects internal-error devices, too many SGEs, and full queues, records WRIDs, consumes the next free WQE, writes scatter segments and a terminate-scatter-list marker when room remains, increments `wqe_ctr`, orders descriptor writes with `wmb()`, and updates the doorbell record.

## State and persistence
Persistent hardware state includes the SRQ/XRC/XRQ/RMP object, low-watermark arm state, doorbell address, PD/CQ/XRCD linkage, and PAS-backed queue memory. In-memory state includes the SRQ mutex, posting spinlock, WQE head/tail free list, WRID array, WQE counter, signature flag, user memory mapping, doorbell mapping, and fragmented kernel buffer.

## Dependencies and integration points
This file integrates with RDMA SRQ verbs, mlx5 SRQ command wrappers in `srq_cmd.c`, PD/CQ/XRCD helpers, mlx5 doorbell and fragment-buffer utilities, userspace ABI structs, tag matching capabilities, and device resource initialization (`mlx5_ib_dev_res_cq_init()`).

## Risks
- Queue depth uses a spare WQE and power-of-two masking; mistakes can make full and empty states ambiguous.
- Descriptor-size calculations mix next segments, data segments, signatures, and hardware maximum WQE size; overflow checks are important.
- Userspace creation depends on exact reserved-field and user-index ABI handling.
- Tag-matching SRQ list size uses `ilog2(max_num_tags) + 1` and must stay within hardware capability.
- Kernel posting assumes callers use kernel SRQs with allocated `wrid`; userspace SRQs are posted by userspace, not this path.
- Doorbell updates require correct memory ordering before writing the counter.

## Test signals
- Create/query/destroy tests should cover basic, XRC, and tag-matching SRQ types, user and kernel creation, invalid reserved fields, invalid sizes, and max capability boundaries.
- Modify tests should verify low-watermark arming and reject resize requests or limits greater than/equal to queue max.
- Kernel post tests should cover full queue, too many SGEs, zero-SGE receives, terminate-scatter-list insertion, internal-error return, and WQE free/reuse.
- Event tests should inject SRQ limit and catastrophic events and verify RDMA event callbacks.
- Tag-matching tests should cover `max_num_tags` capability limits and RNDV flag programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/srq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/srq.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/srq.h

## Purpose
`srq.h` defines mlx5 SRQ command attributes, core SRQ resource state, SRQ table state, flags, and function prototypes shared by SRQ verbs and command code.

## Important APIs, types, and functions
- `MLX5_SRQ_FLAG_ERR`, `MLX5_SRQ_FLAG_WQ_SIG`, and `MLX5_SRQ_FLAG_RNDV` mark error state, WQ signature enablement, and rendezvous/tag-matching behavior.
- `struct mlx5_srq_attr` is the command-facing SRQ description: type, flags, queue geometry, SRQN, XRCD, page offset, CQN, PD, low watermark, user index, doorbell record, PAS, umem, tag-matching fields, and UID.
- `struct mlx5_core_srq` is the tracked hardware SRQ resource. Its `common` resource header must be first, followed by SRQN, queue capacities, WQE shift, event callback, and UID.
- `struct mlx5_srq_table` stores the notifier block and xarray used for SRQ event lookup.
- Declares command helpers `mlx5_cmd_create_srq()`, `mlx5_cmd_destroy_srq()`, `mlx5_cmd_query_srq()`, `mlx5_cmd_arm_srq()`, and `mlx5_cmd_get_srq()`.
- Declares table lifecycle helpers `mlx5_init_srq_table()` and `mlx5_cleanup_srq_table()`.

## Control flow
`srq.c` fills `mlx5_srq_attr` from RDMA verbs attributes and user/kernel buffer state, then passes it to `srq_cmd.c`. `srq_cmd.c` fills hardware command contexts, publishes `mlx5_core_srq` objects in the table, and routes events back through the callback declared in the core SRQ object.

## State and persistence
The header defines the persistent in-memory representation of an SRQ resource and the device-level SRQ event table. Hardware persistence is represented by SRQN, UID, queue geometry, PAS, and command attributes.

## Dependencies and integration points
It depends on mlx5 resource-common layout, RDMA `ib_umem`, notifier blocks, xarray, and mlx5 event types. It is consumed by both verbs-level SRQ code and firmware command wrappers.

## Risks
- `struct mlx5_core_srq.common` must remain first for casts through common resource code.
- Attribute fields are reused across legacy SRQ, XRC SRQ, RMP, and XRQ command formats; callers must set only fields valid for the selected type.
- Event callbacks rely on `srqn` and table lookup state remaining valid until refcounts drain.

## Test signals
- Compile coverage catches structure and prototype drift between `srq.c` and `srq_cmd.c`.
- Event tests should confirm `mlx5_cmd_get_srq()` and notifier lookup work for created SRQs and avoid stale pointers after destroy.
- Command tests should exercise every `mlx5_srq_attr` field used by basic, XRC, RMP, XRQ, and tag-matching flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/srq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/srq_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/srq_cmd.c

## Purpose
`srq_cmd.c` is the mlx5 firmware command backend for SRQ-like receive resources. It converts `mlx5_srq_attr` into legacy SRQ, XRC SRQ, RMP, or XRQ command formats, tracks SRQs in an xarray, and routes SRQ events from mlx5 notifier callbacks.

## Important APIs, types, and functions
- `mlx5_cmd_create_srq()`, `mlx5_cmd_destroy_srq()`, `mlx5_cmd_query_srq()`, and `mlx5_cmd_arm_srq()` are the public command operations used by `srq.c`.
- `get_pas_size()`, `set_wq()`, `set_srqc()`, `get_wq()`, and `get_srqc()` compute PAS sizes and map common attributes into or out of mlx5 WQ/SRQC command structures.
- `create_srq_cmd()`, `destroy_srq_cmd()`, `arm_srq_cmd()`, and `query_srq_cmd()` implement pre-ISSI legacy SRQ commands.
- `create_xrc_srq_cmd()`, `destroy_xrc_srq_cmd()`, `arm_xrc_srq_cmd()`, and `query_xrc_srq_cmd()` implement XRC SRQ commands.
- `create_rmp_cmd()`, `destroy_rmp_cmd()`, `arm_rmp_cmd()`, and `query_rmp_cmd()` implement RMP-backed SRQs.
- `create_xrq_cmd()`, `destroy_xrq_cmd()`, `arm_xrq_cmd()`, and `query_xrq_cmd()` implement XRQ and tag-matching SRQs.
- `create_srq_split()`, `destroy_srq_split()`, and query/arm switch logic select command families based on ISSI and resource type.
- `mlx5_cmd_get_srq()` holds an SRQ by SRQN from the xarray for event users.
- `srq_event_notifier()` receives mlx5 SRQ events, holds the SRQ, calls its event callback, and releases it.

## Control flow
Creation first maps RDMA SRQ type to resource kind: XRC uses `MLX5_RES_XSRQ`, tag matching uses `MLX5_RES_XRQ`, and basic uses `MLX5_RES_SRQ`. The selected create function computes or validates page size for user memory, allocates a command buffer sized for PAS entries, fills SRQ/WQ context fields, populates PAS from `ib_umem` or kernel PAS arrays, executes the firmware command, and stores SRQN/UID. The created resource is refcount-initialized and inserted into `dev->srq_table.array`.

Destroy uses `xa_cmpxchg_irq()` to replace the SRQ entry with `XA_ZERO_ENTRY`, destroys the hardware object, restores the entry if firmware destroy fails, then removes the placeholder only if it still belongs to this destroy sequence. It drops the initial resource reference and waits for event references to complete.

Query and arm operations choose legacy or ISSI-specific command families. Query returns common WQ fields and marks `MLX5_SRQ_FLAG_ERR` when hardware state is not good/ready. XRQ query additionally extracts tag-matching append index and hardware/software phase counters.

Event table initialization clears and initializes the xarray with IRQ locking, registers the notifier, and cleanup unregisters it.

## State and persistence
Persistent hardware state includes SRQ/XRC SRQ/RMP/XRQ contexts and their PAS-backed WQs. In-memory state includes the SRQ xarray, notifier block, resource refcount/completion, resource kind, SRQN, UID, and event callback. `XA_ZERO_ENTRY` is used as temporary destroy state to handle hardware-number reuse races.

## Dependencies and integration points
This file depends on mlx5 firmware command layouts, mlx5 command execution helpers, `mlx5_umem_find_best_quantized_pgoff()`, `mlx5_ib_populate_pas()`, `ib_umem_num_dma_blocks()`, xarray IRQ locking, mlx5 notifier registration, and common resource refcounting from the QP resource code.

## Risks
- PAS sizing must match the selected page size and hardware context layout; mismatches trigger warnings or invalid command buffers.
- Legacy non-ISSI and ISSI command families have different context fields; changes must preserve both paths.
- Destroy races with SRQN reuse are subtle and rely on `XA_ZERO_ENTRY` compare/exchange sequencing.
- `get_wq()` and `get_srqc()` use flag assignment for signature state; changes should avoid accidentally clearing unrelated flags.
- Event callbacks run outside the xarray lock but rely on refcounts being held.
- Tag-matching XRQ fields are only valid for XRQ contexts and must not be assumed for basic SRQs.

## Test signals
- Creation tests should cover legacy SRQ, ISSI basic/RMP, XRC SRQ, and tag-matching XRQ with user and kernel memory.
- Page-size tests should validate quantized offsets, PAS counts, and failure on invalid page sizing.
- Query tests should cover good and error hardware states plus XRQ tag-matching counters.
- Destroy race tests should exercise SRQN reuse and firmware destroy failure retry behavior.
- Event tests should inject SRQ limit and catastrophic events, including events during destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/srq_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/std_types.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/std_types.c

## Purpose
`std_types.c` defines mlx5-specific uverbs methods attached to standard RDMA objects. It lets userspace query mlx5 PD numbers, port eswitch/multiport metadata, and a data-direct sysfs path through the uverbs named-ioctl infrastructure.

## Important APIs, types, and functions
- `UVERBS_HANDLER(MLX5_IB_METHOD_PD_QUERY)` copies the mlx5 PD number (`pdn`) for a PD object.
- `fill_vport_icm_addr()` queries eswitch vport context or uplink capabilities and fills software steering ICM RX/TX addresses when supported.
- `fill_vport_vhca_id()` fills vport VHCA ID via `mlx5_vport_get_vhca_id()`.
- `fill_multiport_info()` returns native-port VHCA ID for multiport devices.
- `fill_switchdev_info()` returns representor vport number, vport VHCA ID, eswitch owner VHCA ID, vport steering ICM addresses, and optional register C0 match metadata.
- `UVERBS_HANDLER(MLX5_IB_METHOD_QUERY_PORT)` validates a port and dispatches to switchdev or multiport metadata fill paths.
- `UVERBS_HANDLER(MLX5_IB_METHOD_GET_DATA_DIRECT_SYSFS_PATH)` returns the sysfs path for the current data-direct device under `data_direct_lock`.
- `DECLARE_UVERBS_NAMED_METHOD()`, `ADD_UVERBS_METHODS()`, and `mlx5_ib_std_types_defs[]` publish the methods for `UVERBS_OBJECT_DEVICE` and `UVERBS_OBJECT_PD`.

## Control flow
For PD query, uverbs resolves the PD object and the handler copies `mpd->pdn` to the mandatory output attribute. For port query, userspace passes a port number; the handler obtains the ucontext and mlx5 device, validates the port, and fills output only when eswitch offloads or multiport mode are active. Switchdev mode derives metadata from the representor, eswitch core device, vport, VHCA ID, optional software steering ICM addresses, and optional metadata register C0. Multiport mode queries the native port core device and reports its VHCA ID.

The data-direct path handler obtains the ucontext, locks `dev->data_direct_lock`, verifies a data-direct device exists, gets its kobject path, checks the output buffer length, copies the path, and unlocks/free resources on all exits.

## State and persistence
This file registers static uverbs method definitions and reads live device state. It does not own persistent mutable state. Output reflects current eswitch mode, representor association, native-port mapping, data-direct device pointer, and mlx5 capabilities.

## Dependencies and integration points
It integrates with RDMA uverbs named ioctl APIs, mlx5 user ioctl ABI headers, eswitch representors, vport VHCA ID APIs, software steering capability fields, data-direct device state, kobject sysfs paths, and mlx5 ucontext/device conversion helpers.

## Risks
- Output ABI is capability- and mode-dependent; userspace must key off flags, and the driver must set flags only for valid fields.
- Switchdev queries require a representor for the requested port; missing representors return `-EOPNOTSUPP`.
- ICM address reporting depends on software steering owner capability and nonzero addresses; incorrect gating can expose invalid addresses.
- Data-direct sysfs path uses a caller-provided output length and must return `-ENOSPC` rather than overrun.
- The data-direct pointer is protected by `data_direct_lock`; future accesses must preserve that locking.

## Test signals
- Uverbs tests should query PDNs and verify exact output length/type handling.
- Port-query tests should cover switchdev representor ports, uplink and non-uplink vports, multiport mode, invalid ports, absent representors, and non-offload/non-multiport mode.
- Capability tests should verify flags for VHCA ID, vport, eswitch owner, ICM RX/TX, and reg C0 are set only when data is valid.
- Data-direct tests should cover no device (`-ENODEV`), too-small output (`-ENOSPC`), normal path copy, and concurrent device removal under the lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/std_types.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/umr.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/umr.c

## Purpose
`umr.c` implements mlx5 UMR (User-Mode Memory Registration) support used to update memory-key attributes and translation tables through a dedicated internal REG_UMR QP. It handles UMR resource initialization, synchronous WQE posting, QP recovery, MR revocation, PD/access reregistration, PAS/XLT updates for regular, ODP, dmabuf, and data-direct memory, and safe dmabuf page-size transitions.

## Important APIs, types, and functions
- `mlx5r_umr_init()`, `mlx5r_umr_cleanup()`, `mlx5r_umr_resource_init()`, and `mlx5r_umr_resource_cleanup()` allocate the internal PD and lazily create/destroy the UMR CQ/QP.
- `mlx5r_umr_qp_rst2rts()` transitions the REG_UMR QP through INIT, RTR, and RTS.
- `mlx5r_umr_post_send()`, `mlx5r_umr_post_send_wait()`, `mlx5r_umr_done()`, and `mlx5r_umr_recover()` post UMR WQEs, wait for completions, limit concurrency with a semaphore, and recover from QP error state.
- Mask helpers `get_umr_enable_mr_mask()`, `get_umr_disable_mr_mask()`, `get_umr_update_translation_mask()`, `get_umr_update_access_mask()`, `get_umr_update_pd_mask()`, and `umr_check_mkey_mask()` build and validate mkey update masks.
- `mlx5r_umr_revoke_mr()` fences DMA by moving an MR to a free/disabled state under the internal PD.
- `mlx5r_umr_rereg_pd_access()` updates MR PD and access flags.
- `mlx5r_umr_alloc_xlt()`, `mlx5r_umr_free_xlt()`, `mlx5r_umr_create_xlt()`, and `mlx5r_umr_unmap_free_xlt()` allocate, DMA-map, and free temporary translation buffers with an emergency page fallback.
- `_mlx5r_umr_update_mr_pas()`, `mlx5r_umr_update_mr_pas_range()`, `mlx5r_umr_update_mr_pas()`, `mlx5r_umr_update_data_direct_ksm_pas_range()`, and `mlx5r_umr_update_data_direct_ksm_pas()` update regular MTT or data-direct KSM PAS entries.
- `mlx5r_umr_update_xlt()` updates ODP translation entries, including optional indirect mkeys.
- `mlx5r_umr_update_mr_page_shift()`, `_mlx5r_umr_zap_mkey()`, and `mlx5r_umr_dmabuf_update_pgsz()` safely change dmabuf MR page size while avoiding partially exposed mappings.

## Control flow
Device initialization allocates an internal PD and initializes `umrc.init_lock`. The actual UMR CQ/QP is created lazily by `mlx5r_umr_resource_init()`, which uses acquire/release ordering to avoid repeated initialization, allocates a CQ, creates a REG_UMR QP, transitions it to RTS, initializes the concurrency semaphore, lock, and active state, and publishes the QP.

UMR updates build a `mlx5r_umr_wqe`, validate masks against hardware capabilities, acquire one semaphore slot, wait if recovery is active, post the WQE under `umrc.lock`, and wait for completion. Successful completions return directly. Flush completions are retried while the QP recovers. Other failures trigger recovery: mark recovery state, post a barrier WQE, wait for its flushed completion, reset the QP, transition it back to RTS, and mark active or error.

PAS update flows allocate a temporary XLT buffer sized as large as practical, fill MTT or KSM entries from `ib_umem` DMA blocks, sync the buffer for DMA, post one or more UMR WQEs with translation offsets, and free/unmap the buffer. ODP updates populate XLT entries through `mlx5_odp_populate_xlt()`. Dmabuf page-size updates first zap enough entries to make the mkey non-present, switch to a large safe page size, load remaining entries at the new page size, update the mkey page-size field, then reload the initially zapped entries.

## State and persistence
The internal `dev->umrc` state persists the PD, CQ, QP, semaphore, lock, initialization lock, and UMR state (`UNINIT`, active, recover, error). MR objects persist updated access flags, page shifts, and hardware mkey state after successful UMR commands. Temporary XLT buffers are freed after each update; `xlt_emergency_page` is a global fallback protected by `xlt_emergency_page_mutex`.

## Dependencies and integration points
This file integrates with mlx5 send-WQE construction helpers (`mlx5r_begin_wqe()`, `mlx5r_finish_wqe()`, doorbells), RDMA core PD/CQ/QP APIs, MR/mkey structures, ODP and dmabuf umem iteration, DMA mapping APIs, PCI relaxed ordering, mlx5 capability bits, data-direct KSM keys, and memory registration/reregistration code that calls these UMR helpers.

## Risks
- UMR QP recovery is concurrency-sensitive; incorrect state transitions can leave waiters spinning, leak semaphore slots, or post to an errored QP.
- The emergency XLT page serializes fallback allocations; any missing unlock in free paths can deadlock later UMR updates.
- Mask validation must match hardware capabilities for page-size, atomic, relaxed-ordering, and indirect-mkey updates.
- PAS chunking and translation offsets must be aligned to `MLX5_UMR_FLEX_ALIGNMENT`; misalignment can update wrong translation entries.
- Dmabuf page-size update intentionally avoids partially valid mappings. Reordering the zap/page-size/load steps can expose stale DMA mappings.
- Some error paths in ODP update return before unmapping/freeing XLT if not handled carefully; this area deserves leak-focused review when changed.
- `mlx5r_umr_revoke_mr()` treats internal device error as success because DMA is already stopped by catastrophic failure; tests should account for that semantic.

## Test signals
- Initialization tests should call UMR resource init concurrently and verify only one CQ/QP is created and later cleaned up.
- UMR post tests should cover successful WQEs, mask rejection, internal-error device state, semaphore concurrency, flushed completions, recovery success, and recovery failure.
- MR tests should cover revoke, PD/access reregistration, relaxed ordering, atomic access, zero-length MRs, and page-size update.
- PAS update tests should cover regular umem, dmabuf zap, data-direct KSM with relaxed-ordering key selection, partial range updates, and allocation fallback to smaller chunks/emergency page.
- ODP tests should cover direct and indirect XLT updates, invalid non-ODP calls, and unsupported indirect mkey capability.
- Dmabuf page-size tests should verify no stale mappings are exposed across the five-step update and that `mr->page_shift` is restored on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/umr.c -->
