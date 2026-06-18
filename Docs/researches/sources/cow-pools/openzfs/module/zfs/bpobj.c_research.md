# File Research: sources/cow-pools/openzfs/module/zfs/bpobj.c

## Scope

Implements persistent block-pointer objects used to store lists of block pointers and nested sub-objects, including allocation, freeing, open/close, iteration with optional removal, enqueueing block pointers/subobjects, prefetching, and space accounting.

## APIs And Behavior

- `bpobj_alloc_empty()`/`bpobj_decr_empty()` manage the shared empty bpobj feature object and its feature refcount.
- `bpobj_alloc()` chooses the on-disk bonus size based on pool version/features and allocates a `DMU_OT_BPOBJ`; `bpobj_free()` recursively frees nested subobjects and the bpobj object.
- `bpobj_open()`, `bpobj_close()`, `bpobj_is_open()`, and `bpobj_is_empty()` manage in-memory handles and detect supported bonus fields (`comp`, `subobj`, `freed`).
- `bpobj_iterate()` removes visited entries and updates accounting; `bpobj_iterate_nofree()` walks without mutation; `livelist_bpobj_iterate_from_nofree()` walks from a given index for livelists.
- The internal iterator avoids recursive C stack use by maintaining an explicit stack of `bpobj_info_t`, visiting direct block pointers, then nested subobjects from deepest to shallowest.
- `bpobj_enqueue_subobj()` adds a subobject to a parent, flattening small subobject lists and/or block-pointer arrays into the parent when possible to reduce future traversal depth.
- `bpobj_prefetch_subobj()` prefetches the metadata that `bpobj_enqueue_subobj()` is likely to touch.
- `bpobj_enqueue()` stores a sanitized block pointer, records whether it represents a free, updates counts and byte/compressed/uncompressed accounting, and caches the current data dbuf.
- `bpobj_space()` and `bpobj_space_range()` return stored or iterated space accounting; `bplist_append_cb()` appends iterated block pointers to a `bplist`.

## State And Dependencies

Persistent state lives in the bpobj data object, bonus `bpobj_phys_t`, optional subobject array object, and stored block-pointer array. In-memory state includes `bpobj_t` locks, cached dbufs, feature capability booleans, and explicit iterator stack nodes. Dependencies include DMU object/buf APIs, ZAP pool directory entries, SPA feature flags, `bp_get_dsize[_sync]`, dsl pool sync-context checks, and bplist callbacks.

## Risks And Invariants

Space accounting must propagate through parent subobjects when freeing nested entries. Iteration with `free=true` assumes dirty bonus buffers and transactional context; early callback errors leave entries unremoved. `bpobj_enqueue()` intentionally strips embedded payload/checksum/fill details for compression while preserving fields needed for accounting and traversal. The shared empty bpobj must never be freed as a normal bpobj.
