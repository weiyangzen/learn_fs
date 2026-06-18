# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-ethtool.c

## Purpose
`dpaa2-ethtool.c` implements ethtool operations for DPAA2 DPNI netdevs. It reports driver/firmware identity, link settings, pause settings, hardware and software statistics, RX flow classification rules, RX hash fields, timestamping capabilities, RX copybreak tunable, DPIO interrupt coalescing, channel counts, and MAC-level standardized statistics.

## Important APIs and functions
`dpaa2_ethtool_ops` is the exported operation table consumed by `dpaa2_eth_netdev_init()`. Link and pause operations route to phylink when a DPMAC PHY/backplane is connected, otherwise they use cached DPNI link state and `dpni_set_link_cfg()`. Stats are assembled by `dpaa2_eth_get_ethtool_stats()` from DPNI statistic pages, per-CPU extra stats, channel stats, instantaneous FQ counts, buffer-pool counts, and optional DPMAC stats.

Classifier support is built around ethtool RX NFC. `dpaa2_eth_prep_eth_rule()`, `dpaa2_eth_prep_uip_rule()`, `dpaa2_eth_prep_l4_rule()`, `dpaa2_eth_prep_ext_rule()`, and `dpaa2_eth_prep_mac_ext_rule()` translate ethtool flow specs into the driver classifier key/mask layout. `dpaa2_eth_do_cls_rule()` DMA maps the key/mask pair and calls `dpni_add_fs_entry()` or `dpni_remove_fs_entry()`. `dpaa2_eth_update_cls_rule()` updates the software `priv->cls_rules` table and handles the no-mask firmware case by constraining all active rules to the same extracted field set. `dpaa2_eth_get_rxnfc()` and `dpaa2_eth_set_rxnfc()` expose rule listing, lookup, insertion, and deletion. `dpaa2_eth_get_rxfh_fields()` and `dpaa2_eth_set_rxfh_fields()` expose the single global RX hash key field mask.

## Control flow
Etntool calls enter through the kernel ethtool core. Read operations aggregate existing driver or MC state and return immediately. Mutating operations call into DPNI or phylink: pause settings check firmware support and reject autoneg for fixed/non-phylink DPNIs; RX hash changes rebuild the DPNI hash key through core helpers; RX class rule insertion removes any existing rule at that location, programs hardware, and then records the new software copy; coalescing updates every channel's affine DPIO and rolls back previous channels if a later update fails.

## State and persistence behavior
The file persists ethtool-installed classifier rules in `priv->cls_rules` for the life of the netdev. RX hash fields are cached in `priv->rx_hash_fields`. RX copybreak writes `priv->rx_copybreak`. Pause settings update `priv->link_state.options` after a successful DPNI configuration. Coalescing writes DPIO service state. None of this survives driver unload or DPNI reset except whatever the MC firmware naturally retains during the object lifetime.

## Dependencies and integration points
This file depends on `dpaa2-eth.h` helpers for classification key offsets/sizes, feature gates, pause helpers, queue counts, and MAC locking helpers. It calls DPNI MC APIs, DPAA2 IO query/coalescing APIs, phylink ethtool helpers, MAC stats functions from `dpaa2-mac.c`, and the global PTP state exported by `dpaa2-ptp.c`.

## Risks and edge cases
The stats array must stay synchronized with DPNI statistic pages; missing firmware pages are treated as zero only for `-EINVAL`. Classifier rules are limited: unsupported flow types, IPv4 TOS in several paths, VLAN ethertype extension, multiple field sets on no-mask firmware, out-of-range ring cookies, and unsupported hash bits are rejected. `array_index_nospec()` is correctly used for rule lookup. Coalescing rollback only restores channels already modified. MAC statistics are protected by `mac_lock`, but DPNI and per-CPU stats are read locklessly and can be approximate.

## Test signals
Use `ethtool -i`, `ethtool -S`, `ethtool -k`, `ethtool -c/-C`, `ethtool -l`, `ethtool -a/-A`, `ethtool -n/-N`, and timestamp capability queries. Validate rule insertion/deletion for ETHER, IP_USER, TCP/UDP/SCTP IPv4, VLAN extension, discard, and queue steering. Test no-mask firmware behavior by adding two rules with different field sets and expecting rejection. Verify MAC stats appear only when a MAC endpoint is connected.
