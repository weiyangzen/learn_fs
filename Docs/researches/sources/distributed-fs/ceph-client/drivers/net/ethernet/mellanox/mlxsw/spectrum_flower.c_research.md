# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_flower.c

## Purpose
This file translates Linux TC flower offload rules into mlxsw ACL rules. It validates supported match keys and action sequences, builds ACL key masks, allocates hardware side resources such as L4 port-range registers and policers, enforces ordering with matchall rules, and exposes replace/destroy/stats/template helpers used by the Spectrum flow-block code.

## Important APIs, Types, And Functions
Key entry points are `mlxsw_sp_flower_replace()`, `mlxsw_sp_flower_destroy()`, `mlxsw_sp_flower_stats()`, `mlxsw_sp_flower_tmplt_create()`, `mlxsw_sp_flower_tmplt_destroy()`, and `mlxsw_sp_flower_prio_get()`. Parsing is split across `mlxsw_sp_flower_parse()`, action parsing in `mlxsw_sp_flower_parse_actions()`, metadata ingress-ifindex handling, IPv4/IPv6 address key builders, exact L4 port matching, range matching via `mlxsw_sp_port_range_reg_get()`, TCP flags, and IP TTL/ECN/DSCP. Action helpers are delegated to ACL rule-info APIs for count, drop, trap, goto, redirect, mirror, VLAN, priority, mangle, police, and sample.

## Control Flow
Replace first checks priority compatibility with installed matchall filters, gets or creates the flower ACL ruleset for the chain, creates an ACL rule keyed by the TC cookie, parses matches and actions into `rulei`, commits the rule-info object, then installs the rule. Destroy looks up the same ruleset and cookie, deletes the rule from hardware, destroys it, and releases the ruleset. Stats query the installed ACL rule counters and feed `flow_stats_update()`. Template create parses a representative rule into element usage and keeps a ruleset reference; destroy drops the template-held reference plus the lookup reference.

## State And Persistence
The file owns no persistent on-disk state. It mutates in-memory ACL rulesets, rule blocker flags, TC stats objects, and per-rule resource references. Hardware-visible state includes ACL entries, counters, policer bindings, port-range key bits, mirroring/sampling actions, VLAN and mangle actions, and goto group identifiers. Error paths destroy partially created ACL rules and release rulesets, while port-range register lifetime is tied to ACL rule-info cleanup in lower layers.

## Dependencies And Integration Points
It depends on Linux flow dissector and TC action APIs, `netlink_ext_ack` diagnostics, mlxsw ACL/flex-key infrastructure, flow-block binding state, matchall priority queries, policer core, SPAN/sample actions, FID redirection helpers, and `spectrum_port_range.c`. It is part of the switchdev/TC offload path and integrates with devlink-visible ACL resources indirectly through the ACL subsystem.

## Risks And Edge Cases
Unsupported keys or actions must return clear extack errors because silent fallback would misrepresent hardware offload. Drop and redirect actions set ingress/egress binding blockers, so future mixed binding behavior depends on those flags. IPv6 mangle is explicitly rejected after action parsing if any mangle touched `rulei->ipv6_valid`. Port-range allocations can fail or exhaust limited hardware bits. Priority checks prevent flower and matchall from being ordered in a way hardware cannot reproduce. Policer validation only supports byte-rate single-rate policing, power-of-two burst after kernel rounding, drop exceed, and pipe/accept conform action.

## Test Signals
Useful tests include TC flower add/delete/stats for exact L2/L3/L4 keys, L4 range keys, ingress-ifindex metadata, drop/trap/goto/redirect/mirror/sample/police actions, invalid action combinations, mixed ingress/egress binding rejection, matchall priority conflicts, template create/destroy reference balance, and devlink resource pressure for port-range registers and policers.
