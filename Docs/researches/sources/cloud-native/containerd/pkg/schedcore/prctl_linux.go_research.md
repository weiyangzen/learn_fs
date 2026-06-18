<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/schedcore/prctl_linux.go -->
# sources/cloud-native/containerd/pkg/schedcore/prctl_linux.go

## Purpose
Linux wrapper for PR_SCHED_CORE operations used to create or join scheduler core-scheduling domains.

## Important APIs, Types, And Functions
PidType constants map to pid, thread-group, and process-group scopes. Create and ShareFrom call unix.Prctl with PR_SCHED_CORE_CREATE or SHARE_FROM.

## Control Flow
Callers choose a scope, then the wrapper forwards raw prctl arguments to the kernel.

## State And Persistence
No package state; changes occur in kernel scheduler state for target processes.

## Dependencies And Integration Points
Depends on x/sys/unix. Used by runtime code that wants core scheduling isolation or sharing.

## Risks And Edge Cases
Requires kernel support and privileges appropriate to PR_SCHED_CORE; errors are passed through without interpretation.

## Test Signals
No local tests; platform/kernel behavior is expected to be integration-tested.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/schedcore/prctl_linux.go -->
