# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_cls.c

## Purpose
`mvpp2_cls.c` implements PPv2 classifier, RSS, and ethtool receive-flow-steering helpers. It initializes classifier flow/lookup/C2 TCAM tables, maps parser result-info patterns to classifier flows, configures hash extraction fields for RSS, manages RSS contexts and indirection tables, and translates ethtool RXNFC rules into C2 TCAM entries for queue steering or drop actions.

## Important APIs, Types, and Functions
- `cls_flows[]` is the static flow catalog tying internal flow types, parser flow IDs, supported HEK fields, and parser result-info masks for IPv4/IPv6, TCP/UDP, fragmented/non-fragmented, tagged/untagged, and non-IP traffic.
- Register inspection APIs: `mvpp2_cls_flow_hits()`, `mvpp2_cls_lookup_hits()`, `mvpp2_cls_c2_hit_count()`, `mvpp2_cls_flow_read()`, `mvpp2_cls_lookup_read()`, and `mvpp2_cls_c2_read()`.
- Initialization APIs: `mvpp2_cls_init()`, `mvpp2_cls_port_config()`, `mvpp2_cls_oversize_rxq_set()`, and `mvpp22_port_rss_init()`.
- RSS APIs: `mvpp22_port_rss_enable()`, `mvpp22_port_rss_disable()`, `mvpp22_port_rss_ctx_create()`, `mvpp22_port_rss_ctx_delete()`, `mvpp22_port_rss_ctx_indir_set()`, `mvpp22_port_rss_ctx_indir_get()`, `mvpp2_ethtool_rxfh_set()`, and `mvpp2_ethtool_rxfh_get()`.
- RFS APIs: `mvpp2_ethtool_cls_rule_get()`, `mvpp2_ethtool_cls_rule_ins()`, and `mvpp2_ethtool_cls_rule_del()`.
- Internal helpers manipulate flow table fields, C2 entries, HEK field lists, ethtool flow type conversion, TCAM match construction, and hardware RSS table programming.

## Control Flow
`mvpp2_cls_init()` enables the classifier, clears the flow table, lookup table, and C2 TCAM, bypasses C2 FIFO stages, then initializes all parser/lookup/flow sequences from `cls_flows[]`. `mvpp2_cls_port_config()` configures a port's default lookup behavior and creates the per-port C2 RSS/default-RXQ entry. `mvpp22_port_rss_init()` allocates RSS context 0, fills its indirection table with `ethtool_rxfh_indir_default()`, writes hardware RSS table entries, and configures default hash keys for IP/TCP/UDP flows. Ettool hash-option changes are converted to HEK field masks, constrained by each flow's supported fields, and written into port-specific hash flow-table entries. Ettool classification insertion creates a kernel flow rule, validates the action, builds a 64-bit C2 TCAM key/mask from VLAN and L4 port match keys, programs the C2 entry, and then wires all compatible classifier flow-table entries to that lookup type.

## State and Persistence
Classifier hardware state lives in flow table registers, lookup table registers, C2 TCAM/action/attribute registers, RSS table registers, and hit counters. Software state lives in `priv->rss_tables[]`, `port->rss_ctx[]`, and `port->rfs_rules[]` / `port->n_rfs_rules`. RSS context deletion invalidates any RFS rules that reference the context before freeing the shared table. Ettool RFS rules are stored as copies of `struct ethtool_rxnfc`; temporary `flow_rule` objects are destroyed after programming hardware.

## Dependencies and Integration Points
This file depends on `mvpp2.h`, `mvpp2_cls.h`, `mvpp2_prs.h`, the parser API `mvpp2_prs_add_flow()`, the shared `mvpp2_read()` / `mvpp2_write()` MMIO helpers, Linux ethtool RX flow rule parsing, flow action validation, CPU topology (`num_possible_cpus()`, `cpu_online()`), and netdev warning paths. Debugfs consumes many read/hit helpers from this file. Main port setup and ethtool operations call the initialization and RSS/RFS APIs.

## Risks and Edge Cases
The static `cls_flows[]` table relies on entries with the same `flow_id` being contiguous for the iteration macros in the header. C2 matching is limited to a 64-bit TCAM key and currently builds matches only for VLAN ID/priority and L4 source/destination ports; unsupported dissector keys/actions return errors. Fragmented flows intentionally mask out L4 hashing to avoid packet reordering. RSS queue mapping divides by `port->nrxqs / num_possible_cpus()`, so configurations with fewer RX queues than possible CPUs require scrutiny. `mvpp22_port_rss_ctx_create()` allocates a table before checking `WARN_ON_ONCE(port->rss_ctx[port_ctx] >= 0)`, which can leak the newly allocated global RSS table on that error path. RFS insertion stores port bits with `mvpp2_cls_flow_port_add(&fe, 0xf)`, relying on the macro shape rather than passing `BIT(port->id)` as in other call sites.

## Test Signals
Key tests are classifier initialization without register faults, debugfs hit counters changing under traffic, ethtool `--config-nfc` insertion/deletion/get for queue and drop actions, invalid rule rejection for unsupported dissector/action combinations, RSS enable/disable, RSS context create/delete, indirection table set/get round trips, hash option set/get for IPv4/IPv6/TCP/UDP, and traffic distribution across RXQs matching the RSS table. Regression tests should include VLAN+L4 rules, fragmented traffic, offline CPUs, low RXQ counts, and deletion of an RSS context used by active RFS rules.
