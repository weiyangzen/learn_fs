# sources/distributed-fs/ceph-client/net/bridge/netfilter/Makefile

## Purpose
Maps bridge netfilter Kconfig symbols to the object files that implement nftables bridge extensions, bridge conntrack, legacy ebtables core, tables, matches, targets, and watchers.

## Important APIs, Types, And Functions
Important object mappings include `nft_meta_bridge.o`, `nft_reject_bridge.o`, `nf_conntrack_bridge.o`, `ebtables.o`, `ebtable_broute.o`, `ebtable_filter.o`, `ebtable_nat.o`, and the `ebt_*` match/target/watcher modules.

## Control Flow
Kbuild includes each object when the matching `CONFIG_*` symbol is `y` or `m`. The ebtables legacy core is gated by `CONFIG_BRIDGE_NF_EBTABLES_LEGACY`, while individual extensions are gated separately.

## State And Persistence Behavior
No runtime state exists. The file contributes build graph state by selecting compiled objects and module names.

## Dependencies And Integration Points
Integrates directly with `Kconfig` symbols in the same directory and with source files in `net/bridge/netfilter`.

## Risks And Test Signals
Risks are missing object mappings for enabled symbols or stale mappings for removed files. Build tests with representative config combinations and module load tests for each object provide the main signals.
