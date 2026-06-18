<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/hns-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/hns-abi.h

## Purpose
Defines HiSilicon HNS RoCE provider private uverbs ABI for CQ/SRQ/QP creation, context allocation, congestion flags, QP response capabilities, PD allocation, and AH creation.

## Important APIs, Types, and Functions
Read coverage: 156 lines and 3973 bytes. Visible type families include struct hns_roce_ib_create_cq, enum hns_roce_cq_cap_flags, struct hns_roce_ib_create_cq_resp, enum hns_roce_srq_cap_flags, enum hns_roce_srq_cap_flags_resp, struct hns_roce_ib_create_srq, struct hns_roce_ib_create_srq_resp, enum hns_roce_congest_type_flags, enum hns_roce_create_qp_comp_mask, struct hns_roce_ib_create_qp, enum hns_roce_qp_cap_flags, struct hns_roce_ib_create_qp_resp, struct hns_roce_ib_modify_qp_resp, struct hns_roce_ib_alloc_ucontext_resp, struct hns_roce_ib_alloc_ucontext, struct hns_roce_ib_alloc_pd_resp, struct hns_roce_ib_create_ah_resp. Important macros/constants include HNS_ABI_USER_H. Explicit ioctl-style command names include none.

## Control Flow
The provider allocates context and PD resources, creates CQs/SRQs/QPs with queue buffer addresses and capability masks, receives object numbers and hardware capabilities, and uses AH response data for address-handle programming.

## State and Persistence Behavior
State is in HNS RoCE kernel objects and user queues: queue IDs, db addresses, congestion algorithm flags, SRQ/QP capabilities, context config, and hardware version/capability values.

## Dependencies and Integration Points
It depends on Linux integer types and generic uverbs. It integrates with the hns_roce driver and rdma-core provider. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Compatibility hazards include capability mask interpretation, congestion type flags, queue address validation, and reserved response fields for older provider versions.

## Test Signals
Cover context/PD/CQ/SRQ/QP/AH creation with min/max queue sizes, congestion-capability negotiation, reserved-bit rejection, 32-bit layout, and provider/kernel mismatch handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/hns-abi.h -->
