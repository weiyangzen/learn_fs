# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/MountTableTest.java

## Purpose
`MountTableTest` validates path-to-UFS mount resolution, reverse resolution, nested mount behavior, deletion constraints, read-only mount enforcement, and mount-info lookup.

## Important APIs, Types, and Functions
The tests exercise `MountTable.add`, `delete`, `resolve`, `reverseResolve`, `getMountPoint`, `isMountPoint`, `containsMountPoint`, `checkUnderWritableMountPoint`, `getMountTable`, and `getMountInfo`.

## Control Flow, State, and Persistence
Each test starts with a root mount to `s3a://bucket/`. It adds mounts under `/mnt`, verifies longest-prefix resolution and reverse resolution, rejects duplicate Alluxio mount points and conflicting UFS prefixes, checks nested mount deletion ordering, and validates read-only access exceptions for mount roots and descendants.

## Dependencies and Integration Points
The test uses mocked `UfsManager`, local UFS clients, `MountContext`, `MountInfo`, `AlluxioURI`, and `ExceptionMessage` text. It covers both path-only and fully qualified Alluxio URIs.

## Risks
Mount conflict rules are path-prefix sensitive and scheme-aware. Nested mount deletion must avoid removing a parent while child mounts remain. Reverse resolution returning `null` for unmounted UFS paths is an important boundary.

## Test Signals
Signals include duplicate mount rejection, UFS prefix conflict rejection, root fallback resolution, nested longest-prefix matching, `containsMountPoint` with include-self toggles, read-only denial, writable success, copy equality from `getMountTable`, and lookup by mount id.
