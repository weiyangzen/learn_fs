<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/helper_test.go -->
# sources/cloud-native/containerd/plugins/content/local/helper_test.go

## Purpose
Shared test setup for local content store tests.

## Important APIs, Types, And Functions
contentStoreEnv creates temp dir, NewStore, cancellable context, and cleanup function.

## Control Flow
Tests call helper, use returned content.Store and temp path, then cleanup cancels context.

## State And Persistence
Creates a temporary filesystem-backed store.

## Dependencies And Integration Points
Used by store_test.go benchmarks and tests.

## Risks And Edge Cases
Uses NewStore without label store, so label-update tests need separate setup.

## Test Signals
Indirect support for local content tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/helper_test.go -->
