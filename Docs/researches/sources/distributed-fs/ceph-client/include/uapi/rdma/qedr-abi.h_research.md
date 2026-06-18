<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/qedr-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/qedr-abi.h

## Purpose
Defines QLogic qedr RoCE provider ABI version 8 for context flags, doorbell page mapping, DPM/EDPM capabilities, PD/CQ/QP/SRQ creation, and user doorbell records.

## Important APIs, Types, and Functions
Read coverage: 174 lines and 4307 bytes. Visible type families include enum qedr_alloc_ucontext_flags, struct qedr_alloc_ucontext_req, enum qedr_rdma_dpm_type, struct qedr_alloc_ucontext_resp, struct qedr_alloc_pd_ureq, struct qedr_alloc_pd_uresp, struct qedr_create_cq_ureq, struct qedr_create_cq_uresp, struct qedr_create_qp_ureq, struct qedr_create_qp_uresp, struct qedr_create_srq_ureq, struct qedr_create_srq_uresp, struct qedr_user_db_rec. Important macros/constants include __QEDR_USER_H__, QEDR_ABI_VERSION, QEDR_LDPM_MAX_SIZE, QEDR_EDPM_TRANS_SIZE, QEDR_EDPM_MAX_SIZE. Explicit ioctl-style command names include none.

## Control Flow
Userspace allocates a context with optional flags, receives DPM mode and doorbell information, allocates PDs, creates CQs/QPs/SRQs with queue and doorbell-record addresses, and uses response fields for low-latency DPM/EDPM datapaths.

## State and Persistence Behavior
State includes DB page mapping, DPI, DPM mode, PD/CQ/QP/SRQ IDs, queue addresses, user DB records, and inline data size limits tied to hardware firmware.

## Dependencies and Integration Points
It depends on Linux integer types and generic uverbs. It integrates with qedr, qede/qed hardware support, and rdma-core provider code. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
EDPM/LDPM size constants and doorbell mapping fields must match hardware. User DB records and queue addresses require validation, and ABI version 8 must remain compatible with deployed providers.

## Test Signals
Run qedr provider create/destroy tests, DPM/EDPM mode negotiation, max inline boundary cases, DB record validation, 32-bit layout, and failure unwinding for CQ/QP/SRQ creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/qedr-abi.h -->
