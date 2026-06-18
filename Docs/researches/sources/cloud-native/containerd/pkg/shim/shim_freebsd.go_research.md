<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_freebsd.go -->
# sources/cloud-native/containerd/pkg/shim/shim_freebsd.go

## Purpose
FreeBSD shim server platform shim.

## Important APIs, Types, And Functions
newServer returns ttrpc.NewServer; subreaper is a no-op.

## Control Flow
Used by shared shim run path on FreeBSD.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Depends on containerd/ttrpc.

## Risks And Edge Cases
Child reaping behavior lacks Linux PR_SET_CHILD_SUBREAPER; lifecycle assumptions differ by platform.

## Test Signals
Indirect platform coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_freebsd.go -->
