# sources/distributed-fs/ceph-client/tools/perf/util/lock-contention.c

## Purpose

`lock-contention.c` provides shared helpers for perf lock contention aggregation. It parses call-stack filters, stores lock statistics in a hash table keyed by lock address, and tests whether sampled call stacks match requested kernel-symbol filters.

## Important APIs, Types, and Functions

`parse_call_stack()` consumes comma/space separated filter names into a private `callstack_filters` list. `needs_callstack()` reports whether call stacks must be collected. `lock_stat_find()` and `lock_stat_findnew()` search or create `struct lock_stat` entries in the global `lockhash_table` using `LOCKHASH_BITS`. `match_callstack_filter()` resolves stack IPs to kernel symbols with `machine__find_kernel_symbol()` and checks substring matches against filter names.

## Control Flow

Filter parsing duplicates the input string, tokenizes it with `strtok_r()`, allocates a variable-size `callstack_filter` for each token, and appends it to a list. Lock-stat lookup computes a bucket with `hash_long()` and linearly scans the bucket hlist. `lock_stat_findnew()` initializes new entries with address, duplicated name, flags, and `wait_time_min = ULLONG_MAX`. Call-stack matching exits early when no filters exist, walks up to `max_stack_depth`, handles powerpc zero entries in early LR/NIP positions specially, resolves kernel symbols, and returns true on the first substring match.

## State and Persistence Behavior

`callstack_filters` and `lockhash_table` are process-global state. The file allocates filter strings and lock names but does not provide a local teardown path; owning perf lock code is responsible for lifetime around one command invocation. `struct lock_stat` persists accumulated counts and timing across processed events until the command reports or frees it.

## Dependencies and Integration Points

The code depends on perf debug, env, machine, and symbol helpers plus Linux list, hlist, hash, and zalloc utilities. It integrates with perf lock's event/BPF readers through the shared structures in `lock-contention.h`, and with machine kernel symbol resolution for call-stack filters.

## Risks and Edge Cases

`lockhash_table` must be allocated before lookup or insertion. Filter matching uses substring comparison, so broad tokens can match unexpected lock functions. Powerpc zero-frame handling intentionally differs from other architectures. Allocation failures during parsing or lock creation are reported but can leave previously parsed filters installed. No synchronization is used here; callers must avoid concurrent mutation or provide external serialization.

## Test Signals

Tests should cover parsing comma and space separated filters, empty filter behavior, duplicate lock-address lookup, allocation failure handling where possible, powerpc call-stack zero handling, and symbol-name substring matches. Integration tests should compare perf lock results with and without call-stack filters.
