<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/testutil/helpers_unix.go -->
# sources/cloud-native/containerd/pkg/testutil/helpers_unix.go

## Purpose
Unix root requirement helpers for tests.

## Important APIs, Types, And Functions
RequiresRoot skips unless -test.root is set and asserts os.Getuid()==0; RequiresRootM exits from TestMain-style contexts.

## Control Flow
Checks rootEnabled first, then UID.

## State And Persistence
No persistence except process exit in RequiresRootM.

## Dependencies And Integration Points
Used by tests needing mounts, namespaces, or privileged syscalls.

## Risks And Edge Cases
Tests running as root without -test.root still skip, preventing accidental privileged execution.

## Test Signals
Indirectly covered by root-gated tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/testutil/helpers_unix.go -->
