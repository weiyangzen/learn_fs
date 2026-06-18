<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystemUnderlying.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystemUnderlying.java

## Purpose

`OrangeFileSystemUnderlying` is a close sibling of `OrangeFileSystem` that exposes the same OrangeFS-backed Hadoop `FileSystem` behavior plus a constructor accepting `Configuration` and `URI`, and a `getFsStatus` method backed by POSIX `fstatfs`. It appears intended for lower-level or test access to the underlying filesystem implementation.

## Important APIs, Types, and Functions

It implements the same major operations as `OrangeFileSystem`: `initialize`, `create`, `append`, `open`, `delete`, `exists`, `getFileStatus`, `listStatus`, `mkdirs`, `rename`, `setPermission`, `copyFromLocalFile`, `copyToLocalFile`, and working-directory accessors. Additional notable APIs are `OrangeFileSystemUnderlying(Configuration, URI)` and `getFsStatus(Path)`. It uses `Orange`, `PVFS2POSIXJNIFlags`, `PVFS2STDIOJNIFlags`, `Stat`, `Statfs`, and OrangeFS stream classes.

## Control Flow

The parameterized constructor initializes immediately. `initialize` mirrors the primary adapter's authority-to-mount matching. File operations map Hadoop paths through `getOFSPathName` into the configured mount path, then call OrangeFS POSIX/stdio JNI methods. `getFsStatus` opens the path with `O_RDONLY`, calls `fstatfs`, and returns Hadoop `FsStatus` from capacity/used/remaining fields.

## State, Persistence, and Concurrency

State is per instance and equivalent to the main adapter: OrangeFS mount mapping, URI, layout, buffer/block settings, working directory, local filesystem, and statistics. Persistent state is entirely OrangeFS-side. The `getFsStatus` implementation opens a file descriptor but does not close it in the inspected code, so repeated calls can leak descriptors.

## Dependencies and Integration Points

It integrates the Hadoop filesystem API with the OrangeFS JNI layer and the same configuration files as the primary adapter. Tests or components that need `FsStatus` may use this class where `OrangeFileSystem` does not expose that override.

## Risks and Test Signals

In addition to the primary adapter risks, `getFsStatus` should be tested for descriptor cleanup and behavior on directories, missing paths, and permission errors. The simplified `create` path does not perform the same overwrite/parent validation as `OrangeFileSystem`, so compatibility tests should compare behavior between the two classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystemUnderlying.java -->
