<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/metadata_fuzz_test.go -->
# sources/cloud-native/containerd/contrib/fuzz/metadata_fuzz_test.go

## Purpose
Stateful fuzz coverage for metadata image store, lease manager, container store, and content store.

## Important APIs, Types, And Functions
Defines `testEnv`, `FuzzImageStore`, `FuzzLeaseManager`, `FuzzContainerStore`, `testOptions`, `testDB`, and `FuzzContentStore`.

## Control Flow
Each fuzz target creates temporary bbolt/metadata stores, chooses up to 50 operations from a set, generates structs/strings/resources, and invokes create/list/update/delete/commit APIs while ignoring normal errors.

## State And Persistence
Creates temporary bbolt databases, native snapshotters, local content stores, leases, images, containers, and content writes.

## Dependencies And Integration Points
bbolt, containerd metadata DB/stores, native snapshotter, local content store, namespaces, go-fuzz-headers.

## Risks And Test Signals
Stateful operation ordering catches panics but ignores most semantic errors. Good regression signal for metadata invariants under malformed input. Source size reviewed: 433 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/metadata_fuzz_test.go -->
