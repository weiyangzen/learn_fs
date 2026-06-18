# sources/distributed-fs/ceph-client/net/ipv6/fib6_notifier.c

## Purpose
Connects IPv6 FIB tables and policy rules to the generic FIB notifier framework. It provides IPv6-specific wrappers that tag events with `AF_INET6`, combines rule/table sequence counters, dumps current IPv6 routing state, and installs per-net notifier operations.

## Important APIs, Types, and Functions
Exports `call_fib6_notifier()` and `call_fib6_notifiers()`. Internal helpers include `fib6_seq_read()` and `fib6_dump()`. Per-net lifecycle is handled by `fib6_notifier_init()` and `fib6_notifier_exit()` using `fib6_notifier_ops_template`.

## Control Flow
Event wrappers set `info->family = AF_INET6` before calling generic notifier functions. The dump path emits IPv6 rules first via `fib6_rules_dump()` and then route tables via `fib6_tables_dump()`. Network namespace init registers a copy of the notifier ops template and stores it in `net->ipv6.notifier_ops`; exit unregisters it.

## State and Persistence
State is per-network-namespace `net->ipv6.notifier_ops`. Sequence values are derived from live FIB table and rule sequence counters. No persistent storage exists.

## Dependencies and Integration Points
Depends on generic `fib_notifier`, IPv6 FIB table/rule dump APIs, network namespace lifecycle, and module ownership. Consumers include switchdev/offload/listener components that need coherent IPv6 routing snapshots and change notifications.

## Risks and Test Signals
Risks include stale notifier ops during namespace teardown, incomplete dumps if rules or tables fail, and sequence mismatches causing missed resyncs. Test signals include namespace create/destroy, notifier registration, route/rule add/delete events, dump ordering, and simulated dump errors.
