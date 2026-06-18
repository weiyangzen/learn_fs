# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeFileView.java

Purpose: read-only interface for file-specific inode metadata.

Important APIs and types: extends `InodeView` and adds persist job timing/id, replication durable/max/min, temporary UFS path, block ids, block size, file length, block container id, indexed block lookup, cacheable flag, and completed flag.

Control flow: concrete file inode implementations expose file fields through this interface. `Inode.wrap` uses it to create `InodeFile`, and file-master code uses it for block and persistence decisions.

State and persistence behavior: interface only. Exposed fields represent persisted inode-file metadata and persistence scheduling state.

Dependencies and integration points: depends on `BlockInfoException` and base inode view. Integrated with block master, file completion, async persistence, metadata sync, and client file-info generation.

Risks: implementations must define whether `getBlockIds` returns a defensive copy; the interface documentation says duplication is expected. Length is not accurate before file close, so callers must check `isCompleted` when correctness matters.

Test signals: implementation tests should verify block id lookup bounds, defensive block list behavior, completion state, persistence fields, replication fields, and journal/proto round trips.
