# sources/cloud-native/containerd/internal/oom/watcher.go

## Purpose
Implements cgroup v2 OOM event monitoring for Linux containers.

## Important APIs, Types, And Functions
`New` returns an `oomWatchers` registry. `Add` creates a per-container `watcher`, opens cgroup event fd, and starts monitoring. `Stop` stops a watcher. `watcher.start` reads inotify events and detects increases in `memory.events` `oom_kill`.

## Control Flow
`Add` resolves cgroup path from PID, opens inotify watches, checks duplicate container IDs, starts a goroutine, and stores it. The goroutine reads events, reloads memory stats, invokes callback on increased kills, exits on fd close or deleted cgroup, and reports errors on `errCh`.

## State And Persistence
In-memory map of container ID to watcher and kernel inotify fd state. It does not persist events.

## Dependencies And Integration Points
Uses `errdefs`, Linux inotify, cgroup v2 files, and the OOM interface.

## Risks
`Stop` does not remove the watcher from the map, so repeated add after stop may still see existing entry. `stop` waits on `errCh`; goroutine exit must happen after fd close. Root/cgroup permissions are required.

## Test Signals
`watcher_test.go` launches a constrained `dd` process in a cgroup and asserts one OOM callback.
