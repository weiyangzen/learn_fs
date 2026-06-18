<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_connmark.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_connmark.h

Purpose: Defines TC connmark action state for copying conntrack marks into skb marks or otherwise applying connmark behavior.

Important APIs/types/functions: `struct tcf_connmark_parms` stores the net namespace, conntrack zone, action result, and RCU head. `struct tcf_connmark_info` embeds `tc_action` and RCU pointer to params. `to_connmark()` casts the action.

Control flow: TC action setup allocates params and installs them through RCU. Packet execution reads params, looks up conntrack state in the configured zone, and applies the configured action.

State and persistence behavior: Per-action params are immutable between replacements and freed after RCU grace period. Namespace and zone select conntrack lookup context.

Dependencies/integration points: Depends on `act_api.h` and conntrack runtime implementation. Called from `tc_wrapper.h` as `tcf_connmark_act` when built in.

Risks: Net namespace lifetime and RCU replacement must be correct. Missing conntrack state should not corrupt skb marks.

Test signals: TC connmark tests with multiple zones/namespaces, action replacement while traffic runs, no-conntrack fallback, and module unload checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_connmark.h -->
