# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/AclTestHelpers.java

## Purpose
`AclTestHelpers` is a small final utility class for NameNode ACL tests. It reduces boilerplate for constructing `AclEntry` instances and asserting permission/access-control outcomes.

## Important APIs, Types, and Functions
- Four overloaded `aclEntry(...)` factory methods build `AclEntry` values with combinations of scope, type, optional name, and optional permission.
- `assertFilePermissionDenied(FileSystem, UserGroupInformation, Path)` expects `DFSTestUtil.readFileBuffer` to throw `AccessControlException`.
- `assertFilePermissionGranted(...)` expects the same read to succeed and fails on `AccessControlException`.
- `assertPermission(FileSystem, Path, short)` delegates to the four-argument overload and infers `hasAcl` from bit 12 of the supplied mode.
- `assertPermission(FileSystem, Path, short, boolean)` masks expected mode to `01777`, reads `FileStatus`, compares `FsPermission.toShort()`, and checks `FileStatus.hasAcl()`.

## Control Flow and Behavior
ACL entry helpers simply configure an `AclEntry.Builder` and call `build`. Permission helpers perform real filesystem operations. The denied/granted helpers use exception control flow around file reads, while mode checks use `FileSystem.getFileStatus`.

## State and Persistence
The class has no state. It observes external HDFS state through `FileSystem` and `FileStatus`. It does not mutate permissions or ACLs itself.

## Dependencies and Integration Points
It depends on Hadoop filesystem, permission, ACL, security, and test utilities plus JUnit assertions. It is used heavily by `FSAclBaseTest` and likely other NameNode ACL suites through static imports.

## Risks and Edge Cases
- `assertPermission(fs, path, perm)` infers `hasAcl` from an encoded high bit convention; callers must pass the extended permission short intentionally.
- Access helpers only test read access through `DFSTestUtil.readFileBuffer`, not write, execute, or traversal permissions.
- Fail messages include the `UserGroupInformation`, which helps diagnosis but does not verify that the `FileSystem` is actually bound to that user.

## Test Signals
This helper contributes signals to ACL tests by making expected `AccessControlException`, exact mode bits, and `hasAcl` status concise and consistent.
