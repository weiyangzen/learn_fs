# sources/distributed-fs/coda/coda-src/venus/comm_daemon.cc

## Purpose
This file implements the Venus probe daemon that periodically checks server liveness and communication quality.

## Important APIs, Types, and Functions
`PROD_Init()` adjusts the down-server probe interval relative to `T1Interval` and starts a `ProbeDaemon` vproc. `ProbeDaemon()` registers a periodic daemon signal and, on wakeup, calls `ServerProbe()` when up/down probe intervals expire and `CheckServerBW()` every communication check interval. `ServerProbe()` marks servers requiring probes, starts separate up/down `probeslave` workers, waits for completion, and updates last-probe times.

## Control Flow
The daemon sleeps on `probe_sync`, wakes through the generic daemon scheduler, checks elapsed logical time, and dispatches work. Server selection suppresses probes when RPC2 liveness data shows recent communication or when interval guards have not expired.

## State and Persistence Behavior
State is transient timing state: last up probe, last down probe, last communication check, and per-server `probeme` flags. It updates server liveness and bandwidth state, which then influences Venus connection behavior.

## Dependencies and Integration Points
It depends on `comm.h`, `venus.private.h`, `venusrecov.h`, `vproc`, the daemon scheduler, server iterators, RPC2 liveness, and `probeslave` workers.

## Risks and Test Signals
Risks include probe suppression errors, stale `probeme` flags, daemon wakeup failures, and poor behavior when intervals are zero or very low. Tests should force probes via pioctl, simulate recent liveness, verify separate up/down worker paths, and confirm bandwidth refreshes continue even when probes are suppressed.
