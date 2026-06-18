<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/testutil/helpers_windows.go -->
# sources/cloud-native/containerd/pkg/testutil/helpers_windows.go

## Purpose
Windows no-op root requirement helpers.

## Important APIs, Types, And Functions
RequiresRoot and RequiresRootM do nothing.

## Control Flow
Immediate return.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Keeps test code portable when root concepts are Unix-specific.

## Risks And Edge Cases
May let Windows tests proceed where equivalent Unix tests would be privilege-gated; Windows-specific APIs must handle their own permissions.

## Test Signals
Build-tag coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/testutil/helpers_windows.go -->
