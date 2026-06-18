# sources/distributed-fs/coda/coda-src/venus/daemon.cc

## Purpose
This file implements the generic Venus daemon scheduler and a helper class for simple periodic daemon vprocs.

## Important APIs, Types, and Functions
`DaemonInit()` initializes the timer list and schedules once-a-day logging. `RegisterDaemon()` inserts a timer element with interval and optional sync byte. `InitOneADay()` schedules the first daily task around midnight. `DispatchDaemons()` rescans expired timers, reinserts them, signals registered daemons, or performs daily log/rusage/malloc reporting. The private `Daemon` class wraps a `PROCBODY` function in a vproc. `FireAndForget()` creates a daemon and waits until it has registered.

## Control Flow
The scheduler stores each daemon as a timer element. When dispatch runs, every expired element is requeued for its next interval and its sync byte is signaled. `Daemon::main()` yields once, signals startup readiness, registers itself, then waits for sync events and runs the target function.

## State and Persistence Behavior
State is in-memory timer list metadata. Daily tasks write diagnostics to the Venus log but do not persist scheduler state.

## Dependencies and Integration Points
It depends on LWP timers, `vproc`, Venus logging, `RusagePrint`, and `MallocPrint`. `comm_daemon.cc` and realm code register daemon work through this scheduler.

## Risks and Test Signals
Risks include leaked timer metadata, drift from reinserting fixed intervals after delayed dispatch, missing synchronization for daemon startup, and daily scheduling edge cases around local time changes. Tests should register short-interval daemons, verify repeated signaling, run once-a-day logic across midnight/DST, and ensure `FireAndForget` does not return before registration.
