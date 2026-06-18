# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-switch-flower.c

## Purpose
`dpaa2-switch-flower.c` translates Linux traffic-control flower and matchall offloads for DPAA2 switch ports into DPSW ACL entries or reflection/mirroring rules. It supports drop, trap, redirect, and mirred actions with a constrained set of match keys.

## Important APIs and functions
The public entry points are `dpaa2_switch_cls_flower_replace()`, `dpaa2_switch_cls_flower_destroy()`, `dpaa2_switch_cls_matchall_replace()`, `dpaa2_switch_cls_matchall_destroy()`, `dpaa2_switch_block_offload_mirror()`, `dpaa2_switch_block_unoffload_mirror()`, and `dpaa2_switch_acl_entry_add()`. `dpaa2_switch_flower_parse_key()` maps supported flower keys into `struct dpsw_acl_key`: basic EtherType/IP protocol, Ethernet addresses, VLAN ID/TPID/PCP/DEI, IPv4 addresses, L4 ports, and DSCP. `dpaa2_switch_tc_parse_action_acl()` maps trap/redirect/drop actions to DPSW ACL results. Mirror parsing is split into `dpaa2_switch_flower_parse_mirror_key()` for per-VLAN flower mirroring and matchall mirroring for ingress-all reflection.

ACL table helpers maintain `block->acl_entries` ordered by tc priority and translate list order into DPSW precedence values. Adding an entry may reprogram higher-priority existing entries to make space. Removing an entry deletes it from hardware/list and shifts preceding entries down. Mirror helpers maintain `block->mirror_entries`, configure a single switch-wide reflection destination, and add/remove `dpsw_if_add_reflection()` filters on every port represented by the filter block.

## Control flow
For flower replace, the code first enforces exactly one action. Drop/trap/redirect allocate an ACL entry, parse keys, parse action, assign priority/cookie, insert into the ordered ACL table, and program hardware. Mirred validates the destination as another DPAA2 switch port, enforces the single mirror-port hardware limitation, parses a VLAN-only key, rejects duplicate VLAN mirror filters, allocates a mirror entry, and applies reflection to all ports in the block. Destroy finds the cookie in ACL entries first, then mirror entries, and removes the matching hardware state.

For matchall replace, the same single-action rule applies. Drop/trap/redirect create an ACL entry with no key match, while mirred creates an ingress-all reflection entry. Block offload/unoffload mirror functions apply or remove all existing mirror rules when a port joins or leaves a shared block, with unwind logic on partial failure.

## State and persistence behavior
Software state is held in per-filter-block linked lists: `acl_entries`, `mirror_entries`, rule counts, cookies, priorities, and mirror configs. Hardware state is programmed into DPSW ACL tables and reflection filters. It is runtime-only and must be rebuilt by tc if the driver or switch object is reset. `ethsw->mirror_port` tracks the one active mirror destination or `num_ifs` as the sentinel for none.

## Dependencies and integration points
The file depends on Linux flow offload dissector/action APIs and `dpaa2-switch.h` data structures/helpers. It calls DPSW MC APIs `dpsw_acl_prepare_entry_cfg()`, `dpsw_acl_add_entry()`, `dpsw_acl_remove_entry()`, `dpsw_set_reflection_if()`, `dpsw_if_add_reflection()`, and `dpsw_if_remove_reflection()`. It uses netlink extack messages to explain unsupported keys/actions.

## Risks and edge cases
Supported keys are intentionally narrow. IPv6 address key is listed as accepted in the top-level mask but is not populated into the DPSW ACL key, which should be reviewed because it could silently ignore IPv6 address matches. TTL and ECN matching are rejected; DSCP is supported by shifting TOS. Mirroring supports only one destination port and only VLAN ID or matchall filters. Per-VLAN mirroring requires the VLAN to already be installed on every block port. ACL precedence reprogramming can leave hardware partially changed if a mid-sequence MC call fails; callers receive an error, but list/hardware reconciliation should be tested. `list_add(&entry->list, pos->prev)` depends on list-head semantics and priority iteration correctness.

## Test signals
Exercise tc flower drop/trap/redirect with Ethernet, VLAN, IPv4, ports, and DSCP keys; unsupported TTL/ECN/extra keys; duplicate cookies and priority ordering; ACL table full behavior; destroy by cookie; matchall drop/trap/redirect; mirred VLAN and matchall reflection to a DPAA2 switch port; rejection of non-switch destinations, multiple mirror destinations, duplicate mirror filters, and VLAN-not-installed cases. Validate hardware counters and packet behavior after partial add/remove failures and when ports join/leave shared blocks.
