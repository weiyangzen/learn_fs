<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/stdio/platform.go -->
# sources/cloud-native/containerd/pkg/stdio/platform.go

## Purpose
Defines platform-specific stdio/console behavior contract.

## Important APIs, Types, And Functions
Platform interface requires CopyConsole, ShutdownConsole, and Close.

## Control Flow
No implementation in this file; concrete platform packages implement the interface.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by task/shim stdio code to abstract console copying and teardown.

## Risks And Edge Cases
Interface stability matters across platform implementations.

## Test Signals
Compile-time implementation checks are expected elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/stdio/platform.go -->
