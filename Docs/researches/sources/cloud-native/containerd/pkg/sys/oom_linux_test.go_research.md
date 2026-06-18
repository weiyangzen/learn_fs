<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/oom_linux_test.go -->
# sources/cloud-native/containerd/pkg/sys/oom_linux_test.go

## Purpose
Tests Linux OOM score helpers.

## Important APIs, Types, And Functions
Tests SetOOMScore positive/negative, boundaries, adjustOom helper, and waitForPid.

## Control Flow
Tests spawn a sleep process, read initial score, set requested score, and read it back. Negative unprivileged test is currently skipped due CI instability.

## State And Persistence
Creates child processes killed by defer and mutates their procfs oom_score_adj.

## Dependencies And Integration Points
Depends on root/userns status and sleep binary.

## Risks And Edge Cases
Some cases are environment-gated; a process with OOMScoreAdjMin limits lower-score tests.

## Test Signals
Direct coverage for range validation and procfs write/read behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/oom_linux_test.go -->
