# sources/distributed-fs/ceph-client/kernel/locking/lock_events.c

## Purpose
`lock_events.c` implements debugfs reporting for low-overhead per-CPU locking event counters. It exposes one file per event under `/sys/kernel/debug/lock_event_counts/` and a `.reset_counts` write-only file.

## Important APIs, Types, and Functions
`lockevent_names[]` is generated from `lock_events_list.h`, with an additional `.reset_counts` entry. `DEFINE_PER_CPU(unsigned long, lockevents[lockevent_num])` stores counters. Public weak `lockevent_read()` sums per-CPU counters for a file's event ID. `lockevent_write()` resets all counters when writing to `.reset_counts`. `init_lockevent_counts()` creates debugfs files at `fs_initcall` time. `skip_lockevent()` hides PV qspinlock events on native bare metal when paravirt spinlocks are configured.

## Control Flow
At init, the code creates the debugfs directory, iterates event IDs, optionally skips PV-only names, and creates readonly files whose `i_private` stores the event ID. Reads sum all possible CPUs and return a decimal count. Writes to non-reset files are ignored by returning count; writes to reset loop over all possible CPUs and clear every event with `WRITE_ONCE()`.

## State and Persistence Behavior
Counters are per-CPU runtime statistics and reset on boot or `.reset_counts`. They are intentionally lossy because updates use raw per-CPU operations without expensive synchronization. Values persist while the kernel is running.

## Dependencies and Integration Points
It depends on debugfs, scheduler/per-CPU iteration, `lock_events.h`, optional paravirt spinlock detection, and event increment sites throughout locking code. The weak read function can be overridden by architecture or specialized code.

## Risks and Test Signals
Reading and resetting can be slow on large CPU systems. Event ID validation protects invalid reads. Debugfs creation failure removes partial entries. Tests should verify directory/file creation, PV event skipping on bare metal, per-CPU aggregation, reset semantics, weak override compatibility, and no measurable overhead when counters are not read.
