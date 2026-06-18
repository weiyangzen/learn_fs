# sources/distributed-fs/ceph-client/kernel/locking/qspinlock_stat.h

## Purpose
Adds optional qspinlock and PV qspinlock lock-event accounting. When lock event counts and paravirt spinlocks are enabled, it provides debugfs-style read support and wraps `pv_wait()`/`pv_kick()` to measure latency.

## Important APIs, Types, and Functions
- `lockevent_read()` formats raw counters or derived averages.
- `lockevent_pv_hop()` accumulates PV hash probe counts.
- `__pv_kick()` measures kick latency and records per-target kick time.
- `__pv_wait()` measures wake latency and counts kicks that woke the current CPU.
- `pv_kick` and `pv_wait` are macro-redefined to wrappers when enabled.

## Control Flow
Reads locate the event id from inode private data, sum per-CPU counters, and for latency or hash-hop events divide by the relevant kick count. PV wait/kick wrappers timestamp with `sched_clock()` around the hypercall or after wake and add results into lockevents.

## State and Persistence
State consists of per-CPU `lockevents[]` from `lock_events.h` and per-CPU `pv_kick_time`. It is runtime diagnostic state only.

## Dependencies and Integration Points
Depends on `CONFIG_LOCK_EVENT_COUNTS`, optional `CONFIG_PARAVIRT_SPINLOCKS`, scheduler clock, simple read buffer helpers, and qspinlock PV code that calls `lockevent_pv_hop()`.

## Risks
Instrumentation must not perturb locking semantics. Per-CPU `pv_kick_time` is a best-effort timing channel and can be overwritten by concurrent events on the target CPU. Derived averages depend on nonzero denominator counters.

## Test Signals
Enable lock event counts and verify readable counters for PV latency, hash hops, kicks, waits, and wakeups. Compare zero-overhead stubs when the config is disabled.
