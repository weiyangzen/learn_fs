# sources/distributed-fs/ceph-client/kernel/liveupdate/luo_file.c

## Purpose
`luo_file.c` implements LUO's preserved file descriptor lifecycle. It lets sessions preserve user file descriptors with type-specific registered handlers, freeze and serialize them before kexec, deserialize them in the next kernel, retrieve replacement file descriptors by token, and finish cleanup after userspace has reattached.

## Important APIs, Types, and Functions
Global registries are `luo_file_handler_list` and xarray `luo_preserved_files`. Internal `struct luo_file` tracks handler, `struct file`, serialized data, runtime private data, retrieve status, mutex, list node, and user token. Constants `LUO_FILE_PGCNT` and `LUO_FILE_MAX` size the preserved serialization array.

Core APIs are `luo_preserve_file()`, `luo_file_unpreserve_files()`, `luo_file_freeze()`, `luo_file_unfreeze()`, `luo_retrieve_file()`, `luo_file_finish()`, `luo_file_deserialize()`, `luo_file_set_init()`, and `luo_file_set_destroy()`. Registration exports are `liveupdate_register_file_handler()` and `liveupdate_unregister_file_handler()`.

## Control Flow
Preservation validates unique token and capacity, gets the user file via `fget()`, allocates preserved serialization memory if needed, finds a registered handler whose `can_preserve()` accepts the file, takes the handler module reference, inserts the file ID into the global xarray to prevent duplicate preservation, preserves dependent FLBs, allocates `struct luo_file`, calls handler `.preserve()`, stores returned serialized/private handles, and appends the file to the session file set.

Abort-before-reboot cleanup walks files in reverse preservation order, calls handler `.unpreserve()`, decrements FLB references, drops module references, erases xarray entries, drops file references, destroys mutexes, and frees serialization memory when empty.

Freeze walks files in FIFO order. Each file optionally calls handler `.freeze()` and updates `serialized_data`, then writes compatible string, serialized data, and token into the preserved array. If a freeze fails, previously frozen files are unfrozen and serialized memory is cleared. Unfreeze can also roll back all files after a reboot abort.

Deserialization maps the preserved file array, finds handlers by compatible string, takes module references, allocates `struct luo_file` objects with `file = NULL`, and stores token/data for later retrieval. Retrieval by token is idempotent after success, permanently returns the saved error after a failed retrieve attempt, calls handler `.retrieve()` on first success, takes LUO's ownership reference, and tracks the file in the xarray. Finish first checks every file's optional `.can_finish()`, then runs `.finish()`, releases FLBs/module refs/files, frees entries, and calls `kho_restore_free()` on the serialized array.

## State and Persistence Behavior
Per-file persistent state is serialized into `struct luo_file_ser` entries in KHO-preserved memory: handler compatible string, user token, and handler-provided opaque data. Runtime-only state includes `private_data`, file references, handler module references, xarray duplicate tracking, retrieve status, and mutexes. Failure policy after deserialization is intentionally leak-and-reboot because partial hardware/file restore cannot be safely undone.

## Dependencies and Integration Points
It depends on liveupdate handler/FLB public APIs, KHO preserved allocations, session-owned `struct luo_file_set`, xarray, module refcounting, file descriptor APIs, and `luo_register_rwlock`. Handlers for memfd, vfio, iommufd, or other subsystems plug in through `struct liveupdate_file_handler`.

## Risks and Test Signals
File IDs from handler `get_id()` must uniquely identify resources or duplicate preservation can slip through. Handler callbacks must maintain their own locking and serialized-data lifetime. Freeze rollback must unfreeze exactly the already frozen prefix. Retrieval records first failure permanently, which may surprise retry logic. Tests should cover duplicate tokens, duplicate file IDs, handler registration/unregistration, preserve error injection at every step, FLB rollback, freeze/unfreeze ordering, deserialize with missing handler, idempotent retrieve success, retrieve failure persistence, finish `-EBUSY`, and release paths for outgoing and incoming sessions.
