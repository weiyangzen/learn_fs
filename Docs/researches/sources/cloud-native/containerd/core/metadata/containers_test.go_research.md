# sources/cloud-native/containerd/core/metadata/containers_test.go

## Purpose

This test file validates the metadata container store's filtering, create/update/delete behavior, validation, timestamp handling, and protobuf Any comparison.

## Important APIs, Types, and Functions

`TestContainersList` creates multiple containers and checks filter results by labels, ID, and runtime name. `TestContainersCreateUpdateDelete` is a large table covering invalid and valid update cases. Helpers include `checkContainerTimestamps`, `checkContainersEqual`, and `testEnv`. The test registers the OCI runtime spec type with typeurl in `init`.

## Control Flow

The list test creates containers inside explicit Bolt transactions using `boltutil.WithTransaction`, mirrors expected objects, applies filters both locally and through the store, and compares results. The create/update/delete test creates a container, checks timestamps and round-trip equality, applies an update with specified field paths, checks expected error causes or updated record, then retrieves the object again for persistence verification.

## State and Persistence Behavior

Tests use a temporary bbolt database with namespace `testing`. They persist real container buckets and verify created/updated timestamps, label removal, extension replacement or isolated field updates, spec Any values, image and snapshot fields, and delete NotFound behavior.

## Dependencies and Integration Points

The tests exercise `NewContainerStore`, `boltutil.WithTransaction`, filters, namespaces, typeurl/protobuf Any, errdefs, bbolt, logtest, go-cmp options from `compare_test.go`, and testify assertions.

## Risks and Edge Cases

The tests account for Windows timestamp granularity. They do not exhaustively test runtime options, sandbox ID persistence, concurrent transactions, or all possible invalid identifiers/labels. Some field names intentionally reflect store API spelling, so tests help catch accidental field-mask changes.

## Test Signals

Passing tests indicate container CRUD persists the expected fields, filters match supported paths, immutable fields stay protected, label/extension field masks work, timestamps are set correctly, and validation errors are wrapped with errdefs causes.
