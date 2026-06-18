# sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_flower.c

## Purpose

This file implements tc-flower classifier offload for the SJA1105 driver. It supports a narrow key/action subset that maps onto hardware L2 policing and virtual-link machinery: broadcast policers, PCP-based traffic-class policers, virtual-link redirect/trap/drop, and gate actions.

## Important APIs, Types, and Data

- `sja1105_rule_find()` searches `priv->flow_block.rules` by flower cookie and is shared with deletion/statistics paths.
- `sja1105_find_free_l2_policer()` scans `priv->flow_block.l2_policer_used` for a dynamic policer slot.
- `sja1105_setup_bcast_policer()` and `sja1105_setup_tc_policer()` allocate/update shared L2 policer entries and reload best-effort policing.
- `sja1105_flower_parse_key()` validates supported dissector keys and maps them into `struct sja1105_key` variants.
- `sja1105_policer_validate()` constrains police actions to the hardware-supported form.
- `sja1105_cls_flower_add()`, `sja1105_cls_flower_del()`, and `sja1105_cls_flower_stats()` are DSA classifier callbacks.
- `sja1105_flower_setup()` and `sja1105_flower_teardown()` initialize and free the rule list.

## Control Flow

Add starts by parsing keys. Unsupported dissector keys, control flags, source MAC matching, masked destination MAC matching, partial VID/PCP masks, protocol matching, or unknown key combinations are rejected with extack messages. Supported keys become broadcast, PCP traffic class, VLAN-aware virtual link, or VLAN-unaware virtual link keys.

The action loop handles `FLOW_ACTION_POLICE`, `TRAP`, `REDIRECT`, `DROP`, and `GATE`. Police actions validate conform/exceed behavior and unsupported rate fields, then install either a broadcast or TC policer. Redirect/trap/drop/gate delegate to `sja1105_vl_redirect()` or `sja1105_vl_gate()`. If a gate was requested, a redirect/trap must also be present so `DESTPORTS` is populated before scheduling is initialized. Virtual-link actions finish by reloading static config for `SJA1105_VIRTUAL_LINKS`.

Delete looks up the cookie. VL rules are delegated to `sja1105_vl_delete()`. Policer rules restore affected lookup entries to their per-port default `sharindx`, clear the port bit from the rule, free the dynamic policer if no ports remain, and reload best-effort policing. Stats are only meaningful for VL rules and use `sja1105_vl_stats()`.

## State and Persistence Behavior

Rules are stored in `priv->flow_block.rules`, and allocated dynamic policers are tracked in `priv->flow_block.l2_policer_used`. The actual policer configuration is written into `priv->static_config.tables[BLK_IDX_L2_POLICING].entries`; virtual-link helpers similarly mutate static tables. Because changes are committed through `sja1105_static_config_reload()`, they persist across the reset that reload itself performs, and the software copies remain authoritative for later reloads.

## Dependencies and Integration Points

The file depends on Linux flow dissector/action APIs, DSA classifier hooks, `sja1105_vl.*` helpers, `sja1105_static_config_reload()`, and the L2 policing table layout initialized in `sja1105_main.c`. It uses extack for user-facing rejection reasons and is wired into `.cls_flower_add`, `.cls_flower_del`, and `.cls_flower_stats`.

## Risks and Edge Cases

- Only exact supported key combinations work; broad flower rules can fail with `-EOPNOTSUPP`.
- Policer allocation is finite. The first `ds->num_ports` policers are reserved for matchall/per-port defaults, leaving the rest for flower.
- Updating a rule that spans multiple ports shares one policer index across those ports. Delete must carefully restore only the removed port and free the policer only when `port_mask` becomes zero.
- `sja1105_static_config_reload()` resets the switch, so active traffic and PTP/TAS state depend on reload preservation logic.
- Gate action without redirect/trap is explicitly rejected because scheduling needs a destination port mask.
- The code assumes static policing entries have their default `sharindx == port` when checking whether a port already has a broadcast or TC policer.

## Test Signals

Useful tests include tc flower police rules for broadcast DMAC and VLAN PCP, rejection of unsupported masks/actions with extack text, redirect/trap/drop virtual-link offloads with traffic verification, gate plus redirect/trap scheduling behavior, deleting shared policers from one of multiple ports, and `tc -s filter show` stats for VL rules. Static config reload messages after policer/VL changes are expected.
