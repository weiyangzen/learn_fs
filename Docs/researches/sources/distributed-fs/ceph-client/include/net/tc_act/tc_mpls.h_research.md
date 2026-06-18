<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_mpls.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_mpls.h

Purpose: Defines TC MPLS action parameters and RCU accessors for push/pop/modify MPLS operations.

Important APIs/types/functions: `struct tcf_mpls_params` stores MPLS action, label, generic TC action, traffic class, TTL, BOS, protocol, and RCU head. Sentinel constants mark unset TC, BOS, and label. `struct tcf_mpls` embeds `tc_action` and RCU params. Accessors return action, protocol, label, TC, BOS, and TTL under RCU.

Control flow: Packet execution reads params and edits MPLS headers according to configured action. Offload code can query exact params through accessors.

State and persistence behavior: Per-action params are immutable for RCU readers and replaced as a whole.

Dependencies/integration points: Depends on MPLS TC UAPI and `act_api.h`. Integrated with `tcf_mpls_act` and hardware offload translation.

Risks: Wrong sentinel handling can push invalid labels or unset fields. RCU readers must not retain param pointers after unlock.

Test signals: MPLS push/pop/modify tests, unset-field validation, offload dump, action replacement under traffic, and protocol endian checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_mpls.h -->
