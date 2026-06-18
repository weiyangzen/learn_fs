<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_ioctl_verbs.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_ioctl_verbs.h

## Purpose
Defines data structures and enums for the generic ioctl uverbs verb payloads, including access flags, QP/WQ/SRQ types, flow-action ESP structures, counter flags, driver IDs, and GID table entries.

## Important APIs, Types, and Functions
Read coverage: 276 lines and 8006 bytes. Visible type families include enum ib_uverbs_core_support, enum ib_uverbs_access_flags, enum ib_uverbs_srq_type, enum ib_uverbs_wq_type, enum ib_uverbs_wq_flags, enum ib_uverbs_qp_type, enum ib_uverbs_qp_create_flags, enum ib_uverbs_query_port_cap_flags, enum ib_uverbs_query_port_flags, enum ib_uverbs_flow_action_esp_keymat, enum ib_uverbs_flow_action_esp_keymat_aes_gcm_iv_algo, struct ib_uverbs_flow_action_esp_keymat_aes_gcm, enum ib_uverbs_flow_action_esp_replay, struct ib_uverbs_flow_action_esp_replay_bmp, enum ib_uverbs_flow_action_esp_flags, struct ib_uverbs_flow_action_esp_encap, struct ib_uverbs_flow_action_esp, enum ib_uverbs_read_counters_flags, enum ib_uverbs_advise_mr_advice, enum ib_uverbs_advise_mr_flag, struct ib_uverbs_query_port_resp_ex, struct ib_uverbs_query_port_resp, struct ib_uverbs_qp_cap, enum rdma_driver_id, enum ib_uverbs_gid_type, struct ib_uverbs_gid_entry. Important macros/constants include IB_USER_IOCTL_VERBS_H, RDMA_UAPI_PTR, IB_UVERBS_ACCESS_OPTIONAL_FIRST, IB_UVERBS_ACCESS_OPTIONAL_LAST. Explicit ioctl-style command names include IB_USER_IOCTL_VERBS_H.

## Control Flow
These structures are nested as attributes in the ioctl command namespace. Userspace supplies access flags, object types, flow-action ESP key/replay/encap payloads, MR advice, and receives query-port or GID-entry responses through the uverbs ioctl dispatcher.

## State and Persistence Behavior
State lives in RDMA objects created or modified by ioctl verbs: memory access permissions, QP/WQ/SRQ types, flow action security parameters, counter read behavior, and GID table snapshots.

## Dependencies and Integration Points
It depends on Linux integer types and `rdma_user_ioctl_cmds.h`. It integrates with the generic uverbs ioctl layer, rdma-core, IPsec/ESP offload flow actions, and driver ID reporting. Direct includes are #include <linux/types.h>, #include <rdma/ib_user_verbs.h>.

## Risks and Edge Cases
Access flags share optional ranges and must not collide with provider bits. ESP structures carry security-sensitive keys, IV algorithms, replay state, and encap data, so length and padding validation matters. Driver IDs are externally visible and must remain stable.

## Test Signals
Validate ioctl attributes for QP/WQ/SRQ creation, MR access/advice flags, ESP flow action create/modify/destroy, query-port extended responses, GID table queries, and bad optional flag handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/ib_user_ioctl_verbs.h -->
