# sources/distributed-fs/ceph-client/net/ipv4/fib_notifier.c

## Purpose
`fib_notifier.c` adapts IPv4 FIB and rule state to the generic fib notifier framework. It tags events as `AF_INET`, maintains an IPv4 FIB sequence counter, combines route and rule sequence state for listeners, dumps current rules and routes to new notifier clients, and registers/unregisters per-net notifier operations.

## Important APIs, Types, and Functions
`call_fib4_notifier()` calls a single notifier block after setting `info->family = AF_INET`. `call_fib4_notifiers()` broadcasts to all registered listeners, asserts RTNL, sets the family, increments `net->ipv4.fib_seq`, and calls the generic notifier fanout.

`fib4_seq_read()` returns the IPv4 route sequence plus `fib4_rules_seq_read()` so listeners can detect changes in both routes and rules. `fib4_dump()` first dumps IPv4 rules through `fib4_rules_dump()` and then dumps routes through `fib_notify()`.

Per-namespace lifecycle is `fib4_notifier_init()` and `fib4_notifier_exit()`, which register and unregister an instance of `fib4_notifier_ops_template`.

## Control Flow
During FIB per-net initialization, `fib4_notifier_init()` resets the route sequence counter and registers notifier ops for the namespace. Route or nexthop changes later call `call_fib4_notifiers()`, which increments the sequence before dispatching. A consumer registering with the generic notifier framework can request a dump; `fib4_dump()` emits rules first and then route entries so consumers see policy and table contents.

## State and Persistence Behavior
State is limited to the runtime per-net `fib_seq` counter and `net->ipv4.notifier_ops` pointer. The counter uses `WRITE_ONCE()` paired with `READ_ONCE()` in `fib4_seq_read()` to avoid torn reads for lockless sequence checks. No durable state exists.

## Dependencies and Integration Points
The file depends on rtnetlink locking, generic `fib_notifier` infrastructure, IPv4 rule dump/sequence helpers, and route dump support from `fib_notify()`. It is used by FIB table/trie and nexthop state changes, including notifier calls from `fib_semantics.c` when nexthops become dead or alive.

## Risks and Edge Cases
Sequence accounting must include both route and rule changes; otherwise hardware offload or monitoring clients can miss updates. `call_fib4_notifiers()` requires RTNL, so callers that mutate FIB state outside RTNL would violate notifier ordering.

Dump ordering matters for clients reconstructing state. If route dump succeeds after rule dump failure or vice versa, callers need the returned error to avoid accepting partial state.

## Test Signals
Tests should register a fib notifier, add/delete IPv4 routes and rules, verify `AF_INET` family tagging, sequence changes for both route and rule mutations, dump ordering of rules before routes, and clean per-net unregister during namespace teardown.
