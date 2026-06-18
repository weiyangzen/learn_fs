# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebtable_broute.c

## Purpose
Defines the legacy ebtables `broute` table, which runs before normal bridge input processing to decide whether a frame should be bridged or routed.

## Important APIs, Types, And Functions
Important items are `initial_chain`, `initial_table`, `broute_table`, `ebt_broute`, `ebt_ops_broute`, `broute_table_init`, per-net exit hooks, and module init/exit.

## Control Flow
The module registers a template table and per-net operations. When a namespace needs the table, `ebt_register_table` installs a single `BROUTING` chain at `NF_BR_PRE_ROUTING` with first priority. Runtime calls `ebt_do_table`; a legacy ebtables `DROP` verdict is remapped to `NF_ACCEPT` plus `BR_INPUT_SKB_CB(skb)->br_netfilter_broute = 1` to signal routing, and packet type is restored when bridge input previously marked a frame as host for the bridge MAC.

## State And Persistence Behavior
State is per-network-namespace ebtables table registration and mutable table contents managed by ebtables core. The runtime side effect is the skb bridge control block broute flag.

## Dependencies And Integration Points
Depends on bridge input code, `br_private.h`, ebtables core APIs, netfilter bridge hooks, pernet operations, and the legacy broute userspace table semantics.

## Risks And Test Signals
Risks include the inverted DROP-means-route compatibility rule, packet-type restoration, forwarding-state gating, and namespace teardown ordering. Tests should cover ACCEPT bridge path, DROP route path, non-forwarding ports, host packet-type restoration, table replacement, and per-net module teardown.
