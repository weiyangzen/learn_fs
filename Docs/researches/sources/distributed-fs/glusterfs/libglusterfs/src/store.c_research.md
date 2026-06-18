# sources/distributed-fs/glusterfs/libglusterfs/src/store.c

## Purpose

`store.c` implements simple durable key/value store-file helpers for Gluster management state. It creates directories and store handles, writes `key=value` lines, iterates and retrieves values, performs temp-file fsync/rename publishing, and provides local advisory locking around store files.

## Important APIs, Types, and Functions

Key APIs include `gf_store_mkdir()`, `gf_store_handle_new()`, `gf_store_handle_retrieve()`, `gf_store_handle_create_on_absence()`, `gf_store_handle_destroy()`, `gf_store_mkstemp()`, `gf_store_rename_tmppath()`, `gf_store_unlink_tmppath()`, `gf_store_sync_direntry()`, `gf_store_save_value()`, `gf_store_save_items()`, `gf_store_retrieve_value()`, `gf_store_iter_new()`, `gf_store_iter_get_next()`, `gf_store_iter_get_matching()`, `gf_store_iter_destroy()`, `gf_store_lock()`, `gf_store_unlock()`, `gf_store_locked_local()`, and `gf_store_strerror()`. The file operates on `gf_store_handle_t`, `gf_store_iter_t`, and `gf_store_op_errno_t`.

## Control Flow and Data Flow

Handle creation opens or creates the store path, fsyncs the parent directory, stores a duplicated path, sets `locked` to `F_ULOCK`, and closes the probe fd. Write helpers duplicate the fd, wrap it with `fdopen("a+")`, append either a formatted key/value line or raw items, flush the stream, and close it. Retrieval opens or seeks the handle fd depending on lock state, wraps a duplicate stream, repeatedly calls `gf_store_read_and_tokenize()`, and duplicates the value for the requested key. Iterators open an independent read stream and duplicate key/value pairs for callers.

Atomic update flow uses `gf_store_mkstemp()` to open `<path>.tmp`, callers write to `tmp_fd`, `gf_store_rename_tmppath()` fsyncs the tmp file, renames it to the final path, fsyncs the containing directory, and closes `tmp_fd`. `gf_store_unlink_tmppath()` removes temporary files and closes the temp fd. Locking opens the path and uses `lockf(F_LOCK)` until `gf_store_unlock()`.

## State and Persistence Behavior

Persistent state is plain text `key=value` data under the handle path. Publishing a tmp file is intended to be crash-safe through file fsync, rename, and directory fsync. A lock keeps `handle->fd` open and changes `handle->locked`; unlocked reads open and close their own fd. Iterators own a `FILE *` until destroyed.

## Dependencies and Integration Points

The file depends on Gluster logging, store type declarations, xlator `THIS`, syscall wrappers, `mkdir_p()`, `gf_unlink()`, `dirname()`, `lockf()`, and memory helpers. It integrates with glusterd and other management code that persists small state files without a database.

## Risks and Edge Cases

Parsing treats blank lines specially but otherwise requires exactly `key=value` with a nonempty value; embedded newline and malformed lines are not supported. `gf_store_iter_get_matching()` uses prefix matching with `strncmp(key, tmp_key, strlen(key))`, so short keys can match longer keys. `gf_store_unlink_tmppath()` appears to map `gf_unlink()` success/failure in a non-obvious way and deserves regression coverage. Directory fsync after rename uses `tmppath` to derive the parent directory, which is equivalent only because temp and final paths share a directory. Lock state is process-local in the handle and must be paired correctly.

## Test Signals

Tests should cover durable create/write/rename/read cycles, tmp cleanup, parent directory fsync failure paths, locked versus unlocked retrieval, iterator EOF and malformed line errors, prefix matching behavior, concurrent lock attempts, file permission mode 0600, and fault injection around `fdopen()`, `fflush()`, `fsync()`, and `rename()`.
