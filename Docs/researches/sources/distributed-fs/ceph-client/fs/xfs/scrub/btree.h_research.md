# sources/distributed-fs/ceph-client/fs/xfs/scrub/btree.h

Purpose: Declares the common btree scrub interface used by XFS metadata scrubbers to walk a btree and validate generic structural invariants while allowing the caller to check records.

Important APIs, types, and functions: Exposes `xchk_btree_process_error()`, `xchk_btree_xref_process_error()`, `xchk_btree_set_corrupt()`, `xchk_btree_set_preen()`, `xchk_btree_xref_set_corrupt()`, and `xchk_btree()`. Defines callback type `xchk_btree_rec_fn`, `struct xchk_btree_key` for per-level last-key tracking, and `struct xchk_btree` for per-walk state. `xchk_btree_sizeof()` computes allocation size for `lastkey[]`.

Control flow: Callers initialize a normal `xfs_btree_cur` and invoke `xchk_btree()` with owner info, private callback data, and a record scrub function. The walker controls traversal and passes each leaf record to the callback via `struct xchk_btree`.

State and persistence: `struct xchk_btree` stores transient traversal state: scrub context, cursor, callback, owner information, private pointer, last leaf record, deferred owner checks, and last key per internal level. No persistent metadata layout is defined here.

Dependencies and integration points: Included by btree-specific scrubbers and by `btree.c`. It depends on XFS btree cursor types, owner info, scrub context, list handling, and kernel flexible-array allocation helpers.

Risks and test signals: The main ABI risk is that `lastkey[]` must remain last and be sized with `xchk_btree_sizeof(nlevels)`; callers that pass invalid cursors or levels can produce bad allocations or traversal state. Test by building scrubbers with one-level btrees, many-level btrees, and callback-private data under KASAN/UBSAN-style instrumentation.
