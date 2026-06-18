<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_ct.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_ct.h

Purpose: Defines TC conntrack action state, optional NAT/label/flowtable configuration, and helpers for hardware/offload code to inspect conntrack action parameters.

Important APIs/types/functions: With conntrack enabled, `struct tcf_ct_params` stores helper, template conntrack, zone, action, mark/mask, label arrays/masks, NAT range, IPv4 range flag, label ownership, ct action, RCU head, TC flow table, and netfilter flowtable pointer. `struct tcf_ct` embeds `tc_action` and RCU params. Accessors return zone, ct action, flowtable, and helper with lockdep-protected dereference. `tcf_ct_flow_table_restore_skb()` restores skb conntrack state from a flowtable cookie when `CONFIG_NET_ACT_CT` is enabled.

Control flow: TC ct action setup creates params from netlink, packet execution commits, clears, NATs, or looks up conntrack state, and flowtable paths can restore skb nfct from a cookie before continuing.

State and persistence behavior: Per-action params are RCU-replaced. Netfilter conntrack objects are refcounted externally. Flowtable restore increments the conntrack ref before attaching it to the skb.

Dependencies/integration points: Depends on `act_api.h`, TC ct UAPI, netfilter conntrack, NAT, labels, and flowtable when enabled. Integrated with `tcf_ct_act`.

Risks: Refcounting nf_conn from cookies is critical. Label array sizing must match `NF_CT_LABELS_MAX_SIZE`. Disabled-config stubs return neutral values, so callers must tolerate no conntrack support.

Test signals: TC ct selftests for commit/zone/NAT/mark/label/helper, flowtable offload restore, disabled-config builds, action replacement under load, and conntrack ref leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_ct.h -->
