# sources/cloud-native/moby/daemon/containerd/image_delete_test.go

## Purpose
Tests image delete semantics for references, digest references, same-target tags, missing images, and remaining image-store records.

## Important APIs, Types, And Functions
- `TestImageDelete` is a table-driven parallel test over reference scenarios.
- `emptyTestContainerStore` and `testContainerStore` provide a no-container store implementation.
- Test helpers such as `nameTag`, `nameDigest`, `desc`, and `digestFor` are assumed from nearby test files.

## Control Flow
Each subtest creates a fresh metadata image store and event service, inserts starting image records, calls `ImageDelete` with default options, compares any expected error string, lists remaining images, and compares their names and target digests in order.

## State And Persistence
State is a temporary containerd metadata database. No content store or real containers are used, so tests focus on image-name records rather than blob deletion or container conflicts.

## Dependencies And Integration Points
Uses containerd metadata image store, namespaces, log test context, daemon image errors, and the image backend remove options. It directly guards `image_delete.go` reference grouping behavior.

## Risks And Edge Cases
The table does not test force, prune, running/stopped containers, platform-specific deletion, events, response records, or labels. The custom container store always reports no containers, so conflict logic is only partially covered.

## Test Signals
Failures indicate regressions in missing-image handling, digest/name matching, untag-only behavior, or full target deletion when references are equivalent.
