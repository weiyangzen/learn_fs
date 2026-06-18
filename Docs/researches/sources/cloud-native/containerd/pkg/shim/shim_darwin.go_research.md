<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_darwin.go -->
# sources/cloud-native/containerd/pkg/shim/shim_darwin.go

## Purpose
Darwin shim server platform shim.

## Important APIs, Types, And Functions
newServer returns ttrpc.NewServer; subreaper is a no-op.

## Control Flow
Used by shared run when building/serving ttrpc on Darwin.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Depends on containerd/ttrpc and platform build tags.

## Risks And Edge Cases
No same-user Unix socket handshaker and no subreaper behavior compared with Linux.

## Test Signals
Indirect platform coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_darwin.go -->
