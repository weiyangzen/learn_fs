<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/efa-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/efa-abi.h

## Purpose
Defines the Amazon Elastic Fabric Adapter userspace ABI, including context, PD, CQ, QP, AH, extended query-device, and provider ioctl definitions for memory-region query methods.

## Important APIs, Types, and Functions
Read coverage: 166 lines and 3747 bytes. Visible type families include struct efa_ibv_alloc_ucontext_cmd, enum efa_ibv_user_cmds_supp_udata, struct efa_ibv_alloc_ucontext_resp, struct efa_ibv_alloc_pd_resp, struct efa_ibv_create_cq, struct efa_ibv_create_cq_resp, struct efa_ibv_create_qp, struct efa_ibv_create_qp_resp, struct efa_ibv_create_ah_resp, struct efa_ibv_ex_query_device_resp, enum efa_query_mr_attrs, enum efa_mr_methods. Important macros/constants include EFA_ABI_USER_H, EFA_UVERBS_ABI_VERSION. Explicit ioctl-style command names include none.

## Control Flow
The provider allocates a context, discovers supported user-data commands and device capabilities, creates PD/CQ/QP/AH objects with EFA private payloads, and uses ioctl methods to query MR attributes. CQ/QP responses return mmap keys, queue identifiers, sub-CQ layout, and device capabilities needed for direct datapath use.

## State and Persistence Behavior
State is in EFA hardware queues, mmaped rings, queue IDs, inline and RDMA read capability masks, AH numbers, and provider-supported command bitmaps. Reserved fields preserve forward extension space.

## Dependencies and Integration Points
It depends on Linux integer types and `ib_user_ioctl_cmds.h`. It integrates with the EFA kernel provider, rdma-core EFA provider, userspace queue mmap, and cloud fabric capabilities. Direct includes are #include <linux/types.h>, #include <rdma/ib_user_ioctl_cmds.h>.

## Risks and Edge Cases
The file documents strict 8-byte alignment and reserved-field naming rules; breaking them would break ABI. Capability masks must gate optional command payloads, and mmap keys/sub-CQ counts must be checked for overflow or mismatched provider assumptions.

## Test Signals
Run EFA rdma-core tests for context/CQ/QP/AH creation, query-device capability parsing, MR query ioctl methods, reserved-field zero validation, 32-bit ABI layout, and unsupported-command negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/efa-abi.h -->
