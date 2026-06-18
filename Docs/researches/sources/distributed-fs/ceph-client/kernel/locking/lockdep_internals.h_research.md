# sources/distributed-fs/ceph-client/kernel/locking/lockdep_internals.h research

## Purpose
`lockdep_internals.h` is the private contract shared by the lockdep engine and its proc reporting code. It defines usage-state bit numbering, mask helpers, bounded storage sizes, lock-chain context bits, externally visible lockdep counters, and debug-stat accessors that are not part of the public lockdep API.

## Important APIs, Types, and Functions
The primary type defined here is `enum lock_usage_bit`. It is generated from `lockdep_states.h` so each tracked IRQ state contributes four bits: used in state, used in state as read, enabled in state, and enabled in state as read. After generated bits, `LOCK_USED`, `LOCK_USED_READ`, and `LOCK_USAGE_STATES` are appended. The header asserts that `LOCK_TRACE_STATES` matches `LOCK_USAGE_STATES`, keeping trace arrays aligned with usage bits.

Mask definitions include `LOCK_USAGE_READ_MASK`, `LOCK_USAGE_DIR_MASK`, `LOCK_USAGE_STATE_MASK`, per-bit `LOCKF_*` constants, aggregate enabled/used masks for all IRQ states, and combined masks such as `LOCKF_IRQ`, `LOCKF_IRQ_READ`, `LOCKF_ENABLED_IRQ_ALL`, and `LOCKF_USED_IN_IRQ_ALL`. These masks drive lockdep's usage conflict checks in `lockdep.c` and summary counts in `lockdep_proc.c`.

Size controls include `MAX_LOCKDEP_ENTRIES`, `MAX_LOCKDEP_CHAINS_BITS`, `MAX_STACK_TRACE_ENTRIES`, `STACK_TRACE_HASH_SIZE`, `MAX_LOCKDEP_CHAINS`, `AVG_LOCKDEP_CHAIN_DEPTH`, and `MAX_LOCKDEP_CHAIN_HLOCKS`. `CONFIG_LOCKDEP_SMALL` provides reduced static allocations for architectures with tight kernel image limits.

The file declares shared globals and functions such as `lock_chains[]`, `get_usage_chars()`, `__get_key_name()`, `lock_chain_get_class()`, lockdep counters, `lockdep_next_lockchain()`, `lock_chain_count()`, `max_lockdep_depth`, `max_bfs_queue_depth`, `max_lock_class_idx`, `lock_classes[]`, and `lock_classes_in_use[]`.

Under `CONFIG_DEBUG_LOCKDEP`, it defines `struct lockdep_stats` and macros/functions for per-CPU debug counters: `debug_atomic_inc()`, `debug_atomic_dec()`, `debug_atomic_read()`, `debug_class_ops_inc()`, and `debug_class_ops_read()`.

## Control Flow
This header has no runtime control flow of its own, but it shapes several critical flows. `lockdep.c` includes it to allocate graph storage and generate usage checks. `lockdep_proc.c` includes it to iterate `lock_classes[]`, traverse lock chains, and print counters. Any addition to `lockdep_states.h` expands the generated enum and masks here, which then changes `LOCK_USAGE_CHARS`, `/proc/lockdep` output, state conflict logic, and stats categorization.

## State and Persistence Behavior
The header declares state that persists globally while the kernel runs. Counters represent live lockdep storage and historical observations, not persisted disk data. Debug counters are per-CPU to avoid cache bouncing and are summed on read by `debug_atomic_read()`. Because many arrays are statically bounded, build-time configuration directly controls how much lockdep history can be retained before lockdep disables itself.

## Dependencies and Integration Points
The header depends on `lockdep_states.h`, public lockdep structures, per-CPU APIs, and architecture local operations for debug stats. It is a tight coupling point between lockdep graph mutation and procfs presentation. It also embeds the expectation that `include/linux/lockdep.h` keeps constants such as `XXX_LOCK_USAGE_STATES` and `LOCK_TRACE_STATES` synchronized with the generated states.

## Risks and Edge Cases
The most important maintenance risk is bit-layout drift. `lockdep.c` assumes the low bit encodes read/write and the direction bit encodes used-in versus enabled, so changing generation order would break `exclusive_mask()`, `original_mask()`, and state-printing logic. Adding a new state requires updating public constants as warned by `lockdep_states.h`. Increasing array sizes affects kernel memory footprint; decreasing them increases validator shutdown risk under complex workloads.

## Test Signals
Compile-time assertions and build failures are the first signal for enum/constant mismatch. Runtime `/proc/lockdep_stats` exposes max counts and can show exhaustion pressure in lock classes, entries, chains, stack traces, BFS queue depth, and chain hlock fragmentation. `CONFIG_DEBUG_LOCKDEP` builds expose redundant/cyclic/find-mask counters and per-class operation counts.
