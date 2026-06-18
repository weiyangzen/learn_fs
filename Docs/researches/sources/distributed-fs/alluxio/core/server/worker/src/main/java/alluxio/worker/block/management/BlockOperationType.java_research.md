# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockOperationType.java

Purpose: Enumerates operation categories emitted by block management tasks.

Important APIs: Enum values are `ALIGN_SWAP`, `PROMOTE_MOVE`, `SWAP_RESTORE_REMOVE`, `SWAP_RESTORE_FLUSH`, and `SWAP_RESTORE_BALANCE`.

Control flow: Tasks use these keys to add results to `BlockManagementTaskResult`.

State and persistence: Stateless enum.

Dependencies and integration: Ties result reporting to `AlignTask`, `PromoteTask`, and `SwapRestoreTask`.

Risks and test signals: Comments reference task classes without imports and do not affect runtime. Tests should assert task result buckets use the expected enum values.
