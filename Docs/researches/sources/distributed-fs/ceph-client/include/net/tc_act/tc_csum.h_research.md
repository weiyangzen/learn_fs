<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_csum.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_csum.h

Purpose: Defines TC checksum-update action state and a safe accessor for offload/driver code.

Important APIs/types/functions: `struct tcf_csum_params` stores `update_flags`, generic TC action, and RCU head. `struct tcf_csum` embeds `tc_action` and RCU params pointer. `tcf_csum_update_flags()` reads the configured checksum update flags under RCU.

Control flow: Classifier action execution reads `update_flags` and fixes selected L3/L4 checksums after packet edits. The accessor supports code that needs to inspect the action without duplicating RCU details.

State and persistence behavior: Params are per-action, RCU-replaced, and otherwise immutable for readers.

Dependencies/integration points: Depends on `linux/tc_act/tc_csum.h` UAPI flags and `act_api.h`; integrated with `tcf_csum_act`.

Risks: Incorrect flags can leave stale checksums after NAT/pedit/skbmod. Readers must not dereference params outside an RCU-safe region.

Test signals: Packet tests for IPv4, TCP, UDP, ICMP checksum repair after edits, action replace/delete races, and hardware offload flag export.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_csum.h -->
