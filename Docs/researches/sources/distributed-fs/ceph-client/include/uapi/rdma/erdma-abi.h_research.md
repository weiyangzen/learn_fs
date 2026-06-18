<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/erdma-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/erdma-abi.h

## Purpose
Defines Alibaba ERDMA userspace ABI version 1 for CQ creation, QP creation, and context allocation private response data.

## Important APIs, Types, and Functions
Read coverage: 49 lines and 811 bytes. Visible type families include struct erdma_ureq_create_cq, struct erdma_uresp_create_cq, struct erdma_ureq_create_qp, struct erdma_uresp_create_qp, struct erdma_uresp_alloc_ctx. Important macros/constants include __ERDMA_USER_H__, ERDMA_ABI_VERSION. Explicit ioctl-style command names include none.

## Control Flow
Provider code creates CQs and QPs with user doorbell and queue buffer addresses, receives object IDs and mmap hints, and allocates context to discover device IDs and page-size information.

## State and Persistence Behavior
State lives in ERDMA kernel objects and mapped queues: CQ/QP IDs, queue depths, user DB records, mmap offsets, and context identity values.

## Dependencies and Integration Points
It depends only on Linux integer types and integrates with the ERDMA kernel RDMA provider plus rdma-core userspace provider code. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
The ABI is compact, so any field insertion would be breaking. User-provided queue addresses and mmap offsets require strict validation and alignment checks.

## Test Signals
Cover ABI-version negotiation, create/destroy CQ and QP with boundary queue sizes, context allocation responses, 32-bit layout checks, and invalid user address rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/erdma-abi.h -->
