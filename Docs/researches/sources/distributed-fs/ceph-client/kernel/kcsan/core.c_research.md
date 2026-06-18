# sources/distributed-fs/ceph-client/kernel/kcsan/core.c

## Purpose
Implements the KCSAN runtime: probabilistic watchpoint setup, conflict detection, value-change inference, scoped/weak-memory checks, and TSAN-compatible compiler instrumentation callbacks.

## Important APIs, Types, and Functions
Global knobs include `kcsan_enabled`, `kcsan_udelay_task`, `kcsan_udelay_interrupt`, skip/watch parameters, and weak-memory mode. Core mechanics are `find_watchpoint`, `insert_watchpoint`, `try_consume_watchpoint`, `check_access`, `kcsan_found_watchpoint`, and `kcsan_setup_watchpoint`. Exported APIs include enable/disable, atomic-region helpers, access masks, scoped accesses, `__kcsan_check_access`, barrier hooks, TSAN read/write/range/volatile/atomic callbacks, function entry/exit, and instrumented memset/memmove/memcpy wrappers.

## Control Flow
Every instrumented access calls `check_access`. The fast path first scans matching encoded watchpoints; if one is found, it attempts to consume it and publish report info. If none is found, a per-CPU skip counter decides whether to set a new watchpoint. Setup encodes the access, inserts it into adjacent slots, samples the old value, delays, samples the new value, consumes/removes the watchpoint, and reports known-origin or unknown-origin races depending on whether another access consumed it.

## State and Persistence
KCSAN state lives in global atomic `watchpoints`, per-CPU skip and random state, per-task/per-CPU `kcsan_ctx`, module parameters, and counters defined in debugfs. State is runtime-only and reset on boot. Scoped access lists are lazily initialized per context.

## Dependencies and Integration Points
Uses `encoding.h` for watchpoint encoding, `report.c` for diagnostics, `permissive.h` for ignore rules, task context fields, user access save/restore, lockdep/IRQ trace preservation, compiler TSAN ABI, and kernel barrier instrumentation.

## Risks
This is extremely hot code; extra branches or dereferences impact the whole kernel under KCSAN. Watchpoint encoding can produce false positives that report code must filter. IRQ and scoped-access interactions share contexts and require careful disabling. Value-change inference can miss races or report unknown-origin races depending on config. Unbalanced KCSAN disable/atomic helpers intentionally warn.

## Test Signals
Boot selftest validates encoding and barrier instrumentation. KUnit tests exercise race reports, atomics, scoped assertions, weak-memory barriers, permissive mode, `data_race`, `__data_racy`, and zero-size access behavior.
