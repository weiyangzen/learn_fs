# sources/distributed-fs/ceph-client/net/bridge/netfilter/Kconfig

## Purpose
Defines build-time configuration for bridge netfilter support: nftables bridge family expressions, native bridge connection tracking, legacy ebtables core, legacy ebtables tables, matches, targets, and logging watchers.

## Important APIs, Types, And Functions
This Kconfig file declares `NF_TABLES_BRIDGE`, `NFT_BRIDGE_META`, `NFT_BRIDGE_REJECT`, `NF_CONNTRACK_BRIDGE`, `BRIDGE_NF_EBTABLES_LEGACY`, `BRIDGE_NF_EBTABLES`, table symbols such as `BRIDGE_EBT_BROUTE`, match symbols such as `BRIDGE_EBT_IP6`, and target/watcher symbols such as `BRIDGE_EBT_DNAT`, `BRIDGE_EBT_LOG`, and `BRIDGE_EBT_NFLOG`.

## Control Flow
Menu visibility is dependency-driven. nft bridge options appear only under `NF_TABLES_BRIDGE`; ebtables tables/matches/targets/watchers appear under `BRIDGE_NF_EBTABLES`; legacy table modules depend on `BRIDGE_NF_EBTABLES_LEGACY`; IPv6 and reject options add their protocol-specific dependencies.

## State And Persistence Behavior
The file has no runtime state. Its selected tristate values persist only through kernel configuration artifacts such as `.config` and determine whether modules are built-in, modules, or absent.

## Dependencies And Integration Points
Coordinates with `net/bridge/netfilter/Makefile`, bridge core, `NETFILTER`, `NETFILTER_XTABLES`, `NETFILTER_XTABLES_LEGACY`, `NF_TABLES`, `NF_CONNTRACK`, `NFT_REJECT`, `NF_REJECT_IPV4`, `NF_REJECT_IPV6`, `IPV6`, and `INET`.

## Risks And Test Signals
Risks are mismatched dependencies that build modules without required protocol helpers, unintentional default enablement, or hiding legacy support needed by old userspace. Signals are `oldconfig`/`allyesconfig`/`allmodconfig` coverage, module link success for each selected symbol, and runtime smoke tests loading nft bridge, conntrack bridge, and ebtables legacy modules.
