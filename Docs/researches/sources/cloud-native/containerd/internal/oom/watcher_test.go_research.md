# sources/cloud-native/containerd/internal/oom/watcher_test.go

## Purpose
Integration-tests the Linux cgroup v2 OOM watcher.

## Important APIs, Types, And Functions
`TestWatcher` creates a cgroup v2 manager, starts `dd`, adds it to the cgroup, registers an OOM callback, sets memory/swap limits, and waits for an OOM kill. Helpers skip unsupported environments.

## Control Flow
The test requires root, unified cgroup v2, and `dd`. It constrains memory below the workload size, waits for the process to be killed, then uses `require.Eventually` to observe callback count.

## State And Persistence
Creates a temporary cgroup and process, plus watcher inotify state. Cleanup stops watchers and waits for the process.

## Dependencies And Integration Points
Uses containerd cgroups v3, `testutil.RequiresRoot`, exec, atomics, and testify.

## Risks
Highly host-dependent and can be slow/flaky due to kernel scheduling and OOM timing. Requires careful cleanup of process/cgroup resources.

## Test Signals
Strong real-kernel signal for watcher functionality when prerequisites are met.
