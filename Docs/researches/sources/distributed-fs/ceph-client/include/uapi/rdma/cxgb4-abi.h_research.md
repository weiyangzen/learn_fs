<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/cxgb4-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/cxgb4-abi.h

## Purpose
Defines Chelsio T4/T5/T6 iWARP uverbs private ABI structures for context allocation, CQ/QP/SRQ creation, PD allocation, and status-page mappings.

## Important APIs, Types, and Functions
Read coverage: 115 lines and 3122 bytes. Visible type families include struct c4iw_create_cq, struct c4iw_create_cq_resp, struct c4iw_create_qp_resp, struct c4iw_create_srq_resp, struct c4iw_alloc_ucontext_resp, struct c4iw_alloc_pd_resp. Important macros/constants include CXGB4_ABI_USER_H, C4IW_UVERBS_ABI_VERSION. Explicit ioctl-style command names include none.

## Control Flow
Userspace allocates a context to receive status-page, page-size, and queue key information, creates CQs and QPs with user queue addresses, optionally creates SRQs, and rings Chelsio-specific doorbells through mapped resources.

## State and Persistence Behavior
Runtime state is in provider-owned queue memory and kernel RDMA objects: CQ/QP/SRQ IDs, queue sizes, doorbell/status-page keys, and write-combining mappings. The ABI structures move these identifiers across uverbs calls.

## Dependencies and Integration Points
It depends on Linux integer types and the generic uverbs command path. It integrates with the cxgb4 RDMA driver and rdma-core c4iw provider. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Queue address and size fields must be validated against user memory registration and hardware limits. ABI version 3 compatibility and status-page mmap key semantics are fragile across provider/kernel combinations.

## Test Signals
Exercise c4iw context allocation, PD/CQ/QP/SRQ create and teardown, queue overflow limits, 32-bit userspace layouts, and provider/kernel ABI-version negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/cxgb4-abi.h -->
