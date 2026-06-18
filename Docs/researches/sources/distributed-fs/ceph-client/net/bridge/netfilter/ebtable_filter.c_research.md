# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebtable_filter.c

## Purpose
Defines the legacy ebtables `filter` table for bridge local input, forwarding, and local output filtering.

## Important APIs, Types, And Functions
Important declarations are `FILTER_VALID_HOOKS`, `initial_chains`, `initial_table`, `frame_filter`, `ebt_ops_filter`, `frame_filter_table_init`, and pernet init/exit wrappers.

## Control Flow
Module init registers pernet operations and a lazy template. Table initialization creates default ACCEPT `INPUT`, `FORWARD`, and `OUTPUT` base chains and registers `ebt_do_table` hooks at the bridge filter priorities. Pre-exit unregisters hooks before final table cleanup.

## State And Persistence Behavior
Per-network-namespace ebtables table state is held by ebtables core and can be replaced by userspace. This file itself only owns the static initial table template and registration lifetime.

## Dependencies And Integration Points
Depends on ebtables core registration, bridge netfilter hook constants, xtables modules referenced by loaded rules, and pernet namespace lifecycle.

## Risks And Test Signals
Risks include hook priority regressions, lazy template registration failures, and namespace cleanup leaks. Tests should cover default ACCEPT behavior, rules at all three hooks, table replacement, module autoload, and netns create/destroy with active rules.
