# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeFile.java

Purpose: read-only forwarding wrapper for file-specific inode view behavior.

Important APIs and types: extends `Inode` and implements `InodeFileView`. Delegates persist job id, should-persist time, replication durable/max/min, temporary UFS path, block ids, block size, length, block container id, block id by index, cacheable flag, and completed flag.

Control flow: created by `Inode.wrap` when the delegate is a file view. Callers access file-only metadata through `asFile` or direct file wrapper references.

State and persistence behavior: no owned persistence. Delegated fields reflect persisted inode-file metadata and runtime persistence state.

Dependencies and integration points: depends on `InodeFileView`, base `Inode`, and `BlockInfoException`. Used by metadata sync to skip non-completed/non-persisted files and by file master/block metadata paths.

Risks: wrapper reflects delegate mutations and does not snapshot block id lists unless the delegate does. Construction assumes a valid file view.

Test signals: tests should cover delegated file fields, block id error propagation, wrapping through `Inode.wrap`, and base `asFile` validation.
