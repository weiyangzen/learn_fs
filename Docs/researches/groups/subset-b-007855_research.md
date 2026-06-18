# subset-b-007855 Research

Grouped research for the listed OrangeFS BMI, NCAC buffer-cache, and I/O distribution source files. Each file section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/zoid.c -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/zoid.c

## Purpose
Implements the OrangeFS BMI method named `bmi_zoid`, targeting ZOID-based Blue Gene style compute-node to I/O-node communication. It provides the BMI method-ops table, client-side send/receive/test/cancel behavior, and delegates server-side behavior to `server.c` helpers declared in `zoid.h`.

## Important APIs, Types, And Functions
The file exports `bmi_zoid_ops` and the global `zoid_method_id`. Core helpers are `zoid_post_send_common`, `zoid_post_recv_common`, `zoid_test_common`, and `zoid_err_to_bmi`. BMI callbacks include `BMI_zoid_initialize`, `finalize`, `set_info`, `get_info`, `memalloc`, `memfree`, `unexpected_free`, `post_send`, `post_sendunexpected`, `post_recv`, `test`, `testsome`, `testcontext`, `testunexpected`, `method_addr_lookup`, list send/recv variants, context open/close, `cancel`, and `rev_lookup_unexpected`.

## Control Flow
Initialization records whether the process is a BMI server or client, stores the method id, allocates a pending `op_list`, and either calls `__zoid_init()` for clients or `BMI_zoid_server_initialize()` for servers. Client sends and receives first try immediate ZOID calls (`zbmi_send`, `zbmi_recv`). If a client send fails with `ENOMEM`, the operation is converted to a queued `method_op`; client receives are queued when no matching send is ready. `zoid_test_common` asks ZOID which queued operations are ready, completes matching sends/receives, handles canceled operations, fills BMI completion arrays, removes finished ops from `zoid_ops`, and deallocates the method ops. Server paths are thin pass-throughs to `zoid_server_*` helpers.

## State And Persistence
State is process-local: `zoid_node_type`, `zoid_method_id`, a static `zoid_ops` pending-op queue, and a cached singleton method address for `zoid://`. No disk persistence exists. The client side supports only the server address, one global BMI context, no compute-node to compute-node traffic, and no client-side multithreading. Pending op `method_data` is reused as a boolean that marks unexpected sends.

## Dependencies And Integration Points
This file integrates BMI method support (`bmi-method-support.h`, `method_op` allocation), `id-generator`, `op-list`, ZOID APIs (`zbmi.h`, `zoid_api.h`), and the server-side `bmi_zoid` implementation. It is selected through the BMI method table and must match BMI core expectations for operation ids, completion arrays, memory allocation, cancellation, max-size queries, and address cleanup.

## Risks And Test Signals
Risks include hard limits of 128 MiB expected and 8 KiB unexpected messages, aborts for unsupported client/server directions, `alloca` use proportional to list and test counts, single cached address lifetime, no real context isolation, and assumptions that `id_gen_fast_lookup` always returns a valid op for cancellation/test. Tests should cover immediate and deferred sends/receives, unexpected client-to-server messages, oversize rejection, `ENOMEM` retry behavior, cancellation completions, `testcontext` enumeration, server delegation, and `BMI_DROP_ADDR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/zoid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/zoid.h -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/zoid.h

## Purpose
Declares shared constants, address metadata, and client/server helper interfaces for the ZOID BMI method.

## Important APIs, Types, And Functions
Defines `ZOID_MAX_EXPECTED_MSG`, `ZOID_MAX_UNEXPECTED_MSG`, `ZOID_ADDR_SERVER_PID`, and `struct zoid_addr { int pid; }`. It declares the global `zoid_method_id`, server lifecycle and memory functions, unexpected-message testing/freeing, common server send/recv/test helpers, cancellation, and client address cleanup.

## Control Flow
`zoid.c` uses this header to route BMI callbacks to server helpers when initialized as a server. The address struct lets `method_addr_lookup` and client post paths assert that string address `zoid://` targets the single server endpoint.

## State And Persistence
The header defines no storage itself, but it fixes the in-memory address payload attached to `bmi_method_addr`. Message-size constants are behavioral limits for all users of the method.

## Dependencies And Integration Points
The prototypes depend on BMI types such as `bmi_op_id_t`, `bmi_method_addr_p`, `bmi_size_t`, `bmi_context_id`, `bmi_msg_tag_t`, and `PVFS_hint`. It is the ABI between `zoid.c` and the ZOID server implementation.

## Risks And Test Signals
Main risks are declaration drift with server implementation and incorrect assumptions around the only valid pid value. Build coverage of `bmi_zoid`, max-size query tests, and address lookup/free tests are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/zoid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/module.mk.in -->
# sources/distributed-fs/orangefs/src/io/bmi/module.mk.in

## Purpose
Adds the BMI core source files to OrangeFS build source variables.

## Important APIs, Types, And Functions
This makefile fragment appends `bmi.c`, `bmi-method-support.c`, `op-list.c`, and `reference-list.c` to `LIBSRC`, `SERVERSRC`, and `LIBBMISRC` using `DIR := src/io/bmi`.

## Control Flow
The build system includes this fragment while composing library, server, and BMI-library compilation units. There is no runtime control flow.

## State And Persistence
No runtime state exists. The persistent effect is build membership for BMI core helper code.

## Dependencies And Integration Points
Integrates with OrangeFS automake-style `module.mk.in` aggregation. It intentionally does not list `bmi_zoid/zoid.c`, which is presumably gated by a method-specific build path.

## Risks And Test Signals
Risks are build omissions or duplicate object inclusion if source ownership changes. Test signals are configure/build success for client library, server binary, and BMI library targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/op-list.c -->
# sources/distributed-fs/orangefs/src/io/bmi/op-list.c

## Purpose
Provides a quicklist-backed container for BMI method operation records. Network method implementations use it to queue, count, search, inspect, and remove pending `method_op` objects.

## Important APIs, Types, And Functions
Public functions are `op_list_new`, `op_list_add`, `op_list_cleanup`, `op_list_remove`, `op_list_empty`, `op_list_count`, `op_list_dump`, `op_list_search`, and `op_list_shownext`. Private helpers are `op_list_cmp_key` and `gossip_print_op`.

## Control Flow
`op_list_new` allocates and initializes a list head. `op_list_add` appends operations to the tail to preserve FIFO behavior. `op_list_search` scans until all enabled fields in `op_list_search_key` match. `op_list_cleanup` walks safely through the list and deallocates each `method_op`, then frees the list head. `op_list_remove` unlinks an op but leaves destruction to the caller.

## State And Persistence
The list owns only in-memory queue membership. No locking is performed; comments state callers must serialize access around operation structures. Cleanup frees queued operations, so ownership must be clear before calling it.

## Dependencies And Integration Points
Depends on `quicklist`, `bmi-method-support`, `gossip`, and `method_op` layout. `bmi_zoid` uses it to retain deferred client operations, and other BMI methods can use it for pending send/recv queues.

## Risks And Test Signals
Risks include no internal synchronization, cleanup deallocating operations still referenced elsewhere, and debug output relying on `method_op` fields that may evolve. Unit tests should cover FIFO order, empty/non-empty behavior, search by address/tag/id combinations, remove without free, and cleanup under multiple entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/op-list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/op-list.h -->
# sources/distributed-fs/orangefs/src/io/bmi/op-list.h

## Purpose
Declares the BMI operation-list API and search-key structure used by BMI method implementations.

## Important APIs, Types, And Functions
Defines `op_list_p` as `struct qlist_head *` and `struct op_list_search_key`, whose fields can optionally match method address, message tag, and operation id via `*_yes` switches. Declares list creation, add, cleanup, remove, dump, empty, next, count, and search functions.

## Control Flow
Callers create a list, append pending `method_op` objects, optionally search or inspect the first entry, remove completed entries, and finally clean up all remaining operations.

## State And Persistence
The header owns no state but defines the query contract for pending operation lists. It deliberately exposes quicklist-based list storage.

## Dependencies And Integration Points
Includes `pvfs2-internal.h`, `quicklist.h`, `bmi-types.h`, and `bmi-method-support.h`. It is shared by BMI core and methods such as `bmi_zoid`.

## Risks And Test Signals
Risks are ABI coupling to `method_op` and broad search-key fields that may not be meaningful for every method. Compile tests for BMI methods and queue behavior tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/op-list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/reference-list.c -->
# sources/distributed-fs/orangefs/src/io/bmi/reference-list.c

## Purpose
Manages BMI address reference records that map public `BMI_addr_t` values, string ids, method addresses, and method operation tables.

## Important APIs, Types, And Functions
Public functions are `ref_list_new`, `ref_list_add`, `ref_list_search_addr`, `ref_list_search_method_addr`, `ref_list_search_str`, `ref_list_rem`, `ref_list_cleanup`, `alloc_ref_st`, and `dealloc_ref_st`. Private state is the global string hash table `str_table`; private comparison logic is `ref_list_compare_key_entry`.

## Control Flow
`ref_list_new` enforces a single live reference list by refusing to create a second global hash table. `alloc_ref_st` allocates/zeros a reference and registers it with the safe id generator to assign `bmi_addr`. `ref_list_add` adds id strings to the hash and links the record into the list. Searches either use `id_gen_safe_lookup`, `method_addr->parent`, or the string hash. Removal unlinks the list/hash entry without freeing it. Cleanup deallocates all records, finalizes the hash table, and frees the list.

## State And Persistence
State is entirely in-memory: a quicklist of references, a global string hash table, id-generator registrations, owned `id_string` memory, and method-address ownership through `interface->set_info(BMI_DROP_ADDR, method_addr)`. No disk persistence exists.

## Dependencies And Integration Points
Uses `quickhash`, `quicklist`, `id-generator`, BMI method support, and method-specific `set_info` cleanup. It is the BMI glue layer between user-visible addresses and transport-specific address records.

## Risks And Test Signals
Risks include the singleton hash table, no internal locking, cleanup calling method code during reference destruction, `ref_list_search_method_addr` assuming `map->parent` is valid, and partial allocation leaks if future code changes add more owned fields. Tests should cover add/search/remove by all keys, duplicate list creation failure, string hash cleanup, method address drop behavior, and id-generator unregister behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/reference-list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/reference-list.h -->
# sources/distributed-fs/orangefs/src/io/bmi/reference-list.h

## Purpose
Defines BMI reference-record structure and declares reference-list management helpers.

## Important APIs, Types, And Functions
Defines `ref_list_p`, `struct ref_st`, and `ref_st_p`. `ref_st` stores `BMI_addr_t`, id string, method address, BMI method ops pointer, list link, reference count, and hash link. Declares creation, add, address/method/string searches, removal, cleanup, allocation, and deallocation helpers.

## Control Flow
Consumers allocate `ref_st`, fill string/method/interface fields, add it to a list, search by desired key, remove on address drop, and deallocate when no longer referenced.

## State And Persistence
The header defines the in-memory shape of address references. The `ref_count` field signals intended shared ownership, although increments/decrements are not implemented in this file.

## Dependencies And Integration Points
Includes BMI types, method support, quicklist, and quickhash. It also works around a Windows `interface` macro by renaming the field under `WIN32`.

## Risks And Test Signals
Risks are structure-field drift against BMI core, ambiguous ownership of `method_addr`, and unused or externally managed `ref_count`. Build coverage across Windows and non-Windows plus address lifecycle tests are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/reference-list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/aiovec.h -->
# sources/distributed-fs/orangefs/src/io/buffer/aiovec.h

## Purpose
Defines a small fixed-size vector for batching NCAC extent operations into a single Trove list I/O request.

## Important APIs, Types, And Functions
Defines `AIOVEC_SIZE` as 6 and `struct aiovec`, holding parallel arrays for extents, stream offsets/sizes, memory offsets/sizes, and count `nr`. Inline helpers are `aiovec_init`, `aiovec_reinit`, `aiovec_count`, `aiovec_space`, and `aiovec_add`.

## Control Flow
NCAC code initializes or reinitializes the vector, appends extent/file/memory tuples until space is exhausted, then passes the arrays to Trove helper functions.

## State And Persistence
State is embedded in requests or inode-like structures and is process-local. `aiovec_init` sets `nr` then zeros the whole struct; `aiovec_reinit` only resets count and leaves old array contents for overwrite.

## Dependencies And Integration Points
Depends on `internal.h` for `struct extent`, `PVFS_offset`, and `PVFS_size`. Used by NCAC Trove batching and inode/request structures.

## Risks And Test Signals
Risks include no bounds check in `aiovec_add`, a hard batch size of six extents, and stale contents after `aiovec_reinit` if callers read beyond `nr`. Tests should verify capacity handling and list-I/O construction under exactly-full and overflow-attempt scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/aiovec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/cache.c -->
# sources/distributed-fs/orangefs/src/io/buffer/cache.c

## Purpose
Implements common NCAC cache item operations independent of a specific cache policy: lookup, insert, remove, free-list extraction, shrinking, discardability checks, and hit promotion.

## Important APIs, Types, And Functions
Public functions are `lookup_cache_item`, `add_cache_item`, `remove_cache_item`, `get_free_extent_list_item`, `shrink_cache`, `is_extent_discardable`, and `hit_cache_item`. Private helpers split radix/inode bookkeeping from policy-list bookkeeping.

## Control Flow
Lookup queries an inode radix tree. Add first inserts into the radix tree and inode clean list, then adds to the selected policy list, currently LRU. Remove performs the inverse order: LRU removal followed by radix deletion and mapping clear. `shrink_cache` dispatches to LRU shrink logic for LRU and ARC constants. Cache hits remove and re-add the item in the policy list to refresh its position.

## State And Persistence
State changes are in-memory inode radix trees, clean-page lists, extent mapping/index fields, and global cache-stack active/inactive/free counters. No persistent state exists. Locking is expected to be handled by callers; helper comments identify inode/cache-stack protection expectations but this file does not acquire locks itself.

## Dependencies And Integration Points
Depends on NCAC internal structs, state/flag macros, `radix`, and `ncac-lru`. It is used by NCAC read/write job processing and eviction.

## Risks And Test Signals
Risks include missing list deletion from `mapping->clean_pages` in `remove_cache_item_no_policy`, double `nrpages` accounting because both radix add and LRU add increment inode counters, ARC falling back to LRU, and no lock enforcement. Tests should cover add/lookup/remove, duplicate insert failure, discard rules for dirty or referenced extents, shrink under pending I/O, and counter/list consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/cache.h -->
# sources/distributed-fs/orangefs/src/io/buffer/cache.h

## Purpose
Declares cache-policy constants and common NCAC cache-management functions.

## Important APIs, Types, And Functions
Defines discard/refill cluster constants, `LRU_POLICY`, `ARC_POLICY`, and `TWOQ_POLICY`. Declares lookup, free extent retrieval, add/remove, shrink, discardability, and hit handlers.

## Control Flow
Callers use these functions from job/state code when locating extents, admitting extents into cache, evicting clean extents, and refreshing policy position on hits.

## State And Persistence
No state is defined directly; the prototypes operate on `struct inode`, `struct extent`, and `struct cache_stack` from `internal.h`.

## Dependencies And Integration Points
This header is included by NCAC job, state, internal, and LRU code. It relies on prior visibility of NCAC internal types.

## Risks And Test Signals
Risks are declaration drift and policy constants that imply ARC/TWOQ support not actually implemented in `cache.c`. Build and policy-dispatch tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/flags.h -->
# sources/distributed-fs/orangefs/src/io/buffer/flags.h

## Purpose
Defines bit positions and macros for manipulating NCAC extent state flags and access counters.

## Important APIs, Types, And Functions
Provides low-level `test_bit`, `set_bit`, `clear_bit`, `test_and_set_bit`, page/extent flag bits (`PG_locked`, `PG_clean`, `PG_dirty`, `PG_readpending`, `PG_writepending`, `PG_rmw`, etc.), and macros such as `PageDirty`, `SetPageClean`, `ClearPageReadPending`, `IncReadCount`, and `ClearPageFlags`.

## Control Flow
NCAC job and state code uses these macros to move extents through blank, pending read/write, clean, dirty, communication, LRU, active, referenced, and read-modify-write states.

## State And Persistence
Macros mutate the `flags`, `reads`, and `writes` fields of `struct extent` in memory. They perform no locking or atomic CPU operations despite Linux-like names.

## Dependencies And Integration Points
Included throughout the buffer cache. It assumes every target object has `flags`, `reads`, and `writes` fields matching `struct extent`.

## Risks And Test Signals
Risks include non-atomic bit updates, macro side effects, trailing semicolons inside macros, no underflow checks on counters, and no-op `extent_ref_release/get`. Concurrency and state-transition tests should verify flag consistency around read/write completion and eviction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/flags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/internal.c -->
# sources/distributed-fs/orangefs/src/io/buffer/internal.c

## Purpose
Implements NCAC internal request construction, buffer-range preparation, progress-list movement, request completion/recycling, inode lookup/allocation, and debug dump helpers.

## Important APIs, Types, And Functions
Public internal functions are `NCAC_rwreq_build`, `NCAC_rwjob_prepare`, `NCAC_do_jobs`, `NCAC_do_a_job`, `NCAC_check_request`, `NCAC_done_request`, `cache_dump_active_list`, and `cache_dump_inactive_list`. Private helpers include request-list lock wrappers, `get_internal_req_lock`, `NCAC_rwjob_prepare_single`, `NCAC_rwjob_prepare_list`, `get_inode`, and inode hash search.

## Control Flow
`NCAC_rwreq_build` draws a preallocated request from `NCAC_dev.free_req_list`, binds it to an inode keyed by `(coll_id, handle)`, classifies it as cached or buffered read/write, and copies vector offsets for multi-region requests. `NCAC_rwjob_prepare` computes extent-aligned communication buffer arrays, queues the request on `prepare_list`, and immediately advances that request via `NCAC_do_a_job`. Single-region and list-region preparation calculate file offsets, cache-buffer offsets, sizes, flags, and extent slots, sorting multi-region input by file position. `NCAC_do_a_job` dispatches by optype to job workers and moves requests from prepare to buffer-complete or complete lists. `NCAC_check_request` progresses unfinished requests on demand. `NCAC_done_request` handles post-communication cleanup and returns request objects to the free list.

## State And Persistence
State is global NCAC memory: preallocated request objects, prepare/buffer-complete/complete/free lists, inode collision chains, cached per-request buffer arrays, and inode page trees. No disk persistence exists. Requests may keep allocated buffer-info arrays across reuse to reduce allocations. Inodes are allocated lazily and never freed in this file.

## Dependencies And Integration Points
Depends on `internal.h`, `state.h`, `flags.h`, `aiovec.h`, `cache.h`, and `ncac-job.h`. It is called by `ncac-interface.c` and drives `ncac-job.c`/`ncac-buf-job.c` workers.

## Risks And Test Signals
Risks include `get_internal_req_lock` returning without unlocking when the free list is empty, pointer recovery through `list_entry(new->prev, ...)` after `list_del_init`, hardcoded debug `fprintf` output, possible zero-size last buffer when a request ends exactly on an extent boundary, request leaks on invalid done status, no inode-table lock, and limited implemented worker types. Tests should stress empty request pools, multi-region sorting and overlapping extents, request status transitions, completion recycling, and concurrent access to the same handle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/internal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/internal.h -->
# sources/distributed-fs/orangefs/src/io/buffer/internal.h

## Purpose
Defines the NCAC internal data model, global device state, status/error constants, list helpers, and function prototypes shared by the buffer-cache implementation.

## Important APIs, Types, And Functions
Key types are `NCAC_info_t`, `NCAC_dev_t`, `NCAC_req_t`, `struct cache_stack`, `struct inode`, and `struct extent`. It defines request optype/status/error constants, `MAX_INODE_NUM`, `MAX_DELT_REQ_NUM`, `INVAL_IOREQ`, global `NCAC_dev`, `inode_arr`, cache initialization, request-build/progress/done APIs, one-piece read/write prototypes, and inline helpers for aiovec and LRU-list manipulation.

## Control Flow
The header supports the pipeline where public cache descriptors become `NCAC_req_t`, requests acquire extents under inode/cache locks, move through prepare/buffer-complete/complete lists, and eventually release extents and return to the free request pool.

## State And Persistence
Defines all primary in-memory NCAC state: cache memory, extent pool, request pool, inode radix trees and dirty/clean lists, active/inactive/free LRU lists, counters, pending Trove ids, and per-request communication arrays. There is no persistence beyond the process.

## Dependencies And Integration Points
Includes `ncac-interface.h`, `ncac-list.h`, `radix.h`, `aiovec.h`, `flags.h`, and `ncac-locks.h`. It exposes internals broadly to all NCAC compilation units.

## Risks And Test Signals
Risks include tight coupling among modules, globally mutable singleton state, mismatched status names with interface comments, no clear ownership/free path for inodes, and counters spread across inode/cache/extent objects. Tests should validate struct initialization, cache counters, request list transitions, and build coverage for all modules using the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/module.mk.in -->
# sources/distributed-fs/orangefs/src/io/buffer/module.mk.in

## Purpose
Adds NCAC buffer-cache implementation files to OrangeFS server builds.

## Important APIs, Types, And Functions
Appends `ncac-interface.c`, `ncac-trove.c`, `ncac-job.c`, `ncac-buf-job.c`, `ncac-init.c`, `internal.c`, `cache.c`, `ncac-lru.c`, `state.c`, and `radix.c` to `SERVERSRC`.

## Control Flow
No runtime control flow. The fragment controls compilation membership for the server-side cache.

## State And Persistence
No runtime state exists. Persistent effect is build inclusion.

## Dependencies And Integration Points
Integrates NCAC only into `SERVERSRC`, not client `LIBSRC`, matching a server-side cache role.

## Risks And Test Signals
Risks are stale source membership if files are renamed or if client-side cache use is later expected. Server build success is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-buf-job.c -->
# sources/distributed-fs/orangefs/src/io/buffer/ncac-buf-job.c

## Purpose
Contains intended workers for NCAC operations where the caller supplies a user buffer and data is copied between cache extents and that buffer.

## Important APIs, Types, And Functions
Exports `NCAC_do_a_bufread_job` and `NCAC_do_a_bufwrite_job`.

## Control Flow
The meaningful read/write copy implementations are inside `#if 0`, so both functions currently return `0` without setting request status or copying data. Disabled code shows intended behavior: process one or multiple file regions, count ready cache buffers, transition to partial/complete, copy data to/from `usrbuf`, and call `NCAC_extent_done_access`.

## State And Persistence
With current compiled code, no state is changed. Intended state would involve `NCAC_req_t` buffer arrays, extent reference counts, and request status transitions.

## Dependencies And Integration Points
Included in `module.mk.in` and dispatched from `NCAC_do_a_job` for `NCAC_BUF_READ` and `NCAC_BUF_WRITE`. Depends on internal NCAC types and state helpers.

## Risks And Test Signals
The primary risk is that public `cache_read_post`/`cache_write_post` classify requests with non-NULL `desc->buffer` as buffered jobs, but these jobs are effectively stubs. Tests should explicitly cover supplied-buffer reads/writes and assert either implemented completion or a deliberate unsupported error; current behavior may leave requests submitted without progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-buf-job.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-init.c -->
# sources/distributed-fs/orangefs/src/io/buffer/ncac-init.c

## Purpose
Initializes global NCAC cache resources: request pool, extent pool, cache memory metadata, free lists, request-progress lists, inode table, radix callbacks, and locks.

## Important APIs, Types, And Functions
Defines global `NCAC_dev` and `inode_arr`. Public entry is `cache_init`; helper functions are `radix_get_value`, `init_free_extent_list`, `init_free_req_list`, `init_cache_stack_list`, and placeholder `extlog2`.

## Control Flow
`cache_init` chooses the request count, allocates/zeros request objects, initializes free request list and lock, sets extent size/cache size/cache memory, computes extent count, allocates/zeros extents, initializes extent free list and cache stack lists, initializes prepare/buffer-complete/complete lists, clears inode buckets, and records radix tree callbacks.

## State And Persistence
All state is process-local global NCAC state. Extent `addr` fields point into caller-provided `info->cachespace`; request and extent metadata are heap-allocated and not freed here. `extlog2` currently returns 15 regardless of the configured extent size, effectively assuming 32 KiB extents for index shifts.

## Dependencies And Integration Points
Depends on `internal.h`, `ncac-list.h`, and `radix.h`. It must run before any `cache_*_post` operation.

## Risks And Test Signals
Risks include checking `free_extent_src` for NULL after `memset`, no cleanup function, `extlog2` hardcoding, no validation that extent size divides cache size or is a power of two, and allowing NULL cache memory after warning. Tests should initialize varied cache sizes, verify free-list counts and extent addresses, reject invalid configs, and exercise non-32KiB extents to expose index errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-interface.c -->
# sources/distributed-fs/orangefs/src/io/buffer/ncac-interface.c

## Purpose
Provides the public NCAC cache request API used by higher layers to post read/write/sync operations, poll request progress, and mark completed buffer communication.

## Important APIs, Types, And Functions
Exports `cache_read_post`, `cache_write_post`, `cache_sync_post`, `cache_req_test`, `cache_req_testsome`, and `cache_req_done`.

## Control Flow
Read/write post functions build an internal request, prepare and submit it, store the internal id/optype/status into the public request handle, and return buffer arrays in `cache_reply_t` when partial or buffer-complete progress is available. `cache_req_test` calls `NCAC_check_request`, updates public status, exposes buffers for partial/buffer-complete state, and sets a completion flag for buffer-complete or complete. `cache_req_done` calls `NCAC_done_request` and marks the public handle complete. Sync and testsome print "not implemented yet" and return zero.

## State And Persistence
State lives in NCAC internal request objects and public handles. `user_ptr` parameters are currently unused. Replies reference internal request arrays, so the caller must finish communication before `cache_req_done` recycles the request.

## Dependencies And Integration Points
Depends on `ncac-interface.h` for public structures and `internal.h` for request engine calls. Higher network or server I/O code should interact through these functions instead of direct internal structures.

## Risks And Test Signals
Risks include sync/testsome stubs, no descriptor validation, supplied-buffer paths dispatching to stubbed workers, reply pointers becoming invalid after done, and mismatch between comments and actual status names. Tests should cover post/test/done for cache-buffer reads, missing free requests, supplied-buffer reads/writes, polling before/after Trove completion, and unsupported sync/testsome behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-interface.h -->
# sources/distributed-fs/orangefs/src/io/buffer/ncac-interface.h

## Purpose
Declares the external NCAC buffer-cache interface, public descriptor/handle/reply types, operation codes, and cache hints.

## Important APIs, Types, And Functions
Defines `NCAC_READ`, `NCAC_WRITE`, `NCAC_BUF_READ`, `NCAC_BUF_WRITE`, `NCAC_QUERY`, `NCAC_DEMOTE`, and `NCAC_SYNC`; `cache_hints_t`; `cache_desc_t`; `cache_read_desc_t`; `cache_write_desc_t`; `cache_sync_desc_t`; `cache_request_t`; `cache_reply_t`; and `cache_info_t`. Declares post/test/done functions and `cache_query_info`.

## Control Flow
Callers fill read/write descriptors with collection, handle, context, stream offset/size arrays, optional user buffer, length, and cache hints. The API returns a request handle and, when data buffers are ready, a reply vector of cache buffer addresses, sizes, and flags.

## State And Persistence
The header defines public in-memory contracts only. `cache_request_t.internal_id` is explicitly internal and should not be modified by callers.

## Dependencies And Integration Points
Includes `pvfs2-types.h` and bridges server/network I/O code to NCAC internals. Its operation codes must match `NCAC_do_a_job` dispatch.

## Risks And Test Signals
Risks include duplicate descriptor structs, comments referencing status names not defined in this header, and `cache_query_info` declaration without an implementation in the listed source files. API tests should verify descriptor layout, request-handle lifecycle, and build/link coverage for declared functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-job.c -->
# sources/distributed-fs/orangefs/src/io/buffer/ncac-job.c

## Purpose
Implements NCAC job workers for cached extent operations, primarily the read path, plus placeholders for write/query/demote/sync jobs.

## Important APIs, Types, And Functions
Exports `NCAC_do_a_read_job`, `NCAC_do_a_write_job`, `NCAC_do_a_query_job`, `NCAC_do_a_demote_job`, and `NCAC_do_a_sync_job`. Private helpers find extents, allocate extents, initialize Trove reads, mark pending reads, test read completion, increment read references, and add extents to cache.

## Control Flow
`NCAC_do_a_read_job` locks the inode, iterates communication buffers, locates or allocates extents by index, starts a Trove read for misses, admits new extents into LRU cache, increments one read reference per distinct extent, checks pending read completion, and sets per-buffer readiness flags. After unlocking, it sets request status to submitted, partial, or buffer-complete based on ready count. The write/query/demote/sync workers currently return success or log "not implemented yet" without meaningful state transitions.

## State And Persistence
Read jobs mutate inode page trees, LRU lists, extent flags, read counters, pending Trove ids, and request buffer/status fields. Extents come from the global free list or eviction. No disk persistence occurs beyond Trove reads into cache memory.

## Dependencies And Integration Points
Uses internal NCAC state, flag macros, cache management, `ncac-trove` read helpers, and LRU policy. It is dispatched by `internal.c`.

## Risks And Test Signals
Risks include only read path being implemented, `free_extent` being a no-op on read-init failure, hardcoded debug output, blocking allocation relying on clean eviction, possible counter inconsistencies, and full-extent reads for partial requests. Tests should cover cache miss/read completion, cache hit promotion, eviction under no free extents, partial request readiness, read failures, and explicit write/query/sync unsupported behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-job.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-job.h -->
# sources/distributed-fs/orangefs/src/io/buffer/ncac-job.h

## Purpose
Declares NCAC job worker functions and the default discard request count.

## Important APIs, Types, And Functions
Defines `DELT_DISCARD_NUM` as 5 and declares workers for read, write, buffered read, buffered write, query, demote, and sync jobs.

## Control Flow
`internal.c` dispatches `NCAC_req_t` objects to these workers based on `optype`.

## State And Persistence
The header has no state; workers operate on `struct NCAC_req`.

## Dependencies And Integration Points
Included by `internal.c`, `ncac-job.c`, and `ncac-buf-job.c`. Its declarations must match worker implementations.

## Risks And Test Signals
Risks are that the header advertises more functionality than is implemented. Build coverage and worker-status tests should catch mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-job.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-list.h -->
# sources/distributed-fs/orangefs/src/io/buffer/ncac-list.h

## Purpose
Provides a local Linux-kernel-style intrusive doubly linked list implementation for NCAC.

## Important APIs, Types, And Functions
Defines `struct list_head`, `LIST_HEAD_INIT`, `LIST_HEAD`, `INIT_LIST_HEAD`, add/delete/move/splice helpers, `list_empty`, `offsetof`, `container_of`, and `list_entry`.

## Control Flow
NCAC uses list heads embedded in requests, extents, inode clean/dirty lists, cache active/inactive/free lists, and progress lists. Add/delete functions manipulate links in O(1).

## State And Persistence
State is stored in caller-embedded `list_head` links. `list_del` poisons pointers while `list_del_init` resets them to a single-item list. No locking is built in.

## Dependencies And Integration Points
Included by `internal.h` and most buffer modules. It duplicates common kernel list semantics without requiring Linux headers.

## Risks And Test Signals
Risks include no iteration macros beyond `list_entry`, GCC-specific `typeof` in `container_of`, overriding `offsetof`, and misuse after `list_del` poisoned entries. Tests should cover add/tail/delete/init/splice behavior and portability builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-locks.h -->
# sources/distributed-fs/orangefs/src/io/buffer/ncac-locks.h

## Purpose
Maps NCAC lock names to generic mutex operations.

## Important APIs, Types, And Functions
Includes `gen-locks.h` and defines `spin_lock_init`, `cache_lock`, `cache_unlock`, `inode_lock`, `inode_unlock`, `list_lock`, and `list_unlock` as `gen_mutex_*` wrappers.

## Control Flow
Buffer-cache code uses semantic lock macros for request lists, inodes, and cache stacks while all are implemented as generic mutexes.

## State And Persistence
No state is defined here. Lock objects are `gen_mutex_t` fields in NCAC structures.

## Dependencies And Integration Points
Used by `internal.h` and therefore all NCAC code. It depends on the OrangeFS generic lock abstraction.

## Risks And Test Signals
Risks include the misleading `spin_lock` name despite mutex semantics and no try-lock/read-write distinction. Threaded cache tests should validate absence of deadlocks under inode/cache/list lock ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-locks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-lru.c -->
# sources/distributed-fs/orangefs/src/io/buffer/ncac-lru.c

## Purpose
Implements the LRU cache policy operations used by NCAC cache admission, removal, and shrinking.

## Important APIs, Types, And Functions
Exports `LRU_add_cache_item`, `LRU_remove_cache_item`, and `LRU_shrink_cache`.

## Control Flow
Admission inserts the extent at the active-list head and sets `PG_lru`. Removal unlinks from the LRU list and decrements counters. Shrink scans from the active-list tail, checks pending I/O completion if needed, converts completed pending extents to clean, and discards clean unreferenced extents by removing them from LRU and adding them to the free extent list until the expected count is reached or no more victims exist.

## State And Persistence
Mutates cache active-list links/counters, extent LRU flags, inode page counters, and free extent list. No persistent state exists. Callers are expected to hold the cache lock.

## Dependencies And Integration Points
Depends on internal NCAC structures, state and flag helpers, cache discardability, and Trove completion checks. Called from `cache.c` and extent allocation.

## Risks And Test Signals
Risks include only active-list scanning, no inactive-list use despite fields, no clearing of LRU flags on removal, no radix removal during shrink, debug output, and counter consistency questions. Tests should validate shrink under clean, dirty, referenced, and pending I/O victims and ensure evicted extents are no longer discoverable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-lru.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-lru.h -->
# sources/distributed-fs/orangefs/src/io/buffer/ncac-lru.h

## Purpose
Declares LRU policy functions for the NCAC cache.

## Important APIs, Types, And Functions
Declares `LRU_add_cache_item`, `LRU_remove_cache_item`, and `LRU_shrink_cache`.

## Control Flow
These functions are called by generic cache-policy wrappers during admission, removal, hit refresh, and eviction.

## State And Persistence
The header has no state. Implementations mutate `struct cache_stack` and `struct extent` objects.

## Dependencies And Integration Points
Relies on internal type visibility from including translation units. Included by `cache.c` and `ncac-lru.c`.

## Risks And Test Signals
Risks are declaration drift and lack of documented locking requirements in the header. Build and eviction-policy tests are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-lru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-trove.c -->
# sources/distributed-fs/orangefs/src/io/buffer/ncac-trove.c

## Purpose
Connects NCAC cache extents to Trove asynchronous storage operations, including list I/O, single-extent reads, read-modify-write reads, completion polling, and in-place coalescing of offset/length arrays.

## Important APIs, Types, And Functions
Exports `NCAC_aio_read_ext`, `NCAC_aio_write`, `do_read_for_rmw`, `NCAC_check_ioreq`, and `init_io_read`. Private helper `offset_shorten` coalesces contiguous stream and memory ranges.

## Control Flow
List I/O helpers adjust partial extents to full extent-size operations, coalesce adjacent file and memory ranges, submit Trove list operations, and return an op id. `init_io_read` starts a `trove_bstream_read_at` for a single extent. `NCAC_check_ioreq` polls `trove_dspace_test` for the stored op id and invalidates it after completion. `do_read_for_rmw` reads a full extent into cache memory before write modification.

## State And Persistence
State changes include returned Trove op ids stored on extents or requests and cache memory contents filled by Trove. Persistence is external storage through Trove reads/writes; this file itself stores no durable metadata.

## Dependencies And Integration Points
Depends on Trove APIs, NCAC internal state, `aiovec`, and state helpers. Job and state code use it to start reads, flush dirty extents, and detect I/O completion.

## Risks And Test Signals
Risks include `NCAC_aio_read_ext` calling `trove_bstream_write_list` despite its read name, `offset_shorten` using `s_cnt` in the memory compaction loop, pointer arithmetic that can move memory offsets backward when aligning to extent boundaries, fixed dummy user pointer, and only single-op completion state. Tests should verify read/write direction, coalescing correctness, alignment behavior, pending-op completion, and dirty flush data reaching Trove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-trove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-trove.h -->
# sources/distributed-fs/orangefs/src/io/buffer/ncac-trove.h

## Purpose
Declares NCAC storage/Trove helper functions.

## Important APIs, Types, And Functions
Declares `NCAC_aio_read_ext`, `NCAC_aio_write`, `do_read_for_rmw`, and `init_io_read`.

## Control Flow
NCAC workers call these functions to start list reads/writes, read extents for read-modify-write, and initiate single-extent reads.

## State And Persistence
No state is defined directly. Functions return Trove op ids through output pointers and operate on cache memory buffers.

## Dependencies And Integration Points
Requires PVFS/Trove types, `struct aiovec`, and `struct extent` from surrounding includes. It is used by job and state modules.

## Risks And Test Signals
Risks are type drift for `ioreq` output (`int *` in some prototypes versus `PVFS_id_gen_t *` for `init_io_read`) and mismatch between read/write naming and implementation. Compile and Trove integration tests are needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/ncac-trove.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/radix.c -->
# sources/distributed-fs/orangefs/src/io/buffer/radix.c

## Purpose
Implements a standalone radix search tree used as an inode page tree for mapping extent indexes to `struct extent` pointers.

## Important APIs, Types, And Functions
Public functions are `rst_alloc`, `rst_free`, `rst_insert`, `rst_find`, `rst_delete`, and `rst_init`. Internal helpers are `rst_free_dfs`, unused `rst_find_min`, and unused `rst_finalize`.

## Control Flow
Insert traverses key bits from most significant to least, creates internal nodes only when needed to distinguish colliding key paths, and rejects duplicate keys by returning the existing item. Find traverses by key bits until reaching an item slot and validates via `get_value`. Delete records the traversal stack, removes the item, collapses unnecessary internal nodes, and returns the deleted item.

## State And Persistence
State is an in-memory tree with root node, node count, max bit depth, traversal stack, path-info stack, and `get_value` callback. No persistence exists. `rst_init` initializes an embedded tree root; `rst_alloc` creates heap-owned roots.

## Dependencies And Integration Points
`radix.h` wraps these functions with Linux-like `radix_tree_lookup/insert/delete` helpers used by NCAC inode page trees.

## Risks And Test Signals
Risks include no allocation failure checks in `rst_alloc/rst_init`, stack depth limited by `max_b`, comments noting non-commercial algorithm risk, possible `n` counter not decremented on delete, and no cleanup path for embedded trees in NCAC inodes. Tests should cover insert/find/delete for sparse keys, duplicate inserts, delete root/branch collapse cases, and allocation failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/radix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/radix.h -->
# sources/distributed-fs/orangefs/src/io/buffer/radix.h

## Purpose
Declares radix search tree types and Linux-like wrapper functions for NCAC extent lookup.

## Important APIs, Types, And Functions
Defines `rst_node_t`, `rst_t`/`struct radix_tree_root`, radix core prototypes, inline `radix_tree_lookup`, `radix_tree_insert`, `radix_tree_delete`, `init_single_radix_tree`, and `RADIX_MAX_BITS` of 24.

## Control Flow
Callers initialize a tree with a key extractor, then insert, look up, and delete items by unsigned long index through the inline wrappers.

## State And Persistence
No global state exists. Each tree stores node pointers, traversal stacks, max key bits, and key extractor callback.

## Dependencies And Integration Points
Used by `internal.h`/`cache.c` to map inode extent indexes. Its wrapper names intentionally mimic kernel radix-tree APIs.

## Risks And Test Signals
Risks include 24-bit index limit by default, allocation hidden in initialization, and wrappers reducing duplicate insert information to `-1`. Tests should cover maximum index behavior and duplicate handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/radix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/state.c -->
# sources/distributed-fs/orangefs/src/io/buffer/state.c

## Purpose
Implements NCAC extent state transitions for read/write access, communication completion, dirty tracking, synchronous dirty flush, pending I/O completion propagation, and read-modify-write locking.

## Important APIs, Types, And Functions
Exports `NCAC_extent_read_access`, `NCAC_extent_write_access`, `NCAC_extent_first_read_access`, `NCAC_extent_first_write_access`, `NCAC_extent_done_access`, `NCAC_extent_read_comm_done`, `NCAC_extent_write_comm_done`, `list_set_clean_page`, `NCAC_extent_read_access_recheck`, `NCAC_extent_write_access_recheck`, `data_sync_inode`, and `mark_extent_rmw_lock`.

## Control Flow
Read access increments read count, promotes inactive LRU extents, waits behind writes or pending I/O, and marks read communication when data is clean/dirty. Write access increments write count, waits behind earlier read/write communication or pending I/O, and marks write communication when safe. Done access clears communication flags, decrements/increments completion counters, marks written extents dirty, adds them to inode dirty list, and aggressively calls `data_sync_inode` unless `LAZY_SYNC` is defined. Dirty sync builds Trove list I/O arrays, submits a write, links all dirty extents through `ioreq_next`, marks them write-pending, and clears inode dirty count.

## State And Persistence
Mutates extent flags, read/write counters, completion counters, dirty lists, inode dirty counts, cache dirty counts, and Trove op ids. Persistence occurs only when dirty extents are flushed to Trove via `NCAC_aio_write`.

## Dependencies And Integration Points
Depends on internal NCAC structures, cache/list helpers, flag macros, and `ncac-trove`. It is called from job workers, request completion, eviction, and RMW paths.

## Risks And Test Signals
Risks include complex counter semantics, aggressive sync on every write completion, disabled `balance_dirty_extents`, no free of `data_sync_inode` temporary arrays, possible circular `ioreq_next` assumptions, and return values where completion may still report not ready. Tests should cover read/write transition matrices, pending I/O completion, dirty flush, RMW state, cache dirty counters, and repeated completion of shared extents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/state.h -->
# sources/distributed-fs/orangefs/src/io/buffer/state.h

## Purpose
Declares NCAC extent state-transition functions and allocation-mode constants.

## Important APIs, Types, And Functions
Defines `BLOCKING_EXTENT_ALLOC` and `NONBLOCKING_EXTENT_ALLOC`. Declares read/write access, first-access, communication-done, I/O check, recheck, request done-access, RMW mark, and clean-page propagation helpers.

## Control Flow
Job and cache-policy code use these functions when acquiring extents, checking pending I/O, finishing communication, and preparing eviction or dirty flush.

## State And Persistence
No direct state. Implementations mutate `NCAC_req_t` and `struct extent` state.

## Dependencies And Integration Points
Requires NCAC internal type declarations from including files. It is included by cache, job, internal, LRU, and Trove modules.

## Risks And Test Signals
Risks are declaration drift and missing documentation of return-value meanings. Build coverage plus state-transition unit tests are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/buffer/state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/dist-basic.c -->
# sources/distributed-fs/orangefs/src/io/description/dist-basic.c

## Purpose
Implements the basic OrangeFS distribution where all data resides on a single data file/server.

## Important APIs, Types, And Functions
Defines static distribution methods for logical/physical offset identity mapping, next mapped offset, fixed contiguous length, logical file size, one-data-file selection, block size, empty parameter encode/decode, registration/unregistration, and params string. Exports `PINT_dist basic_dist`.

## Control Flow
All offset conversions return the input offset. `logical_file_size` returns `psizes[0]` and errors on NULL. `get_num_dfiles` always returns one. Method table `basic_methods` is attached to `basic_dist` for registry lookup and encoding/decoding.

## State And Persistence
Uses a static zero-sized parameter struct and static method table. No runtime persistence exists beyond distribution registration.

## Dependencies And Integration Points
Depends on `pint-distribution.h`, `pint-dist-utils.h`, PVFS types, and `pvfs2-dist-basic.h`. Registered by `PINT_dist_initialize`.

## Risks And Test Signals
Risks are minimal, but `contiguous_length` returns arbitrary 64 KiB chunks rather than unlimited contiguity and parameter encoding is intentionally empty. Tests should verify one-data-file selection, identity mappings, logical size from first physical size, and encode/decode of zero-parameter distribution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/dist-basic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/dist-simple-stripe.c -->
# sources/distributed-fs/orangefs/src/io/description/dist-simple-stripe.c

## Purpose
Implements the default simple stripe distribution that round-robin stripes fixed-size strips across all selected data files.

## Important APIs, Types, And Functions
Defines methods for `logical_to_physical_offset`, `physical_to_logical_offset`, `next_mapped_offset`, `contiguous_length`, `logical_file_size`, parameter encode/decode, registration/unregistration, params string, block-size reporting, and exports `PINT_dist simple_stripe_dist`.

## Control Flow
Logical-to-physical divides the logical offset into full global stripes and leftover bytes, then determines whether the leftover belongs to this server's strip. Physical-to-logical reverses by combining physical strip number, server number, and strip remainder. `logical_file_size` maps each server's physical size back to a logical endpoint and returns the maximum. `next_mapped_offset` moves arbitrary logical offsets to the next byte mapped to this server. Registration exposes `strip_size` to default parameter setting.

## State And Persistence
Static state is default `PVFS_simple_stripe_params` and method table. Per-file distribution copies hold their own parameter blob after creation/decoding.

## Dependencies And Integration Points
Uses distribution registry APIs, PVFS encode helpers, `pvfs2-dist-simple-stripe.h`, and `pvfs2-util.h`. Called by request distribution logic through `PINT_dist_methods`.

## Risks And Test Signals
Risks include divide/modulo by zero if strip size is invalid, subtle off-by-one handling around exact strip boundaries, and `next_mapped_offset` handling negative modulo cases. Tests should round-trip physical/logical offsets across multiple server counts, strip sizes, boundary offsets, logical file size reconstruction, and parameter encode/decode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/dist-simple-stripe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/dist-twod-stripe.c -->
# sources/distributed-fs/orangefs/src/io/description/dist-twod-stripe.c

## Purpose
Implements a two-dimensional stripe distribution that partitions servers into groups, stripes within a group for a configurable factor, then advances across groups.

## Important APIs, Types, And Functions
Defines methods for logical/physical mapping, next mapped offset, contiguous length, logical file size, custom parameter setting, parameter encode/decode, registration/unregistration, params string, block size, default params, and exports `PINT_dist twod_stripe_dist`.

## Control Flow
Mapping functions compute effective group count, small group size, server's group, servers in that group, group-local server number, global stripe size, and per-group offsets. Logical-to-physical accumulates full global stripes and, when the logical offset falls inside this server's group, adds group strip progress. Physical-to-logical reconstructs the global logical position from physical strip count, group position, and server position. `next_mapped_offset` advances an arbitrary logical offset to this server's next represented byte. Parameter setting validates positive `strip_size`, `num_groups`, and `group_strip_factor` before copying.

## State And Persistence
Static default params include default groups, strip size, and factor. Per-distribution instances persist params in encoded metadata. No other persistent state exists.

## Dependencies And Integration Points
Depends on PVFS encode stubs, `pint-distribution.h`, `pint-dist-utils.h`, `pvfs2-dist-twod-stripe.h`, logging, and utility macros. Registered by distribution initialization.

## Risks And Test Signals
Risks include division by zero if invalid parameters still flow after logging, behavior when `num_groups > server_ct`, uneven last-group math, `physical_to_logical_offset` using `strips > factor` versus `>=`, and complex boundary cases. Tests should cover even and uneven group partitions, group counts larger than servers, strip-factor boundaries, parameter encode/decode, and offset round trips for every server.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/dist-twod-stripe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/dist-varstrip-parser.c -->
# sources/distributed-fs/orangefs/src/io/description/dist-varstrip-parser.c

## Purpose
Parses variable-stripe distribution parameter strings into an ordered array of strip descriptors.

## Important APIs, Types, And Functions
Exports `PINT_dist_strips_parse` and `PINT_dist_strips_free_mem`. Private helpers are `strips_parse_elem` and `strips_alloc_mem`.

## Control Flow
The parser copies the input into a bounded local buffer, allocates one descriptor per colon in the string, then repeatedly parses `<server>:<size>[K|M|G]` elements using `strtok_r`. Each strip offset is the previous offset plus previous size. Size suffixes scale by powers of 1024. Parsing stops when no next server token exists and returns the count.

## State And Persistence
Allocates an array that callers must release with `PINT_dist_strips_free_mem`. No global state or persistence exists.

## Dependencies And Integration Points
Used by `dist-varstrip.c` to interpret `PVFS_varstrip_params.strips`. Depends on PVFS size/offset types and varstrip max string length.

## Risks And Test Signals
Risks include `atoi/atoll` accepting malformed prefixes, no overflow checks for suffix multiplication, repeated `strlen` scans, and comment typo around counting separators. Tests should parse valid multi-strip strings, invalid/missing/too-long inputs, zero/negative sizes, suffixes, malformed tokens, and free behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/dist-varstrip-parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/dist-varstrip-parser.h -->
# sources/distributed-fs/orangefs/src/io/description/dist-varstrip-parser.h

## Purpose
Declares the varstrip parser descriptor type and parser/free functions.

## Important APIs, Types, And Functions
Defines `struct PINT_dist_strips_s` with `server_nr`, `offset`, and `size`; typedefs `PINT_dist_strips`; declares `PINT_dist_strips_parse` and `PINT_dist_strips_free_mem`.

## Control Flow
Consumers parse a string into a dynamically allocated descriptor array and free it after mapping calculations.

## State And Persistence
The header defines no state. Parsed arrays are caller-managed heap memory.

## Dependencies And Integration Points
Includes `pvfs2-internal.h` and `pvfs2-types.h`; consumed by `dist-varstrip.c`.

## Risks And Test Signals
Risks are declaration drift and lack of ownership comments beyond function names. Parser unit tests and compile coverage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/dist-varstrip-parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/dist-varstrip.c -->
# sources/distributed-fs/orangefs/src/io/description/dist-varstrip.c

## Purpose
Implements the variable-stripe distribution, where a parameter string defines an arbitrary repeating sequence of strips assigned to data-file numbers.

## Important APIs, Types, And Functions
Defines methods for logical-to-physical and physical-to-logical mapping, next mapped offset, contiguous length, logical file size, data-file count, custom parameter setting, encode/decode, registration/unregistration, params string, block size, and exports `PINT_dist varstrip_dist`.

## Control Flow
Most methods parse `params->strips` into strip descriptors on every call. Logical-to-physical finds the stripe repeat, locates the strip on the current server containing the logical offset, and accounts for earlier strips assigned to the same server. Physical-to-logical computes the stripe number from total strips assigned to this server and finds the descriptor containing the physical in-stripe offset. `next_mapped_offset` finds the current descriptor and either returns the logical offset, a later strip for this server, or the first strip for this server in the next stripe. `get_num_dfiles` verifies all data-file numbers from zero through the maximum appear and fit within available servers.

## State And Persistence
Static default params contain an empty strip string. Actual distribution instances persist the strip string in encoded metadata. Parsed strip arrays are temporary heap allocations.

## Dependencies And Integration Points
Depends on `pint-distribution`, `pint-dist-utils`, `pvfs2-dist-varstrip.h`, `dist-varstrip-parser`, and gossip logging. Registered by `PINT_dist_initialize`.

## Risks And Test Signals
Risks include repeated parsing overhead, incomplete logical-to-physical handling for offsets not mapped to the current server, possible memory leak on some `get_num_dfiles` error returns, no explicit rejection of unknown parameter names, and divide by zero if a server has no strips despite validation gaps. Tests should cover valid variable layouts, missing server numbers, too many data files, next-mapped wrapping, physical/logical round trips, contiguous lengths, and encode/decode of strip strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/dist-varstrip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/module.mk.in -->
# sources/distributed-fs/orangefs/src/io/description/module.mk.in

## Purpose
Adds request-description and distribution source files to OrangeFS library and server builds.

## Important APIs, Types, And Functions
Appends `pvfs-request.c`, `pint-request.c`, `pint-distribution.c`, `pint-dist-utils.c`, `dist-basic.c`, `dist-simple-stripe.c`, `dist-varstrip-parser.c`, `dist-twod-stripe.c`, and `dist-varstrip.c` to both `LIBSRC` and `SERVERSRC`.

## Control Flow
No runtime control flow. It controls which distribution and request-description modules are compiled into client/library and server targets.

## State And Persistence
No runtime state exists. Build membership is the persistent project effect.

## Dependencies And Integration Points
Integrates all built-in distributions and request encoders with both client and server code, which is necessary because distributions are encoded/decoded and evaluated on both sides.

## Risks And Test Signals
Risks are build omissions if a new distribution is added without this file, or duplicate registration if sources are included twice elsewhere. Configure/build success and distribution availability tests are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/pint-dist-utils.c -->
# sources/distributed-fs/orangefs/src/io/description/pint-dist-utils.c

## Purpose
Registers built-in distributions and manages a small parameter-offset table used by distribution `set_param` implementations.

## Important APIs, Types, And Functions
Exports `PINT_dist_initialize`, `PINT_dist_finalize`, `PINT_dist_default_get_num_dfiles`, `PINT_dist_default_set_param`, `PINT_dist_register_param_offset`, and `PINT_dist_unregister_param_offset`. Private type `PINT_dist_param_offset` records distribution name, parameter name, field offset, and field size.

## Control Flow
Initialization registers `basic`, `varstrip`, `simple_stripe`, and `twod_stripe` distributions. Finalization unregisters them and frees the parameter table. Registration grows the table in increments of ten, allocates name strings, stores offset/size metadata, and increments entry count. Default parameter setting looks up a `(dist,param)` row and `memcpy`s the provided value into the parameter blob. Unregistration frees matching strings and bubbles later entries down.

## State And Persistence
State is an in-memory global parameter table and distribution registry entries. No durable persistence exists, but encoded distributions depend on these registrations being active during decode/lookup.

## Dependencies And Integration Points
Depends on built-in distribution globals, `pint-distribution.h`, dist-specific headers, and server configuration type. Called during OrangeFS distribution subsystem startup/shutdown.

## Risks And Test Signals
Risks include not freeing individual dist/param strings in `PINT_dist_finalize` before freeing the table, leak if param-name allocation fails after dist-name allocation, no duplicate registration check, and default setter only supporting plain POD fields. Tests should cover init/finalize cycles, param set/unregister, duplicate params, allocation failures, and distribution lookup after registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/pint-dist-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/pint-dist-utils.h -->
# sources/distributed-fs/orangefs/src/io/description/pint-dist-utils.h

## Purpose
Declares distribution utility functions and macros for initialization, finalization, default data-file selection, default parameter setting, and parameter offset registration.

## Important APIs, Types, And Functions
Declares `PINT_dist_initialize`, `PINT_dist_finalize`, `PINT_dist_default_get_num_dfiles`, `PINT_dist_default_set_param`, `PINT_dist_register_param_offset`, and `PINT_dist_unregister_param_offset`. Defines `PINT_dist_register_param` and `PINT_dist_unregister_param` macros.

## Control Flow
Distribution implementations call register/unregister macros in their method registration hooks. Startup code calls initialize/finalize to populate and tear down the distribution registry.

## State And Persistence
No direct state. Utilities manage process-local distribution and parameter registries in the `.c` file.

## Dependencies And Integration Points
Includes `pint-distribution.h` and `server-config.h`. It is used by all built-in distribution implementations.

## Risks And Test Signals
Risks include offsetof macro technique only being safe for simple fields and the need for every registered parameter to be unregistered. Build coverage and parameter setting tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/pint-dist-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/pint-distribution.c -->
# sources/distributed-fs/orangefs/src/io/description/pint-distribution.c

## Purpose
Implements the core distribution registry, cloning/copying/freeing distribution descriptors, parameter get/set helpers, packed encode/decode wrappers, lookup, and debug dump.

## Important APIs, Types, And Functions
Exports `PINT_register_distribution`, `PINT_unregister_distribution`, `PINT_dist_create`, `PINT_dist_free`, `PINT_dist_copy`, `PINT_dist_getparams`, `PINT_dist_setparams`, `PINT_dist_lookup`, `PINT_dist_encode`, `PINT_dist_decode`, and `PINT_dist_dump`. Global private state is `PINT_Dist_table` and `PINT_Dist_count`.

## Control Flow
Registration appends a static distribution to the fixed table and calls its `registration_init`. Unregistration finds by name, calls `unregister`, bubbles table entries down, and clears the last slot. `PINT_dist_create` looks up a named static distribution, allocates one contiguous packed object, copies the name and params into that object, and keeps method pointers shared. Copy duplicates an already packed distribution and fixes internal pointers. Encode/decode defer to macros that serialize the name and method-specific params.

## State And Persistence
State is a fixed-size in-memory table of registered distributions. Packed distribution objects are heap allocations owned by callers. Encoded distributions are persistent metadata only when stored by higher layers; this file just packs/unpacks buffers.

## Dependencies And Integration Points
Depends on `pint-distribution.h`, encode stubs, gossip logging, and built-in distribution globals. Used by request encode/decode and distribution evaluation across clients and servers.

## Risks And Test Signals
Risks include a hard table size of eight, no duplicate registration checks, `PINT_dist_create` copying only `strlen+1` bytes of name while using rounded name space, decode macros exiting the process on missing methods, and shallow sharing of method tables. Tests should cover registry overflow, duplicate names, create/copy/free, parameter get/set, encode/decode before and after initialization, and lookup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/pint-distribution.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/pint-distribution.h -->
# sources/distributed-fs/orangefs/src/io/description/pint-distribution.h

## Purpose
Defines the OrangeFS internal distribution abstraction, its method table, packed-size and encode/decode macros, and registry/copy APIs.

## Important APIs, Types, And Functions
Defines `PINT_DIST_NAME_SZ`, `PINT_dist_methods`, `PINT_dist`, `PINT_DIST_PACK_SIZE`, `encode_PINT_dist`, `decode_PINT_dist`, and prototypes for create/free/copy/getparams/setparams/lookup/encode/decode/dump/register/unregister.

## Control Flow
Consumers create or decode a `PINT_dist`, then call its method table for offset mapping, contiguous length, logical file size, data-file count, parameter setting, block size, parameter encode/decode, and lifecycle hooks.

## State And Persistence
Defines packed distribution layout: structure, rounded name bytes, and rounded parameter bytes in one allocation. Decode allocates a packed object and fixes internal pointers. Persistent encoded form contains distribution name and parameter payload, not function pointers.

## Dependencies And Integration Points
Includes `pint-request.h` for `PINT_request_file_data` and PVFS types. Distribution implementations populate `PINT_dist_methods`; request encoding and metadata storage use the encode/decode macros.

## Risks And Test Signals
Risks include macros that call `exit(1)` on decode/encode method lookup failure, pointer fix-up complexity, and reliance on distribution registry being initialized before decode. Tests should verify packed-size layout, encode/decode for every built-in distribution, and behavior for unknown distribution names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/pint-distribution.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/pint-request-encode.h -->
# sources/distributed-fs/orangefs/src/io/description/pint-request-encode.h

## Purpose
Provides inline helpers to encode and decode `PINT_Request` trees by linearizing nested request structures into a contiguous array with pointer fields represented as encoded offsets/integers.

## Important APIs, Types, And Functions
Defines `PVFS_REQ_LIMIT_PINT_REQUEST_NUM` as 100. Inline functions are `linearize_PVFS_Request`, `encode_PVFS_Request_fields`, `encode_linearized_PVFS_Request`, `encode_PINT_Request`, and `decode_PINT_Request`.

## Control Flow
Encoding verifies nested request count, allocates a linearized request array, commits the request tree into it, encodes pointer fields into relocatable form, writes the nested count and all request fields, then frees the temporary array. Decoding reads the nested count, allocates an array, decodes scalar fields, stores encoded `ereq`/`sreq` integers into pointer fields, and leaves final pointer repair to `PINT_Request_decode`.

## State And Persistence
No global state exists. Encoded buffers persist request layout for transport/storage. Decode uses `decode_malloc`; callers must later free through the request decode/free path.

## Dependencies And Integration Points
Depends on PVFS encode/decode helpers, `PINT_request_commit`, `PINT_request_encode`, `PINT_Request_decode`, and request struct definitions from including context. Included by `pint-request.h`.

## Risks And Test Signals
Risks include the hard nesting limit of 100, encoding pointer offsets through 32-bit integers via `uintptr_t` casts, allocation/free family consistency (`decode_malloc` with `free` or `decode_free`), and reliance on later pointer fix-up. Tests should encode/decode nested request trees at boundaries, invalid over-limit trees, 64-bit builds, and request structures with multiple `ereq`/`sreq` relationships.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/description/pint-request-encode.h -->
