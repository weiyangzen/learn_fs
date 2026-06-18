# sources/distributed-fs/ceph-client/include/net/aligned_data.h

## Purpose

`aligned_data.h` centralizes high-contention networking counters into `struct net_aligned_data`, with fields cacheline-aligned on SMP builds to reduce false sharing.

## Important APIs, Types, and Functions

`struct net_aligned_data` always contains `atomic64_t net_cookie`. When `CONFIG_INET` is enabled it also contains cacheline-aligned `tcp_memory_allocated` and `udp_memory_allocated`. The global instance `net_aligned_data` is exported for networking code that needs these shared counters.

## Control Flow

There are no functions. Runtime code atomically updates or reads counters through the global object. Cacheline attributes affect layout and contention behavior rather than logical flow.

## State and Persistence Behavior

The counters are process-lifetime kernel memory only. They persist across namespaces and sockets while the kernel runs, but not across reboot. Atomic operations provide update safety; no file-backed persistence exists.

## Dependencies and Integration Points

The header depends on atomic types and cacheline alignment attributes from Linux headers. It integrates with core networking cookie allocation and, when enabled, INET TCP/UDP memory accounting.

## Risks and Edge Cases

Adding new fields without `____cacheline_aligned_in_smp` can reintroduce false sharing. Code must treat these as global counters, not per-net namespace state. Counter semantics depend on atomic type width and initialization in the corresponding definition.

## Test Signals

Check layout with and without SMP and `CONFIG_INET`, concurrent TCP/UDP memory accounting stress, net cookie uniqueness/monotonicity expectations, and performance regressions from cacheline sharing.
