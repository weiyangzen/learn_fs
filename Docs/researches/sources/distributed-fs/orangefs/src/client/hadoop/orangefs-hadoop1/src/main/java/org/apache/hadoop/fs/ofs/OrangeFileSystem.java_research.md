<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystem.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystem.java

## Purpose
Implements a Hadoop 1 `FileSystem` adapter for OrangeFS. It maps `ofs://authority/path` Hadoop operations to OrangeFS JNI POSIX/stdio operations under a configured local OrangeFS mount.

## Important APIs, Types, And Functions
The class extends `FileSystem` and overrides `initialize`, `getUri`, `getWorkingDirectory`, `setWorkingDirectory`, `makeAbsolute`, `open`, `create`, `append`, `delete`, `exists`, `getFileStatus`, `listStatus`, `mkdirs`, `rename`, `setPermission`, local-copy helpers, and local-output helpers. State includes singleton `Orange`, POSIX/stdio flags, configured buffer/block size, file layout, URI, selected mount path, working directory, local filesystem, Hadoop statistics, and initialization guard.

## Control Flow
`initialize` validates URI/config, reads `fs.ofs.systems` and `fs.ofs.mntLocations`, matches URI authority to a mount, configures buffer/block/layout defaults, initializes local FS and working directory, then calls `super.initialize`. Path operations call `getOFSPathName`, which prepends `ofsMount` to the absolute Hadoop path. `create` handles overwrite and parent creation before constructing `OrangeFileSystemOutputStream` and setting permissions. `delete` chooses recursive stdio directory deletion or POSIX unlink. `listStatus` stats the path, returns a singleton for files, or enumerates directory entries and stats each child.

## State And Persistence
Persists filesystem changes through JNI: file creation, appends, deletes, mkdirs, chmod, rename, and directory listings. Hadoop operation statistics are incremented for read/write calls. Working directory is in-memory per instance.

## Dependencies And Integration Points
Depends on Hadoop 1 APIs, `org.orangefs.usrint` JNI classes (`Orange`, `Stat`, stream wrappers, layout enum), and configuration keys `fs.ofs.systems`, `fs.ofs.mntLocations`, `fs.ofs.file.buffer.size`, `fs.ofs.block.size`, and `fs.ofs.file.layout`.

## Risks And Test Signals
Risks include Hadoop 1 deprecated API behavior, returning `null` from `listStatus` on errors, `delete(Path)` deprecated overload always returning false, block replication hard-coded to zero, sticky bit stripped in permissions, parent path handling based on string split, no atomic rename fallback, and reliance on local mount paths matching URI authorities. Test signals are Hadoop contract tests for create/open/append/delete/list/mkdir/rename/permissions, multiple authority mappings, relative working-directory paths, local copy helpers, buffer/layout property overrides, and JNI error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystem.java -->
