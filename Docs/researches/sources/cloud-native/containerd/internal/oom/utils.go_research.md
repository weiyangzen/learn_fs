# sources/cloud-native/containerd/internal/oom/utils.go

## Purpose
Contains Linux helpers for opening inotify watches on cgroup v2 memory event files and parsing cgroup stat files.

## Important APIs, Types, And Functions
`memoryEventNonBlockFD` creates an inotify fd and watches `memory.events` and `cgroup.events`. `getCgroup2Path` maps a PID to `/sys/fs/cgroup/<group>`. `readKVStatsFile`, `parseKV`, and `parseUint` read key/value stats.

## Control Flow
Watcher setup opens nonblocking inotify, adds two modify watches, and returns an `os.File`. Stat parsing scans fields and treats negative values as zero for compatibility with cgroups parsing.

## State And Persistence
Creates kernel inotify watch state held by the returned fd. No file writes.

## Dependencies And Integration Points
Uses cgroups v3 cgroup2 helpers, `unix` syscalls, and cgroup v2 files.

## Risks
Requires unified cgroup v2, readable cgroup files, and valid PID mapping. Inotify setup must close the fd on partial failure.

## Test Signals
Covered indirectly by `watcher_test.go`.
