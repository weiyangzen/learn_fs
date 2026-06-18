<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ocrdma-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/ocrdma-abi.h

## Purpose
Defines Emulex/Broadcom OCRDMA userspace ABI for context, PD, CQ, QP, and SRQ allocation, including BE RoCE compatibility versioning and fixed page-array limits.

## Important APIs, Types, and Functions
Read coverage: 152 lines and 4116 bytes. Visible type families include struct ocrdma_alloc_ucontext_resp, struct ocrdma_alloc_pd_ureq, struct ocrdma_alloc_pd_uresp, struct ocrdma_create_cq_ureq, struct ocrdma_create_cq_uresp, struct ocrdma_create_qp_ureq, struct ocrdma_create_qp_uresp, struct ocrdma_create_srq_uresp. Important macros/constants include OCRDMA_ABI_USER_H, OCRDMA_ABI_VERSION, OCRDMA_BE_ROCE_ABI_VERSION, MAX_CQ_PAGES, MAX_QP_PAGES, MAX_UD_AV_PAGES. Explicit ioctl-style command names include none.

## Control Flow
Provider code allocates context/PD, creates CQs and QPs by passing page arrays and queue attributes, optionally creates SRQs, and receives IDs, DB page indices, and queue metadata for hardware programming.

## State and Persistence Behavior
State is in OCRDMA objects and user queue pages: CQ/QP/SRQ IDs, page-list mappings, doorbell resources, firmware/hardware capability values, and compatibility version fields.

## Dependencies and Integration Points
It depends on Linux integer types and generic uverbs. It integrates with the ocrdma kernel provider and rdma-core provider for older Emulex/Broadcom RoCE adapters. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Fixed `MAX_CQ_PAGES`, `MAX_QP_PAGES`, and `MAX_UD_AV_PAGES` arrays require strict count validation. Version compatibility with BE RoCE and page-list pinning are high-risk areas.

## Test Signals
Cover context/PD/CQ/QP/SRQ create/destroy, page count boundary checks, BE RoCE ABI version negotiation, invalid page arrays, 32-bit layout, and teardown after partial failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ocrdma-abi.h -->
