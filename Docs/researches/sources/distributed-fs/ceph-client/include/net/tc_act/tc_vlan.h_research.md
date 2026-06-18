<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_vlan.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_vlan.h

Purpose: Defines TC VLAN action state and RCU accessors for VLAN push, pop, modify, and Ethernet push parameters.

Important APIs/types/functions: `struct tcf_vlan_params` stores generic action, VLAN action, push destination/source MACs, push VID, protocol, priority, priority-present flag, and RCU head. `struct tcf_vlan` embeds `tc_action` and RCU params. Accessors return VLAN action, push VID/protocol/priority, and copy push Ethernet addresses under RCU.

Control flow: Packet action reads params and manipulates VLAN tags or pushed Ethernet metadata. Offload code uses accessors to translate VLAN edits into hardware rules.

State and persistence behavior: Params are per-action and RCU-replaced. Accessors do not retain pointers after RCU unlock.

Dependencies/integration points: Depends on `act_api.h` and VLAN TC UAPI; integrated with `tcf_vlan_act`.

Risks: VLAN protocol endian handling, priority-present semantics, and MAC copy ordering must match action configuration. Missing linear header data can break packet edits.

Test signals: VLAN push/pop/modify tests for 802.1Q and 802.1ad, priority-present cases, push Ethernet address copying, hardware offload translation, and action replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_vlan.h -->
