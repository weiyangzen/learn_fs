# sources/distributed-fs/ceph-client/tools/perf/scripts/python/futex-contention.py

## Purpose

`futex-contention.py` measures time spent blocked in futex waits and prints per-thread, per-lock contention statistics. It is a perf Python translation of an older SystemTap futex contention example and is designed for syscall tracepoint runs where contention is inferred from `futex(FUTEX_WAIT, ...)` duration.

## Important APIs, Types, and Functions

The script imports `FUTEX_CMD_MASK`, `FUTEX_WAIT`, `nsecs()`, and `add_stats()` from perf's `Util` library. Global dictionaries are `thread_thislock`, `thread_blocktime`, `lock_waits`, and `process_names`.

Perf callbacks are `syscalls__sys_enter_futex()`, `syscalls__sys_exit_futex()`, `trace_begin()`, and `trace_end()`. The enter callback records wait start state for `FUTEX_WAIT`; the exit callback computes elapsed nanoseconds and updates aggregate min/max/average/count stats.

## Control Flow and Data Flow

On futex enter, the script masks `op` with `FUTEX_CMD_MASK` and ignores anything other than `FUTEX_WAIT`, so wake operations and non-blocking commands do not contribute. For wait calls, it stores the thread's command name, lock address `uaddr`, and start time in nanoseconds.

On futex exit, if the tid has a recorded start time, elapsed time is `nsecs(exit) - thread_blocktime[tid]`. The script calls `add_stats(lock_waits, (tid, lock), elapsed)` and removes the per-thread active wait state. At trace end it iterates `lock_waits` and prints command, tid, lock address, count, average, max, and min nanoseconds.

## State and Persistence Behavior

State is entirely in-memory. `thread_blocktime` and `thread_thislock` hold active waits, while `lock_waits` holds long-lived aggregate stats keyed by `(tid, lock)`. `process_names` maps tid to the last observed command name. No files or databases are written.

## Dependencies and Integration Points

The script depends on perf's Python syscall tracepoint naming and `PERF_EXEC_PATH` utility modules. The helper wrapper `scripts/python/bin/futex-contention-report` runs it via `perf script`. It integrates with syscall traces that include futex enter and exit events with arguments `nr`, `uaddr`, `op`, `val`, `utime`, `uaddr2`, and `val3`.

## Risks and Edge Cases

The script measures syscall duration for all `FUTEX_WAIT` calls, which includes scheduler time and may include waits that return due to timeout, signal, or error. It does not inspect the futex exit return value, so failed or interrupted waits still contribute elapsed time. Active waits left open at trace end are not reported. Reused tids can merge stats if the trace spans thread exit and new thread creation. Lock addresses are process virtual addresses, so the same numeric address in different processes may not represent the same futex object, although the key includes tid.

## Test Signals

A workload with two threads contending on a pthread mutex should print at least one `lock <addr> contended` line with count and nanosecond stats. A workload with futex wakes but no waits should produce no contention rows. Tests should include interrupted waits and timeouts to decide whether current inclusion semantics are acceptable. A trace with unmatched enter or exit events should not crash.
