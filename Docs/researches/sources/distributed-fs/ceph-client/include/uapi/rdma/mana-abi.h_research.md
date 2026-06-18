<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mana-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/mana-abi.h

## Purpose
Defines the Microsoft Azure MANA RDMA userspace ABI for CQ, QP, RC QP, WQ, RSS QP creation, RX hash flags, and RSS indirection responses.

## Important APIs, Types, and Functions
Read coverage: 90 lines and 1616 bytes. Visible type families include enum mana_ib_create_cq_flags, struct mana_ib_create_cq, struct mana_ib_create_cq_resp, struct mana_ib_create_qp, struct mana_ib_create_qp_resp, struct mana_ib_create_rc_qp, struct mana_ib_create_rc_qp_resp, struct mana_ib_create_wq, enum mana_ib_rx_hash_function_flags, struct mana_ib_create_qp_rss, struct rss_resp_entry, struct mana_ib_create_qp_rss_resp. Important macros/constants include MANA_ABI_USER_H, MANA_IB_UVERBS_ABI_VERSION. Explicit ioctl-style command names include none.

## Control Flow
Userspace creates CQs and queue pairs, optionally uses RC-specific creation payloads or RSS QP creation with hash-function flags and indirection table information, and receives queue IDs plus mmap handles needed for datapath rings.

## State and Persistence Behavior
Kernel/hardware state includes MANA queue IDs, CQ/QP memory mappings, WQ descriptors, RSS configuration, and response-table entries used by accelerated networking.

## Dependencies and Integration Points
It depends on Linux integer types and integrates with the MANA RDMA kernel driver, Azure netvsc/MANA hardware, and rdma-core provider support. Direct includes are #include <linux/types.h>, #include <rdma/ib_user_ioctl_verbs.h>.

## Risks and Edge Cases
RSS hash-function flags and response-entry counts must be validated. Azure device capabilities can vary, so provider code must not assume RC/RSS support without kernel response bits.

## Test Signals
Test CQ/QP/RC-QP/WQ/RSS creation, invalid RSS table sizes, hash flag negotiation, mmap handle use, provider/kernel ABI version, and teardown under active traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mana-abi.h -->
