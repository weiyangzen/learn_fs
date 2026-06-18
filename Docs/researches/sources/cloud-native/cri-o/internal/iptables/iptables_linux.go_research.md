# sources/cloud-native/cri-o/internal/iptables/iptables_linux.go

## Purpose
Implements Linux manual xtables locking for iptables-restore when native restore wait flags are unavailable.

## Important APIs, Types, And Functions
- `locker` holds a 1.6-style file lock and 1.4-style Unix listener lock.
- `(*locker).Close` releases both locks.
- `grabIptablesLocks(lockfilePath14x, lockfilePath16x string) (iptablesLocker, error)` acquires both lock styles with polling.
- `grabIptablesFileLock` uses `unix.Flock`.

## Control Flow
`grabIptablesLocks` opens/creates the 1.6 lock file, polls for a non-blocking exclusive flock, then polls for a Unix listener at the 1.4 lock path. A deferred cleanup closes partially acquired locks unless both acquisitions succeed.

## State And Persistence
Creates/opens a lock file under the configured xtables lock path and binds a Unix socket at the old lock path. These are process-level synchronization artifacts, not CRI-O state.

## Dependencies And Integration Points
Called by `runner.restoreInternal` in `iptables.go` when iptables-restore lacks wait support. Depends on Linux `flock`, `net.ListenUnix`, and Kubernetes wait polling.

## Risks And Edge Cases
Lock acquisition times out after two seconds per lock style. Failure to close locks is logged by caller. The old Unix socket lock can conflict with stale filesystem entries or permissions.

## Test Signals
No direct tests in this subset. Behavior is indirectly important for safe production restore serialization.
