# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/state/DirectoryId.java

## Purpose
`DirectoryId` is a small mutable value object representing a directory id split into a container id and sequence number. It also exposes a live read-only view for callers that should not mutate the id.

## Important APIs, types, and functions
The constructor initializes both fields to zero and creates an anonymous `UnmodifiableDirectoryId` view. Getters and setters cover `containerId` and `sequenceNumber`. The nested `UnmodifiableDirectoryId` interface exposes only getters, and `getUnmodifiableView()` returns the stable view instance.

## Control flow
There is no control flow beyond direct field access. The immutable view reads the outer object's current fields, so it reflects later mutations.

## State and persistence behavior
State is in-memory in two longs. Persistence, if any, is handled by callers that serialize directory id allocation state elsewhere.

## Dependencies and integration points
It is used by file-master directory id generation/allocation code. It has no external library dependencies.

## Risks
The class is not synchronized or annotated thread-safe; concurrent readers of the view and writers through setters can race. The view is immutable only in API surface, not in snapshot semantics.

## Test signals
Tests should verify default zero state, setter/getter behavior, live view updates after mutation, and caller-level synchronization where shared across threads.
