<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_skbedit.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_skbedit.h

Purpose: Defines TC skbedit action state and helpers for editing skb metadata such as mark, priority, packet type, queue mapping, and DS field inheritance.

Important APIs/types/functions: `struct tcf_skbedit_params` stores action, flags, priority, mark/mask, queue mapping, mapping modulo, packet type, and RCU head. `struct tcf_skbedit` embeds `tc_action` and RCU params. Helpers test exact configured flags and read mark, ptype, priority, queue mapping; ingress helper distinguishes RX and TX queue mapping based on `tcfa_flags`.

Control flow: Action execution reads params and updates skb metadata fields. Offload/classifier code uses helpers to detect which metadata edit is represented.

State and persistence behavior: Params are per-action and RCU-replaced. Helpers take short RCU read sections for param fields.

Dependencies/integration points: Depends on `act_api.h` and skbedit UAPI. Queue mapping integrates with device TX/RX queue selection.

Risks: `is_tcf_skbedit_with_flag()` checks equality, not bit inclusion, so combined flags need careful handling. Ingress/egress queue mapping depends on `tcfa_flags`.

Test signals: Mark/mask, priority, ptype, TX/RX queue mapping, inherit DS field tests, combined flag behavior, and action replacement under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_skbedit.h -->
