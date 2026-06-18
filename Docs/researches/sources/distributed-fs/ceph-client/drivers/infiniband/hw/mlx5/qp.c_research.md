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
