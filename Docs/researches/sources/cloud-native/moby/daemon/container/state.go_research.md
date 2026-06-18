<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/state.go -->
# sources/cloud-native/moby/daemon/container/state.go

## Purpose
Models container lifecycle state, wait semantics, containerd handle access, and state-to-API/status string conversions.

## Important APIs, Types, And Functions
`State`, `StateStatus`, `String`, `State`, `Wait`, `conditionAlreadyMet`, `IsRunning`, `GetPID`, `SetExitCode`, `SetRunning`, `SetRunningExternal`, `SetStopped`, `SetRestarting`, `SetError`, `IsPaused`, `IsRestarting`, `SetRemovalInProgress`, `ResetRemovalInProgress`, `IsRemovalInProgress`, `IsDead`, `SetRemoved`, `SetRemovalError`, `Err`, `notifyAndClear`, `C8dContainer`, and `Task`.

## Control Flow
State precedence is running paused, running restarting, running, removing, dead, created, exited. `Wait` returns immediately for already-met conditions or registers stop/removal waiters and bridges them to a context-aware result channel. Stop/restart/removal setters notify and clear relevant waiters.

## State And Persistence Behavior
Many fields serialize inside container config; removal-related fields, waiters, and containerd handles are runtime-only. The embedded mutex is the global container/state lock.

## Dependencies And Integration Points
Integrates API state/wait constants, libcontainerd container/task handles, and human-duration formatting. Used throughout daemon lifecycle and wait APIs.

## Risks And Test Signals
Risks include non-mutually-exclusive running/paused/restarting flags, wait goroutines retained until context/status, and lock requirements for handle access. Tests cover run/stop loops, timeout waits, removal waits, and correct exit status during restart.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/state.go -->
