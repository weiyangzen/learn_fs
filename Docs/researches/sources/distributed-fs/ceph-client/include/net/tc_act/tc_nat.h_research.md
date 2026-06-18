<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_nat.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_nat.h

Purpose: Defines TC NAT action state for simple IPv4 address translation.

Important APIs/types/functions: `struct tcf_nat_parms` stores action, old address, new address, mask, flags, and RCU head. `struct tcf_nat` embeds `tc_action` and RCU params. `to_tcf_nat()` casts the action.

Control flow: Configuration installs address/mask/flag params. Packet execution matches and rewrites IPv4 addresses and fixes dependent checksums, returning the configured TC action.

State and persistence behavior: Params are per-action and RCU-replaced.

Dependencies/integration points: Depends on `linux/types.h`, `act_api.h`, and packet checksum helpers in implementation; integrated with `tcf_nat_act`.

Risks: Endian and mask handling errors can rewrite wrong addresses. NAT edits must be paired with checksum updates.

Test signals: Source and destination NAT packet tests, partial mask cases, checksum validation, replace/delete under traffic, and invalid address netlink validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_nat.h -->
