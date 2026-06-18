<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/irdma-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/irdma-abi.h

## Purpose
Defines Intel iRDMA/iWARP/RoCE provider ABI version 5, retaining compatibility with legacy i40iw generation-1 userspace while covering context, PD, CQ, SRQ, QP, MR registration, QP modification, and AH responses.

## Important APIs, Types, and Functions
Read coverage: 134 lines and 2681 bytes. Visible type families include enum irdma_memreg_type, struct irdma_alloc_ucontext_req, struct irdma_alloc_ucontext_resp, struct irdma_alloc_pd_resp, struct irdma_resize_cq_req, struct irdma_create_cq_req, struct irdma_create_srq_req, struct irdma_create_srq_resp, struct irdma_create_qp_req, struct irdma_mem_reg_req, struct irdma_modify_qp_req, struct irdma_create_cq_resp, struct irdma_create_qp_resp, struct irdma_modify_qp_resp, struct irdma_create_ah_resp. Important macros/constants include IRDMA_ABI_H, IRDMA_ABI_VER. Explicit ioctl-style command names include none.

## Control Flow
The provider allocates a context with feature flags and hardware limits, creates PD/CQ/SRQ/QP resources, registers memory using typed registration requests, modifies QP state, and receives response IDs and mmap keys for queues and doorbells.

## State and Persistence Behavior
State is in iRDMA hardware/kernel objects: queue IDs, push-page and doorbell mappings, WQE allocation state, memory-registration type, QP modification responses, and AH IDs.

## Dependencies and Integration Points
It depends on Linux integer types and generic uverbs. It integrates with Intel irdma kernel provider, legacy i40iw compatibility, and rdma-core. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Legacy ABI version compatibility is explicit and high risk. Memory-registration type interpretation, push-mode support, queue mmap keys, and reserved fields must match both old and new providers.

## Test Signals
Run iWARP and RoCE provider tests, legacy i40iw userspace compatibility checks, MR registration variants, QP modify paths, queue-size limits, 32-bit layouts, and unsupported feature fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/irdma-abi.h -->
