# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/NotInMountpointException.java

`NotInMountpointException` is a public evolving exception used when an operation cannot be associated with a mounted target. It extends `UnsupportedOperationException` and stores a formatted message in a final `msg` field returned by `getMessage()`.

The constructors distinguish path-specific failures, such as `getStatus` on a path outside all mount points, from operations on an empty path such as default block-size queries without a target path. There is no mutable state beyond the stored message and no persistence behavior.

Integration points include `ViewFileSystem` default replication/block/server-default APIs, path capability lookups outside mount points, trash/enclosing-root failures, overload-scheme admin helpers, `ViewFileSystemUtil.getStatus`, and internal directory operations that cannot delegate to a target filesystem.

Risks are mostly diagnostic and type-semantic risks. Because it is unchecked, callers may not expect it from filesystem metadata queries. Tests should assert message content for both constructors and verify public APIs throw this type, not generic `IOException`, where no target mount exists.
