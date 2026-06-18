<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/reaper/reaper_unix.go -->
# sources/cloud-native/containerd/pkg/sys/reaper/reaper_unix.go

## Purpose
Unix process reaper and subscription monitor for child exit notifications.

## Important APIs, Types, And Functions
ErrNoSuchProcess, Reap, Default Monitor, Monitor.Start, StartLocked, Wait, WaitTimeout, Subscribe, Unsubscribe, notify, reap, and exitStatus.

## Control Flow
SIGCHLD handlers call Reap, which wait4-reaps all children and notifies subscribers. Wait consumes matching exit events then calls cmd.Wait and unsubscribes. notify retries subscriber sends with short timeouts until all receive.

## State And Persistence
Maintains in-memory subscriber map and per-subscriber channels. Reaps kernel child process state.

## Dependencies And Integration Points
Used by shim signal loop and command execution that needs subreaper-style wait semantics. Depends on go-runc Exit and x/sys/unix.

## Risks And Edge Cases
Slow or abandoned subscribers can make notify spin until delivery. WaitTimeout kills only the command pid. Correct use requires Reap to be called on SIGCHLD.

## Test Signals
Indirectly covered by shim/reaper integration; no local test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/reaper/reaper_unix.go -->
