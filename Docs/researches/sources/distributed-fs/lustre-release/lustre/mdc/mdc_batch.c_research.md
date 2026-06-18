<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_batch.c -->
# sources/distributed-fs/lustre-release/lustre/mdc/mdc_batch.c

## Purpose
`mdc_batch.c` implements client-side packing and interpretation for batched metadata getattr updates. It lets llite statahead aggregate many getattr intent requests into batch RPCs while preserving LDLM lock enqueue semantics and callback delivery.

## Important APIs, Types, And Functions
Public entry point is `mdc_batch_add()`. Internal helpers include `mdc_ldlm_lock_pack()`, `mdc_batch_getattr_pack()`, `mdc_batch_getattr_interpret()`, and opcode dispatch tables `mdc_update_packers[]` and `mdc_update_interpreters[]` indexed by `MD_OP_GETATTR`.

## Control Flow
`mdc_batch_add()` validates the metadata opcode, allocates a sub-request capsule, and delegates to `cli_batch_add()`. Packing initializes an `RQF_BUT_GETATTR` subrequest, sizes the name and optional security-context-name field, writes the LDLM intent, calls `mdc_getattr_pack()`, creates and packs an LDLM inodebits lock request with lookup/update policy, declares expected reply fields for layout, ACL, default LMV, security context, and encryption context, and marks the subrequest opcode `BUT_GETATTR`. Interpretation rebuilds the reply capsule, finalizes LDLM enqueue, normalizes lock reply status, calls `mdc_finish_enqueue()`, then invokes the original item callback.

## State And Persistence
Per-item state is carried in `struct md_op_item`: op data, lookup intent, enqueue info, lock flags/handle, callback, and allocated sub-pill. Batch-level state is in `struct batch_update_head` and lower `lu_batch`; this file does not persist state beyond request completion.

## Dependencies And Integration Points
It integrates with MDC getattr packing, LDLM client enqueue/finish, batch update infrastructure, security context name forwarding, encryption-context fetching for encrypted connections, ACL maximum sizing, DOM glimpse callback setup, and llite statahead's `sa_getattr()` batching path.

## Risks And Edge Cases
Subrequest size is checked against remaining batch space and returns `-E2BIG` when too large. Unsupported opcodes return `-EFAULT`. The glimpse callback is installed before enqueue to avoid Data-on-MDT races. Security and encryption reply sizing must match server capabilities and intent operation bits.

## Test Signals
Test batched statahead getattr with and without security/encryption context requests, batch full `-E2BIG`, unsupported opcodes, LDLM enqueue failures, callback error propagation, DOM glimpse callback behavior, ACL/default-MEA reply sizing, and mixed batch/non-batch statahead operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_batch.c -->
