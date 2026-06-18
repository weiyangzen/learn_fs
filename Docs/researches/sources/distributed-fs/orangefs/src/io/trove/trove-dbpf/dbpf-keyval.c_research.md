# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-keyval.c

## Purpose
Implements the DBPF backend's `TROVE_keyval_ops` table for OrangeFS metadata key/value records. It stores directory entries, object attributes, extended attributes, and per-handle count metadata in the collection keyval database using composite Berkeley-DB-style keys made from `(handle, type, key-bytes)`.

## Important APIs, Types, And Functions
The exported integration point is `dbpf_keyval_ops`, binding read, write, remove, remove-list, validate, iterate, iterate-keys, read-list, write-list, flush, and get-handle-info operations. Public-looking helpers exported through `dbpf.h` include `PINT_dbpf_keyval_iterate` and `PINT_dbpf_dspace_remove_keyval` callback integration. The major service routines are `dbpf_keyval_read_op_svc`, `dbpf_keyval_write_op_svc`, `dbpf_keyval_remove_op_svc`, list variants, `dbpf_keyval_iterate_op_svc`, `dbpf_keyval_iterate_keys_op_svc`, `dbpf_keyval_flush_op_svc`, and `dbpf_keyval_get_handle_info_op_svc`. Internal helpers manage cursor stepping, position-cache lookup/insert, deletion, and count metadata.

## Control Flow
Each API wrapper first finds the registered collection, initializes either a stack `dbpf_op` or heap `dbpf_queued_op_t` through `dbpf_op_init_queued_or_immediate`, fills the operation union, optionally starts a PINT event/perf counter, then calls `dbpf_queue_or_service`. Service functions construct `struct dbpf_keyval_db_entry` keys, dispatch to `dbpf_db_get`, `dbpf_db_put`, `dbpf_db_putonce`, `dbpf_db_del`, cursor APIs, or `dbpf_db_sync`, and return `DBPF_OP_COMPLETE`, success `1`, or negative TROVE errors. Iteration uses `SET_RANGE` to seek to the first matching `(handle,type)` key, skips the null count key, caches the last returned key by logical position, and falls back to linear stepping after restart/cache miss.

## State And Persistence
Persistent state is the collection's `keyval.db`. Key type selects directory entries (`DBPF_DIRECTORY_ENTRY_TYPE`), attributes/xattrs (`DBPF_ATTRIBUTE_TYPE`), or special count records (`DBPF_COUNT_TYPE`). The file also updates the in-memory attribute cache for non-binary keys, the keyval position cache for iterators, metadata perf counters, and a static `readdir_session` value embedded in iterator positions. `TROVE_KEYVAL_HANDLE_COUNT` maintains a count record that increments on no-overwrite creates and decrements on removes/iterate-remove.

## Dependencies And Integration Points
Depends on DBPF DB wrappers, op queueing, sync coalescing through the queue layer, `dbpf-attr-cache`, `dbpf-keyval-pcache`, `trove-internal`, PINT events, and perf counters. Directory-entry iteration can call `PINT_dbpf_dspace_remove_keyval`, connecting keyval cleanup to dataspace removal. The object/key layout must match the DB comparison function used when `keyval.db` is opened in `dbpf-mgmt.c`.

## Risks And Test Signals
Risks include fixed `DBPF_MAX_KEY_LENGTH` assumptions, `memcpy` with caller-supplied key lengths, partial list semantics that return success if any read succeeds, count-record underflow assertions, stale iterator positions after concurrent deletes, and a suspicious remove-list wrapper initializing the op as `KEYVAL_WRITE_LIST` while using the remove-list service. Tests should cover binary and string keys, no-overwrite/only-overwrite behavior, too-small read buffers and `read_sz`, list partial failures, iterate restart after server restart, iterate-remove count updates, attr-cache hits, and forced DB sync/flush behavior.
