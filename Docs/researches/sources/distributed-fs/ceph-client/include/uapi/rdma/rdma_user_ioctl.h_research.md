<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_ioctl.h

## Purpose
Collects ioctl command numbers for legacy RDMA character devices, including user MAD agent registration and HFI1 context/TID/control operations.

## Important APIs, Types, and Functions
Read coverage: 85 lines and 3751 bytes. Visible type families include none. Important macros/constants include RDMA_USER_IOCTL_H, IB_IOCTL_MAGIC, IB_USER_MAD_REGISTER_AGENT, IB_USER_MAD_UNREGISTER_AGENT, IB_USER_MAD_ENABLE_PKEY, IB_USER_MAD_REGISTER_AGENT2, HFI1_IOCTL_ASSIGN_CTXT, HFI1_IOCTL_CTXT_INFO, HFI1_IOCTL_USER_INFO, HFI1_IOCTL_TID_UPDATE, HFI1_IOCTL_TID_FREE, HFI1_IOCTL_CREDIT_UPD, HFI1_IOCTL_RECV_CTRL, HFI1_IOCTL_POLL_TYPE, HFI1_IOCTL_ACK_EVENT, HFI1_IOCTL_SET_PKEY, HFI1_IOCTL_CTXT_RESET, HFI1_IOCTL_TID_INVAL_READ, HFI1_IOCTL_GET_VERS. Explicit ioctl-style command names include RDMA_USER_IOCTL_H, IB_IOCTL_MAGIC, IB_USER_MAD_REGISTER_AGENT, IB_USER_MAD_UNREGISTER_AGENT, IB_USER_MAD_ENABLE_PKEY, IB_USER_MAD_REGISTER_AGENT2, HFI1_IOCTL_ASSIGN_CTXT, HFI1_IOCTL_CTXT_INFO, HFI1_IOCTL_USER_INFO, HFI1_IOCTL_TID_UPDATE, HFI1_IOCTL_TID_FREE, HFI1_IOCTL_CREDIT_UPD, HFI1_IOCTL_RECV_CTRL, HFI1_IOCTL_POLL_TYPE, HFI1_IOCTL_ACK_EVENT, HFI1_IOCTL_SET_PKEY, HFI1_IOCTL_CTXT_RESET, HFI1_IOCTL_TID_INVAL_READ, HFI1_IOCTL_GET_VERS.

## Control Flow
UMAD users issue register/unregister/P_Key ioctls with `ib_user_mad` payloads. HFI1 users issue context assignment, info queries, TID update/free/invalidation, credit update, receive control, poll type, event ack, P_Key setting, context reset, and version queries.

## State and Persistence Behavior
The ioctls operate on per-file kernel state: MAD agent registrations and HFI1 user contexts, TID mappings, event bits, receive modes, poll policy, and P_Key settings.

## Dependencies and Integration Points
It depends on `rdma_user_ioctl_cmds.h`, `ib_user_mad.h`, and HFI1 ioctl payload headers. It integrates with ib_umad and hfi1 character-device implementations. Direct includes are #include <rdma/ib_user_mad.h>, #include <rdma/hfi/hfi1_ioctl.h>, #include <rdma/rdma_user_ioctl_cmds.h>.

## Risks and Edge Cases
Ioctl numbers are stable ABI and share the RDMA magic. Payload structure compatibility, HFI1 high command numbers, and operation ordering such as enabling P_Key headers before use are key hazards.

## Test Signals
Run umad and hfi1 ioctl suites, verify command numbers with ioctl decoders, test invalid payload sizes, 32-bit compat, HFI1 context lifecycle, and MAD register/unregister error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_ioctl.h -->
