<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/compat.go -->
# sources/cloud-native/containerd/pkg/shim/compat.go

## Purpose
Compatibility adapter from pre-2.3 shim launch inputs to the new bootstrap protocol.

## Important APIs, Types, And Functions
readBootstrapParamsFromDeprecatedFields fills BootstrapParams from parsed flags, legacy env vars, publish binary, debug flag, and optionally runc options unmarshaled from stdin.

## Control Flow
The start path in shim.go first tries new proto input and falls back here when input is empty or not a BootstrapParams proto.

## State And Persistence
No persistent state; it reads process environment and adds extensions to an in-memory BootstrapParams.

## Dependencies And Integration Points
Integrates bootapi, runc options, ReadRuntimeOptions, and shim env constants.

## Risks And Edge Cases
Compatibility path is intentionally permissive until the new API is stable; malformed runtime options are ignored unless adding a successfully parsed extension fails.

## Test Signals
Covered indirectly by shim start compatibility and runtime option tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/compat.go -->
