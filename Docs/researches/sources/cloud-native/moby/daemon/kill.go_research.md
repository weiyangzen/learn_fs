# sources/cloud-native/moby/daemon/kill.go

## Purpose
Implements daemon container signal delivery and force-kill behavior, including stop-signal parsing, paused-container handling, manual-stop persistence, and exit-event races.

## Important APIs, Types, And Functions
`ContainerKill` parses an optional signal, validates platform support, resolves the container, and dispatches to `Kill` for default SIGKILL or `killWithSignal` otherwise. `killWithSignal` locks the container, gets its running task, marks `ExitOnNext` for configured stop signals or SIGKILL, checkpoints manual-stop state, handles restarting containers, calls task `Kill`, resumes paused containers when needed, and logs kill events. `Kill` sends SIGKILL, waits, tries direct process kill on timeout, then waits again. `errNoSuchProcess` implements `NotFound`.

## Control Flow
Signal parse errors are invalid-parameter errors. Not-found task kill errors trigger an asynchronous wait and possible exit handling rather than immediate failure. Windows receives a longer force-kill wait timeout.

## State And Persistence
Mutates container state flags (`ExitOnNext`, `HasBeenManuallyStopped`), checkpoints to `containersReplica`, emits events, and may resume paused tasks.

## Dependencies And Integration Points
Integrates daemon container store, containerd task APIs, event logging, signal parsing, and platform-specific `killProcessDirectly`.

## Risks And Test Signals
Races with already-exited tasks are explicitly handled but still timing-sensitive. Checkpoint failures are logged but nonfatal. No direct tests are included in this subset.
