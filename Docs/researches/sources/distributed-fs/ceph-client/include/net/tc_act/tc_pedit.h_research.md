<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_pedit.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_pedit.h

Purpose: Defines TC packet edit action state and accessors for key-based header modifications.

Important APIs/types/functions: `struct tcf_pedit_key_ex` stores extended header type and command. `struct tcf_pedit_parms` stores key array, optional extended key array, action, max offset hint, key count, flags, and RCU head. `struct tcf_pedit` embeds `tc_action` and RCU params. Helpers identify pedit actions and read key count, header type, command, mask, value, and offset under RCU.

Control flow: Netlink setup builds key arrays. Packet execution iterates keys, computes offsets, applies masks/values, and returns configured action. Offload code uses accessors to translate edits.

State and persistence behavior: Params are per-action and RCU-replaced. Key arrays must remain valid until RCU free.

Dependencies/integration points: Depends on TC pedit UAPI, `act_api.h`, and packet header parsing code.

Risks: Index bounds are caller responsibility for accessors. Offset calculation and mask/value endian handling can corrupt headers. Missing extended keys default to network header type and max command sentinel.

Test signals: Pedit tests for IPv4, IPv6, TCP/UDP fields, extended command modes, malformed key counts, offload translation, and concurrent replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_pedit.h -->
