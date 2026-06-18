<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/siw-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/siw-abi.h

## Purpose
Defines the Software iWARP provider ABI: context/CQ/QP/SRQ/MR responses, opcodes, SGEs, send/receive queue elements, completion entries, CQ notification flags, and shared CQ control.

## Important APIs, Types, and Functions
Read coverage: 186 lines and 3426 bytes. Visible type families include struct siw_uresp_create_cq, struct siw_uresp_create_qp, struct siw_ureq_reg_mr, struct siw_uresp_reg_mr, struct siw_uresp_create_srq, struct siw_uresp_alloc_ctx, enum siw_opcode, struct siw_sge, enum siw_wqe_flags, struct siw_sqe, struct siw_rqe, enum siw_notify_flags, enum siw_wc_status, struct siw_cqe, struct ib_qp, struct siw_cq_ctrl. Important macros/constants include _SIW_USER_H, SIW_NODE_DESC_COMMON, SIW_ABI_VERSION, SIW_MAX_SGE, SIW_UOBJ_MAX_KEY, SIW_INVAL_UOBJ_KEY, SIW_MAX_INLINE. Explicit ioctl-style command names include none.

## Control Flow
Userspace allocates context and objects, registers memory, posts SQ/RQ elements with SIW opcodes and flags, uses inline data storage within SGE space, polls `siw_cqe` completions, and arms CQs through shared control fields.

## State and Persistence Behavior
State is in software iWARP queues and shared control memory: object keys, queue IDs, work queue entries, completion entries, notification flags, and memory registration keys.

## Dependencies and Integration Points
It depends on Linux integer types and integrates with the siw kernel provider, rdma-core, and TCP/iWARP software datapath. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Inline data depends on `SIW_MAX_SGE >= 2`; shared CQ arming requires memory ordering; opcode/status values must match userspace provider expectations; and software validation must reject malformed WQEs.

## Test Signals
Run siw loopback RDMA tests, MR registration, all send/RDMA/atomic opcode paths, inline send limits, CQ notification/arming, error completions, and invalid WQE fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/siw-abi.h -->
