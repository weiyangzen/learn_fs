# sources/distributed-fs/ceph-client/net/ipv4/fib_lookup.h

## Purpose
`fib_lookup.h` is the internal IPv4 FIB lookup contract shared by trie lookup, frontend, rules, and semantics code. It defines the route alias node stored under trie leaves, the route property table shape, and prototypes for creating, matching, serializing, notifying, and releasing shared `fib_info` objects.

## Important APIs, Types, and Functions
`struct fib_alias` represents one route alias for a prefix. It links through `fa_list`, points to shared `fa_info`, stores DSCP selector, route type, state flags, suffix length, table ID, default-route selection cache, offload flags, trap/offload-failure flags, and RCU head.

`fib_alias_accessed()` lazily sets `FA_S_ACCESSED` with `READ_ONCE()` and `WRITE_ONCE()` to avoid unnecessary cacheline writes on lookup. `fib_result_assign()` assigns a `struct fib_info` and first nexthop common pointer to a lookup result without refcount games because readers use RCU.

The header declares `fib_release_info()`, `fib_create_info()`, `fib_nh_match()`, `fib_metrics_match()`, `fib_dump_info()`, `rtmsg_fib()`, `fib_nlmsg_size()`, and the global `fib_props[]` table mapping route types to scope and error semantics.

## Control Flow
`fib_trie.c` allocates and orders `fib_alias` instances under trie leaves, calls `fib_create_info()` to deduplicate nexthop/metric state, and uses `rtmsg_fib()` plus notifier helpers to advertise route changes. Lookup paths return a `fib_result` by selecting a matching alias and assigning its shared `fib_info` through `fib_result_assign()`.

`fib_semantics.c` implements the declared functions and uses `fib_alias` metadata when dumping and notifying routes. `fib_frontend.c` and `fib_rules.c` depend on the result contract for table lookup, source validation, and rule action callbacks.

## State and Persistence Behavior
`fib_alias` is runtime route-table state owned by trie leaves and freed with RCU. It does not own the nexthop payload; `fa_info` points to refcounted shared `fib_info`. Offload flags reflect runtime driver or switchdev state and are included in route notifications/dumps.

## Dependencies and Integration Points
The header depends on generic list/RCU types, DSCP helpers, IPv4 FIB public definitions, and nexthop objects. It is internal to the IPv4 FIB implementation and is the bridge between prefix trie nodes and shared route semantics.

## Risks and Edge Cases
Because lookup readers are RCU-based, `fib_result_assign()` must not take references and writers must keep `fib_info` alive until grace periods finish. `fib_alias_accessed()` deliberately avoids writes unless the accessed bit is absent; changing that could add lookup-path cacheline contention.

The route alias fields are compact and visible to multiple subsystems. DSCP, table ID, offload state, and default-route cache semantics must remain aligned with trie insertion, dump, and path-selection logic.

## Test Signals
Coverage comes from route add/delete/lookup/dump tests that create multiple aliases for the same prefix with different priorities, DSCP selectors, route types, and tables; default-route selection tests; route offload flag update tests; and RCU stress tests around deleting routes while lookups and dumps run.
