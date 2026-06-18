# sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/src/thin-arbiter.c

## Purpose
Implements the `thin-arbiter` GlusterFS feature translator. Its behavior is intentionally narrow: it only permits `xattrop` and `fxattrop`, validates thin-arbiter source/pending xattr consistency against the child brick, and fails nearly all other filesystem operations with `EINVAL`.

## Important APIs, Types, and Functions
- `ta_prepare_fop()` allocates `ta_fop_t`, copies `loc` or refs `fd`, refs the incoming dict, builds `brick_xattr`, and stores it on `frame->local`.
- `ta_set_incoming_values()` creates zero-filled xattr buffers in `brick_xattr` matching incoming xattr lengths so the child `xattrop` can fetch current brick values.
- `ta_get_incoming_and_brick_values()` compares incoming values and brick values against zero-filled source buffers, setting `fop->on_disk[]`.
- `ta_verify_on_disk_source()` iterates returned brick xattrs and rejects cases where both tracked sources look on disk/nonzero.
- `ta_xattrop()` and `ta_fxattrop()` are the only passed-through operations. They first wind a child xattrop/fxattrop with `brick_xattr`, then on success wind the original xattrop/fxattrop.
- `TA_FAILED_FOP` and numerous `ta_*` fop stubs map unsupported operations to default failure callbacks with `EINVAL`.
- `mem_acct_init()`, `init()`, `reconfigure()`, `fini()`, `fops`, `cbks`, `options`, and `xlator_api` provide translator lifecycle and registration.

## Control Flow
`ta_xattrop()`/`ta_fxattrop()` allocate local state and issue a read-like child xattrop/fxattrop using `fop->brick_xattr`. `ta_get_xattrop_cbk()` receives the child dict, validates on-disk source state, and if valid winds the original xattrop/fxattrop to the child. `ta_set_xattrop_cbk()` finally unwinds the original caller and releases `ta_fop_t`.

All other registered fops immediately invoke `default_<fop>_failure_cbk()`. `init()` requires exactly one child and warns on dangling volume parents.

## State and Persistence
Per-call state lives in `ta_fop_t` on `frame->local`; it owns refs to `fd`, `loc`, incoming dict, and generated `brick_xattr`. Persistent data is the child brick's xattr state, especially thin-arbiter source/pending values. The translator has no private persistent configuration.

## Dependencies and Integration Points
Uses GlusterFS stack winding/unwinding, dict APIs, fd/loc refcounting, and xlator registration. It depends on `thin-arbiter.h` for state/macros and `thin-arbiter-mem-types.h` for allocation classes. It sits above one child translator and is integrated in AFR/thin-arbiter workflows via xattrop/fxattrop.

## Risks
- `ta_get_incoming_and_brick_values()` assumes at most two entries because `on_disk` has length two; unexpected dict sizes can exceed intended indexing.
- Failure-path errno conversion uses negative returns in several places and must remain consistent.
- Unsupported fops fail hard; placing this xlator in the wrong graph position will break normal file access.
- Correctness depends on exact xattr value lengths and zero-fill semantics.

## Test Signals
Useful tests should exercise accepted xattrop/fxattrop cases, both-source rejection, allocation failures, dict length mismatches, and unsupported fop failures. Integration tests should place thin-arbiter in a replica/thin-arbiter graph and validate that only source-state transitions pass.
