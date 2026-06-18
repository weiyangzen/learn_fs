<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_cfm_netlink.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_cfm_netlink.c

Purpose: parses bridge CFM nested netlink attributes into CFM core operations and serializes CFM configuration/status back into bridge netlink responses.

Important APIs, types, and functions: policy arrays define accepted attributes for MEP create/delete/config, CC config, peer MEP add/remove, RDI, and CCM TX. `br_cfm_parse` is the main setter entry point. Parser helpers call into `br_cfm_mep_create`, `br_cfm_mep_delete`, `br_cfm_mep_config_set`, `br_cfm_cc_config_set`, `br_cfm_cc_peer_mep_add`, `br_cfm_cc_peer_mep_remove`, `br_cfm_cc_rdi_set`, and `br_cfm_cc_ccm_tx`. Dump functions are `br_cfm_config_fill_info` and `br_cfm_status_fill_info`.

Control flow: `br_cfm_parse` adjusts a port-scoped call to the owning bridge, parses the top-level nested CFM attribute, then applies any present nested operations in a fixed order: create, delete, MEP config, CC config, peer add, peer remove, RDI, and CCM TX. Each parser verifies required attributes, copies binary MAC/MAID fields, decodes scalar values, and delegates semantic validation to `br_cfm.c`. Config dumping iterates all MEPs and peers, emitting nested create/config/CC/RDI/TX/peer-info records. Status dumping emits MEP and peer status, and on GETLINK clears edge-triggered "seen" flags after reporting them.

State and persistence: this file owns no long-lived state. It mutates CFM state indirectly through core APIs and clears selected status flags during status reporting when `getlink` is true.

Dependencies and integration points: depends on rtnetlink/genetlink attribute helpers, CFM UAPI attribute IDs and constants, bridge private structures, CFM core implementation, and RCU iteration over MEP/peer lists while filling skb responses.

Risks: required-attribute checks are strict, so userspace must send complete nested records. Applying multiple operations from one netlink message can partially mutate state before a later operation fails. Status dumping has read-and-clear semantics for several flags, which can surprise pollers. `-EMSGSIZE` paths must cancel only the active nest.

Test signals: rtnetlink tests for every CFM operation, missing attribute rejection, policy max enforcement for mdlevel and MEP ID, nested dump layout compatibility with `ip link`/bridge tools, status read-and-clear behavior, and multi-operation error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_cfm_netlink.c -->
