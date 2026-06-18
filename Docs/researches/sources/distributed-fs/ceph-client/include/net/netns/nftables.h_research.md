# sources/distributed-fs/ceph-client/include/net/netns/nftables.h

Purpose: Defines the compact nftables fields embedded directly in `struct net`.

Important APIs/types/functions: `struct netns_nftables` stores `base_seq`, used to sequence base-chain hook updates, and `gencursor`, the two-generation cursor used by nftables generation masks.

Control flow: nftables control-plane commits flip or consult `gencursor` to stage current/next generation activity; hook update code uses `base_seq` to coordinate base-chain changes.

State and persistence: Runtime per-net scalar state. Full ruleset lists and transactions live in generic pernet data described in `nf_tables.h`.

Dependencies/integration: Depends on nftables core, generic pernet handling, netfilter hooks, and netlink control paths.

Risks/test signals: Test generation cursor flipping during atomic commit/abort, base sequence updates during base-chain replacement, per-net initialization defaults, and namespace isolation.
