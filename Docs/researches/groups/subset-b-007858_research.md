# subset-b-007858 grouped research

This grouped report covers OrangeFS DBPF/Trove storage files in `sources/distributed-fs/orangefs/src/io/trove/trove-dbpf`. Each section is source-tree aligned and is intended to be split into its corresponding `Docs/researches/<source_path>_research.md` file.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-alt-aio.c -->
# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-alt-aio.c

## Purpose
`dbpf-alt-aio.c` provides a pthread-backed replacement for the subset of POSIX AIO that DBPF needs for bytestream list I/O. It exists for configurations where real AIO is missing, unreliable, or replaced by OrangeFS's alternate path. The file wires this fallback into a `TROVE_bstream_ops` table named `alt_aio_bstream_ops`.

## Important APIs, types, and functions
The local `struct alt_aio_item` wraps one `struct aiocb`, the shared completion `sigevent`, master-thread metadata, and the thread id array. `alt_lio_listio()` is the only meaningful AIO operation: it spawns one thread per list entry, sets `__error_code` to `EINPROGRESS` when available, and either joins all threads for `LIO_WAIT` or makes the last worker the detached master for `LIO_NOWAIT`. `alt_lio_thread()` performs `pread()` or `pwrite()` according to `aio_lio_opcode`, stores optional libc-private `aiocb` error/return fields, and has the master join siblings before invoking `sigev_notify_function`. `alt_aio_bstream_read_list()` and `alt_aio_bstream_write_list()` delegate to `dbpf_bstream_rw_list()` with the alternate `dbpf_aio_ops`.

## Control flow and state
For `LIO_NOWAIT`, all non-master workers are joinable and the final worker is detached, joins earlier threads, frees the shared `tids` array, and triggers the bstream progress callback. For `LIO_WAIT`, `alt_lio_listio()` joins all workers before returning. Standalone `aio_read`, `aio_write`, `aio_cancel`, `aio_suspend`, and `aio_fsync` are stubs returning `-1`/`ENOSYS`.

## Persistence and integration
The file does not persist state directly. It integrates with `dbpf-bstream.c` through `struct dbpf_aio_ops` and `dbpf_bstream_rw_list()`, so persistence effects are the same as buffered bstream reads/writes: bytestream file I/O plus metadata updates in dspace after writes.

## Dependencies
It depends on pthreads, `pread`/`pwrite`, `aio.h` layout compatibility, `quicklist.h`, `dbpf.h`, `dbpf-alt-aio.h`, and OrangeFS gossip/debug infrastructure.

## Risks and test signals
The implementation relies on nonportable `struct aiocb` internals guarded by `HAVE_AIOCB_ERROR_CODE` and `HAVE_AIOCB_RETURN_VALUE`; without them, error and return reporting degrade to zero. Failure paths can leak already allocated `tmp_item` objects if allocation fails after earlier threads were spawned in `LIO_NOWAIT`. Tests should cover mixed read/write list conversion through `alt_aio_bstream_ops`, callback firing exactly once, short read/write return accounting, `LIO_WAIT` behavior, thread-create failure cleanup, and operation with libc configurations that do not expose private aiocb fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-alt-aio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-alt-aio.h -->
# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-alt-aio.h

## Purpose
`dbpf-alt-aio.h` is the private include surface for the alternate AIO implementation. It centralizes system and OrangeFS headers needed by `dbpf-alt-aio.c`.

## Important APIs, types, and functions
The header exports no functions of its own. Its value is dependency aggregation: `trove-internal.h`, POSIX file headers, `assert.h`, `errno.h`, `gossip.h`, `pvfs2-debug.h`, `trove.h`, `dbpf.h`, and `aio.h`.

## Control flow and state
There is no runtime control flow or state. The include guard `__DBPF_ALT_AIO_H__` prevents duplicate declarations and the `extern "C"` block allows C++ translation units to include the header.

## Persistence and integration
The header does not persist data. It integrates the alternate AIO source with the DBPF bytestream/AIO structures defined elsewhere, especially `struct dbpf_aio_ops` from `dbpf.h`.

## Dependencies
It assumes platform availability of POSIX file APIs and an `aio.h` implementation, even though the source file may replace much of POSIX AIO behavior with pthread-backed operations.

## Risks and test signals
Because it exposes only includes, risks are mostly build-configuration risks: missing `aio.h`, conflicting system declarations, or `malloc.h` portability. A compile matrix with and without `HAVE_MALLOC_H` and with different AIO-capability macros is the relevant test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-alt-aio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-attr-cache.c -->
# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-attr-cache.c

## Purpose
`dbpf-attr-cache.c` implements a bounded in-memory cache from `TROVE_object_ref` to `TROVE_ds_attributes`, with optional small keyval payload caching for configured key names. It reduces dspace database lookups and keeps bstream size metadata available to hot paths.

## Important APIs, types, and functions
The global `dbpf_attr_cache_mutex` is intentionally public; callers must hold it around cache operations. Configuration entry points are `dbpf_attr_cache_set_keywords()`, `dbpf_attr_cache_set_size()`, `dbpf_attr_cache_set_max_num_elems()`, and `dbpf_attr_cache_do_initialize()`. Lifecycle functions are `dbpf_attr_cache_initialize()` and `dbpf_attr_cache_finalize()`. Lookup/update functions include `dbpf_attr_cache_elem_lookup()`, `dbpf_attr_cache_ds_attr_fetch_cached_data()`, `dbpf_attr_cache_ds_attr_update_cached_data()`, `dbpf_attr_cache_ds_attr_update_cached_data_bsize()`, `dbpf_attr_cache_insert()`, and `dbpf_attr_cache_remove()`. Keyval helpers include `dbpf_attr_cache_elem_get_data_based_on_key()`, `dbpf_attr_cache_elem_set_data_based_on_key()`, and `dbpf_attr_cache_keyval_pair_fetch_cached_data()`.

## Control flow and state
Initialization validates the configured keyword count, initializes `s_key_to_attr_table`, seeds `rand()`, and resets `s_current_num_cache_elems`. Insertions replace existing entries or evict an arbitrary entry when the max element count is exceeded. Eviction starts at a random hash bucket and scans forward. Finalization drains every hash bucket, frees cached keyval payloads, finalizes the qhash, and frees the keyword string list.

## Persistence and integration
The cache is not persistent; it shadows the dspace DB. `dbpf-dspace.c` populates the cache on `dbpf_dspace_attr_get()` and updates it after `dbpf_dspace_attr_set()`. Bstream write paths remove or update entries when datafile sizes may change.

## Dependencies
It depends on `quickhash`, `quicklist`, `gen-locks`, `PINT_split_string_list()`, `PINT_free_string_list()`, `TROVE_ds_attributes`, and gossip debug categories.

## Risks and test signals
The implementation assumes external locking and does not lock internally, so misuse can race table mutation and free. `dbpf_attr_cache_elem_set_data_based_on_key()` asserts malloc success instead of returning `-TROVE_ENOMEM`. The header declares `dbpf_attr_cache_keyval_pair_update_cached_data()`, but this source does not define it; builds only pass if no code references that symbol or another file provides it. Tests should cover max-entry eviction, keyword count rejection, keyval payload overwrite/free, cache invalidation on dspace removal and bstream writes, and concurrent caller lock discipline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-attr-cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-attr-cache.h -->
# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-attr-cache.h

## Purpose
`dbpf-attr-cache.h` defines the DBPF attribute cache contract, cache element layouts, defaults, and setinfo-style configuration hooks.

## Important APIs, types, and functions
`DBPF_ATTR_CACHE_MAX_NUM_KEYVALS` caps cached keyval names at 8, `DBPF_ATTR_CACHE_DEFAULT_SIZE` defaults the hash table to 511 buckets, and `DBPF_ATTR_CACHE_DEFAULT_MAX_NUM_CACHE_ELEMS` defaults the hard element cap to 1024. `dbpf_keyval_pair_cache_elem_t` stores a key string, copied payload pointer, and payload length. `dbpf_attr_cache_elem_t` stores the qhash link, `TROVE_object_ref`, cached `TROVE_ds_attributes`, the fixed keyval pair array, and active keyval count. Public methods cover lifecycle, lookup, dspace attr updates/fetches, keyval pair lookup/fetch/update, insert/remove, and configuration.

## Control flow and state
The header describes state held by the implementation but owns no runtime state. Its comments establish return conventions: generally `0` on success and `-1` on failure, with some Trove-specific errors from buffer-size checks.

## Persistence and integration
The structures mirror persistent dspace records stored in DBPF's database and optional keyval entries but are volatile. Callers in dspace, bstream, and keyval code include this header to coordinate cache population and invalidation.

## Dependencies
It includes `pvfs2-internal.h`, `dbpf.h`, `trove-types.h`, and `quickhash.h`.

## Risks and test signals
The declaration for `dbpf_attr_cache_keyval_pair_update_cached_data()` has no definition in the paired source file, which is a link-time risk if callers use it. The fixed-size keyval array makes configuration validation important. Tests should compile all users, verify ABI assumptions for `TROVE_object_ref`, and check that configured keyword lists above eight are rejected without corrupting existing cache state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-attr-cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-bstream-aio.c -->
# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-bstream-aio.c

## Purpose
`dbpf-bstream-aio.c` converts Trove bytestream list I/O vectors into POSIX `struct aiocb` entries. It is the common adapter used by buffered POSIX AIO and alternate AIO paths.

## Important APIs, types, and functions
The single exported function is `dbpf_bstream_listio_convert()`. Inputs are memory extents, stream extents, current `bstream_listio_state`, an aiocb array, and an in/out aiocb count. The function emits at most the requested number of aiocbs and returns `1` when all input extents are consumed, `0` when more conversion remains.

## Control flow and state
The converter walks memory and stream arrays in lockstep, emitting an aiocb for the minimum remaining byte count between the current memory and stream extent. It updates `aio_fildes`, `aio_offset`, `aio_buf`, `aio_reqprio`, `aio_lio_opcode`, and disables per-entry notification with `SIGEV_NONE`. When the caller supplies `lio_state`, the function resumes from prior counters and stores partial progress back when the aiocb array fills before all extents are converted.

## Persistence and integration
The file has no persistence. It directly feeds `lio_listio()` calls in `dbpf-bstream.c` and the alternate AIO wrapper. Correct conversion determines which file offsets receive reads/writes and therefore affects bytestream data durability indirectly.

## Dependencies
It depends on `aio.h`, Trove size/offset types, DBPF operation structures, and `assert(fd > 0)`.

## Risks and test signals
The converter assumes non-empty memory and stream arrays and does not validate negative or zero counts. State-update logic around exhausted memory versus stream arrays is subtle and should be tested with unequal vector lengths, partial aiocb arrays, exact boundary equality, and repeated calls with a preserved `bstream_listio_state`. Boundary tests should verify that no bytes are skipped or duplicated and that the returned aiocb count matches emitted entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-bstream-aio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-bstream-direct.c -->
# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-bstream-direct.c

## Purpose
`dbpf-bstream-direct.c` implements the direct-I/O Trove bytestream backend. It bypasses buffered POSIX AIO and posts read/write work to the PINT manager thread pool, while handling direct-I/O alignment constraints, byte-range locking, metadata size updates, and operation cancellation.

## Important APIs, types, and functions
The exported ops table is `dbpf_bstream_direct_ops`. List operations are `dbpf_bstream_direct_read_list()` and `dbpf_bstream_direct_write_list()`, which allocate DBPF queued ops, acquire direct file descriptors from the open cache, and post service routines through `PINT_manager_id_post()`. `dbpf_bstream_direct_read_op_svc()` and `dbpf_bstream_direct_write_op_svc()` are the worker functions. Low-level helpers include `direct_aligned_read()`, `direct_read()`, `direct_locked_read()`, `direct_aligned_write()`, `direct_write()`, and `direct_locked_write()`. `dbpf_bstream_get_extents()` maps Trove memory/stream vectors into concrete stream extents. Grow serialization uses `grow_bstream_handle_table_init()`, `grow_bstream_handle_acquire_lock()`, and `grow_bstream_handle_release_lock()`.

## Control flow and state
Read and write requests become `struct dbpf_bstream_rw_list_op` payloads. Reads fetch current datafile size from dspace, derive extents, and perform locked direct reads. Writes derive extents, lazily initialize `grow_bstream_table`, acquire a per-handle grow lock before reading size, release it early if the write does not extend the file, perform locked direct writes, update `out_size_p`, and if the end-of-request exceeds recorded size, update dspace attributes and convert the queued op into a sync-coalesced `DSPACE_SETATTR`.

## Persistence and integration
Data persists through direct `pread`/`pwrite` against open-cache descriptors. Metadata persists through `dbpf_dspace_attr_get()` and `dbpf_dspace_attr_set()`, with sync coalescing through `dbpf_sync_coalesce()` when size changes. Resize updates attributes and truncates the direct-write file descriptor. Flush is a no-op complete because direct writes are treated as synchronous enough for this backend.

## Dependencies
This file depends on DBPF queued ops, open cache, dspace attr helpers, sync coalescing, `PINT_manager`, `fcntl` locks, `posix_memalign`, qhash, and direct-I/O flags such as `O_DIRECT` or `F_NOCACHE` when available.

## Risks and test signals
The alignment path is high risk: unaligned writes use aligned bounce buffers and read-modify-write edge blocks, so tests must cover front edge, tail edge, EOF extension, zero-fill beyond EOF, and already-aligned pass-through. `posix_memalign()` return values are not checked directly; only the pointer is tested. The direct header prototypes do not match the static function signatures in this file, and the functions are static, so the header appears stale. Grow-lock refcount/free logic should be stress-tested with concurrent extending writes to the same handle. Tests should also cover lazy reads before a bytestream exists, cancellation through `PINT_manager_cancel()`, size update coalescing, `ftruncate()` failure, and platforms without real direct-I/O flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-bstream-direct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-bstream-direct.h -->
# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-bstream-direct.h

## Purpose
`dbpf-bstream-direct.h` is intended to expose direct bytestream worker service routines to code that posts manager operations.

## Important APIs, types, and functions
It declares `dbpf_bstream_direct_read_op_svc(void *ptr, TROVE_hint *hints)` and `dbpf_bstream_direct_write_op_svc(void *ptr, TROVE_hint *hints)`.

## Control flow and state
The header owns no state. It includes `pvfs2-internal.h` and `trove-types.h`, and uses an include guard.

## Persistence and integration
The declarations correspond conceptually to the service routines that perform direct reads/writes and dspace size updates, but the paired source defines those routines as `static int ... (void *ptr, PVFS_hint hint)`. In the current file set, the header is not the source of truth for linkage.

## Dependencies
It depends on the Trove hint type and internal PVFS definitions.

## Risks and test signals
The signature and linkage mismatch is a maintenance risk: including this header in a translation unit that expects external definitions would fail to link or warn. A compile-all test with warnings enabled should catch the mismatch. If the intended design is private static callbacks only, this header may be obsolete or should be aligned with actual callback signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-bstream-direct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-bstream.c -->
# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-bstream.c

## Purpose
`dbpf-bstream.c` implements the buffered POSIX-AIO Trove bytestream backend. It queues list reads/writes, limits concurrent AIO globally, updates datafile size metadata after writes and resizes, supports flushing, and provides the `dbpf_bstream_ops` method table.

## Important APIs, types, and functions
Public bstream entry points include `dbpf_bstream_flush()`, `dbpf_bstream_rw_list()`, `dbpf_bstream_resize()`, `dbpf_pread()`, and `dbpf_pwrite()`. `dbpf_bstream_read_at()`, `dbpf_bstream_write_at()`, and `dbpf_bstream_validate()` return `-TROVE_ENOSYS`. Internal scheduling is handled by `issue_or_delay_io_operation()` and `start_delayed_ops_if_any()`. In threaded AIO mode, `aio_progress_notification()` drives completion and posts additional chunks; in non-threaded mode, `dbpf_bstream_rw_list_op_svc()` polls progress from the DBPF op queue.

## Control flow and state
`dbpf_bstream_rw_list()` validates the collection, allocates a queued op, records vector arrays and AIO ops, starts trace events, obtains a buffered open-cache descriptor, invalidates attr-cache entries on writes, and either queues service or immediately posts AIO depending on `__PVFS2_TROVE_AIO_THREADED__`. A fixed 64-entry aiocb array is reused as chunks are converted. Global state `s_dbpf_ios_in_progress` and `s_dbpf_io_ready_queue` enforce `TROVE_max_concurrent_io` and delay excess operations.

## Persistence and integration
Buffered I/O writes to bytestream files through AIO, flush uses `fdatasync()`, and resize uses `ftruncate()` followed by dspace attr update. Write completion may update `TROVE_ds_attributes.u.datafile.b_size`; if `TROVE_SYNC` requires metadata durability, the op is transformed into a `DSPACE_SETATTR` for sync coalescing.

## Dependencies
It depends on POSIX AIO, `dbpf-bstream-aio.c`, DBPF queued ops, open cache, attr cache, dspace attr helpers, sync coalescing, id generation, event tracing, and optional alternate AIO support.

## Risks and test signals
Concurrency accounting is subtle because `issue_or_delay_io_operation()` and `start_delayed_ops_if_any()` both adjust `s_dbpf_ios_in_progress`. Non-threaded read accounting treats reads differently because `aio_return()` may not report bytes with `SIGEV_NONE`. Cancellation can only cancel queued ops reliably; in-service AIO depends on backend `aio_cancel()`. Tests should cover concurrency limiting, delayed queue restart, write size extension, resize sync behavior, attr-cache invalidation, flush errors, cancellation states, and threaded versus non-threaded compile paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-bstream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-bstream.h -->
# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-bstream.h

## Purpose
`dbpf-bstream.h` exposes the bytestream AIO conversion helper used by DBPF bstream implementations.

## Important APIs, types, and functions
It declares `dbpf_bstream_listio_convert()`, taking file descriptor, operation type, memory vectors, stream vectors, aiocb storage, aiocb count, and optional `struct bstream_listio_state`.

## Control flow and state
The header owns no state, but the declared function mutates aiocb entries, the aiocb count, and optional conversion state. The `extern "C"` block supports C++ consumers.

## Persistence and integration
No persistence occurs here. The function declaration is the bridge between bytestream operation setup and the actual POSIX/alternate AIO posting paths.

## Dependencies
It includes `pvfs2-internal.h`, `aio.h`, `trove.h`, and `dbpf.h`, so users inherit POSIX AIO and DBPF type dependencies.

## Risks and test signals
The header exposes a low-level helper with many parallel arrays and counts; callers must validate non-empty vectors and consistent lengths. Tests should compile both buffered and alternate AIO paths and exercise incremental conversion state across multiple calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-bstream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-collection.c -->
# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-collection.c

## Purpose
`dbpf-collection.c` maintains the process-local registry of opened DBPF collections by collection id. Other DBPF modules use this registry to resolve a `TROVE_coll_id` into the active `struct dbpf_collection`.

## Important APIs, types, and functions
`dbpf_collection_register()` appends a collection to the global list. `dbpf_collection_find_registered()` performs a linear search by `coll_id`. `dbpf_collection_deregister()` removes a registered entry from the list.

## Control flow and state
The only state is `static struct dbpf_collection *root_coll_p`. Registration appends at tail. Lookup walks `next_p` until a matching `coll_id` or `NULL`. Deregistration special-cases the root entry and otherwise relinks the predecessor.

## Persistence and integration
The registry is volatile and does not persist collection metadata. It is a central integration point for bstream, dspace, and keyval entry points, which generally return `-TROVE_EINVAL` when lookup fails.

## Dependencies
It depends on DBPF collection layout from `dbpf.h` and Trove collection ids.

## Risks and test signals
There is no locking in this file, so collection lifecycle must be serialized externally. `dbpf_collection_deregister()` sets `root_coll_p = NULL` when removing the root even if the root has successors, which drops the rest of the list. Tests should cover registering multiple collections, removing head/middle/tail entries, lookup after deregistration, duplicate registration behavior, and concurrent lifecycle assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-collection.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-context.c -->
# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-context.c

## Purpose
`dbpf-context.c` implements Trove context lifecycle for DBPF. Contexts own completion queues used by DBPF operation testing and threaded completion paths.

## Important APIs, types, and functions
`dbpf_open_context()` allocates a free slot in `dbpf_completion_queue_array`, creates a queue, initializes its mutex, returns the context index, and initializes sync coalescing state with `dbpf_sync_context_init()`. `dbpf_close_context()` destroys the mutex, cleans up the queue, clears the slot, and calls `dbpf_sync_context_destroy()`. `dbpf_context_ops` exposes these functions to the Trove method table.

## Control flow and state
Global state includes `dbpf_completion_queue_array[TROVE_MAX_CONTEXTS]`, `dbpf_completion_queue_array_mutex[TROVE_MAX_CONTEXTS]`, and `dbpf_context_mutex` protecting allocation/free. Context ids are array indexes, selected by the first `NULL` queue slot.

## Persistence and integration
Contexts are runtime-only. They integrate directly with `dbpf-dspace.c` test/testsome/testcontext and with threaded DBPF completions that push completed operations into context-specific queues.

## Dependencies
It depends on DBPF op queues, sync coalescing, Trove context ops, and `gen_mutex`.

## Risks and test signals
If `dbpf_sync_context_init()` fails after a queue is allocated, the function returns the error without tearing down the queue slot, leaving a leaked/occupied context. `dbpf_close_context()` does not bounds-check `context_id`. Tests should cover maximum context exhaustion, sync init failure cleanup, close of unopened contexts, queue cleanup with pending operations, and repeated open/close cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-context.h -->
# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-context.h

## Purpose
`dbpf-context.h` declares DBPF context open/close entry points for the Trove context method implementation.

## Important APIs, types, and functions
It declares `dbpf_open_context(TROVE_coll_id, TROVE_context_id *)` and `dbpf_close_context(TROVE_coll_id, TROVE_context_id)`.

## Control flow and state
No state is defined in the header. It wraps declarations in `extern "C"` for C++ compatibility.

## Persistence and integration
Contexts are runtime-only completion domains. The header lets method-table setup and DBPF internals bind to the context implementation.

## Dependencies
It includes `pvfs2-internal.h` and `trove-types.h`.

## Risks and test signals
The declaration surface is small. Build tests should ensure context methods remain signature-compatible with `struct TROVE_context_ops`; runtime tests belong to `dbpf-context.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-db-bdb.c -->
# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-db-bdb.c

## Purpose
`dbpf-db-bdb.c` implements the `dbpf-db.h` key/value abstraction using Berkeley DB BTREE databases. It stores dspace attributes and keyval records behind a common API used by DBPF metadata code.

## Important APIs, types, and functions
`struct dbpf_db` wraps `DB *`; `struct dbpf_cursor` wraps `DBC *`. `dbpf_db_open()` creates and opens a BTREE database, applies comparison functions, cache size, mmap/NOMMAP flags, and `DB_THREAD`. The file implements get/put/putonce/delete, sync, cursor open/close/get/delete, and `db_error()` mapping BDB status values to Trove errors. `ds_attr_compare()` sorts handles descending, and `keyval_compare()` orders keyval database entries by handle, type, encoded key size, and key bytes.

## Control flow and state
Each operation builds `DBT` wrappers around caller-owned buffers. `dbpf_db_get()` and cursor get use `DB_DBT_USERMEM`; if BDB reports `DB_BUFFER_SMALL`, they allocate temporary storage, retry, copy up to the caller's original buffer length, and update `val->len` to the database value size.

## Persistence and integration
Persistence is Berkeley DB's on-disk BTREE file. `dbpf_db_sync()` calls `DB->sync()`. Dspace and keyval code rely on this backend for durable metadata and cursor iteration.

## Dependencies
It depends on `<db.h>`, `server-config.h`, DBPF keyval entry layout macros, and gossip logging.

## Risks and test signals
`dbpf_db_open()` returns raw `errno` instead of mapped negative Trove error when the initial wrapper malloc fails. Buffer-small retry copies only the caller's original length but advertises the full stored length, so callers must treat larger lengths as truncation. Comparator aborts on corrupt small keys. Tests should cover create/open existing DBs, mmap and NOMMAP config, duplicate putonce, cursor operations, undersized buffers, comparator ordering, and BDB error mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-db-bdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-db-lmdb.c -->
# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-db-lmdb.c

## Purpose
`dbpf-db-lmdb.c` implements the same DBPF key/value abstraction using LMDB environments and transactions. Each database name is an LMDB environment directory.

## Important APIs, types, and functions
`struct dbpf_db` holds `MDB_env *` and `MDB_dbi`; `struct dbpf_cursor` holds an `MDB_cursor *` and its owning `MDB_txn *`. `dbpf_db_open()` creates the environment, sets map size from server/global filesystem config, optionally creates the directory, opens with `MDB_MAPASYNC|MDB_WRITEMAP`, opens the DBI, and installs comparators. CRUD functions wrap each operation in a read-only or write transaction. Cursor functions keep a transaction open for iteration.

## Control flow and state
Reads begin a read-only transaction, call `mdb_get()`, commit, copy returned memory into caller buffers, and set `val->len`. Writes begin a write transaction, call `mdb_put()` or `mdb_del()`, and commit. `dbpf_db_cursor_get()` maps DBPF cursor constants to LMDB cursor operations and copies key/value bytes into caller buffers before updating lengths.

## Persistence and integration
LMDB persists through memory-mapped environments. `dbpf_db_sync()` calls `mdb_env_sync()`. `MDB_MAPASYNC|MDB_WRITEMAP` favors performance and makes explicit sync policy important for crash durability.

## Dependencies
It depends on `<lmdb.h>`, `server-config.h`, the external `filesystem_configuration_s *cfg_fs`, DBPF keyval entry layout macros, and gossip.

## Risks and test signals
The implementation copies `db_data.mv_size` bytes into `val->data` after using the caller's initial `val->len` only as a copy length in some cursor paths; no explicit buffer-size check is performed, unlike BDB's buffer-small handling. `mdb_txn_commit()` failure in open returns `db_error(errno)` instead of the LMDB return code. `create` requires `mkdir()` success and will error if the directory already exists. Tests should cover map-full behavior, configured map sizes, small caller buffers, cursor iteration/deletion, putonce duplicate errors, explicit sync, and crash-recovery expectations under `MDB_MAPASYNC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-db-lmdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-db.h -->
# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-db.h

## Purpose
`dbpf-db.h` defines the backend-neutral database abstraction used by DBPF metadata code. It lets DBPF compile against Berkeley DB, LMDB, or another backend with the same API.

## Important APIs, types, and functions
Opaque `dbpf_db` and `dbpf_cursor` hide backend details. `struct dbpf_data` is the shared key/value buffer descriptor. Comparison modes `DBPF_DB_COMPARE_DS_ATTR` and `DBPF_DB_COMPARE_KEYVAL` select key ordering. Cursor operation constants map to backend cursor positioning. The API includes open, close, sync, get, put, putonce, delete, cursor open/close/get/delete.

## Control flow and state
The header defines no state, but it establishes caller-owned buffer semantics: `dbpf_data.data` points to provided storage and `dbpf_data.len` carries size in and actual size out for reads/cursor reads.

## Persistence and integration
Backends persist dspace and keyval metadata. Dspace creation/removal/getattr/setattr and keyval iteration/write paths depend on these functions for durable metadata operations.

## Dependencies
The open call references `struct server_configuration_s`, so backend implementations can use server configuration such as cache size or LMDB map size.

## Risks and test signals
The abstraction does not precisely specify buffer-too-small behavior, and the BDB and LMDB implementations differ. Tests for any backend must validate error sign conventions, caller buffer ownership, cursor mutation of keys, duplicate-key behavior, sync semantics, and comparator consistency across backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-db.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-dspace.c -->
# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-dspace.c

## Purpose
`dbpf-dspace.c` implements DBPF dataspace operations for Trove: create, create-list, remove, remove-list, handle iteration, verify, getattr, getattr-list, setattr, cancel, and completion testing. It is the central metadata layer that connects handle allocation, DB persistence, attr caching, keyval cleanup, bstream cleanup, event tracing, and DBPF operation queues.

## Important APIs, types, and functions
The method table `dbpf_dspace_ops` exports all dspace operations. Creation uses `dbpf_dspace_create()`, `dbpf_dspace_create_op_svc()`, `dbpf_dspace_create_list()`, and `dbpf_dspace_create_list_op_svc()`. Removal uses `remove_one_handle()`, `dbpf_dspace_remove_op_svc()`, and `dbpf_dspace_remove_list_op_svc()`. Attribute helpers `dbpf_dspace_attr_get()` and `dbpf_dspace_attr_set()` are also used by bstream code. Completion paths are `dbpf_dspace_test()`, `dbpf_dspace_testsome()`, and `dbpf_dspace_testcontext()`. `PINT_dbpf_dspace_remove_keyval()` is a cursor deletion callback.

## Control flow and state
Most operations resolve the collection, initialize a queued-or-immediate `dbpf_op`, attach operation-specific payload, start events/perf counters, and call `dbpf_queue_or_service()`. Service functions perform DB work and return `DBPF_OP_COMPLETE`/`1` or negative Trove errors. Threaded builds wait on per-context completion queues and condition variables; non-threaded builds poll/service the queued operation directly. `organize_post_op_statistics()` updates metadata read/write counters after completion.

## Persistence and integration
Dspace records are stored in `coll_p->ds_db` keyed by handle with `TROVE_ds_attributes` as the value. Creation allocates handles and writes attributes, moving any stale bytestream file to a stranded-bstreams location before inserting the record. Removal deletes the dspace record, invalidates attr cache, removes open-cache/bstream state, deletes keyval entries through keyval iteration, syncs keyval DB when needed, and frees the handle. Setattr persists attributes and updates the attr cache. Getattr reads from cache first, then DB, then inserts into cache.

## Dependencies
It depends on handle management, DB abstraction, attr cache, keyval iteration, open cache, bstream method tables, sync/coalescing macros, DBPF thread/queue infrastructure, PINT performance counters, PINT events, and global method callbacks.

## Risks and test signals
This file has broad blast radius. `dbpf_dspace_create_list_op_svc()` passes `op_p->u.d_create.type` instead of `op_p->u.d_create_list.type`, which looks like a union-field bug. Error sign conventions vary between `dbpf_db_*()` positive Trove errors and negative returned service errors. Cache fast paths must preserve behavior identical to queued paths. Threaded completion paths assume valid context ids and non-empty completion queues. Tests should cover forced handles, range allocation failure rollback, stale bstream renaming, attr cache hit/miss behavior, getattr-list partial cache hits, remove cleanup of keyvals and bstreams, iterate position semantics, cancel delegation to bstream ops, threaded and non-threaded completion, and sync-on-remove/setattr behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-dspace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-keyval-pcache.c -->
# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-keyval-pcache.c

## Purpose
`dbpf-keyval-pcache.c` implements a small position-to-keyname cache for DBPF keyval iteration. It maps `(handle, TROVE_ds_position)` to the key name and length, reducing repeated database cursor work for keyval position lookups.

## Important APIs, types, and functions
`PINT_dbpf_keyval_pcache_initialize()` allocates the cache wrapper, initializes its mutex, creates a `PINT_tcache`, disables expiration, and sets a hard limit of 51200 entries. `PINT_dbpf_keyval_pcache_finalize()` destroys the tcache and mutex. `PINT_dbpf_keyval_pcache_lookup()` returns a cached key pointer and length. `PINT_dbpf_keyval_pcache_insert()` replaces any existing entry for the same handle/position and inserts a copied key name. Static helpers implement compare, hash, and payload free.

## Control flow and state
State is `PINT_dbpf_keyval_pcache`, containing a `PINT_tcache *` and mutex. Lookup and insert both lock around tcache access. The hash mixes high and low handle bits with the position and masks into a 1024-entry table. Entries store `keyname[PVFS_NAME_MAX]` and an integer length.

## Persistence and integration
The cache is volatile and mirrors keyval iteration state. It is initialized for collections in DBPF management code and passed into keyval iteration helpers, including dspace removal cleanup.

## Dependencies
It depends on `tcache`, `quickhash`, `gen-locks`, `TROVE_handle`, `TROVE_ds_position`, `PVFS_NAME_MAX`, and gossip debug logging.

## Risks and test signals
`PINT_dbpf_keyval_pcache_initialize()` leaks the wrapper if tcache initialization fails. `PINT_dbpf_keyval_pcache_insert()` does not validate `length <= PVFS_NAME_MAX`, so overlong key names can overflow `keyname`. `dbpf_keyval_pcache_hash()` casts the lookup key to `dbpf_keyval_pcache_entry` even though callers pass `dbpf_keyval_pcache_key`; current first fields match, but it is fragile. Tests should cover replacement, lookup miss/hit, hard-limit eviction, overlong key rejection expectation, finalize after partial init failure, and thread contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-keyval-pcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-keyval-pcache.h -->
# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-keyval-pcache.h

## Purpose
`dbpf-keyval-pcache.h` declares the keyval position-cache wrapper used by DBPF keyval iteration code.

## Important APIs, types, and functions
`PINT_dbpf_keyval_pcache` contains a `PINT_tcache *` and `gen_mutex_t`. The public API includes `PINT_dbpf_keyval_pcache_initialize()`, `PINT_dbpf_keyval_pcache_finalize()`, `PINT_dbpf_keyval_pcache_lookup()`, and `PINT_dbpf_keyval_pcache_insert()`.

## Control flow and state
The header defines the cache state layout but no behavior. It exposes a concrete struct rather than an opaque handle, so users can access internals if they include the header.

## Persistence and integration
The cache is runtime-only. It integrates with DBPF keyval iteration and collection management; dspace removal passes the cache into keyval cleanup iteration.

## Dependencies
It includes `pvfs2-internal.h`, `gen-locks.h`, `tcache.h`, and `trove.h`.

## Risks and test signals
Because the struct is public, ABI changes affect all users. The API does not document ownership/lifetime of the `keyname` pointer returned by lookup; callers must treat it as cache-owned and valid only until replacement/finalization. Tests should compile all users and verify lookup pointer lifetime assumptions through cache mutations and finalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-keyval-pcache.h -->
