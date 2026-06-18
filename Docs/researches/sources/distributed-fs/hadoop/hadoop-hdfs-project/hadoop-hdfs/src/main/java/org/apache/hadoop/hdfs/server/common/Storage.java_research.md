<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/Storage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/Storage.java

## Purpose

`Storage` is the abstract base for HDFS NameNode/DataNode local storage metadata management. It owns storage directories, layout constants, startup-state analysis, upgrade/rollback/checkpoint recovery, locking, formatting confirmation, and VERSION file writing.

## Important APIs and types

Major types are `StorageState`, `StorageDirType`, nested `StorageDirectory`, and `FormatConfirmable`. Directory APIs include iterators, `getFiles`, `addStorageDir`, duplicate checks, `writeAll`, and `unlockAll`. `StorageDirectory` exposes path helpers for `current`, `previous`, temp transition directories, `VERSION`, locking, `analyzeStorage`, `doRecover`, `clearDirectory`, and `hasSomeData`. Static helpers include `confirmFormat`, `checkVersionUpgradable`, `writeProperties`, `rename`, `nativeCopyFileUnbuffered`, `deleteDir`, `getBuildVersion`, and `getRegistrationID`.

## Control flow

Startup calls `analyzeStorage`, which handles provided storage as normal, creates missing directories only for format/hotswap, locks usable directories, checks old layout support, inspects `VERSION` and transition temp directories, and returns a `StorageState`. `doRecover` completes or rolls back interrupted transitions by renaming/deleting `previous.tmp`, `removed.tmp`, `finalized.tmp`, or `lastcheckpoint.tmp`. VERSION writes use `RandomAccessFile`, store properties, then truncate to the written position.

## State and persistence behavior

Persistent state is the storage directory tree and `VERSION` properties: layout version, storage type, namespace ID, cluster ID, and cTime. Runtime state includes a copy-on-write list of `StorageDirectory` objects and file locks. Shared directories skip locking.

## Dependencies and integration points

It integrates with `StorageInfo`, `NamespaceInfo`, NameNode/DataNode storage subclasses, `StorageLocation`, layout-version classes, native IO, filesystem permissions, upgrade/finalize/rollback flows, and format prompts.

## Risks and edge cases

Directory transition recovery is sensitive to exact temp-directory combinations. File locking may be unsupported or unreliable on NFS. Asynchronous deletion renames directories before background deletion, so failures leave `.tmp` cleanup work. `StorageDirectory` supports null roots for provided storage, so callers must handle null path helpers.

## Test signals

Tests should cover every `StorageState`, recovery rename/delete effects, format confirmation force/noninteractive/interactive paths, VERSION write truncation, lock acquisition failures, shared-directory locking bypass, duplicate storage detection, provided storage paths, and native copy validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/Storage.java -->
