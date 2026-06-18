<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_mad.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_mad.h

## Purpose
Defines the userspace Management Datagram ABI for `/dev/infiniband/umad*`: MAD packet headers, registration requests, method masks, ABI version, and registration flags.

## Important APIs, Types, and Functions
Read coverage: 234 lines and 8530 bytes. Visible type families include struct ib_user_mad_hdr_old, struct ib_user_mad_hdr, struct ib_user_mad, typedef packed_ulong, struct ib_user_mad_reg_req, struct ib_user_mad_reg_req2. Important macros/constants include IB_USER_MAD_H, IB_USER_MAD_ABI_VERSION, IB_USER_MAD_LONGS_PER_METHOD_MASK, IB_USER_MAD_REG_FLAGS_CAP. Explicit ioctl-style command names include none.

## Control Flow
Applications register an agent on QP0 or QP1, optionally enable P_Key-index-aware packet headers, send and receive `ib_user_mad` packets with address/GRH metadata, and unregister agents when done. `REGISTER_AGENT2` supports extended flags such as userspace RMPP handling.

## State and Persistence Behavior
Kernel state includes registered MAD agents, assigned agent IDs, method masks, QP bindings, RMPP policy, and file-handle mode for old versus P_Key-aware headers. Packet headers carry per-message routing and retry/timeout state.

## Dependencies and Integration Points
It depends on Linux integer types and `rdma_user_ioctl.h`. It integrates with the ib_umad driver, subnet administration, performance management, vendor MAD agents, and userspace SM/SA tools. Direct includes are #include <linux/types.h>, #include <rdma/rdma_user_ioctl.h>.

## Risks and Edge Cases
The file calls out historical 32/64-bit and big-endian `method_mask` ambiguity, so compat handling is critical. Header mode must be enabled before other actions, QPN must be restricted, and RMPP/user flags must be validated.

## Test Signals
Run umad registration/send/receive tests, P_Key enablement ordering, REGISTER_AGENT and REGISTER_AGENT2 compatibility, 32-bit big-endian method-mask layout checks, timeout/retry behavior, and invalid QPN/method mask rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_mad.h -->
