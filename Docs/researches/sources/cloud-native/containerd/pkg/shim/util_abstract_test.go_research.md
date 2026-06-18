<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util_abstract_test.go -->
# sources/cloud-native/containerd/pkg/shim/util_abstract_test.go

## Purpose
Non-Windows, non-Darwin test for abstract Unix socket support.

## Important APIs, Types, And Functions
TestNewSocketAbstract calls NewSocket on an abstract-style address and dials the translated Unix path.

## Control Flow
Creates listener, dials it, closes connection and listener via cleanup.

## State And Persistence
No filesystem state for abstract sockets.

## Dependencies And Integration Points
Exercises util_unix.go socket path parsing and NewSocket behavior.

## Risks And Edge Cases
Skipped on Darwin/Windows because abstract sockets are not available there.

## Test Signals
Direct coverage for abstract socket creation/connectivity.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util_abstract_test.go -->
