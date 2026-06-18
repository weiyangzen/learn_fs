# subset-b-007666 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/osc_cache.c -->
# sources/distributed-fs/lustre-release/lustre/osc/osc_cache.c research

## Purpose
`osc_cache.c` is the OSC client-side cache and RPC batching engine. It turns CLIO page submissions into `osc_extent` ranges, accounts write grants and dirty pages, maintains per-object ready lists, builds BRW RPC batches through `osc_build_rpc()`, and coordinates truncate, writeback, discard, and LDLM high-priority handling. It is the central state machine between `osc_io.c` page submission, `osc_page.c` page/LRU lifetime, `osc_lock.c` lock cancellation, and lower `osc_request.c` RPC construction.

## Important APIs, Types, and Functions
The file revolves around `struct osc_extent`, whose observed fields include the red-black tree node `oe_node`, object pointer `oe_obj`, range `oe_start/oe_end/oe_max_end`, state `oe_state`, page list `oe_pages`, wait queue `oe_waitq`, DLM lock `oe_dlmlock`, grant counters, priority flags, direct-IO markers, layout version, and reference/user counts. The source uses states named by `oes_strings`: `OES_INV`, `OES_ACTIVE`, `OES_CACHE`, `OES_LOCKING`, `OES_LOCK_DONE`, `OES_RPC`, and `OES_TRUNC`.

Key exported entry points are `__osc_io_unplug()`, `osc_prep_async_page()`, `osc_cache_truncate_start()`, `osc_cache_wait_range()`, `osc_cache_writeback_range()`, `osc_page_gang_lookup()`, and `osc_discard_cb()`. Local core helpers include `osc_extent_find()`, `osc_extent_release()`, `osc_extent_finish()`, `osc_extent_wait()`, `osc_extent_make_ready()`, `osc_enter_cache()`, `osc_queue_async_io()`, `osc_queue_sync_pages()`, `osc_queue_dio_pages()`, `osc_send_write_rpc()`, `osc_send_read_rpc()`, and `osc_check_rpcs()`.

## Control Flow
Async buffered write flow starts in `osc_io_commit_async()` from `osc_io.c`, which calls `osc_page_cache_add()` and then `osc_queue_async_io()`. `osc_queue_async_io()` validates import health, quota, and page list state, reserves grants through `osc_enter_cache()`, finds or creates an active extent with `osc_extent_find()`, attaches the page to `oe_pages`, and leaves the active extent in `osc_io->oi_active`. Releasing that active extent through `osc_extent_release()` moves it to cached state, optionally merges neighboring extents, updates pending counters, places it on high-priority, urgent, full, or normal lists, and unplugs IO.

Synchronous read/write and direct IO flow is different: `osc_io_submit()` or `osc_dio_submit()` passes prepared page lists to `osc_queue_sync_pages()` or `osc_queue_dio_pages()`. These allocate a one-shot extent, mark it `OES_LOCK_DONE`, add it to read or write ready lists, update pending counters, and schedule unplug. `osc_check_rpcs()` chooses ready objects from client lists, sends high-priority work first, alternates write/read work per object, and calls `osc_send_write_rpc()` or `osc_send_read_rpc()`. Write RPC preparation transitions cached extents through `OES_LOCKING` to `OES_RPC` after `osc_extent_make_ready()` has made pages ready and stabilized transfer counts. Both read and write paths then call `osc_build_rpc()` and expect it to drain the `rpclist`.

Completion enters through `osc_extent_finish()`, usually from request completion code. It determines CRT read/write, optionally adds non-DIO pages back to the LRU, clears pending/rpc list links, completes each CL page through `osc_completion()`, releases or records lost grant, removes the extent from the object tree/list, and drops the RPC reference.

## State and Persistence Behavior
State is in-memory only: per-object extent trees/lists, client dirty/grant counters, page list links, and wait queues. The code persists user data only indirectly by forcing dirty cached pages into OST BRW RPCs. Grant accounting is critical: `osc_enter_cache_try()`, `osc_consume_write_grant()`, `osc_unreserve_grant()`, and `osc_free_grant()` coordinate `cl_avail_grant`, `cl_reserved_grant`, `cl_dirty_grant`, `cl_lost_grant`, `cl_dirty_pages`, and global `obd_dirty_pages`.

The extent tree is protected by the object lock, while client ready lists and grant accounting use `cl_loi_list_lock`. List membership invariants are maintained by `__osc_list_maint()`. Extent waiters use `oe_waitq`; state changes use release/acquire barriers in `osc_extent_state_set()` and `osc_extent_wait()`. Truncate is staged: `osc_cache_truncate_start()` moves or waits on affected extents, `osc_extent_truncate()` discards local pages and recalculates grants, and `osc_cache_truncate_end()` returns a partially truncated extent to cache if needed.

## Dependencies and Integration Points
This file depends heavily on private definitions from `<lustre_osc.h>` plus LDLM, CLIO, PTLRPC, quota, and page-cache APIs. It calls lower request helpers declared in `osc_internal.h`, especially `osc_build_rpc()`, `osc_send_empty_rpc()`, quota functions, and `osc_*_base()` RPC wrappers. It integrates with `osc_page.c` through `osc_prep_async_page()`, `osc_lru_add_batch()`, and page completion; with `osc_io.c` through queue/flush APIs; with `osc_lock.c` through high-priority lock callbacks and discard/writeback; and with `osc_object.c` through object fields initialized there.

## Risks
The largest risks are state-machine races and accounting drift. The code deliberately avoids holding object locks while taking page locks, waits up to 600 seconds for extent state transitions, and uses comments warning about deadlocks around `oe_memalloc`, writeback, and active extents. Grant bugs can cause false ENOSPC/EDQUOT, dirty-page leaks, or cache stalls. List corruption is possible if an extent is left on both tree and ready lists with the wrong owner. Truncate and lock-cancel paths are especially sensitive because they discard or write back pages while DLM state is changing.

## Test Signals
Useful tests should cover buffered writeback coalescing, grant exhaustion fallback to sync IO, quota-denied writes, truncate racing with active dirty extents, partial-page truncation grant recalculation, lock-cancel discard/writeback, high-priority callback-triggered writeout, invalid-import draining, direct IO read/write batching, RDMA-only and NDELAY flag propagation, and recovery paths where `osc_build_rpc()` fails. Assertions around `oo_nr_reads`, `oo_nr_writes`, `obd_dirty_pages`, and `cl_dirty_grant` are strong regression signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/osc_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/osc_dev.c -->
# sources/distributed-fs/lustre-release/lustre/osc/osc_dev.c research

## Purpose
`osc_dev.c` registers the OSC CL device type, allocates per-device state, wires Lustre context keys, and defines slab caches for OSC runtime objects. It is the construction/destruction layer for the OSC client layer rather than a data path file.

## Important APIs, Types, and Functions
The file defines slab-cache globals for `osc_lock`, `osc_object`, `osc_thread_info`, `osc_session`, `osc_extent`, and `obdo`, collected in `osc_caches[]`. It exports `osc_lock_kmem`, `osc_object_kmem`, `osc_key`, and `osc_session_key`. `osc_key_init()`/`osc_key_fini()` allocate and free per-thread `osc_thread_info`, including freeing `oti_ladvise_buf`. `osc_session_init()`/`osc_session_fini()` manage per-session `osc_session`.

The device operations are `osc_lu_ops`, with `ldo_object_alloc = osc_object_alloc` and config processing delegated to `osc_process_config()`. The device-type operations are `osc_device_type_ops`, and the global `osc_device_type` is registered with `LU_DEVICE_CL`, `LUSTRE_OSC_NAME`, and `LCT_CL_THREAD` context tags.

## Control Flow
Type initialization is generated by `LU_TYPE_INIT_FINI(osc, &osc_key, &osc_session_key)`, which ties the thread and session keys into Lustre type lifecycle. `osc_device_alloc()` allocates `struct osc_device`, initializes the embedded `cl_device`, looks up the backing `obd_device` by config name, links `obd->obd_lu_dev` and `d->ld_obd`, calls `osc_setup()`, stores the self-export in `osc_exp`, and records init time in stats. If setup fails, it invokes `osc_device_free()`.

Shutdown is split. `osc_device_fini()` unregisters lprocfs data and calls `osc_precleanup_common()`. `osc_device_free()` finalizes the CL device, calls `osc_cleanup_common()`, and frees `struct osc_device`. Config changes flow through `osc_process_config()`, which calls `class_modify_config()` with `PARAM_OSC` against the OBD kobject.

## State and Persistence Behavior
All state is in-memory lifecycle state: slab cache descriptors, per-thread buffers, per-session objects, device stats, and the device-to-OBD linkage. There is no persistent storage in this file. The important persistence-adjacent behavior is making sure config updates reach the OBD sysfs/kobject path and that cleanup unwinds lprocfs and common OSC resources before freeing the device.

## Dependencies and Integration Points
The file depends on `obd_class.h`, `<lustre_osc.h>`, Lustre param UAPI definitions, and local prototypes in `osc_internal.h`. It integrates with `osc_object.c` through `osc_object_alloc()`, with setup/cleanup code in other OSC files through `osc_setup()`, `osc_precleanup_common()`, and `osc_cleanup_common()`, and with all other files through the slab caches they allocate from.

## Risks
Lifecycle ordering is the main risk. `osc_device_alloc()` links `obd_lu_dev` before `osc_setup()`; failure paths must leave no dangling partially initialized state. `osc_key_fini()` assumes the thread info allocation succeeded and owns `oti_ladvise_buf`; invalid context-key handling could leak buffers or free invalid data. Slab cache descriptor sizes must track the real private struct definitions from `<lustre_osc.h>`.

## Test Signals
Tests should cover OSC device setup/failure cleanup, repeated setup/teardown, context allocation under memory pressure, config updates through `PARAM_OSC`, and module unload checks for slab leaks. Runtime signals include successful object allocation through `ldo_object_alloc`, lprocfs unregister during teardown, and no stale OBD `obd_lu_dev` references after failed setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/osc_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/osc_internal.h -->
# sources/distributed-fs/lustre-release/lustre/osc/osc_internal.h research

## Purpose
`osc_internal.h` is the private OSC interface header shared by the files in this directory. It does not define the main private structs; those come from `<lustre_osc.h>`, which is external to the listed source set. Instead, this header declares cross-file functions, global caches/device symbols, quota hooks, shrinker hooks, and small helpers used by cache, page, object, IO, lock, and request paths.

## Important APIs, Types, and Functions
The header declares cache/writeback interfaces such as `osc_extent_finish()`, `osc_extent_release()`, `osc_build_rpc()`, `osc_send_empty_rpc()`, `osc_lru_reserve()`, `osc_lru_unreserve()`, `osc_lock_discard_pages()`, and `osc_ldlm_hp_handle()`. Lock/RPC wrappers include `osc_enqueue_base()`, `osc_match_base()`, `osc_setattr_async()`, `osc_fallocate_base()`, `osc_sync_base()`, and `osc_ladvise_base()`. Device/object interfaces include `osc_setup()`, `osc_tunables_init()`, `osc_device_type`, and `osc_object_alloc()`.

Helpers include `osc_env_new_io()`, which zeroes and returns `osc_env_info(env)->oti_io`; `osc_recoverable_error()`, which classifies `-EIO`, `-EROFS`, `-ENOMEM`, `-EAGAIN`, and `-EINPROGRESS`; `rpcs_in_flight()`, which sums client read/write RPCs; `list_empty_marker()` for debug output; `osc_max_write_chunks()`, which limits write RPC chunk spread to `PTLRPC_MAX_BRW_SIZE >> cl_chunkbits`; and `osc_set_io_portal()`, which selects MDS or OST IO portal based on `IBITS` connection data.

## Control Flow
The header sets the call graph boundaries. `osc_io.c` calls cache APIs declared here to submit pages, reserve LRU slots, flush fsync ranges, and touch page attributes. `osc_lock.c` calls cache discard/writeback and matching/enqueue base helpers. `osc_page.c` calls cache queue/teardown helpers and LRU reservation. `osc_object.c` calls lock matching and cache invalidation helpers. `osc_request.c` is expected to provide the lower RPC base functions and `osc_build_rpc()`.

## State and Persistence Behavior
The header declares global request-pool state (`osc_pool_req_count`, `osc_reqpool_maxreqcount`, `osc_rq_pool`), slab cache descriptors (`osc_caches`), shrinker state (`osc_shrink_list`, `osc_shrink_lock`, `osc_page_cache_shrink_enabled`), and quota/unstable-page interfaces. It does not own persistence. It formalizes access to in-memory client state and RPC request state, which affects when dirty data is sent to OSTs and when unstable pages are considered committed.

## Dependencies and Integration Points
`<lustre_osc.h>` is the key dependency and supplies the struct definitions consumed by every prototype. The header integrates with LDLM (`ldlm_lock`, policy data, match flags), OBD exports/devices/imports, PTLRPC requests and request sets, CLIO (`cl_io`, `cl_object`, priorities), quota control, shrinkers, and LNet/portal selection. The `osc_max_write_chunks()` comment documents a ZFS transaction-size constraint that shapes batching behavior in `osc_cache.c` and `osc_io.c`.

## Risks
Because this is a private cross-file ABI, signature drift can silently break multiple paths. The inline helpers encode policy: misclassifying recoverable errors, write chunk limits, or IO portal selection can affect recovery, performance, and correctness. `osc_env_new_io()` zeroes a reusable environment object; callers must not retain stale pointers across nested CLIO operations.

## Test Signals
Compile coverage is essential because this header fans out across many OSC translation units. Behavioral tests should verify max-write-chunk enforcement for large `cl_chunkbits`, correct portal selection for MDS-vs-OST clients, recoverable error handling in request paths, shrinker enable/disable behavior, and cross-file call compatibility when adding fields or changing request-base helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/osc_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/osc_io.c -->
# sources/distributed-fs/lustre-release/lustre/osc/osc_io.c research

## Purpose
`osc_io.c` implements `cl_io_operations` for the OSC layer. It translates high-level CLIO operations into OSC page submissions, setattr/fallocate/sync/ladvise/lseek RPCs, attribute updates, active IO accounting, read-ahead setup, LRU reservation, and cleanup of active extents.

## Important APIs, Types, and Functions
Major exported functions include `osc_io_submit()`, `osc_dio_submit()`, `osc_io_commit_async()`, `osc_io_extent_release()`, `osc_io_iter_init()`, `osc_io_iter_fini()`, `osc_io_rw_iter_fini()`, `osc_io_fault_start()`, `osc_punch_start()`, `osc_io_setattr_end()`, `osc_io_read_start()`, `osc_io_write_start()`, `osc_fsync_ost()`, `osc_io_fsync_end()`, `osc_io_end()`, `osc_io_lseek_start()`, `osc_io_lseek_end()`, and `osc_io_lru_reserve()`. The private `osc_io_ops` table maps CLIO operation types to these callbacks.

Key per-IO state is `struct osc_io`, accessed through `osc_env_io()` or `cl2osc_io()`. Observed fields include `oi_active`, `oi_is_active`, `oi_lockless`, `oi_write_osclock`, `oi_read_osclock`, `oi_lru_reserved`, `oi_oa`, `oi_cbarg`, capability flags, and truncate state.

## Control Flow
For normal read/write submission, `osc_io_submit()` prepares pages using `cl_page_prep()` except for transient direct-IO pages, stamps BRW flags, calls `osc_page_submit()`, batches pages up to max pages or write chunk limits, then queues them with `osc_queue_sync_pages()`. `osc_dio_submit()` performs the same batching over `cl_dio_pages` and calls `osc_queue_dio_pages()`.

Buffered dirty-page commit uses `osc_io_commit_async()`. It clips partial lockless writes, loops through input pages, calls `osc_page_cache_add()` if a page is not already pending, updates KMS/size through `osc_page_touch_at()`, batches VM folios for the caller callback, updates shrink timing, and releases `oi_active` early for sync writes.

Operation-specific control is implemented through `osc_io_ops`. Reads update atime unless `ci_noatime`; writes update ctime/mtime. Faults touching writable mappings expand KMS. Setattr/truncate first freezes local cache with `osc_cache_truncate_start()`, sends async setattr, punch, or fallocate RPCs, then `osc_io_setattr_end()` waits for completion and releases truncate state. Fsync writes back the requested range, optionally waits, and sends OST_SYNC. Data-version, ladvise, and lseek allocate PTLRPC requests or call base helpers and complete through per-IO completions.

## State and Persistence Behavior
`osc_io_iter_init()` rejects invalid imports, supports fast mirror switching for non-delay reads with unhealthy imports by returning `-EAGAIN`, increments `oo_nr_ios`, and marks the OSC IO active. Fini decrements `oo_nr_ios` and wakes `oo_io_waitq`. Attribute persistence is indirect: local LVB/KMS updates happen through `cl_object_attr_update()`, while OST persistence happens through BRW, setattr, fallocate, sync, ladvise, getattr, and seek RPCs. `oi_lockless` causes server-lock (`OBD_FL_SRVLOCK`/`OBD_BRW_SRVLOCK`) behavior rather than relying on local LDLM handles.

## Dependencies and Integration Points
The file depends on CLIO page queues, OSC page/cache APIs, LDLM lock references, PTLRPC request packing, OBD `obdo` wire helpers, LNet RDMA-only page detection, and Linux fallocate/lseek constants. It integrates with `osc_cache.c` for all page queueing/writeback/truncation, `osc_page.c` for page submit/touch behavior, `osc_lock.c` through `oi_read_osclock` and `oi_write_osclock`, and `osc_request.c` base RPC wrappers.

## Risks
Risk centers on partial-page and lockless paths, asynchronous completion lifetime, and attribute ordering. `osc_io_submit()` returns success when pages reached `qout`, even if later pages failed, so callers must honor queue semantics. Setattr/truncate must not discard data before server punch support is known; the file flushes before punch/zero-range to avoid reorder loss. Fsync reclaim mode intentionally skips work when active IO, dirty writes, and unstable pages are zero; stale counters would produce data-integrity bugs.

## Test Signals
Tests should exercise buffered and direct read/write batching, chunk-limit splitting, RDMA-only flag propagation, `ci_ndelay` mirror fallback, lockless IO server-lock flags, mtime/ctime/atime updates, writable fault KMS extension, truncate and fallocate punch ordering, data-version fallback/error handling, `SEEK_HOLE`/`SEEK_DATA` with and without server support, fsync local/all/reclaim/discard modes, and LRU reservation under low-cache conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/osc_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/osc_lock.c -->
# sources/distributed-fs/lustre-release/lustre/osc/osc_lock.c research

## Purpose
`osc_lock.c` implements OSC `cl_lock_operations` and bridges CL locks to LDLM extent locks. It builds lock policies, sends enqueue requests, handles enqueue callbacks, lockless conversion, blocking/cancel/glimpse ASTs, early-cancel weight, conflicting-lock wait queues, and DLM lock lookup by page offset.

## Important APIs, Types, and Functions
Important exported functions include `osc_lock_fini()`, `osc_ldlm_glimpse_ast()`, `osc_ldlm_weigh_ast()`, `osc_lock_to_lockless()`, `osc_lock_wake_waiters()`, `osc_lock_enqueue_wait()`, `osc_lock_cancel()`, `osc_lock_print()`, `osc_lock_set_writer()`, `osc_lock_set_reader()`, and `osc_obj_dlmlock_at_pgoff()`. The operation tables are `osc_lock_ops` and `osc_lock_lockless_ops`.

The private `struct osc_lock` state is observed through fields such as `ols_state`, `ols_dlmlock`, `ols_handle`, `ols_hold`, `ols_has_ref`, `ols_flags`, `ols_lvb`, `ols_glimpse`, `ols_speculative`, `ols_locklessable`, `ols_owner`, `ols_waiting_list`, and links into `osc_object::oo_ol_list`.

## Control Flow
`osc_lock_init()` allocates a lock slice, initializes wait lists and flags, translates CL enqueue flags to LDLM flags, detects glimpse/speculative requests, builds enqueue info, optionally converts to lockless mode, and records read/write locks in the current `osc_io`. `osc_lock_enqueue()` waits for conflicting local OSC locks unless the request is glimpse/speculative/test-only, grants lockless locks locally, or calls `osc_enqueue_base()` with `osc_lock_upcall()` or `osc_lock_upcall_speculative()`.

`osc_lock_upcall()` runs when a lock is matched or the server replies. It transitions `OLS_ENQUEUED` to `OLS_UPCALL_RECEIVED`, calls `osc_lock_granted()` on success, maps NDELAY failures to `-EAGAIN`, handles glimpse `-ENAVAIL` by using the returned LVB, and wakes the sync owner. `osc_lock_granted()` takes the LDLM reference, stores handle/hold state, updates the CL descriptor to the granted extent, and refreshes object attributes from the LVB unless already cached.

Blocking AST flow is split: `osc_ldlm_blocking_ast()` handles `LDLM_CB_BLOCKING` by asynchronously cancelling the DLM lock; `LDLM_CB_CANCELING` creates a fresh environment and calls `__osc_dlm_blocking_ast()`. Canceling flushes or discards pages in the lock extent via `osc_lock_flush()`, clears `l_ast_data`, shifts KMS down with `ldlm_extent_shift_kms()`, and drops the object reference.

## State and Persistence Behavior
The file does not persist data itself, but it protects persistence by ensuring dirty pages are written before lock cancellation and by updating object LVB/KMS from lock replies and glimpses. `oo_ol_list` serializes local lock compatibility and lockless waiters. LDLM lock lifetime is reference-counted through `ldlm_handle2lock_long()`, `ldlm_lock_addref()`, `ldlm_lock_decref()`, and `ldlm_lock_put()`. `osc_lock_detach()` is the central cleanup point for LDLM references.

## Dependencies and Integration Points
Dependencies include LDLM policy/mode/AST APIs, FID/OST resource naming, CL lock and sync IO primitives, object attribute APIs, and `osc_cache.c` writeback/discard/high-priority helpers. The lock code integrates with `osc_io.c` by setting `oi_write_osclock`, `oi_read_osclock`, and `oi_lockless`; with `osc_object.c` through `oo_ol_list` and object LVB updates; and with lower request code through `osc_enqueue_base()` and `osc_match_base()`.

## Risks
The main risks are races between CL lock state and LDLM lock destruction, recursive cancel callbacks, and missing writeback during lock loss. `osc_lock_invariant()` documents expected relationships between handle, DLM pointer, state, and hold reference. The code intentionally avoids taking `cl_lock` mutex in glimpse AST; this relies on server-side race tolerance. Lockless conversion depends on connection flags and IO lock requirements; wrong conversion could bypass required client-side locking.

## Test Signals
Tests should cover normal enqueue and local match, glimpse success and `-ENAVAIL`, speculative enqueue cleanup, NDELAY `-EAGAIN`, lockless reads/writes, lock cancellation with dirty writeback, discard-data callbacks, KMS update after lock loss, waiter wakeups for incompatible locks, early-cancel weight for dirty/locked/writeback pages, and `osc_obj_dlmlock_at_pgoff()` retry when a matched lock is concurrently canceled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/osc_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/osc_object.c -->
# sources/distributed-fs/lustre-release/lustre/osc/osc_object.c research

## Purpose
`osc_object.c` implements OSC `cl_object` and `lu_object` behavior. It initializes per-stripe object state, exposes attribute get/update/glimpse, manages LDLM AST data pruning, sends FIEMAP requests, populates request attributes for page RPCs, allocates objects, and invalidates objects during teardown or layout changes.

## Important APIs, Types, and Functions
Exports include `osc_object_init()`, `osc_object_free()`, `osc_lvb_print()`, `osc_object_print()`, `osc_attr_get()`, `osc_attr_update()`, `osc_object_glimpse()`, `osc_object_prune()`, and `osc_object_invalidate()`. The local operation tables are `osc_object_ops`, `osc_ops`, and `osc_lu_obj_ops`. `osc_object_alloc()` allocates from `osc_object_kmem` and wires CL/LU ops.

Observed `osc_object` state initialized here includes `oo_oinfo`, ready/read/write list items, red-black extent root, high-priority/urgent/full/read extent lists, pending read/write counters, object and page-tree locks, radix page tree and page count, lock-list spinlock/list, active IO counter, and IO wait queue.

## Control Flow
Object initialization copies `lov_oinfo` from the CL object config, initializes all cache/RPC and lock lists, sets counters to zero, initializes the radix tree, and calls `cl_object_page_init()` with `sizeof(struct osc_page)`. Free asserts that all object-owned lists, trees, counters, and lock lists are empty, then finalizes and frees the object.

Attribute flow is local LVB/KMS translation. `osc_attr_get()` copies `loi_lvb` to `cl_attr` and reports KMS only when valid. `osc_attr_update()` writes selected CL attrs back to the LVB and calls `loi_kms_set()` for `CAT_KMS`. `osc_object_glimpse()` reports KMS as size for LDLM glimpse callbacks.

`osc_object_prune()` iterates the LDLM resource and clears any lock `l_ast_data` that points at the object, first copying the current object LVB into the lock LVB and clearing `LDLM_FL_LVB_CACHED`. `osc_object_fiemap()` optionally matches or obtains server-side locking for sync FIEMAP, packs an `OST_GET_INFO` request, and copies the returned fiemap data. `osc_req_attr_set()` populates `obdo` identity, timestamps, group/id, and DLM handle for page RPCs, with a hard failure if a non-server-lock page is uncovered by a local DLM lock.

## State and Persistence Behavior
Object state is volatile but mirrors server object identity and attributes through `lov_oinfo`. LVB fields (`size`, `blocks`, timestamps) and KMS are updated locally and sent or exposed through lock/RPC paths. `osc_object_invalidate()` waits for active IOs to drain, truncates dirty cache to zero, discards cached pages, and prunes DLM AST data, making it the strong object cleanup path before the object can disappear.

## Dependencies and Integration Points
The file depends on CL object/page APIs, LDLM resource iteration and matching, OSTID resource naming, PTLRPC request capsules, FIEMAP structures, `lov_oinfo`, `obdo`, and local cache/lock functions declared in `osc_internal.h`. It integrates with `osc_page.c` through page initialization and `osc_cl_page_osc()`, with `osc_lock.c` through lock lookup/build resource functions, with `osc_cache.c` through invalidation and discard, and with request code through request attribute population.

## Risks
Risks include stale `l_ast_data` pointing to freed objects, incorrect KMS/LVB ordering, FIEMAP lock reference leaks, and uncovered-page failures in `osc_req_attr_set()`. The comment about atime reset in request attributes is an explicit maintainability warning. Object free assertions are strict; leaks in cache, LRU, lock, or active IO paths will surface here.

## Test Signals
Tests should cover object init/free with empty state, attr get/update for size/times/blocks/KMS, glimpse size from KMS, prune clearing lock AST data and copying LVB, FIEMAP with cached PR/PW lock and server-lock fallback, request attr handle lookup for normal and server-lock pages, object invalidation while IOs are active, and cleanup assertions after truncation/discard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/osc_object.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/osc_page.c -->
# sources/distributed-fs/lustre-release/lustre/osc/osc_page.c research

## Purpose
`osc_page.c` implements OSC `cl_page` operations, page-to-async-page initialization, transfer pinning, per-OSC LRU slot management, VM shrinker callbacks, unevictable-page handling, and unstable writeback accounting. It is the page lifetime and memory-pressure companion to `osc_cache.c`.

## Important APIs, Types, and Functions
Important exported functions include `osc_dio_pages_init()`, `osc_page_init()`, and `osc_lru_shrink()`. Non-exported but cross-file-used functions include `osc_page_cache_add()`, `osc_index2policy()`, `osc_page_submit()`, `osc_lru_add_batch()`, `lru_queue_work()`, `osc_lru_reserve()`, `osc_lru_unreserve()`, `osc_unevict_cache_shrink()`, `osc_inc_unstable_pages()`, `osc_dec_unstable_pages()`, and `osc_over_unstable_soft_limit()`, with prototypes in `osc_internal.h`.

The file operates on `struct osc_page`, especially `ops_oap`, `ops_lru`, `ops_transfer_pinned`, `ops_srvlock`, `ops_from/ops_to`, `ops_intree`, `ops_in_lru`, and `ops_vm_locked`. It also uses client cache fields such as normal/unevictable LRU lists, LRU counters, shrinker counts, unstable counters, and shared `cl_lru_left`.

## Control Flow
Page initialization sets the default byte range, initializes the LRU link, calls `osc_prep_async_page()`, stores whether the current IO is server-lock/lockless, and registers page operations. Transient direct-IO pages get only print/clip operations and no cache LRU slot. Cacheable pages reserve an LRU slot with `osc_lru_alloc()`, preload and insert into `osc_object::oo_tree`, increment `oo_npages`, and mark `ops_intree`.

Submission and cache-add pin pages so they cannot be freed while transfer is pending. `osc_page_cache_add()` pins, calls `osc_queue_async_io()`, and either unpins on failure or marks the page as recently used. `osc_page_submit()` stamps BRW command, offset/count, sync flags, sys-resource flag, pins non-transient pages, and moves them out of the idle LRU.

Deletion reverses all page state: unpins transfer, tears down async cache state, removes the LRU slot, and deletes the page from the object radix tree. LRU shrink flow scans client LRU lists, groups pages by CL object to initialize one `CIT_MISC` IO per object, tries to own pages, moves mlocked pages to the unevictable list, discards freeable pages in folio batches, and updates counters. VM shrinker entry points count and scan all OSC clients in `osc_shrink_list`.

## State and Persistence Behavior
LRU state is in memory and controls client cache pressure, not durable storage. `osc_lru_alloc()` consumes shared LRU slots, possibly reclaiming from this or other OSC clients and waiting on `osc_lru_waitq`. `osc_lru_unreserve()` returns slots and wakes waiters. Unstable-page accounting marks pages as writeback/unstable after BRW dispatch and decrements when the request commits, using zone or node page-state counters depending on kernel feature macros. `osc_over_unstable_soft_limit()` piggybacks soft-sync pressure when global unstable pages and this OSC's unstable count exceed thresholds.

## Dependencies and Integration Points
The file depends on CL page/object ownership APIs, Linux radix tree, folio/page flags and refcounts, kernel shrinker APIs, node/zone writeback counters, client cache structures, and cache queueing in `osc_cache.c`. It integrates with `osc_object.c` through the page radix tree initialized there, with `osc_io.c` through LRU reservation and server-lock flags, with request completion through unstable-page callbacks, and with global shrinker registration state declared in `osc_internal.h`.

## Risks
Risks include page reference leaks from transfer pinning, LRU counter drift between busy/in-list/left/unevictable counters, reclaim deadlocks if page ownership is attempted under the wrong locks, radix tree duplicate or delete failures, incorrect handling of mlocked pages, and unstable-page accounting imbalance when requests are already committed. The shrinker has explicit logic to avoid infinite VM shrink loops when count and scan race with cache invalidation.

## Test Signals
Tests should cover cacheable and transient page initialization, radix tree duplicate handling, transfer pin/unpin on success and failure, page deletion while pending or in RPC, LRU reserve/reclaim under exhaustion, readahead failure to reserve slots, mlocked page migration to and from unevictable LRU, shrinker count/scan with empty and populated clients, unstable-page inc/dec including already-committed requests, and soft-sync threshold behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/osc_page.c -->
