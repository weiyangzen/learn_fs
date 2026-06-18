# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebtable_nat.c

## Purpose
Defines the legacy ebtables `nat` table for bridge destination/source MAC translation at prerouting, local output, and postrouting.

## Important APIs, Types, And Functions
Important declarations are `NAT_VALID_HOOKS`, `initial_chains`, `initial_table`, `frame_nat`, `ebt_ops_nat`, `frame_nat_table_init`, and module/pernet lifecycle functions.

## Control Flow
The module registers a lazy ebtables table template. On namespace table initialization, default ACCEPT `PREROUTING`, `OUTPUT`, and `POSTROUTING` chains are installed with `ebt_do_table` hooks at bridge NAT priorities: destination NAT for bridged prerouting/local-output and source NAT for postrouting.

## State And Persistence Behavior
Runtime table contents are per-net ebtables state managed by the core. The file contributes static initial chains and hook registration lifetime only.

## Dependencies And Integration Points
Depends on ebtables core, bridge netfilter hook ordering, and target modules such as `ebt_dnat`, `ebt_snat`, `ebt_redirect`, and `ebt_arpreply`.

## Risks And Test Signals
Risks include hook priority/order regressions relative to bridge forwarding, invalid teardown ordering, and interaction with MAC rewrite targets. Tests should cover each hook, MAC DNAT/SNAT/redirect/arpreply behavior, table replacement, module autoload, and netns teardown.
