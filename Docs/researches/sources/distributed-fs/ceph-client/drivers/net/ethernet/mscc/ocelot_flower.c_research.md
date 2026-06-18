# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_flower.c

## Purpose
Translates tc flower rules into Ocelot VCAP and optional PSFP hardware filters. It owns chain-number mapping, goto-topology validation, action/key parsing, dummy chain-anchor rules, and flower replace/destroy/stats operations.

## Important APIs/types/functions
Exports `ocelot_cls_flower_replace`, `ocelot_cls_flower_destroy`, and `ocelot_cls_flower_stats`. Chain helpers map chain IDs to IS1, IS2, ES0, and PSFP. `ocelot_flower_parse_action` handles drop, accept, trap, police, redirect, mirror, VLAN pop/mangle/push, priority, goto, and gate. `ocelot_flower_parse_key` handles VLAN, MAC, IPv4, L4 ports, and ES0 ingress-device metadata.

## Control flow, state, persistence
Replace rejects non-zero chains without an existing goto anchor, reuses shared ingress cookies across ports, creates and parses a new filter, patches ES0 VLAN delta actions after key parsing, then inserts dummy, PSFP, or VCAP rules. Destroy removes a port from shared ingress filters or deletes the rule. State lives in allocated `ocelot_vcap_filter` objects, VCAP block rule lists, dummy rule list, and hardware VCAP entries.

## Dependencies and integration
Depends on tc flower/flow action APIs, `ocelot_vcap`, policing validation, and optional PSFP ops. Called from `ocelot_net.c` tc setup.

## Risks and test signals
Risks are chain UAPI regressions, invalid action ordering around GOTO, unsupported key combinations, and PSFP hook absence. Test valid/invalid chains, shared filters, VLAN rewrite, police indexes, mirror/redirect with `skip_sw`, PSFP, and stats.
