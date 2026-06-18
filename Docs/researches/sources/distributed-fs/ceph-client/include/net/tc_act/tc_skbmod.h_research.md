<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_skbmod.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_skbmod.h

Purpose: Defines TC skbmod action state for modifying Ethernet header fields.

Important APIs/types/functions: `struct tcf_skbmod_params` stores RCU head, 64-bit operation flags, action, destination MAC, ethertype, and source MAC. `struct tcf_skbmod` embeds `tc_action` and RCU params. `to_skbmod()` casts the action.

Control flow: Setup stores requested Ethernet modifications. Packet execution reads params, updates source/destination MAC and/or ethertype, and returns configured TC action.

State and persistence behavior: Params are per-action and RCU-replaced as a unit.

Dependencies/integration points: Depends on `act_api.h`, skbmod UAPI, and Ethernet header helpers; integrated with `tcf_skbmod_act`.

Risks: Flags must match initialized fields. Header edits require sufficient headroom/linear data and must not be applied to non-Ethernet packets.

Test signals: Source/destination MAC and ethertype modification tests, invalid packet type handling, action dump, hardware offload translation, and replacement while traffic runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_skbmod.h -->
