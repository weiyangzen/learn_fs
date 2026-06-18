# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_flow_rule.c

## Purpose

`gve_flow_rule.c` bridges Linux ethtool RXNFC flow specs and the device adminq flow-rule format. It supports querying individual rules, listing rule ids, adding rules, and deleting rules when the device reports flow-rule capacity.

## Important APIs, types, and functions

- `gve_fill_ethtool_flow_spec`: converts queried adminq rules into `struct ethtool_rx_flow_spec` for TCP/UDP/SCTP/AH/ESP over IPv4 and IPv6.
- `gve_generate_flow_rule`: validates an ethtool flow spec, checks the target queue, maps Linux flow type to GVE flow type, and fills adminq key/mask/action fields.
- `gve_get_flow_rule_entry`: refreshes the rules cache when unsynced or outside cached location range, then converts the requested cached rule.
- `gve_get_flow_rule_ids`: pages through adminq rule-id queries and fills ethtool rule locations.
- `gve_add_flow_rule`, `gve_del_flow_rule`: allocate/submit add requests or delete by location.

## Control flow and state

Flow-rule support is conditional on `priv->max_flow_rules`. The cache state lives in `priv->flow_rules_cache`: arrays for queried rules and ids, counters populated by adminq, and a `rules_cache_synced` flag. Querying a rule can trigger an adminq refresh starting at the requested location. Listing ids iterates until the device returns an empty page. Adding validates queue action and flow type before submitting; deleting forwards the requested location.

## Dependencies and integration points

The file depends on `gve_adminq.h` for device rule structs and query/config commands, ethtool flow constants, IPv6 address layouts, and `priv->rx_cfg.num_queues`. `gve_ethtool.c` calls these helpers from `get_rxnfc` and `set_rxnfc`. `gve_main.c` allocates/frees the caches and resets flow rules when device resources are torn down or ntuple is disabled.

## Risks and test signals

Risks include key/mask field mixups between AH/ESP and TCP/UDP structs, stale cache contents after add/delete, invalid ring-cookie handling, and pagination errors if more ids exist than `cmd->rule_cnt`. A notable review signal is the AH/ESP IPv6 generation path, which assigns `rule->key.spi` twice and does not visibly set `rule->mask.spi`. Tests should cover every supported flow type, masks, invalid queue ids, unsupported discard/RSS flags, cache refresh after mutation, and list truncation returning `-EMSGSIZE`.
