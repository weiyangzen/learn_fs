# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsFileStatus.java

## Purpose
`HdfsFileStatus` is the HDFS-specific metadata interface for filesystem entities. It extends writable, comparable, serializable, and validation contracts while exposing inode ID, local-name bytes, symlink bytes, encryption info, EC policy, storage policy, child count, namespace, and FileStatus-like methods.

## APIs and Control Flow
The nested `Builder` collects file status fields and decides whether to build `HdfsNamedFileStatus` or `HdfsLocatedFileStatus`: no locations and not directory/symlink yields the named variant; otherwise it uses the located variant for compatibility. Default methods convert local bytes to strings, build full paths, and qualify status paths. Static `convert` methods map HDFS flags into `FsPermissionExtension` and `FileStatus.AttrFlags`.

## State, Dependencies, and Integration
Implementations store local names as Java UTF-8 byte arrays until qualified by a parent path. The interface integrates with `FileStatus`, `LocatedFileStatus`, `DFSUtilClient`, encryption metadata, EC policies, and listing/status RPCs.

## Risks and Test Signals
Builder defaults are explicitly compatibility-sensitive. The builder defensively copies path and symlink arrays, but downstream implementations return raw arrays. Tests should cover variant selection, permission/flag conversion, default permissions for files/dirs/symlinks, path qualification, namespace fields, and compatibility with `FsPermissionExtension`.
