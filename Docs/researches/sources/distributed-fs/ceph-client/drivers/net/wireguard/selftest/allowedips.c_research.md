# sources/distributed-fs/ceph-client/drivers/net/wireguard/selftest/allowedips.c

Purpose: Provides DEBUG-only init-time tests for the WireGuard allowedips trie, including deterministic IPv4/IPv6 route cases, removal behavior, list iteration normalization, optional Graphviz dumping, and optional randomized comparison against a simple reference implementation.

Important APIs and functions: `wg_allowedips_selftest()` is the public DEBUG selftest. Helpers build fake peers, insert/remove/test IPv4 and IPv6 prefixes, print trie nodes, and optionally run `randomized_test()`. The "horrible" reference table implements ordered CIDR match with simple hlist nodes for cross-checking. Macros `insert`, `remove`, `test`, `test_negative`, and `test_boolean` structure the deterministic cases.

Control flow: The deterministic test initializes an allowedips trie, creates fake peers, inserts overlapping routes, validates longest-prefix lookups, removes by peer and exact prefix, checks invalid CIDR handling, stresses deep IPv6 free paths, validates peer allowedips list normalization, optionally runs random tests, then frees all structures. Random testing inserts many random/mutated IPv4 and IPv6 routes into both implementations, compares lookup results over many queries, then removes peers one by one.

State and persistence: Allocates temporary fake peers, allowedips trie nodes, and reference hlist nodes during module init in DEBUG builds. No state persists after the test, except printk output.

Dependencies and integration points: Included by the allowedips implementation in DEBUG builds and invoked from `main.c` before module registration. Depends on allowedips internal functions such as `lookup()` and `wg_allowedips_read_node()`, peer krefs/lists, mutex locking, siphash for graph colors, and random APIs.

Risks: It reaches into internal allowedips details and can become stale when trie internals change. Optional random mode is intentionally very expensive. Static `ip4()`/`ip6()` helpers reuse storage, so tests rely on immediate consumption. DEBUG-only coverage means production builds do not run it.

Test signals: DEBUG module load should print allowedips self-tests pass. Failures indicate lookup, prefix normalization, replacement, exact removal, invalid CIDR handling, peer removal, list iteration, or trie free-depth regressions.
