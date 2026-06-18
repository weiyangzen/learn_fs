# sources/cloud-native/cri-o/server/server_linux.go

## Purpose
Linux-only server support for CRI-O startup behavior that depends on kernel facilities: seccomp notifier restoration/watch handling and Go runtime thread-limit tuning.

## Important APIs, Types, And Functions
`(*Server).startSeccompNotifierWatcher(ctx)` initializes `s.seccompNotifierChan`, reconciles the configured seccomp notifier directory, restores live notifiers for still-running containers, and starts the watcher goroutine. `configureMaxThreads()` reads `/proc/sys/kernel/threads-max`, sets Go's max thread threshold to 90 percent of that value with `debug.SetMaxThreads`, and logs the result.

## Control Flow
Startup stats the notifier path. If it is an existing directory, it walks files, removes stale listener files, maps each filename to a container short ID, skips missing or non-running containers, recreates seccomp notifiers, and stores them in `s.seccompNotifiers`. If the path is absent or invalid, it removes and recreates the directory with mode `0700`. The goroutine then receives seccomp notifications, looks up the notifier by container ID, records syscalls, optionally arms an expiry callback that marks container state as seccomp-killed and stops the container, and increments the seccomp notifier metric.

## State And Persistence
Uses the filesystem notifier directory as restart state. Live notifier instances are persisted only in `s.seccompNotifiers`; container state is mutated on notifier expiry. The goroutine is long-lived and reads from an unbuffered channel.

## Dependencies And Integration Points
Depends on CRI-O seccomp notifier internals, OCI runtime state constants, server container lookup and stop paths, CRI-O metrics, logging, and Linux `/proc`.

## Risks And Test Signals
The watcher loop does not select on `ctx.Done()`, so shutdown relies on broader server teardown. It removes listener files before attempting restoration, which is intentional cleanup but risky if restoration fails. The log call for `os.RemoveAll` uses `logrus.Error` with formatting text, so the wrapped error may not render as intended. Coverage is indirect through Linux server startup and seccomp notifier integration tests; this file has no direct unit test in the subset.
