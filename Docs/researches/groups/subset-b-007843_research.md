# Research: subset-b-007843

Grouped source research for OrangeFS common miscellaneous support code. Each section preserves the original source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/mkspace.c -->
# sources/distributed-fs/orangefs/src/common/misc/mkspace.c

Purpose: Implements the server-side storage-space and collection creation/removal helpers used by OrangeFS tooling to initialize or remove TROVE-backed filesystem storage. `pvfs2_mkspace()` creates DBPF storage spaces when requested, creates a TROVE collection, installs handle ranges, optionally creates the root directory handle, stores the root handle collection eattr, and seeds root directory attributes. `pvfs2_rmspace()` removes a collection and optionally removes the entire DBPF storage space.

Important APIs and functions: `pvfs2_mkspace()` is the main create path and consumes data/meta paths, collection name/id, requested root handle, meta/data handle range strings, a collection-only flag, and verbosity. `pvfs2_rmspace()` is the destructive cleanup path. The local `mkspace_print` macro routes output to gossip or stderr. `s_used_handles` records handles allocated by this process, though the active code only stores the root handle; older exclusion helpers are disabled under `#if 0`.

Control flow: `pvfs2_mkspace()` warns when metadata or data paths appear to be on the root device, rejects pre-existing storage when creating a full storage space, creates storage, initializes TROVE, verifies the collection does not already exist, creates and looks up the collection, opens a TROVE context, merges meta/data handle range strings, and passes them to `TROVE_COLLECTION_HANDLE_RANGES`. If a root handle is requested, it creates a forced-handle directory dataspace, waits for completion through `trove_dspace_test()`, writes `ROOT_HANDLE_KEYSTR`, fills `TROVE_ds_attributes_s`, and writes attributes synchronously. Cleanup closes the context, finalizes TROVE, and frees temporary arrays. `pvfs2_rmspace()` lazily initializes TROVE once, removes the collection, and removes storage only when not in collection-only mode.

State and persistence behavior: Persistent state is the DBPF storage space on `data_path`/`meta_path`, the TROVE collection, collection-level root-handle eattr, handle allocator ranges, and root directory dataspace attributes. In-memory state includes `trove_is_initialized` in removal, `s_used_handles`, the server config pointer obtained from `PINT_server_config_mgr_get_config()`, and the opened TROVE context. Failure paths can leave partially-created persistent storage or collections because cleanup is limited and there is no rollback sequence after collection creation or root setup.

Dependencies and integration points: Integrates with TROVE DBPF APIs, server config manager, handle range utilities (`PINT_merge_handle_range_strs()`), internal PVFS key strings, time helpers, and gossip logging. It participates in filesystem provisioning and is built into server-side sources via `module.mk.in`. Root directory distributed-dir and lost+found creation are explicitly delegated to `pvfs2-server.c`.

Risks and test signals: Error handling should be tested for existing storage, bad handle range strings, bad forced root handle, failed `trove_collection_seteattr()`, and collection-only operation. `stat()` return values are ignored before device comparison. Several early returns skip `trove_close_context()` or `trove_finalize()`, making resource cleanup and partial persistent state important regression targets. Tests should verify full create/remove round trips, root-handle eattr readability, range enforcement, and behavior when meta/data ranges overlap or are malformed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/mkspace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/mkspace.h -->
# sources/distributed-fs/orangefs/src/common/misc/mkspace.h

Purpose: Declares the public interface for creating and removing OrangeFS/TROVE storage spaces and collections. It is a small server/tooling header that exposes the two implementation functions in `mkspace.c` and the verbosity selectors used by callers.

Important APIs and types: `PVFS2_MKSPACE_GOSSIP_VERBOSE` selects gossip debug output, while `PVFS2_MKSPACE_STDERR_VERBOSE` selects direct stderr output. `pvfs2_mkspace()` accepts storage paths, collection name and id, root handle, metadata/data handle range strings, a collection-only mode flag, and a verbosity mode. `pvfs2_rmspace()` accepts the same storage identity and collection id plus a removal-only flag.

Control flow and integration: The header itself has no control flow; it supplies the provisioning contract to utilities and server code that need to manipulate storage spaces. It includes `pvfs2-internal.h` and `trove.h`, so callers see the `TROVE_coll_id` and `TROVE_handle` types required by the function signatures.

State and persistence behavior: The declarations describe functions that mutate persistent DBPF/TROVE storage and collections, but the header owns no state. The collection-only and remove-collection-only flags are key semantic controls for whether the storage directories themselves are created or removed.

Dependencies and risks: Because this header exposes destructive filesystem provisioning operations, callers must pass validated paths, collection ids, and range strings. ABI or signature changes affect server utilities that compile against `mkspace.h`. Test signals are compile coverage for all callers and runtime coverage of both full-space and collection-only modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/mkspace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/mmap-ra-cache.c -->
# sources/distributed-fs/orangefs/src/common/misc/mmap-ra-cache.c

Purpose: Implements an mmap-oriented readahead cache used by the client core for workloads that issue many small reads, such as mmap or executable access. It maintains a global cache of aligned buffers indexed by `PVFS_object_ref`, tracks pending VFS requests waiting for fills, and returns status codes that tell the I/O path whether to use cached data, wait, post readahead, or fall back to normal I/O.

Important APIs and functions: Initialization and tuning are handled by `pint_racache_initialize()`, `pint_racache_buf_resize()`, `pint_racache_set_buff_count_size()`, `pint_racache_set_read_count()`, and `pint_racache_set_pinned()`. The hot path is `pint_racache_get_block()`, which returns `RACACHE_HIT`, `RACACHE_WAIT`, `RACACHE_READ`, `RACACHE_NONE`, or an error. `pint_racache_flush()` removes all cached buffers for a file, `pint_racache_make_free()` returns a completed buffer to the free list, `pint_racache_finish_resize()` frees old busy buffers after resize, and `pint_racache_finalize()` releases hash tables and backing memory.

Control flow: Initialization sizes the global `racache`, allocates page-aligned buffers, optionally faults and `mlock()`s them, links them on the free list, and creates a quickhash table. `pint_racache_get_block()` locks the cache, looks up a file record, scans its buffer list for a covering block, and either returns a valid hit, queues the VFS request on an invalid buffer, allocates or evicts a buffer for a miss, or creates a new file record. Buffer selection prefers the free list, then the LRU list if the candidate has no waiters. Flush removes file records from the hash table and either marks busy buffers `being_freed` or returns idle buffers to the free list. Resize culls active buffers into `oldarray`, destroys the hash table, recreates storage, and relies on later completion to drain old busy buffers.

State and persistence behavior: State is entirely process-local and global: `racache` holds the mutex, size tunables, free/LRU lists, file hash table, active buffer array, old resizing array, and counters; `lock_mem` permanently disables future memory locking after the first `mlock()` failure. Buffers carry validity, waiter count/list, data size, file offset, read-ahead count, resize/free flags, and file ownership. No data is persisted, but stale state directly affects client read behavior until flushed, resized, or finalized.

Dependencies and integration points: Uses `quickhash`, `quicklist`, `gen-locks`, `PVFS_object_ref`, gossip logging, POSIX `posix_memalign()`, `mlock()`, `munlock()`, and `sysconf()`. The caller is responsible for actually issuing reads into returned buffers and later marking/freeing buffers; this module only orchestrates cache metadata and waiter lists.

Risks and test signals: Allocation error paths are fragile, including missing unlocks in one `glink` allocation failure path and unchecked `posix_memalign()` return semantics. Resize/free paths contain suspicious operations such as `memset(&racache.buffarray[i], ...)` in `pint_racache_finish_resize()` when freeing `oldarray` entries, and a `munlock()` retry loop that never assigns the return value. `pint_racache_finalize()` destroys the mutex after unlocking with a FIXME race note. Tests should stress hits, invalid-buffer waiters, speculative readahead, flush with in-flight reads, resize with waiters, zero-count/size disabling, pinned-memory failure, and concurrent get/flush/finalize behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/mmap-ra-cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/mmap-ra-cache.h -->
# sources/distributed-fs/orangefs/src/common/misc/mmap-ra-cache.h

Purpose: Defines the public data structures, defaults, status codes, and function prototypes for the mmap readahead cache. It is the contract between client-core I/O code and `mmap-ra-cache.c`.

Important APIs and types: Default and maximum tunables include buffer size/count, read count, and pinned-memory setting. Status constants distinguish no cache, valid hit, wait-on-fill, need-read, and posted-read states. `gen_link_t` wraps queued VFS request payloads. `racache_file_t` indexes cached buffers by `PVFS_object_ref` and per-file read count. `racache_buffer_t` holds list links, validity/free/resize flags, buffer id, waiter count, file offset, data size, buffer size, read count, raw buffer pointer, and owning file. `racache_t` is the singleton cache state with mutex, tunables, free/LRU lists, quickhash table, active buffer array, and old resize array.

Control flow and integration: Consumers initialize the cache, tune counts/sizes/read-ahead/pinning, call `pint_racache_get_block()` before normal I/O, fill returned buffers when `RACACHE_READ` is returned, call `pint_racache_make_free()` when buffers are reusable, flush per file, and finalize on shutdown. `pint_racache_buff_offset()` standardizes cache-line alignment for file offsets.

State and persistence behavior: The header exposes mutable state types but does not define the singleton. All state is volatile process memory and is meant to optimize reads rather than persist correctness data. The wait-list fields make buffer lifetime depend on external request completion.

Dependencies and risks: Depends on quickhash, PVFS internal types, and quicklist-compatible list links. External callers can see internal structures, so invariants such as list membership, `valid`, `vfs_cnt`, `being_freed`, and `resizing` must be honored by all users. Test signals include compile compatibility with client-core call sites and ABI-level validation that status codes are interpreted consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/mmap-ra-cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/module.mk.in -->
# sources/distributed-fs/orangefs/src/common/misc/module.mk.in

Purpose: Build-system fragment that registers common miscellaneous OrangeFS sources into library, server, and BMI-library source lists. It also declares state-machine-generated C outputs.

Important build variables: `DIR` points to `src/common/misc`. `LIBSRC` includes general utility modules used by libraries, including server config, string/digest/xattr utilities, mmap readahead cache, extent utilities, perf counters, event tracing, cached config, message pair arrays, state-machine helpers, eattr, malloc, hints, memory, UID management, distributed directory utilities, and MD5. `SERVERSRC` includes overlapping server-side utility sources plus `mkspace.c`. `LIBBMISRC` includes the small subset needed by BMI. `SMCGEN` lists generated `msgpairarray.c` and `void.c`.

Control flow and integration: This make fragment has no runtime control flow; it controls compilation and linkage boundaries. The notable integration signal is that `mkspace.c` is server-only, while `mmap-ra-cache.c` is in common library sources, and `pint-event.c`, `pint-mem.c`, and `pint-malloc.c` participate in multiple build products.

State and persistence behavior: Build metadata only; persistent effect is on generated make output and linked binaries. Incorrect source placement changes which components export or depend on utility functionality.

Risks and test signals: Regression tests are build-oriented: clean configure/build, generated state-machine source generation, static/shared library linkage, and platform-specific builds with or without optional features such as custom malloc and event tracing. Duplicate or missing source membership can produce symbol conflicts or unresolved references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/msgpairarray.h -->
# sources/distributed-fs/orangefs/src/common/misc/msgpairarray.h

Purpose: Declares the state-machine interface and state records used to send and receive one or more PVFS server request/response message pairs. It groups per-message request encoding, BMI addressing, job ids/status, retry state, and completion callbacks for generated `msgpairarray.c`.

Important APIs and types: `pvfs2_msgpairarray_sm` is the exported state machine. `PINT_sm_msgpair_state` holds filesystem id, target handle, retry flags/count, completion callback, server BMI address, session tag, server request, encoded request, encoding type, response buffer, send/recv job ids/status, operation status, and completion marker. `PINT_sm_msgpair_params` carries timeout, retry delay/limit, job context, quiet flag, and remaining completion count. `PINT_sm_msgarray_op` embeds either a single `msgpair` or an allocated `msgarray`. Macros initialize single-message operations and iterate arrays.

Control flow and integration: Callers fill `fs_id`, `handle`, `retry_flag`, and `comp_fn`, initialize a single or array operation, resolve addresses with `PINT_serv_msgpairarray_resolve_addrs()`, and enter the generated state machine. Completion callbacks inspect decoded server responses. Helper functions initialize/destroy arrays, compute aggregate status, decode responses, and release encoded/decoded resources.

State and persistence behavior: State is transient per state-machine operation. Persistent state is not modified by the header, but server requests carried in `req` can mutate filesystem state when processed remotely. The `retry_count`, `complete`, and job status fields govern idempotence and retry behavior.

Dependencies and risks: Depends on PVFS request protocol, encoding, BMI/job interfaces, and state machine generation. The `PINT_msgpair_init` and `PINT_init_msgpair` macros free existing dynamic arrays when switching back to a single embedded message; callers must not retain stale pointers. Tests should cover single vs multi-message initialization, address resolution, retry/no-retry paths, failed send/recv status, decode failures, and resource cleanup after partial completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/msgpairarray.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-cached-config.c -->
# sources/distributed-fs/orangefs/src/common/misc/pint-cached-config.c

Purpose: Implements the cached filesystem-configuration service used by clients and servers to map filesystem ids, handles, logical server roles, BMI addresses, and datafile layout decisions without repeatedly walking parsed configuration structures. It caches per-filesystem server arrays, handle lookup tables, local-server mappings, and root/timeout settings.

Important APIs and functions: Lifecycle functions are `PINT_cached_config_initialize()`, `PINT_cached_config_finalize()`, and `PINT_cached_config_reinitialize()`. Mapping load is done by `PINT_cached_config_handle_load_mapping()`. Lookup APIs include `PINT_cached_config_get_server()`, `PINT_cached_config_get_next_meta()`, `PINT_cached_config_map_servers()`, `PINT_cached_config_map_addr()`, `PINT_cached_config_map_to_server()`, `PINT_cached_config_check_type()`, `PINT_cached_config_count_servers()`, `PINT_cached_config_get_server_array()`, `PINT_cached_config_get_num_dfiles()`, `PINT_cached_config_get_num_meta()`, `PINT_cached_config_get_num_io()`, `PINT_cached_config_get_server_handle_count()`, `PINT_cached_config_get_server_name()`, `PINT_cached_config_get_root_handle()`, `PINT_cached_config_get_handle_timeout()`, `PINT_cached_config_get_server_list()`, and `PINT_cached_config_io_server_names()`.

Control flow: Initialization allocates the fsid hash table and seeds `rand()` with time, pid, hostname, and optionally SHA1-mixed entropy. Loading a mapping allocates `config_fs_cache_s`, stores the filesystem pointer, initializes cursors and local alias/mapping, builds a sorted handle lookup table by resolving every meta/data extent to BMI addresses, and adds the cache object by collection id. Server arrays are lazily populated by `cache_server_array()`, which resolves unique physical servers, merges meta/io role flags, and builds role-specific arrays. `PINT_cached_config_map_servers()` implements LIST, LOCAL, NONE, ROUND_ROBIN, and RANDOM datafile placement layouts. Handle-to-server lookups use `find_handle_lookup_entry()` with binary search over sorted extents.

State and persistence behavior: Global state is `PINT_fsid_config_cache_table`. Each cache entry owns cached arrays and the handle lookup table but only borrows `filesystem_configuration_s` and string pointers from server configuration. No persistent storage is written; the cache mirrors parsed config and BMI address mappings. `PINT_cached_config_finalize()` frees cached arrays and cache wrappers but deliberately leaves filesystem objects to `PINT_config_release()`.

Dependencies and integration points: Integrates with server config structures, `PINT_llist`, `quickhash`, BMI address lookup/reverse lookup, extent utilities, distribution methods (`PINT_dist`), PVFS system layout structures, and management server type flags. It is a central dependency for metadata placement, datafile placement, management queries, and handle routing.

Risks and test signals: There is little locking around the global cache, so concurrent reinitialize/finalize/lookups are risky. `PINT_cached_config_reinitialize()` returns `0` even after a load failure, losing the error. `find_handle_lookup_entry()` can compute `table_index = -1` when a handle is before the first extent, then dereference it. Some allocation failure paths leak partial allocations or return without freeing temporary arrays, for example `PINT_cached_config_get_server_list()` after `map_servers()` failure. Tests should cover every layout algorithm, local layout fallback, overlapping/empty/extreme handle extents, duplicate physical servers with combined roles, address resolution failures, fsid misses, concurrent reloads, and boundary handle values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-cached-config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-cached-config.h -->
# sources/distributed-fs/orangefs/src/common/misc/pint-cached-config.h

Purpose: Declares the cached configuration API for mapping OrangeFS filesystem configuration data into fast lookup services. It is the public interface for server arrays, handle routing, server typing, filesystem root metadata, and layout-aware datafile selection.

Important APIs and constants: `PINT_SERVER_TYPE_IO`, `PINT_SERVER_TYPE_META`, and `PINT_SERVER_TYPE_ALL` mirror management server flags. The API exposes lifecycle, load/reinitialize, alias/address mapping, role-specific server counts and arrays, handle-to-server mapping, datafile count calculation, root handle and handle timeout retrieval, server name/list retrieval, and IO server name listing.

Control flow and integration: Callers initialize the cache, load each parsed `filesystem_configuration_s` together with the owning `server_configuration_s`, then use lookup methods during request routing, datafile creation, management queries, and client system-interface setup. Several functions return borrowed pointers to cached or configuration-owned arrays; callers must not free or retain them beyond config cache lifetime unless explicitly documented.

State and persistence behavior: The header describes an in-memory cache only. It depends on stable parsed server configuration and BMI address mappings. Reinitialization refreshes all cached entries from a server configuration object.

Dependencies and risks: Includes PVFS internal/storage/management types, BMI, TROVE, and server config types. The API mixes borrowed-output semantics, caller-owned arrays, and allocated string-list outputs, so misuse can produce leaks or dangling pointers. Test signals include compile coverage of all users and lifecycle tests that validate no stale pointers remain after reinitialize/finalize.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-cached-config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-clean-malloc.h -->
# sources/distributed-fs/orangefs/src/common/misc/pint-clean-malloc.h

Purpose: Declares escape-hatch allocation functions that call the platform allocator directly instead of the OrangeFS malloc wrappers from `pint-malloc.h`. These are used when code must allocate memory compatible with external ownership or must avoid recursive macro interception.

Important APIs: The header declares clean variants for `malloc`, `calloc`, `posix_memalign`, `memalign`, `valloc`, `realloc`, `strdup`, `strndup`, and `free`. They are implemented in `pint-malloc.c` before the wrapper macros are included and undefined.

Control flow and integration: This header has no runtime logic. It is included by `pint-malloc.c` and can be used by code that needs uninstrumented allocation. The clean functions are especially relevant around stdio/client interfaces or external libraries that free memory outside OrangeFS wrapper conventions.

State and persistence behavior: No state is declared. The called allocator state is the process allocator state. These APIs intentionally bypass wrapper metadata, zeroing, magic checks, and debug tracing.

Risks and test signals: Memory returned by clean allocators must be freed with `clean_free()` or the real allocator, not `PINT_free()`, because it lacks the `extra_t` header used by wrapper allocations. Tests should cover mixed allocation ownership boundaries and ensure wrapper redefinition does not affect these functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-clean-malloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-eattr.c -->
# sources/distributed-fs/orangefs/src/common/misc/pint-eattr.c

Purpose: Implements extended-attribute namespace validation and special encoding/decoding for OrangeFS attributes, especially PVFS internal attributes exposed through `system.pvfs2.*` names. It protects set/list/get behavior from unsupported namespaces and normalizes internal key names.

Important APIs and functions: Public functions are `PINT_eattr_check_access()`, `PINT_eattr_namespace_verify()`, `PINT_eattr_system_verify()`, `PINT_eattr_list_access()`, `PINT_eattr_encode()`, and `PINT_eattr_decode()`. Internal check tables define accepted access namespaces, settable namespaces, system ACL checks, list-prefix handling, and encode/decode handlers. `PINT_handle_array` plus generated endecode helpers support endian-safe datafile handle arrays.

Control flow: All checks use `PINT_eattr_verify()`, which walks an ordered `PINT_eattr_check` array, matches namespace/key prefixes, returns configured error codes, or invokes a handler. Get/access strips `system.pvfs2.` before TROVE lookup. Set namespace verification rejects `system.pvfs2.` writes, accepts POSIX-like namespaces, and validates ACL sizes for supported system ACL names. List handling adds `system.pvfs2.` to internal keys that lack a standard namespace. Encoding recognizes `DATAFILE_HANDLES_KEYSTR`, replaces raw handle arrays with encoded buffers, and decoding reverses the public `system.pvfs2.dh` form.

State and persistence behavior: The module mutates caller-provided `PVFS_ds_keyval` buffers in place and may free/replace `val->buffer` during encode. Persistent xattr state is owned by TROVE; this module controls the names and byte layout used before storage or after retrieval.

Dependencies and integration points: Uses PVFS request limits, internal key strings, ACL structures, generated endecode functions, PVFS error codes, and memory allocation. It integrates with server eattr operations, xattr utilities, and tools such as viewdist that read datafile handle arrays.

Risks and test signals: `PINT_eattr_strip_prefix()` uses `sscanf()` into a fixed-size temporary buffer and assumes key buffer string termination. `PINT_eattr_add_pvfs_prefix()` relies on caller-provided buffer capacity and uses `sprintf()`. Decode frees `harray.handles` only on size error, so generated decode ownership must be verified. Tests should cover every namespace branch, malformed/non-terminated keys, ACL sizes, list prefix capacity errors, endian round trips for datafile handles, and set rejection for `system.pvfs2.*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-eattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-eattr.h -->
# sources/distributed-fs/orangefs/src/common/misc/pint-eattr.h

Purpose: Declares the extended-attribute validation and conversion interface used by OrangeFS server paths. It documents the separation between namespace access checks, set/list validation, and known-attribute encode/decode hooks.

Important APIs: `PINT_eattr_list_access()` validates attributes returned by list operations and adds the PVFS system prefix when needed. `PINT_eattr_check_access()` validates request attributes and strips PVFS internal prefixes for storage lookup. `PINT_eattr_namespace_verify()` checks whether a key can be set by users. `PINT_eattr_encode()` and `PINT_eattr_decode()` handle known special attributes such as datafile handle arrays.

Control flow and integration: The header is used by eattr/xattr request handling code before interacting with TROVE keyvals or returning attributes to clients. It includes PVFS internal and type definitions for `PVFS_ds_keyval`.

State and persistence behavior: No state is owned by the header. The declared functions can mutate key/value buffers supplied by callers, so callers must provide writable buffers with valid `buffer_sz` and `read_sz` fields.

Dependencies and risks: API users must account for negative PVFS error returns and for buffer ownership changes during encode. Test signals include compile coverage and request-path tests for namespace rejection, prefix stripping/adding, and cross-endian handle array conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-eattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-event.c -->
# sources/distributed-fs/orangefs/src/common/misc/pint-event.c

Purpose: Implements optional event tracing support for OrangeFS using event and group registries plus optional TAU trace emission. It lets code define named groups/events, enable/disable them by name or group, start/stop per-thread tracing, and emit start/end events when enabled.

Important APIs and functions: Lifecycle is `PINT_event_init()` and `PINT_event_finalize()`. Runtime controls are `PINT_event_enable()`, `PINT_event_disable()`, `PINT_event_thread_start()`, and `PINT_event_thread_stop()`. Definitions use `PINT_event_define_group()` and `PINT_event_define_event()`. Emission uses `PINT_event_start_event()` and `PINT_event_end_event()`; `PINT_event_log_event()`, `PINT_event_setinfo()`, and `PINT_event_getinfo()` are declared in the header but not implemented in the visible source. `PINT_event_enabled_mask` controls active events.

Control flow: Initialization creates event and group hash tables, defines a default group, and initializes TAU if requested and available. Group/event definitions allocate records, duplicate names, register ids with `id_gen_fast_register()`, link events into group lists, and assign event masks as `1 << event_count`. Enabling/disabling splits a string list, looks up event names first then group names, and updates the global mask; special values `all` and `none` set broad masks. Start/end functions look up event ids, test the mask, and forward variable arguments to TAU calls when compiled with TAU.

State and persistence behavior: Global in-memory state includes `events_table`, `groups_table`, `default_group`, `event_count`, and `PINT_event_enabled_mask`. TAU output may persist in trace files under the TAU-selected output folder, but this module otherwise owns no persistent storage.

Dependencies and integration points: Uses quickhash/quicklist, `id-generator`, string splitting utilities, gossip, PVFS management types, and optional TAU APIs. Header macros compile event calls to no-ops unless `__PVFS2_ENABLE_EVENT__` is set, so runtime availability also depends on build flags.

Risks and test signals: Mask assignment uses `1 << event_count`, which overflows after the width of an `int` despite storing in `uint64_t`. There is no apparent locking around global registries or enabled mask. Some allocation failure paths leak partially allocated group/event strings. The source contains a typo in a TAU-only forward declaration (`strcut`). Tests should cover builds with and without TAU/event flags, enable/disable unknown events, group masks, many events near mask limits, finalize after partial init, and linkage for all header-declared functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-event.h -->
# sources/distributed-fs/orangefs/src/common/misc/pint-event.h

Purpose: Declares the OrangeFS event tracing interface and hides tracing calls behind compile-time macros. It defines event, group, and id types, lifecycle/configuration APIs, event definition and emission APIs, and no-op behavior when event tracing is disabled.

Important APIs and types: `PINT_event_type`, `PINT_event_id`, and `PINT_event_group` are generated-id types. `enum PINT_event_method` currently names TAU tracing. `enum PINT_event_info` describes runtime options for max traces, blocking, and buffer size. Public functions cover init/finalize, enable/disable, set/get info, thread start/stop, group/event definitions, and start/end/log emission. `PINT_EVENT_START`, `PINT_EVENT_END`, and `PINT_EVENT_LOG` either call the runtime functions or compile to empty `do { } while(0)` blocks.

Control flow and integration: Callers use macros rather than raw functions when instrumentation should disappear from non-event builds. The macros support both Windows and GNU variadic syntax. `PINT_EVENT_ENABLED` allows compile-time feature checks.

State and persistence behavior: The header exposes `PINT_event_enabled_mask` as external global runtime state. No persistent data is managed by the header, though enabled tracing backends may write trace files.

Dependencies and risks: Depends on PVFS internal/types and quickhash. Several declared APIs require matching definitions at link time; implementations are feature-sensitive. Test signals include no-event builds proving macros erase instrumentation, event-enabled builds linking every declared function, and Windows/non-Windows variadic macro coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-hint.c -->
# sources/distributed-fs/orangefs/src/common/misc/pint-hint.c

Purpose: Implements OrangeFS/PVFS request hint management, including known hint metadata, linked-list storage, duplicate handling, encode/decode for transferable hints, copying/freeing, environment-variable import, and value lookup by type or name.

Important APIs and functions: Public operations include `PVFS_hint_add()`, `PVFS_hint_add_internal()`, `PVFS_hint_replace()`, `PVFS_hint_replace_internal()`, `PVFS_hint_check()`, `PVFS_hint_check_transfer()`, `encode_PINT_hint()`, `decode_PINT_hint()`, `PVFS_hint_copy()`, `PVFS_hint_free()`, `PVFS_hint_import_env()`, `PINT_hint_get_value_by_type()`, and `PINT_hint_get_value_by_name()`. `hint_types[]` maps known hint enums to names, flags, generated encode/decode functions, and fixed lengths.

Control flow: Add paths resolve a name or type against `hint_types`, reject duplicate known hints or replace them for internal adds, allocate list nodes and value copies, and mark unknown hints as transferable strings. Encode counts hints with `PINT_HINT_TRANSFER`, serializes count/type, and serializes either known fixed values or unknown name/value strings. Decode reconstructs a new hint list from the encoded stream. Environment import parses `PVFS2_HINTS` as `name:value+...`, prefixes names with `pvfs2.hint.`, coerces known integer/string values, and adds them without overwriting existing hints.

State and persistence behavior: Hints are caller-owned in-memory linked lists. Persistent behavior is limited to reading `PVFS2_HINTS` from the process environment. The transfer flag determines which hints cross request boundaries and which remain local-only.

Dependencies and integration points: Uses generated endecode helpers, PVFS hint names from `pvfs2-hint.h`, gossip logging, PVFS error codes, and request encoding paths. Macros in `pint-hint.h` read common values directly from hint lists.

Risks and test signals: `PVFS_hint_check()` dereferences `info` without checking unknown names. `PVFS_hint_check_transfer()` assumes every hint type has metadata, so unknown hints can crash. `PVFS_hint_import_env()` builds names with `sprintf()` into a fixed array and mistakenly parses uint64-encoded hints into a `uint32_t`. It also returns success without assigning `*out_hint` at the end, leaving parsed hints unreachable. Tests should cover unknown hints, transfer-only encode/decode, duplicate replace semantics, environment import success/failure, long names/values, and copy/free ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-hint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-hint.h -->
# sources/distributed-fs/orangefs/src/common/misc/pint-hint.h

Purpose: Defines the internal hint representation and helper API for OrangeFS request hints. It bridges public PVFS hint names to internal typed hints and provides convenience macros for extracting frequent typed values.

Important APIs and types: `PVFS_HINT_MAX`, string length/separator constants, and `PINT_HINT_TRANSFER` define limits and transfer behavior. `enum PINT_hint_type` lists known hints such as request id, client id, handle, op id, rank, distribution, layout, dfile count, server list, cache, local uid, owner gid, and distribution physical view. `PINT_hint` nodes store type, optional type string, value pointer/length, encode/decode callbacks, flags, and next pointer. The header declares encode/decode, lookup by type/name, and internal add/replace functions. Getter macros return typed scalar values or defaults.

Control flow and integration: Higher-level PVFS hint APIs build linked lists. Request encoders call `encode_PINT_hint()` when a request carries transferable hints, and decoders call `decode_PINT_hint()` on incoming messages. Server and client code use getter macros to avoid repetitive lookups.

State and persistence behavior: Hints are transient linked lists attached to requests or local operations. The header does not own allocation, but the representation requires explicit freeing.

Dependencies and risks: Depends on `pvfs2-hint.h` and PVFS scalar types. Getter macros call lookup functions multiple times, so side-effect-free inputs are assumed. Unknown hints and length mismatches are main API risks. Test signals include typed extraction defaults, cross-endian encode/decode, and malformed hint stream handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-hint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-malloc.c -->
# sources/distributed-fs/orangefs/src/common/misc/pint-malloc.c

Purpose: Implements OrangeFS allocation wrappers that can zero allocations, attach metadata/magic values, validate frees/reallocs, support optional debug logging, and redirect calls to the real libc allocator via `dlsym()`. It also implements the clean allocator wrappers that bypass interception.

Important APIs and functions: Clean functions include `clean_malloc()`, `clean_calloc()`, `clean_posix_memalign()`, `clean_memalign()`, `clean_valloc()`, `clean_realloc()`, `clean_strdup()`, `clean_strndup()`, and `clean_free()`. Wrapper APIs include `PINT_malloc_minimum()`, `PINT_malloc()`, `PINT_calloc()`, `PINT_posix_memalign()`, `PINT_memalign()`, `PINT_valloc()`, `PINT_realloc()`, `PINT_strdup()`, `PINT_strndup()`, `PINT_free()`, `PINT_free2()`, `PINT_check_address()`, `PINT_check_malloc()`, and constructor `init_glibc_malloc()`.

Control flow: Clean wrappers are defined before `pint-malloc.h` macro redefinitions. The implementation then includes the wrapper header and undefines allocator macros so internal calls can reach real libc. Wrapped allocations allocate extra header space, optionally zero memory, store original pointer/size/magic/alignment, and return the user pointer after `extra_t`. Aligned allocation overallocates and positions `extra_t` immediately before the aligned user pointer. Realloc validates magic, computes the offset between user pointer and original allocation, calls real realloc, then fixes header metadata. Free validates magic, optionally zeros the full original allocation, and frees the original pointer. `init_glibc_malloc()` uses a recursive mutex and `dlsym()` to populate the real allocator operation table.

State and persistence behavior: Process-global state is `glibc_malloc_ops`, debug file pointer/flag when enabled, and constructor initialization flags. Allocation metadata is embedded before every wrapped allocation and persists until free. Debug logs may persist when `OFS_MALLOC_DEBUG` is set.

Dependencies and integration points: Depends on `pvfs2-config.h`, `pvfs2-internal.h`, `gen-locks`, gossip, `dlfcn`, libc allocator symbols, and optional malloc configuration macros. `pint-malloc.h` can redefine standard allocator names across most OrangeFS code, making this module foundational.

Risks and test signals: `PINT_calloc()` has unreachable code after return and does not check multiplication overflow. `clean_memalign()` has inverted Darwin return logic. `PINT_check_address()` assumes `glibc_malloc_ops.pipe/write/close` are populated and writes 128 bytes from arbitrary pointers. `PINT_free()` refuses invalid magic without freeing, which prevents crashes but can leak if allocator families are mixed. Tests should cover wrapper and clean allocation families, aligned allocations, realloc of aligned/nonaligned pointers, zeroing options, debug logging, constructor recursion, invalid free detection, and builds with `PVFS_MALLOC_REDEF` on/off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-malloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-malloc.h -->
# sources/distributed-fs/orangefs/src/common/misc/pint-malloc.h

Purpose: Declares OrangeFS allocation wrappers and, when configured, redefines standard allocation calls to those wrappers. It centralizes allocation debugging, zeroing, magic validation, and direct-libc operation-table declarations.

Important APIs and macros: `struct glibc_malloc_ops_s` holds real libc allocator and small I/O function pointers. Configuration macros include `PVFS_MALLOC_DEBUG`, `PVFS_MALLOC_REDEF`, `PVFS_MALLOC_MAGIC`, `PVFS_MALLOC_CHECK_ALIGN`, `PVFS_MALLOC_ZERO`, and `PVFS_MALLOC_FREE_ZERO`. Public wrappers include `PINT_malloc`, `PINT_calloc`, `PINT_posix_memalign`, `PINT_memalign`, `PINT_valloc`, `PINT_realloc`, `PINT_strdup`, `PINT_strndup`, `PINT_free`, and `PINT_free2`. Macro blocks redirect `malloc`, `calloc`, `posix_memalign`, `memalign`, `valloc`, `realloc`, `strdup`, `strndup`, `free`, and `cfree` to wrapper calls with optional file/line metadata.

Control flow and integration: Including this header can alter subsequent allocator calls at preprocessing time. On non-Windows systems it also declares the constructor `init_glibc_malloc()`. On Windows, wrapper redefinition is disabled. The non-redef branch maps direct `PINT_*` use back to system allocators or `PINT_malloc_minimum()`.

State and persistence behavior: The header itself owns no state, but its macros decide whether allocations carry wrapper metadata and whether memory is zeroed on allocation/free. These choices affect all included translation units.

Dependencies and risks: Header inclusion order is critical because it intentionally redefines common allocator names. Mixed clean/system/wrapped allocation families must be kept separate. Test signals include preprocessor smoke tests under all config combinations, Windows builds, debug file/line macro coverage, and external-library memory ownership cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-malloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-mem.c -->
# sources/distributed-fs/orangefs/src/common/misc/pint-mem.c

Purpose: Provides portable aligned allocation/free helpers used by OrangeFS code that needs a pointer divisible by a requested alignment. It also zeroes allocated memory before returning it.

Important APIs and functions: `PINT_mem_aligned_alloc(size, alignment)` returns a zero-filled aligned region or `NULL` with `errno` set. `PINT_mem_aligned_free(ptr)` frees memory allocated by the aligned helper using `_aligned_free()` on Windows or `free()` elsewhere.

Control flow: On Windows it calls `_aligned_malloc()` and converts null to `ENOMEM`. With Electric Fence it falls back to plain `malloc()` because Electric Fence cannot support the usual aligned allocator. Otherwise it calls `posix_memalign()`. After successful allocation it zeroes the requested byte range. Free dispatches to the platform-specific matching free.

State and persistence behavior: No module-level state. The only persistent effect is process heap allocation until the caller frees it.

Dependencies and integration points: Depends on `pvfs2-config.h`, standard allocation APIs, optional `malloc.h`, and Windows support headers. It is a smaller aligned-memory utility separate from the more invasive `pint-malloc` macro wrappers.

Risks and test signals: `ptr` is uninitialized before `posix_memalign()` failure unless callers only use the returned value. Alignment validity follows the platform allocator contract. Tests should cover power-of-two alignments, invalid alignments, zero sizes, Electric Fence configuration, Windows build paths, and verifying returned memory is zeroed and correctly aligned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-mem.h -->
# sources/distributed-fs/orangefs/src/common/misc/pint-mem.h

Purpose: Declares OrangeFS aligned memory allocation helpers. It is a simple header for callers that need portable aligned allocation without directly depending on platform-specific allocator names.

Important APIs: `PINT_mem_aligned_alloc()` accepts a byte size and alignment and returns zero-filled aligned memory. `PINT_mem_aligned_free()` frees memory returned by that allocator.

Control flow and integration: The header has no logic. It is included by modules that need aligned buffers and delegates implementation to `pint-mem.c`.

State and persistence behavior: No state is declared. The allocated memory belongs to the caller until explicitly freed.

Dependencies and risks: The prototypes use `size_t`, so including contexts must provide the standard type through other headers or the compile environment. Test signals are basic compile/link coverage and allocator pairing checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-perf-counter.c -->
# sources/distributed-fs/orangefs/src/common/misc/pint-perf-counter.c

Purpose: Implements OrangeFS performance counters and timers with rolling history samples. It supplies server-wide key tables, allocation/reset/finalize logic, count/timer operations, configurable history/interval settings, retrieval into numeric arrays, and text rendering for management output.

Important APIs and functions: `server_keys[]` and `server_tkeys[]` define counter/timer names keyed to management enums. Lifecycle helpers are `PINT_perf_initialize()`, `PINT_free_pc()`, `PINT_perf_reset()`, and `PINT_perf_finalize()`. Mutation APIs are `__PINT_perf_count()`, `__PINT_perf_timer_start()`, `__PINT_perf_timer_end()`, and `PINT_perf_rollover()`. Runtime options use `PINT_perf_set_info()` and `PINT_perf_get_info()`. Export uses `PINT_perf_retrieve()` and `PINT_perf_generate_text()`.

Control flow: Initialization validates key ordering from zero, determines sample value size based on counter vs timer mode, initializes defaults, allocates a linked list of history samples, and stamps the current sample start time. Count operations lock the counter, validate key/op/type, and add/sub/set counter values or aggregate timer sum/count/min/max. Timer start captures monotonic raw time and timer end computes nanoseconds then records a timer end value. Rollover rotates the head sample to the tail, copies current values into the new head, resets non-preserved keys, and updates interval timestamps. Retrieval copies all samples into a caller-provided packed array and auto-rolls over afterward; text generation formats start times, intervals, and values.

State and persistence behavior: Each `PINT_perf_counter` owns a mutex, key metadata pointer, type, key count, history length, rollover state, interval, optional state-machine callback, and linked samples. State is in memory and represents process-local metrics. Server-global counter pointers are declared in the header but owned elsewhere.

Dependencies and integration points: Uses PVFS management perf enums, `gen-locks`, time helpers, `CLOCK_MONOTONIC_RAW` or Windows QPC shim, gossip logging, and state-machine timer hooks. Management interfaces call retrieve/text APIs to expose performance data.

Risks and test signals: `PINT_perf_reset()` locks `pc->mutex` before checking `pc`, making null input unsafe. It also calls `memset(&s->value.v, ...)`, clearing the pointer field rather than the pointed-to sample data. Initialization checks `tmp->value.v` instead of `tmp->next->value.v` after allocating subsequent samples and zeros only `pc->perf_counter_size` bytes for new samples instead of all keys. `PINT_perf_generate_text()` returns without unlocking when the supplied max size is too small. Tests should cover allocation failure injection, key ordering validation, history resize up/down, counter and timer operations, rollover preserve semantics, retrieve buffer sizing, text generation truncation, null inputs, and Windows/non-Windows timer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-perf-counter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-perf-counter.h -->
# sources/distributed-fs/orangefs/src/common/misc/pint-perf-counter.h

Purpose: Declares the OrangeFS performance counter/timer framework. It defines defaults, operation enums, option enums, key/sample/counter structures, server key tables, server counter globals, and public mutation/export functions.

Important APIs and types: `PINT_perf_key` binds display names, numeric keys, and flags such as `PINT_PERF_PRESERVE`. `PINT_perf_sample` stores a start time, interval, value array, and next link. `PINT_perf_counter` stores locking, key/type/count metadata, history settings, rollover state, state-machine callback, and sample list. Operations include add/sub/set/start/end and options include history size, key count, and update interval. Macros erase counting/timer calls when `__PVFS2_DISABLE_PERF_COUNTERS__` is defined.

Control flow and integration: Servers and clients initialize counters with key arrays, record counts/timers throughout request paths, periodically roll over samples, and retrieve data for management APIs. The header intentionally keeps key arrays extern so management enum ordering can be shared.

State and persistence behavior: Counter state is volatile process memory. The `PINT_PERF_PRESERVE` flag controls what survives rollovers. No persistent storage is defined.

Dependencies and risks: Depends on PVFS management enums, `gen-locks`, and state-machine types. The caller must size retrieval buffers from key count, history, and counter type. Test signals include disabled-counter builds, timer/counter type separation, and management output compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-perf-counter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-uid-mgmt.c -->
# sources/distributed-fs/orangefs/src/common/misc/pint-uid-mgmt.c

Purpose: Implements a small in-memory UID activity history for OrangeFS. It records recent user ids, access counts, first/last timestamps, and exposes a dump function for statistics.

Important APIs and functions: `PINT_uid_mgmt_initialize()` allocates the fixed-size LRU list and hash table. `PINT_uid_mgmt_finalize()` frees both. `PINT_add_user_to_uid_mgmt()` records an occurrence for a UID, incrementing existing entries or evicting the least-recently-used slot. `PINT_dump_all_uid_stats()` copies all slots into a caller-provided `PVFS_uid_info_s` array. `uid_hash_compare_keys()` supports quickhash lookup.

Control flow: Initialization first frees any existing list/hash state, allocates a list head and hash table, then allocates `UID_MGMT_MAX_HISTORY` empty entries linked into LRU order. Add looks up the UID in the hash table, updates count/time if found, or evicts the tail entry, removes its old hash mapping when occupied, fills new UID/count/timestamps, adds it to the hash, and moves it to the LRU head. Dump locks the mutex, walks exactly `UID_MGMT_MAX_HISTORY` entries, and copies their info.

State and persistence behavior: Global state is `uid_lru_list`, `uid_hash_table`, and `uid_mgmt_mutex`. Entries are volatile and reset on initialize/finalize. Timestamps use current timeval helpers and counts persist only in process memory.

Dependencies and integration points: Uses quicklist, quickhash, PVFS uid types, `PINT_util_get_current_timeval()`, and gen mutexes. The encoded `PVFS_uid_info_s` type in the header allows stats to cross protocol boundaries.

Risks and test signals: `PINT_add_user_to_uid_mgmt()` mutates list/hash state without taking `uid_mgmt_mutex`, while dump does lock, so concurrent add/dump/finalize is unsafe. Initialization failure paths leak prior allocations and newly allocated partial entries/hash table. `PINT_dump_all_uid_stats()` assumes initialization and a non-null output array. Tests should cover repeated initialize/finalize, LRU eviction after 25 unique UIDs, counter increments, timestamp ordering, null/uninitialized calls, and multi-threaded add/dump races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-uid-mgmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-uid-mgmt.h -->
# sources/distributed-fs/orangefs/src/common/misc/pint-uid-mgmt.h

Purpose: Defines the UID management statistics structures, constants, encoding metadata, and API prototypes for OrangeFS UID activity tracking.

Important APIs and types: `UID_MGMT_MAX_HISTORY` fixes the history to 25 entries and `UID_HISTORY_HASH_TABLE_SIZE` sets the lookup table size. `PVFS_uid_info_s` stores a uid, count, first timestamp, and latest timestamp and has generated encode/decode descriptors. `PINT_uid_mgmt_s` wraps stats with LRU and hash links. `IN_UID_HISTORY(current, oldest)` compares timeval values in microseconds. Public functions initialize/finalize the subsystem, add a UID occurrence, and dump all stats.

Control flow and integration: Server paths call `PINT_add_user_to_uid_mgmt()` when recording per-user activity and management/reporting paths call `PINT_dump_all_uid_stats()` to export the fixed-size array. Encoding metadata allows stats to be serialized using OrangeFS request protocol helpers.

State and persistence behavior: The header declares types for in-memory history only. Persistent behavior is absent; the history is bounded and reset on subsystem initialization.

Dependencies and risks: Depends on quicklist, quickhash, PVFS uid/time types, and endecode macro availability. The `IN_UID_HISTORY` macro performs floating-point-like multiplication through `1e6`, which may introduce type surprises; integer constants would be safer. Test signals include encode/decode of `PVFS_uid_info_s`, fixed-size dump compatibility, and boundary timestamp comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-uid-mgmt.h -->
