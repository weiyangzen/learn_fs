# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/NoopUfsDeleter.java

## Purpose
`NoopUfsDeleter` is a null-object `UfsDeleter` for delete operations that should not remove corresponding UFS entries, such as Alluxio-only deletes.

## Important APIs, types, and functions
It exposes singleton `INSTANCE` and implements `delete(AlluxioURI, Inode)` as an empty method.

## Control flow
The delete call returns immediately. Callers can use it to avoid conditional checks around optional UFS deletion.

## State and persistence behavior
It stores no state and does not mutate Alluxio or UFS data.

## Dependencies and integration points
It implements the local `UfsDeleter` interface and is used by delete internals when UFS deletion is disabled or unnecessary.

## Risks
Using the no-op deleter for a delete expected to propagate to UFS leaves UFS data intact. The singleton is thread-safe because it has no state.

## Test signals
Delete tests should assert Alluxio-only operations select no UFS deletion and that persisted deletes requiring UFS cleanup do not use this deleter.
