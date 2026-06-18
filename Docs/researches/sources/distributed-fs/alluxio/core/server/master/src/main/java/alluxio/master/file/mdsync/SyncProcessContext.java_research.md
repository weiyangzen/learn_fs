# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/SyncProcessContext.java

Purpose: per-load metadata sync processing context. It wraps journal/RPC context state, descendant type, common TTL options, concurrent-modification policy, task info, load result, operation metrics, and absent-cache updates.

Important APIs and types: main getters expose descendant type, recursive status, metadata sync RPC context, metadata sync journal context, common options, concurrent-modification flag, and task info. Mutators record directories for direct-children-loaded and absent-cache updates, report operation success, and report failure reasons. Nested `MetadataSyncRpcContext` narrows journal context type, and `Builder` constructs the wrapped journal context.

Control flow: `DefaultSyncProcess.performSync` builds this context around a non-merging journal RPC context. The builder wraps the base journal context in `MetadataSyncMergeJournalContext` with a `FileSystemJournalEntryMerger`, so many inode updates are merged and submitted asynchronously rather than hard-flushed one by one.

State and persistence behavior: owns no durable state, but mediates durable journal writes through `MetadataSyncMergeJournalContext`. On close it closes both metadata-sync and base RPC contexts. Recorded absent-cache directories are applied to `UfsAbsentPathCache` after processing.

Dependencies and integration points: integrates `RpcContext`, `BlockDeletionContext`, journal context types, `OperationContext`, `TaskInfo`, `TaskStats`, `SyncOperation`, `SyncFailReason`, `UfsAbsentPathCache`, and `DefaultSyncProcess`.

Risks: double context wrapping must be closed correctly to avoid losing or prematurely flushing journals. The builder asserts the base context is not already a `FileSystemMergeJournalContext`. Concurrent modification policy defaults to allowed, which affects whether races are skipped or fail the sync.

Test signals: tests should cover journal context wrapping, close behavior, operation counter/report updates, failure reason recording, absent-cache directory updates, and allow-modification behavior.
