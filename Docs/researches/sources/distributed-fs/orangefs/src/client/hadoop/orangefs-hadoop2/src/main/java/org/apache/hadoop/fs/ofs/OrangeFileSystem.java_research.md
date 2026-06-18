<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystem.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystem.java

## Purpose

`OrangeFileSystem` is the primary Hadoop 2 `FileSystem` adapter for OrangeFS. It translates Hadoop `Path`, stream, permission, status, mkdir, delete, rename, and local-copy operations into OrangeFS JNI calls through the singleton `org.orangefs.usrint.Orange` facade.

## Important APIs, Types, and Functions

Important overridden APIs include `initialize`, `create`, deprecated `createNonRecursive`, `append`, `open`, `delete`, `exists`, `getFileStatus`, `listStatus`, `mkdirs`, `rename`, `setPermission`, local-copy hooks, `getUri`, `getWorkingDirectory`, and `setWorkingDirectory`. Internal helpers `getOFSPathName`, `getParentPaths`, `makeAbsolute`, and `isDirectory` handle Hadoop-to-mounted-path translation and directory walking. The class uses `PVFS2POSIXJNIFlags`, `PVFS2STDIOJNIFlags`, `OrangeFileSystemInputStream`, `OrangeFileSystemOutputStream`, `Stat`, and `OrangeFileSystemLayout`.

## Control Flow

Construction grabs the Orange singleton and flag objects but leaves the instance uninitialized. `initialize` validates URI authority, reads `fs.ofs.file.buffer.size`, `fs.ofs.block.size`, `fs.ofs.file.layout`, `fs.ofs.systems`, and `fs.ofs.mntLocations`, matches the URI authority to a mount path, initializes Hadoop statistics/local FS, and sets the working directory. File creation optionally deletes existing files, creates missing parents, opens an OrangeFS output stream with configured buffer/block/layout overrides, then applies Hadoop permissions. Reads construct `OrangeFileSystemFSInputStream`; metadata calls use POSIX `stat`; directory listing uses stdio directory enumeration and per-entry status calls.

## State, Persistence, and Concurrency

The class keeps per-instance configuration state: URI, mount prefix, working directory, local filesystem, buffer size, block size, layout, Hadoop statistics, and initialization flag. Persistent data is in OrangeFS via POSIX calls; Hadoop metadata is reconstructed from `stat` results on demand. Methods are mostly unsynchronized except stream reads/seeks, so callers rely on Hadoop `FileSystem` usage patterns and OrangeFS/POSIX semantics for concurrent mutation.

## Dependencies and Integration Points

It depends on Hadoop Common 2.x APIs, the OrangeFS JNI jar/native library, mounted OrangeFS paths, `core-site.xml` authority-to-mount configuration, and OrangeFS server/client processes. It integrates with MapReduce/YARN through `fs.ofs.impl` and with Hadoop statistics by incrementing read/write operation counters.

## Risks and Test Signals

Important risks are authority/mount mismatches, null-return-to-`null` behavior in `listStatus` where Hadoop often expects exceptions, `createNonRecursive` parent handling, hard-coded replication value `0`, sticky-bit removal in `setPermission`, and path translation through a local mount rather than pure URI access. Tests should cover initialization errors, multiple authorities, mkdir parent creation, overwrite behavior, permissions/umask, delete recursion, listStatus on files/directories/missing paths, working-directory relative paths, and live read/write through a mounted OrangeFS server.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystem.java -->
