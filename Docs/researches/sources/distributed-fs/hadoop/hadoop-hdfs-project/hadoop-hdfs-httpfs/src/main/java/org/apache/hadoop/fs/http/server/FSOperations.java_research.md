<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/FSOperations.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/FSOperations.java

## Purpose
`FSOperations` is the executor library behind `HttpFSServer`: each nested class adapts one HttpFS/WebHDFS operation into a `FileSystemAccess.FileSystemExecutor<T>` that runs against an authenticated Hadoop `FileSystem`. It also owns the JSON wire-shape helpers for file status, directory listings, ACLs, checksums, xattrs, quota/content summaries, storage policies, block locations, fs status, snapshot data, and erasure-coding responses.

## Important APIs, Types, And Functions
The file is a final utility class with a configurable static `bufferSize` set by `setBufferSize(Configuration)`. Core helpers include `toJson(FileStatus)`, `toJson(FileStatus[], boolean)`, `toJson(FileSystem.DirectoryEntries, boolean)`, `aclStatusToJSON`, `fileChecksumToJSON`, `xAttrsToJSON`, `contentSummaryToJSON`, `quotaUsageToJSON`, `storagePoliciesToJSON`, and `copyBytes`. Nested executors cover create, append, concat, truncate, delete, open, rename, mkdirs, status/listing, batched listing, checksum, content/quota, ACL mutation and lookup, ownership/permission/times/replication, xattr mutation and lookup, trash roots, storage policies, snapshots, block locations, fs status, access checks, and erasure-coding policy/codecs.

## Control Flow
`HttpFSServer` constructs the relevant executor, then `FileSystemAccessService.execute` supplies a per-user `FileSystem` and invokes `execute(FileSystem)`. Most executors are thin one-method wrappers over Hadoop `FileSystem` calls. `FSCreate` and `FSAppend` stream request bodies through `copyBytes`, close both streams, and increment bytes-written metrics. `FSOpen` returns an `InputStream`; the servlet entity owns byte accounting. HDFS-only operations check `fs instanceof DistributedFileSystem` and throw `UnsupportedOperationException` otherwise.

## State And Persistence
State is intentionally transient: each executor stores only parsed constructor arguments such as `Path`, permissions, flags, names, offsets, and lengths. Persistent effects are delegated to HDFS or the configured filesystem. Static mutable state is limited to `bufferSize`, which affects streaming and open/create/append buffer allocation process-wide.

## Dependencies And Integration Points
The class depends heavily on Hadoop `FileSystem`, HDFS protocol classes, `JsonUtil`, `HttpFSFileSystem` JSON constants, ACL/xattr/permission types, and `HttpFSServerWebApp.get().getMetrics()`. It integrates with `FileSystemAccess` by implementing its executor contract and with client compatibility by preserving WebHDFS-compatible JSON key names.

## Risks
HDFS-only features fail at runtime when `fs.defaultFS` is not a `DistributedFileSystem`. `copyBytes` always closes both streams, so callers must not reuse request or output streams after execution. `xAttrNamesToJSON` stores a JSON string under the xattr names key rather than a raw array, which is compatibility-sensitive. `FSCreateSnapshot` uses `HOME_DIR_JSON` as the response key and strips backslashes from JSON, a brittle behavior worth regression testing. `FSSatisyStoragePolicy` contains a misspelled class name but maps to a real operation.

## Test Signals
Useful tests exercise JSON output compatibility for status/listing/quota/xattrs/storage policy, stream close and byte metrics for create/append/open, access-mode behavior via `HttpFSServer`, HDFS-only operation failure on a non-DFS `FileSystem`, and default replication/block-size/umask handling in `FSCreate` and `FSMkdirs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/FSOperations.java -->
