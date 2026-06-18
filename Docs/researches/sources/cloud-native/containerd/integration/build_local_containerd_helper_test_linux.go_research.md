# sources/cloud-native/containerd/integration/build_local_containerd_helper_test_linux.go

## Purpose
This Linux-only helper imports additional plugins required for in-memory service initialization.

## Important APIs, Types, and Functions
It has blank imports for image verifier, sandbox, sandbox service, overlay snapshotter, and streaming plugins.

## Control Flow
No runtime flow beyond package initialization side effects from blank imports.

## State and Persistence
Plugin registrations are added to containerd's global plugin registry.

## Dependencies and Integration Points
Complements `build_local_containerd_helper_test.go` for Linux-specific plugin coverage.

## Risks
Missing blank imports can cause `WithInMemoryServices` tests to fail due to absent plugin registrations.

## Test Signals
Build and integration initialization signal only.
