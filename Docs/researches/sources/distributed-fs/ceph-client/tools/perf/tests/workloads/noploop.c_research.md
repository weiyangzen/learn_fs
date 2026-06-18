# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/noploop.c

## Purpose
This is a minimal timed busy loop used as a generic perf sampling workload with a recognizable thread name and almost no application-side behavior.

## Important APIs, Types, And Functions
The workload entry is `noploop()`, registered with `DEFINE_WORKLOAD(noploop)`. It uses `pthread_setname_np()`, `signal()`, `alarm()`, `atoi()`, and a `volatile sig_atomic_t done` flag.

## Control Flow
`noploop()` sets the thread name to `perf-noploop`, parses an optional duration, installs SIGINT/SIGALRM handlers, arms an alarm, and spins in an empty loop until the handler sets `done`.

## State, Dependencies, And Integration
There is no persisted state and no data structure dependency beyond the signal flag. Its integration value is to provide stable CPU activity for tests that need samples without branch, syscall, data, or thread complexity.

## Risks And Test Signals
The empty loop is intentionally simple; changes that add syscalls or sleeps would reduce sample density. The main risk is compiler optimization, mitigated by volatile signal state. Downstream success is a bounded process that consumes CPU and exits after the alarm.
