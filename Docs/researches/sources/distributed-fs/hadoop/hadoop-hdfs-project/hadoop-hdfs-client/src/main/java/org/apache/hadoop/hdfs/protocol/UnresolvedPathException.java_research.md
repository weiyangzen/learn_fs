# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/UnresolvedPathException.java

## Purpose
`UnresolvedPathException` represents encountering a symbolic link while resolving an HDFS path. It extends `UnresolvedLinkException` and carries enough path components to compute the resolved path for clients.

## Important APIs, Types, and Functions
One constructor accepts a message for `RemoteException` instantiation. The main constructor stores the original path, preceding path component, remainder, and symlink target. `getResolvedPath` combines the target and remainder differently depending on whether the link target is absolute. `getMessage` returns the superclass message if present; otherwise it returns the resolved path string.

## Control Flow
`getResolvedPath` checks whether the remainder is null/empty. If the link target is absolute, it discards `preceding` and appends only the remainder. If relative, it joins `preceding`, `linkTarget`, and optional `remainder`.

## State and Persistence Behavior
The fields are plain strings populated at construction. There is no persistence, but the message constructor supports remote exception reconstruction where only a message is available.

## Dependencies and Integration Points
It depends on Hadoop `Path` and `UnresolvedLinkException`. It is thrown by path resolution logic and consumed by FileSystem link resolvers such as those in `DistributedFileSystem` methods.

## Risks and Edge Cases
Path joining behavior must preserve absolute-target semantics. The `path` field is stored but not used in resolution. Null `preceding` or `linkTarget` would fail through `Path` construction, so callers must populate them. The comment has a typo but no behavioral impact.

## Test Signals
Symlink resolution tests should assert absolute and relative target behavior with and without remainders. RemoteException wrapping tests should cover the message-only constructor.
