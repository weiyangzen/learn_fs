# sources/distributed-fs/ceph-client/net/core/fib_notifier.c

Purpose: Per-network-namespace FIB notifier infrastructure. It lets route-family providers register dump and sequence callbacks, and lets consumers register notifier blocks after receiving a consistent dump of current FIB state.

Important APIs, types, and functions: `struct fib_notifier_net` stores the per-net list of `fib_notifier_ops` and an atomic notifier chain. Exports include `call_fib_notifier()`, `call_fib_notifiers()`, `register_fib_notifier()`, `unregister_fib_notifier()`, `fib_notifier_ops_register()`, and `fib_notifier_ops_unregister()`. Internal helpers `fib_seq_sum()`, `fib_net_dump()`, and `fib_dump_is_consistent()` implement dump-then-subscribe consistency.

Control flow and state: Route-family code registers a copied `fib_notifier_ops` template per net namespace. Consumers call `register_fib_notifier()`, which reads the aggregate sequence sum, asks all registered ops to dump current state into the notifier block, registers the block, then rechecks the sequence. If state changed during the dump, it unregisters, calls an optional cleanup callback, and retries up to `FIB_DUMP_MAX_RETRIES`. Events later use `atomic_notifier_call_chain()` and convert notifier return values to errno.

Dependencies and integration points: The file depends on pernet generic storage, RCU-protected ops lists, module owner references around family callbacks, atomic notifier chains, netlink extack reporting, and route-family implementations such as IPv4/IPv6 FIB rules or route tables.

Risks: Consistency relies on each provider's sequence counter changing for every state transition and dump output matching that sequence. `try_module_get()` failures skip a provider, so unload races need careful owner management. Registration can fail with `-EBUSY` under continuous FIB churn. Per-net exit warns if providers remain registered.

Test signals: Register providers for multiple families, register consumers during concurrent route changes, verify cleanup callback on retry, trigger max retry failure under artificial churn, unregister notifier blocks, unregister ops under RCU, and check pernet cleanup warnings remain silent.
