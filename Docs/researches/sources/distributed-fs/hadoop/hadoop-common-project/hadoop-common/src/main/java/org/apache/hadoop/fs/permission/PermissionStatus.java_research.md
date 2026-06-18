<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/PermissionStatus.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/PermissionStatus.java

## Purpose
Bundles owner, group, and `FsPermission` into a writable value object used in filesystem metadata.

## Important APIs, Types, And Functions
Constructors, `createImmutable`, getters, `applyUMask`, `write`, `readFields`, static `read`, and `toString` form the API.

## Control Flow
`applyUMask` returns a new `PermissionStatus` with the same owner/group and masked permission. Serialization writes owner/group strings with `Text` and delegates permission serialization.

## State And Persistence
Stores `username`, `groupname`, and `permission`. Writable factory registration supports Hadoop serialization. The immutable subclass rejects `readFields`.

## Dependencies And Integration Points
Used by filesystem metadata paths needing ownership plus mode. Depends on `FsPermission`, `Text`, and `WritableFactories`.

## Risks
The no-arg constructor exists for writable deserialization and can produce partially initialized objects before `readFields`. Immutability is enforced only by the private subclass.

## Test Signals
Writable round-trip, immutable read rejection, umask application preserving owner/group, and null/empty owner/group handling as expected by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/PermissionStatus.java -->
