<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filerstore_wrapper_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filerstore_wrapper_test.go

## Purpose
Tests selected `FilerStoreWrapper` behavior around MIME normalization and context cancellation policy.

## Important APIs and Functions
`TestFilerStoreWrapperMimeNormalization`, `cancelledCtx`, `expiredCtx`, `TestFilerStoreWrapperWriteOpsRejectCancelledContext`, `TestFilerStoreWrapperWriteOpsSucceedWithActiveContext`, `TestFilerStoreWrapperReadOpsSucceedWithCancelledContext`, and `TestFilerStoreWrapperRollbackSucceedsWithCancelledContext`.

## Control Flow and State
Tests use the stub store, wrap it, run operation tables, and assert errors or persisted state. Write operation tests cover insert, insert-known-absent, update, delete, delete-one, delete-folder-children, transaction begin/commit, KV put/delete. Read tests verify find and KV get ignore canceled contexts.

## Persistence Behavior
In-memory stub store records entries and KV values, proving wrapper behavior before backend persistence.

## Dependencies and Integration Points
Uses `NewFilerStoreWrapper`, `Entry`, stub store, context cancellation/deadline, and testify assertions. It codifies the wrapper's policy used by all filer metadata operations.

## Risks
Does not cover path-specific stores, prefix fallback, bucket callbacks, hard-link hydration/deletion, or metrics. `TestFilerStoreWrapperWriteOpsSucceedWithActiveContext` reuses one path across operations in a way that depends on forgiving stub semantics.

## Test Signals
Strong signal for cancellation contracts and MIME normalization: files strip `application/octet-stream`, directories keep it, writes reject already-bad contexts, reads and rollback remain cleanup-friendly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filerstore_wrapper_test.go -->
