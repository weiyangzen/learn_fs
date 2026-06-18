<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/vmw_pvrdma-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/vmw_pvrdma-abi.h

## Purpose
Defines VMware paravirtual RDMA userspace ABI: UAR doorbell bits, work request opcodes, completion status/opcode/flags, network types, object create responses, address vectors, SGEs, SQ/RQ WQE headers, masked atomics, and CQEs.

## Important APIs, Types, and Functions
Read coverage: 310 lines and 8011 bytes. Visible type families include enum pvrdma_wr_opcode, enum pvrdma_wc_status, enum pvrdma_wc_opcode, enum pvrdma_wc_flags, enum pvrdma_network_type, struct pvrdma_alloc_ucontext_resp, struct pvrdma_alloc_pd_resp, struct pvrdma_create_cq, struct pvrdma_create_cq_resp, struct pvrdma_resize_cq, struct pvrdma_create_srq, struct pvrdma_create_srq_resp, struct pvrdma_create_qp, struct pvrdma_create_qp_resp, struct pvrdma_ex_cmp_swap, struct pvrdma_ex_fetch_add, struct pvrdma_av, struct pvrdma_sge, struct pvrdma_rq_wqe_hdr, struct pvrdma_sq_wqe_hdr, struct pvrdma_cqe. Important macros/constants include __VMW_PVRDMA_ABI_H__, PVRDMA_UVERBS_ABI_VERSION, PVRDMA_UAR_HANDLE_MASK, PVRDMA_UAR_QP_OFFSET, PVRDMA_UAR_QP_SEND, PVRDMA_UAR_QP_RECV, PVRDMA_UAR_CQ_OFFSET, PVRDMA_UAR_CQ_ARM_SOL, PVRDMA_UAR_CQ_ARM, PVRDMA_UAR_CQ_POLL, PVRDMA_UAR_SRQ_OFFSET, PVRDMA_UAR_SRQ_RECV. Explicit ioctl-style command names include none.

## Control Flow
Guest userspace creates RDMA objects through uverbs, mmaps a paravirtual UAR, posts SQ/RQ WQEs using PVRDMA layouts, rings doorbells with send/recv/CQ/SRQ bits, and polls CQEs returned by the hypervisor-backed device.

## State and Persistence Behavior
State is shared between guest userspace, guest kernel driver, and virtual device: UAR doorbell pages, queue memory, object handles, AV data, WQE headers, completion entries, and ABI versioned capabilities.

## Dependencies and Integration Points
It depends on Linux integer types and generic uverbs. It integrates with VMware PVRDMA virtual hardware, hypervisor transport, and rdma-core provider support. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
This is a guest/hypervisor ABI; doorbell bit definitions, queue layouts, and completion codes must remain stable across host and guest versions. Masked atomic fields and network type enums need strict validation.

## Test Signals
Run PVRDMA guest/provider tests for object creation, SQ/RQ posting, CQ polling and arming, masked atomic operations, UAR doorbells, live migration/version compatibility, and malformed WQE rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/vmw_pvrdma-abi.h -->
