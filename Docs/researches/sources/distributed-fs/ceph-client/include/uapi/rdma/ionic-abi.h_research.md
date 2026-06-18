<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ionic-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/ionic-abi.h

## Purpose
Defines AMD/Pensando Ionic RDMA provider ABI version 1 for context, queue descriptors, AH/CQ/QP/SRQ requests and responses, combined-memory-bar options, and expanded doorbell sizing.

## Important APIs, Types, and Functions
Read coverage: 115 lines and 1774 bytes. Visible type families include struct ionic_ctx_req, struct ionic_ctx_resp, struct ionic_qdesc, struct ionic_ah_resp, struct ionic_cq_req, struct ionic_cq_resp, struct ionic_qp_req, struct ionic_qp_resp, struct ionic_srq_req, struct ionic_srq_resp. Important macros/constants include IONIC_ABI_H, IONIC_ABI_VERSION, IONIC_EXPDB_64, IONIC_EXPDB_128, IONIC_EXPDB_256, IONIC_EXPDB_512, IONIC_EXPDB_SQ, IONIC_EXPDB_RQ, IONIC_CMB_ENABLE, IONIC_CMB_REQUIRE, IONIC_CMB_EXPDB, IONIC_CMB_WC, IONIC_CMB_UC. Explicit ioctl-style command names include none.

## Control Flow
Userspace requests a context with optional CMB and expanded doorbell preferences, receives device and doorbell capability data, creates AH/CQ/QP/SRQ resources with queue descriptors, and maps queue and doorbell resources for datapath use.

## State and Persistence Behavior
State includes provider context IDs, admin/user queue descriptors, CMB allocation policy, doorbell format capabilities, and object IDs for CQs, QPs, SRQs, and AHs.

## Dependencies and Integration Points
It depends on Linux integer types and generic uverbs. It integrates with the Ionic RDMA kernel driver and rdma-core provider. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
CMB requirement versus enablement flags must be negotiated carefully. Doorbell size and SQ/RQ flags affect mmap layout, and queue descriptor addresses/lengths must be validated.

## Test Signals
Cover context allocation with each CMB mode, expanded doorbell sizes, AH/CQ/QP/SRQ create/destroy, invalid queue descriptors, ABI version checks, and 32-bit layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ionic-abi.h -->
