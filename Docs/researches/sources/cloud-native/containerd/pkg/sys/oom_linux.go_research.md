<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/oom_linux.go -->
# sources/cloud-native/containerd/pkg/sys/oom_linux.go

## Purpose
Linux OOM score adjustment utilities for processes.

## Important APIs, Types, And Functions
OOMScoreAdjMin/Max, AdjustOOMScore, SetOOMScore, GetOOMScoreAdj, and runningPrivileged.

## Control Flow
AdjustOOMScore clips input and calls SetOOMScore. SetOOMScore validates range, writes /proc/<pid>/oom_score_adj, and ignores permission errors for unprivileged/userns cases. GetOOMScoreAdj reads and parses the file.

## State And Persistence
Persists kernel OOM adjustment for target process through procfs.

## Dependencies And Integration Points
Used by shim AdjustOOMScore and runtime process setup. Depends on moby/sys/userns and x/sys/unix.

## Risks And Edge Cases
Ignoring permission errors for negative scores in unprivileged contexts preserves compatibility but can hide failed hardening. GetOOMScoreAdj cannot distinguish unset from zero.

## Test Signals
oom_linux_test.go covers positive, negative privileged, bounds, and skipped unprivileged behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/oom_linux.go -->
