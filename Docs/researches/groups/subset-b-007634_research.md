# Research: subset-b-007634

Grouped research for the requested LizardFS mount write path, NFS-Ganesha FSAL plugin, and selected protocol definitions. Each section title preserves the original source path and is delimited for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/writedata.cc -->
# sources/distributed-fs/lizardfs/src/mount/writedata.cc

## Purpose
Implements the mount client's asynchronous write-back engine. It accepts FUSE/client writes into per-inode `WriteCacheBlock` chains, schedules background workers to lock LizardFS chunks through the master, streams block operations to chunkservers through `ChunkWriter`, handles retries and delayed requeueing, and provides flush/truncate/end APIs used by the mount/client layer.

## Important APIs, Types, And Functions
The central private type is `inodedata`, which tracks inode id, cached max file length, status, queue flags, flush/write wait counters, reference count, retry count, minimum worthwhile batch size, pending block chain, current `WriteChunkLocator`, data-arrival pipe, and timers. `InodeChunkWriter` owns one queued inode job and drives `processJob`, `processDataChain`, journal return, and "is this block worth sending" decisions. Public entry points are `write_data_init`, `write_data_term`, `write_data_new`, `write_data_end`, `write_data_flush`, `write_data_flush_inode`, `write_data_getmaxfleng`, `write_data_truncate`, and `write_data`.

## Control Flow
`write_data_init` initializes global cache counters, inode hash table, a producer-consumer queue, the delayed queue worker, and write worker threads. `write_data_new` returns/refcounts inode state. `write_data` blocks behind active flushes, updates `maxfleng`, then decomposes the input into chunk/block ranges via `write_blocks` and `write_block`. `write_block` expands the last writable cache block when possible; otherwise it waits for global/per-inode cache allowance, appends a block, and enqueues or wakes workers. Workers pull `inodedata` from `jqueue`; `InodeChunkWriter` chooses the front chunk, obtains or resumes a chunk locator, initializes `ChunkWriter`, drains worthwhile cache blocks into the writer under a time/window policy, finishes and unlocks the chunk, then either requeues, delays, or completes the inode. Flushes increment `flushwaiting`, expedite delayed jobs, and wait until `inqueue` clears.

## State And Persistence Behavior
All mutable write state is in process memory and protected by `gMutex`; persistence happens only when worker operations reach chunkservers and the master receives write/truncate completion messages through locator/master APIs. `freecacheblocks` is the global write cache budget in block units, while `gCachePerInodePercentage` prevents one inode from consuming too much free cache. `lastWriteToDataChain` and `lastWriteToChunkservers` force old partial data to flush even without explicit flush calls. `write_data_truncate` is a special two-phase flow: it flushes current writes, asks the master for truncate metadata/lock, optionally writes zeroes after the new EOF to update xor/EC parity, then calls `fs_truncateend`.

## Dependencies And Integration Points
Depends on common queueing, sockets, CRC/datapack, `ChunkConnectorUsingPool`, `ChunkWriter`, `WriteCacheBlock`, `WriteChunkLocator`, master communication helpers (`fs_truncate`, `fs_truncateend`, chunk lock/unlock), read invalidation (`read_inode_ops`), global chunkserver stats, protocol constants from `MFSCommunication.h`, and tweak registration for `WriteMaxRetries`. The header exposes this module to mount/client file operations.

## Risks And Edge Cases
The module is concurrency-heavy: condition variables, delayed queues, pipes, queue shutdown, and refcounted `inodedata` deletion all rely on strict lock discipline. Error mapping compresses several lower-level write failures into `EBADF`, `QUOTA`, `NOSPACE`, or `IO`, so diagnostics can be lossy. Retry behavior keeps locators and unwritten journals for recoverable errors; incorrect journal/block accounting would corrupt cache pressure or write order. Partial blocks are intentionally delayed unless a flush/age/multiblock condition forces them out, which affects latency. Truncate parity zeroing depends on correct old length, lock id, and EC stripe bounds. The Windows/Cygwin pipe path disables wake-up optimization and may have higher write latency.

## Test Signals
No direct unit test is listed for this file in the subset. Indirect coverage should come from mount write/read/truncate integration tests, chunkserver protocol tests, EC/xor write tests, and stress tests that exercise retry, flush, delayed queue, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/writedata.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/writedata.h -->
# sources/distributed-fs/lizardfs/src/mount/writedata.h

## Purpose
Declares the mount client's write-data API implemented in `writedata.cc`.

## Important APIs, Types, And Functions
The API initializes and tears down the write subsystem (`write_data_init`, `write_data_term`), creates and releases per-inode write handles (`write_data_new`, `write_data_end`), writes buffered data (`write_data`), flushes data by handle or inode (`write_data_flush`, `write_data_flush_inode`), exposes cached maximum file length (`write_data_getmaxfleng`), and coordinates truncate with master/chunkserver state (`write_data_truncate`). `write_data_truncate` returns updated `Attributes`.

## Control Flow
Callers initialize once with cache size, retry count, worker count, write window, chunkserver timeout, and per-inode cache percentage. File operations obtain a `void*` inode handle, pass write ranges to `write_data`, flush as needed, and close with `write_data_end`.

## State And Persistence Behavior
The header intentionally hides `inodedata`; all persistent effects are delegated to the implementation and master/chunkserver writes.

## Dependencies And Integration Points
Depends only on `common/platform.h`, integer types, and `common/attributes.h`, keeping the public mount API small for FUSE/client users.

## Risks And Edge Cases
The `void*` handle API requires correct pairing of `write_data_new` and `write_data_end`; misuse can leak or prematurely free inode state. Return values are LizardFS status/error codes, not standard errno in all paths.

## Test Signals
Covered indirectly by write subsystem tests and call sites that validate flush/truncate semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/writedata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/nfs-ganesha/CMakeLists.txt

## Purpose
Builds the LizardFS NFS-Ganesha FSAL plugin as a module named `fsallizardfs`.

## Important APIs, Types, And Functions
Uses `collect_sources(NFS_GANESHA_PLUGIN)`, includes external Ganesha and NTIRPC headers, links the module against `lizardfs-client_pic`, and installs it under `${LIB_SUBDIR}/ganesha` in the `fsal` component.

## Control Flow
CMake collects plugin sources, creates a `MODULE` library from `${NFS_GANESHA_PLUGIN_MAIN}` and `${NFS_GANESHA_PLUGIN_SOURCES}`, then wires the LizardFS client PIC library.

## State And Persistence Behavior
No runtime state. It defines build/install topology for the plugin artifact.

## Dependencies And Integration Points
Depends on external source variables `NFS_GANESHA_DIR_NAME` and `NTIRPC_DIR_NAME`, the local source collector macros, and the LizardFS client library.

## Risks And Edge Cases
Header path compatibility is tied to the vendored/external Ganesha and NTIRPC layouts. Missing PIC client library or changed external include trees will break plugin builds.

## Test Signals
Build success of `fsallizardfs` and any Ganesha FSAL/plugin tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/context_wrap.c -->
# sources/distributed-fs/lizardfs/src/nfs-ganesha/context_wrap.c

## Purpose
Provides credential-aware wrapper functions around the LizardFS C client API for the NFS-Ganesha FSAL.

## Important APIs, Types, And Functions
Exports `liz_cred_*` helpers for lookup, mknod, open, read, write, flush, getattr, opendir/readdir, mkdir, rmdir, unlink, setattr, fsync, rename, symlink, readlink, link, chunk info, ACL get/set, and POSIX byte-range lock get/set. Each wrapper creates a `liz_context_t` with `lzfs_fsal_create_context`, calls the corresponding `liz_*` API, destroys the context, and returns the result.

## Control Flow
Every wrapper follows the same pattern: create context from `liz_t` instance and `struct user_cred`, return failure on context allocation failure, invoke the underlying client call, then destroy the context. Read/write/open wrappers return pointer or byte counts; most others return integer status.

## State And Persistence Behavior
Wrappers do not own persistent state beyond transient contexts. Persistent effects are delegated to the LizardFS client instance and remote master/chunkserver operations.

## Dependencies And Integration Points
Depends on `lzfs_internal.h` for context creation and on `mount/client/lizardfs_c_api.h` declarations via the header. Used throughout FSAL export, handle, DS, ACL, and MDS files to preserve NFS request credentials.

## Risks And Edge Cases
`liz_cred_getlk` creates a context but does not destroy it before returning, unlike all other wrappers; that is a likely context leak. Passing `cred == NULL` intentionally creates root-like context in `lzfs_fsal_create_context`, used by pNFS DS paths. Errors are usually `-1`/`NULL` plus `liz_last_err`, so callers must convert immediately.

## Test Signals
No direct unit test. Coverage should come from FSAL request tests validating that operations run under expected UID/GID/group credentials and from leak checks around lock probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/context_wrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/context_wrap.h -->
# sources/distributed-fs/lizardfs/src/nfs-ganesha/context_wrap.h

## Purpose
Declares the credential-wrapped LizardFS C API used by the NFS-Ganesha plugin.

## Important APIs, Types, And Functions
The header exposes all `liz_cred_*` wrappers for namespace operations, file I/O, directory I/O, attributes, ACLs, chunk info, and locking. It includes Ganesha `fsal_types.h` for `user_cred` and the LizardFS C API for `liz_t`, `liz_fileinfo_t`, inode, ACL, and lock types.

## Control Flow
Consumers call these functions instead of raw `liz_*` calls when an operation must be executed under `op_ctx->creds` or an explicit credential pointer.

## State And Persistence Behavior
No direct state. The header establishes a convention that contexts are temporary and wrapper-owned.

## Dependencies And Integration Points
Integrated by `handle.c`, `export.c`, `ds.c`, `lzfs_acl.c`, `mds_export.c`, `mds_handle.c`, and `main.c`.

## Risks And Edge Cases
The API mirrors raw LizardFS return conventions, so callers must handle `NULL` vs negative integer failures consistently. As a C header without include guards beyond implicit compiler behavior, duplicate inclusion is tolerated by declarations but not explicitly protected.

## Test Signals
Compilation of all FSAL files confirms declaration compatibility; functional credential behavior needs integration testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/context_wrap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/ds.c -->
# sources/distributed-fs/lizardfs/src/nfs-ganesha/ds.c

## Purpose
Implements pNFS data-server handle operations for the LizardFS FSAL.

## Important APIs, Types, And Functions
Registers DS operations in `lzfs_fsal_ds_handle_ops_init`: make handle, handle release, read, write, commit, read_plus, write_plus, pDS release, and permission setup. Internal helpers include `lzfs_int_openfile`, which lazily opens/caches a `liz_fileinfo_t`, and `lzfs_int_clear_fileinfo_cache`, which retires expired fileinfo cache entries.

## Control Flow
`lzfs_fsal_make_ds_handle` decodes a wire handle containing an inode, applies endian correction, allocates `lzfs_fsal_ds_handle`, and initializes Ganesha DS state. DS read/write/commit resolve the export from `ds_hdl->pds->mds_fsal_export`, lazily open the file with no request credentials, extract cached fileinfo, call `liz_cred_read`, `liz_cred_write`, or `liz_cred_flush`, and translate errors to NFSv4 status. Release returns any acquired cache entry, finalizes the DS handle, frees it, and opportunistically clears expired cache entries.

## State And Persistence Behavior
The DS handle stores inode and optional cache entry. The export-level `fileinfo_cache` reuses open LizardFS fileinfo handles across DS operations, bounded by max entries and timeout. Writes persist through LizardFS write/flush semantics; stable writes call flush when requested.

## Dependencies And Integration Points
Depends on Ganesha FSAL/pNFS APIs, `context_wrap`, `lzfs_internal`, and `fileinfo_cache`. It integrates with pNFS MDS layout data emitted by `mds_handle.c` and `mds_export.c`.

## Risks And Edge Cases
DS operations pass `cred == NULL`, creating root-like contexts; that is intentional for data-server access but must match the security model. `lzfs_int_openfile` erases cache entries when open fails but callers must not release erased handles afterward. `read_plus` and `write_plus` are explicitly unsupported. Commit returns success when lazy open fails, assuming there is no descriptor to flush; that can hide unexpected cache/open failures.

## Test Signals
No direct unit test in subset. pNFS read/write/commit integration tests and cache eviction tests are needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/ds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/export.c -->
# sources/distributed-fs/lizardfs/src/nfs-ganesha/export.c

## Purpose
Implements export-level operations for the LizardFS FSAL: export teardown, path lookup, wire-handle conversion, object-handle creation, filesystem dynamic info, static capability accessors, and state allocation/free.

## Important APIs, Types, And Functions
`lzfs_fsal_export_ops_init` fills `struct export_ops`. Key operations include `lzfs_fsal_release`, `lzfs_fsal_lookup_path`, `lzfs_fsal_wire_to_host`, `lzfs_fsal_create_handle`, `lzfs_fsal_get_fs_dynamic_info`, static info accessors such as maxread/maxwrite/ACL support, and `lzfs_fsal_alloc_state`/`lzfs_fsal_free_state`.

## Control Flow
Lookup path normalizes Ganesha export paths, validates the requested path begins with `ctx_export->fullpath`, handles root specially, then uses `liz_cred_lookup` from `SPECIAL_INODE_ROOT` and creates a FSAL handle if needed. Wire handles are inode-sized blobs with endian correction. Create-handle fetches attributes for the inode and builds an object handle. Release detaches export, frees root handle, drains fileinfo cache while releasing underlying LizardFS file handles, destroys the LizardFS instance, and frees export memory.

## State And Persistence Behavior
Owns export lifetime state: root handle, `liz_t` instance, optional pNFS fileinfo cache, and static operation tables. Runtime persistence is remote LizardFS state; this file manages local cleanup.

## Dependencies And Integration Points
Depends on Ganesha FSAL config/commonlib, `common/special_inode_defs.h`, `context_wrap`, `lzfs_internal`, and `fileinfo_cache` APIs. It composes with `main.c` export creation and `handle.c` object operations.

## Risks And Edge Cases
Path prefix validation is string-based and depends on exact `fullpath` normalization. Root lookup sets `*pub_handle` but still proceeds to call `liz_cred_lookup`, so root attrs can be refreshed but unnecessary errors could affect root path resolution. Release must drain cache entries only after marking cache max/timeout zero; leaks or double releases would affect long-running Ganesha processes.

## Test Signals
Export creation/destruction, path lookup under subfolder exports, handle serialization round trips, and statfs behavior are key integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/fileinfo_cache.c -->
# sources/distributed-fs/lizardfs/src/nfs-ganesha/fileinfo_cache.c

## Purpose
Implements a thread-safe fileinfo handle cache for pNFS DS operations.

## Important APIs, Types, And Functions
Defines opaque `liz_fileinfo_cache` with LRU and used lists, AVL lookup by inode, entry count, max entries, min timeout, and mutex. `liz_fileinfo_entry` stores list/tree hooks, inode, attached `liz_fileinfo_t`, timestamp, used flag, and lookup mode. Public functions create/destroy/reset cache, acquire/release/erase entries, pop expired entries, free entries, and attach/extract fileinfo.

## Control Flow
Acquire looks for an unused LRU entry by inode in the AVL tree. If found it removes it from LRU/tree and moves it to used; otherwise it allocates a new entry and increments count. Release marks an entry unused, timestamps it, moves it to LRU tail, and inserts it into the AVL tree. `pop_expired` examines the oldest LRU entry and removes it if the cache is over capacity or its age exceeds the timeout. Erase removes a currently used entry without putting it into cache.

## State And Persistence Behavior
State is process-local and protected by `pthread_mutex_t`. The cache owns entries, not the underlying `liz_fileinfo_t`; callers release the LizardFS file handle after `pop_expired` and before `liz_fileinfo_entry_free`.

## Dependencies And Integration Points
Uses Ganesha `glist`, `avltree`, `gsh_calloc/free`, and pthread wrappers. Integrated by `ds.c` and export cleanup.

## Risks And Edge Cases
`get_time_ms` divides nanoseconds by `1000`, yielding microseconds added to milliseconds; this makes timestamps too large within each second and can distort timeout behavior. The comparator allows multiple entries per inode when not in lookup mode, enabling concurrent opens for the same inode but making tree ordering pointer-dependent. Destroy frees entries but does not release attached fileinfo handles; callers must drain/release first. `liz_fileinfo_cache_acquire` documentation mentions possible NULL on full cache, but implementation always allocates.

## Test Signals
`fileinfo_cache_unittest.cc` covers basic reuse, over-capacity expiry, and parameter reset. Additional timing and concurrency tests would be valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/fileinfo_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/fileinfo_cache.h -->
# sources/distributed-fs/lizardfs/src/nfs-ganesha/fileinfo_cache.h

## Purpose
Declares the opaque fileinfo cache API used by pNFS data-server code.

## Important APIs, Types, And Functions
Declares `liz_fileinfo_cache_t`, `liz_fileinfo_entry_t`, create/reset/destroy, acquire/release/erase, pop expired, entry free, fileinfo extract, and fileinfo attach functions.

## Control Flow
Callers acquire an entry for an inode, open and attach a `liz_fileinfo_t` if extraction returns `NULL`, release the entry when a DS handle is done, and periodically pop expired entries to release associated LizardFS file handles and free entries.

## State And Persistence Behavior
The header documents cache ownership boundaries: entries are cache-owned until popped/erased, while attached fileinfo must be released by the caller after expiry.

## Dependencies And Integration Points
Includes the LizardFS C API for `liz_fileinfo_t` and `liz_inode_t`; C++ callers use the `extern "C"` block.

## Risks And Edge Cases
The comments say acquire may return NULL if full, but implementation does not enforce a hard cap. API users must pair acquire with release or erase and must not free active entries.

## Test Signals
The unit test exercises this interface directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/fileinfo_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/fileinfo_cache_unittest.cc -->
# sources/distributed-fs/lizardfs/src/nfs-ganesha/fileinfo_cache_unittest.cc

## Purpose
Provides GoogleTest coverage for the pNFS fileinfo cache.

## Important APIs, Types, And Functions
Defines tests `FileInfoCache.Basic`, `FileInfoCache.Full`, and `FileInfoCache.Reset`. They use create/acquire/attach/extract/release/pop/free/reset/destroy APIs.

## Control Flow
The basic test verifies that acquiring new entries has no fileinfo, attaching values persists across release/reacquire by inode, and expired entries can be popped after release. The full test creates more entries than the configured max, erases one active entry, releases the rest, and expects three expired pops. Reset confirms a long-timeout cache does not expire until parameters are reset to zero.

## State And Persistence Behavior
Tests use fake pointer values as fileinfo payloads and do not release real LizardFS handles. They exercise in-memory cache state only.

## Dependencies And Integration Points
Depends on `fileinfo_cache.h` and GoogleTest. It is built as part of the local test suite when nfs-ganesha tests are enabled.

## Risks And Edge Cases
No concurrency test, no real time delay test, and no attached-handle cleanup verification. The timestamp-unit bug is unlikely to be detected because all tested timeouts are zero or reset to zero.

## Test Signals
These tests are useful smoke coverage for list/tree transitions and parameter reset but should be supplemented with race and timeout-boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/fileinfo_cache_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/handle.c -->
# sources/distributed-fs/lizardfs/src/nfs-ganesha/handle.c

## Purpose
Implements object-handle operations for the LizardFS FSAL: namespace manipulation, file open/read/write/commit/close, attributes, links, locks, and handle serialization.

## Important APIs, Types, And Functions
`lzfs_fsal_handle_ops_init` installs the object operation table. Major functions include lookup/readdir/mkdir/mknode/symlink/readlink/getattrs/rename/unlink/link, `handle_to_wire`, `handle_to_key`, `open2`, `reopen2`, `read2`, `write2`, `commit2`, `setattr2`, `close2`, `status2`, `merge`, and `lzfs_fsal_lock_op2`. Internal helpers manage `lzfs_fsal_fd` open/close, share reservations, and `fsal_find_fd` integration.

## Control Flow
Directory and metadata operations translate FSAL parameters to LizardFS C API calls through `liz_cred_*`, convert attributes with `posix2fsal_attributes_all`, and wrap results in `lzfs_fsal_handle`. Open flows either open an existing handle/name or create with `mknod`, handle exclusive verifier checks, set requested attributes, and maintain share counters for stateful opens. Read/write find or temporarily open a usable FD, call LizardFS I/O, optionally fsync for stable writes, then close temporary descriptors and unlock Ganesha object locks. `setattr2` maps FSAL attr masks to LizardFS set masks and handles ACL updates. Lock operations convert FSAL locks to `liz_lock_info_t`, set lock owner on fileinfo, and call getlk/setlk.

## State And Persistence Behavior
Each FSAL object stores inode, unique key, optional global FD, export pointer, and share state. Per-open state stores an FD in `lzfs_fsal_state_fd`. Persistent namespace, attribute, lock, and file data changes are delegated to LizardFS master/client APIs.

## Dependencies And Integration Points
Depends on Ganesha FSAL commonlib/share helpers, `common/lizardfs_error_codes.h`, `context_wrap`, `lzfs_internal`, and ACL helpers. It is the core bridge from NFS requests to LizardFS client operations.

## Risks And Edge Cases
Share counter updates and FD reopen/close paths are subtle; error unwinds must undo reservations. `close2` updates share counters using `lzfs_obj->fd.openflags` rather than the state FD, which may be wrong for stateful descriptors. `read2` treats `offset == -1` as error even though offset is unsigned. Some create paths unset and restore `ATTR_MODE` on caller-provided attr lists, so side effects must be expected. Lock operations retry once on `ERR_FSAL_DELAY`, but temporary FD cleanup and leaked context risk in `liz_cred_getlk` matter.

## Test Signals
Needs broad FSAL integration tests: create/open/exclusive verifier, directory pagination, stable write/commit, setattr size/truncate, ACL get/set, link/rename/unlink, and lock conflict/probe behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/lzfs_acl.c -->
# sources/distributed-fs/lizardfs/src/nfs-ganesha/lzfs_acl.c

## Purpose
Converts ACLs between NFS-Ganesha FSAL ACL representation and LizardFS ACL representation, and implements get/set ACL helpers.

## Important APIs, Types, And Functions
`lzfs_int_convert_fsal_acl` builds `liz_acl_t` from allow/deny FSAL ACEs. `lzfs_int_convert_lzfs_acl` allocates FSAL ACE storage and creates an `fsal_acl_t` via `nfs4_acl_new_entry`. `lzfs_int_getacl` fetches a LizardFS ACL, applies owner masks, converts it, and replaces any old FSAL ACL. `lzfs_int_setacl` converts and sends FSAL ACLs to LizardFS.

## Control Flow
Conversion preserves ACE type, flags, mask, uid/gid, and maps special owner/group/everyone identifiers between FSAL and LizardFS constants. Unsupported ACE types are skipped on FSAL-to-LizardFS conversion. Get releases any existing ACL entry, fetches remote ACL with request credentials, applies masks using owner id, converts, and destroys the LizardFS ACL.

## State And Persistence Behavior
Conversion allocations are transient. `setacl` persists ACL changes through the LizardFS master/client API. FSAL ACL references are managed through Ganesha ACL allocation/release functions.

## Dependencies And Integration Points
Depends on `context_wrap`, `lzfs_internal`, Ganesha NFSv4 ACL helpers/macros, and LizardFS ACL C API. Called from `handle.c` getattrs/setattr2.

## Risks And Edge Cases
The unused `count` variable in FSAL-to-LizardFS conversion suggests incomplete preallocation logic. Skipping non-allow/deny ACEs changes ACL semantics if other ACE types are expected. Invalid special IDs are logged and skipped or normalized. Memory ownership must be exact: failed conversions need no leaked ACE arrays or ACL handles.

## Test Signals
No direct tests in subset. Round-trip ACL tests for special IDs, group/user IDs, allow/deny masks, empty ACLs, and invalid ACE handling are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/lzfs_acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/lzfs_internal.c -->
# sources/distributed-fs/lizardfs/src/nfs-ganesha/lzfs_internal.c

## Purpose
Provides shared FSAL helpers for error conversion, credential context creation, static-info access, and FSAL object handle allocation/deletion.

## Important APIs, Types, And Functions
`lizardfs2fsal_error`, `lizardfs2nfs4_error`, `lzfs_fsal_last_err`, and `lzfs_nfs4_last_err` translate `liz_last_err`/LizardFS errors to FSAL or NFSv4 status. `lzfs_fsal_create_context` builds `liz_context_t` from Ganesha `user_cred`, including supplementary groups. `lzfs_fsal_staticinfo` returns module static info. `lzfs_fsal_new_handle` and `lzfs_fsal_delete_handle` allocate/finalize object handles.

## Control Flow
Context creation maps anonymous uid/gid to zero, builds a LizardFS user context, and updates groups from either a stack array or allocated array. New-handle initializes inode, unique key, Ganesha object handle, object ops, fsid, fileid, and export pointer.

## State And Persistence Behavior
No persistent remote state. It allocates FSAL handle memory and transient client contexts.

## Dependencies And Integration Points
Depends on FSAL conversion/commonlib, pNFS utils, LizardFS C API, and declarations in `lzfs_internal.h`. Used by nearly every FSAL source file.

## Risks And Edge Cases
Anonymous-to-root mapping is security-sensitive and depends on export permissions. If supplementary group allocation fails for large group lists, it falls through to the stack-limited path and silently truncates to 64 groups. Error conversion warns and maps missing errno to `EINVAL`, which can hide upstream bugs.

## Test Signals
Credential mapping tests, group-list length tests, error conversion tests, and object-handle lifecycle tests would validate this shared layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/lzfs_internal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/lzfs_internal.h -->
# sources/distributed-fs/lizardfs/src/nfs-ganesha/lzfs_internal.h

## Purpose
Defines private FSAL module/export/handle/FD/state/pNFS structures, constants, and shared function declarations for the LizardFS NFS-Ganesha plugin.

## Important APIs, Types, And Functions
Defines `lzfs_fsal_module`, `lzfs_fsal_export`, `lzfs_fsal_fd`, `lzfs_fsal_state_fd`, `lzfs_fsal_key`, `lzfs_fsal_handle`, `lzfs_fsal_ds_wire`, and `lzfs_fsal_ds_handle`. Constants include lease time, supported attribute mask, largest pNFS stripe count, standard chunk part type, backup DS count, and TCP protocol number. Declares shared functions from internal, export, handle, pNFS, DS, and ACL modules.

## Control Flow
This header is included by all FSAL implementation files to share container layouts and operation initialization hooks.

## State And Persistence Behavior
Defines all in-process state carriers for exports, object handles, open file descriptors, stateful opens, and pNFS DS handles. Remote persistence is outside the header.

## Dependencies And Integration Points
Depends on Ganesha `fsal_api.h`/commonlib, fileinfo cache, and LizardFS C API. It is the internal ABI of the plugin.

## Risks And Edge Cases
Because structs are shared across C files, layout changes have broad impact. `kDisconnectedChunkserverVersion` macro includes a trailing semicolon, which is harmless in assignments/comparisons as used but fragile. `LZFS_SUPPORTED_ATTRS` advertises ACL and rich attribute support that must remain consistent with implementations.

## Test Signals
Compilation across all FSAL modules is the first signal; runtime tests should validate advertised capabilities against actual operation support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/lzfs_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/main.c -->
# sources/distributed-fs/lizardfs/src/nfs-ganesha/main.c

## Purpose
Registers and configures the LizardFS FSAL module for NFS-Ganesha, parses module/export parameters, creates exports, and initializes pNFS support.

## Important APIs, Types, And Functions
Defines static FSAL info defaults, module-level config items, export config items, `lzfs_fsal_create_export`, `lzfs_fsal_init_config`, `lzfs_fsal_support_ex`, `MODULE_INIT init`, and `MODULE_FINI finish`.

## Control Flow
Module init registers the FSAL, installs module ops, DS ops, export creation, config initialization, and pNFS module ops. Config init copies default static info and applies config file overrides. Export creation allocates `lzfs_fsal_export`, initializes export ops, loads export parameters, initializes the LizardFS client instance with the Ganesha export fullpath as subfolder, attaches the export, optionally sets up pNFS DS fileinfo cache and DS registration, optionally enables pNFS MDS ops, fetches root attributes, and creates the root handle. Finish unregisters the FSAL and aborts if unload fails.

## State And Persistence Behavior
Owns global module object `gLizardFSM` and per-export initialization of `liz_t`, cache parameters, pNFS flags, and root handle. Persistent cluster state is accessed but not stored locally beyond the mounted client instance.

## Dependencies And Integration Points
Depends on Ganesha FSAL init/config/commonlib, pNFS utils, `common/special_inode_defs.h`, `context_wrap`, `lzfs_internal`, and protocol size constants. Integrates the entire FSAL plugin into Ganesha.

## Risks And Edge Cases
Export error cleanup frees the LizardFS instance/cache but does not detach an export if failure occurs after attach. Config defaults bound write workers/cache/timeouts and pNFS cache sizes; mismatch with production load can cause performance issues. Password and md5 password config values are handled as plain config fields. `support_ex` returns true unconditionally.

## Test Signals
Plugin load/unload tests, config parsing tests, export mount failure tests, pNFS DS registration conflicts, and root lookup tests are core signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/mds_export.c -->
# sources/distributed-fs/lizardfs/src/nfs-ganesha/mds_export.c

## Purpose
Implements pNFS metadata-server export/module operations, especially device-info encoding from LizardFS chunk and chunkserver metadata.

## Important APIs, Types, And Functions
Key helpers include chunkserver comparison/filtering/shuffling, `lzfs_int_get_randomized_chunkserver_list`, `lzfs_int_fill_chunk_ds_list`, and `lzfs_int_fill_unused_ds_list`. Export/module hooks include `lzfs_fsal_getdeviceinfo`, `lzfs_fsal_getdevicelist`, layout type/blocksize/segment/body-size accessors, `lzfs_fsal_export_ops_pnfs`, and `lzfs_fsal_ops_pnfs`.

## Control Flow
`getdeviceinfo` validates NFSv4.1 file layout, resolves the export by device id, fetches up to 4096 file chunks, fetches chunkservers, removes disconnected and duplicate-IP entries, randomizes server order, encodes stripe indices, then encodes multipath DS lists. For existing chunks it prefers chunkservers holding standard parts, then non-standard parts, then fills remaining DS slots from the randomized list. Remaining stripe entries are filled only from randomized chunkservers.

## State And Persistence Behavior
No persistent local state beyond temporary arrays. It reads chunk/chunkserver topology from the LizardFS client instance and serializes it into NFS-Ganesha XDR responses.

## Dependencies And Integration Points
Depends on FSAL/pNFS XDR helpers, `context_wrap`, `lzfs_internal`, LizardFS C API, and `MFSCommunication.h` constants. Complements `mds_handle.c` layoutget, which embeds device ids and DS wire handles.

## Risks And Edge Cases
The local `remove_if` copies from destination index `j` into source index `i`, which appears reversed and may corrupt filtering. Duplicate-IP detection assumes sorted entries and pointer arithmetic. If all chunkservers are disconnected or filtering empties the list, deviceinfo fails. Randomization uses `rand()` without visible seeding. Stripe count is capped to 4096, so very large files rely on the design assumption that every DS can serve every chunk.

## Test Signals
Needs tests for deviceinfo encoding, disconnected/duplicate filtering, empty chunkserver handling, multipath ordering, and large-file stripe cap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/mds_export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/mds_handle.c -->
# sources/distributed-fs/lizardfs/src/nfs-ganesha/mds_handle.c

## Purpose
Implements pNFS object-handle layout operations for LizardFS FSAL metadata-server mode.

## Important APIs, Types, And Functions
Provides `lzfs_fsal_layoutget`, `lzfs_fsal_layoutreturn`, `lzfs_fsal_layoutcommit`, and `lzfs_fsal_handle_ops_pnfs` to install those operations.

## Control Flow
`layoutget` validates NFSv4.1 file layout, builds a pNFS device id from export id and inode, writes a DS wire handle containing the inode, uses `MFSCHUNKSIZE` as layout utility/stripe unit, encodes a file layout via `FSAL_encode_file_layout`, and marks the layout as last segment and return-on-close. `layoutreturn` validates layout type and otherwise succeeds. `layoutcommit` optionally updates file size and mtime based on layout commit arguments by fetching current attrs and sending a LizardFS setattr.

## State And Persistence Behavior
Layoutget itself does not persist state; it returns layout metadata to clients. Layoutcommit can persist size/mtime changes through `liz_cred_setattr`.

## Dependencies And Integration Points
Depends on Ganesha pNFS helpers, `context_wrap`, `lzfs_internal`, and `MFSCommunication.h`. Works with `mds_export.c` deviceinfo and `ds.c` DS handles.

## Risks And Edge Cases
`layoutcommit` has a FIXME questioning whether the operation makes sense. It assigns `attr.st_mtim.tv_sec = arg->new_time.nseconds` instead of `tv_nsec`, likely corrupting mtime nanoseconds. It calls `setattr` even with mask 0, which may be harmless but unnecessary. Layoutget grants one whole-file segment and assumes DS can serve chunks according to the encoded device info.

## Test Signals
pNFS layoutget/layoutcommit integration tests should validate encoded handles, device ids, file-size extension, mtime update, and unsupported layout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/nfs-ganesha/mds_handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/protocol/CMakeLists.txt

## Purpose
Builds the LizardFS protocol library and its unit tests.

## Important APIs, Types, And Functions
Includes the protocol source directory, collects `PROTOCOL` sources, builds `lzfsprotocol`, creates the `lzfsprotocol` unittest target from `${PROTOCOL_TESTS}`, and links tests with `mfscommon`.

## Control Flow
CMake source collection feeds both the library and test macro, making protocol headers and helpers available to other components.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
Depends on project-local CMake macros `collect_sources`, `create_unittest`, and `link_unittest`. The resulting library is a dependency for components that serialize/deserialize LizardFS wire packets.

## Risks And Edge Cases
Protocol code is mostly header/macros; source collection must include tests and generated/inline-heavy headers correctly. Missing `mfscommon` linkage would break serialization helper tests.

## Test Signals
Successful build and execution of protocol unit tests such as `cltocs_unittest.cc` and `cltoma_unittest.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/MFSCommunication.h -->
# sources/distributed-fs/lizardfs/src/protocol/MFSCommunication.h

## Purpose
Defines the core LizardFS/MooseFS wire protocol constants: packet framing, block/chunk geometry, file/object type codes, mode/flag enums, session flags, and command ids with documented payload layouts.

## Important APIs, Types, And Functions
This is a macro/constant header, not an implementation file. It defines packet frame comments (`type:32 length:32 data`), block and chunk masks/sizes (`MFSBLOCKSIZE`, `MFSCHUNKSIZE`, `MFSCHUNKBITS`, etc.), filesystem limits, file type chars, attribute/set flags, session flags, lock operations, xattr modes, server status constants, and hundreds of command IDs across any-to-any, metalogger-master, chunkserver-master, client-chunkserver, chunkserver-chunkserver, client-master, admin, quota, lock, task, tape, and stats protocols. It also defines the C++ `SugidClearMode` enum when not building C/Wireshark code.

## Control Flow
There is no executable control flow. Other protocol headers and components include this file to choose packet ids and interpret payload comments. Static preprocessor checks enforce power-of-two block/chunk assumptions.

## State And Persistence Behavior
No state. The constants define persistent wire compatibility: changing values would break client/master/chunkserver interoperability and stored protocol assumptions.

## Dependencies And Integration Points
Included by mount write code, Ganesha pNFS code, and protocol serializers such as `cltocs.h`, `cltoma.h`, and `cstocl.h`. It is also likely used by master/chunkserver/client implementations and tools.

## Risks And Edge Cases
This is a compatibility-critical registry with legacy and LizardFS-extended IDs interleaved. Duplicate comments/defines appear around chunks health and numeric comments, so maintainers must avoid accidental ID reuse. Payload comments are documentation rather than compiler-checked schemas except where newer serializer headers wrap them. Any change to geometry macros affects cache/write paths, protocol sizes, and pNFS layout sizing.

## Test Signals
Protocol serialization unit tests validate selected packet wrappers. Full compatibility depends on integration tests across mixed-version clients, masters, and chunkservers, plus Wireshark/tooling consumers if enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/MFSCommunication.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/chunks_with_type.h -->
# sources/distributed-fs/lizardfs/src/protocol/chunks_with_type.h

## Purpose
Defines serializable chunk-id plus chunk-part-type records for protocol messages.

## Important APIs, Types, And Functions
Uses `LIZARDFS_DEFINE_SERIALIZABLE_CLASS` to declare `legacy::ChunkWithType` using `legacy::ChunkPartType` and modern `ChunkWithType` using `ChunkPartType`, each with `uint64_t id` and `type`.

## Control Flow
No executable flow beyond generated serialization/deserialization methods from macros.

## State And Persistence Behavior
No runtime state; it defines wire-serializable value types.

## Dependencies And Integration Points
Depends on `common/chunk_part_type.h` and `common/serialization_macros.h`. Used by protocol messages that need to carry chunk ids with standard/xor/EC part type information.

## Risks And Edge Cases
Legacy and modern names differ only by namespace, so call sites must choose the correct type for packet version compatibility. Serialization size changes follow `ChunkPartType` representation changes.

## Test Signals
Covered indirectly by packet tests that serialize chunk type fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/chunks_with_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/chunkserver_list_entry.h -->
# sources/distributed-fs/lizardfs/src/protocol/chunkserver_list_entry.h

## Purpose
Defines the serializable chunkserver status/list entry used in newer client-master chunkserver list responses.

## Important APIs, Types, And Functions
`ChunkserverListEntry` contains version, server IP/port, used/total space, chunk count, to-delete used/total space, to-delete chunk count, error counter, and label.

## Control Flow
No executable control flow beyond generated serialization methods.

## State And Persistence Behavior
No local state. Instances represent a snapshot of chunkserver state transmitted over the protocol.

## Dependencies And Integration Points
Depends on serialization macros and is referenced by `LIZ_MATOCL_CSERV_LIST` payload documentation in `MFSCommunication.h` and likely by master/client protocol handlers.

## Risks And Edge Cases
Field order is the wire contract. The string label extends older fixed-size records; mixed-version callers must use the correct packet version.

## Test Signals
Should be covered by protocol serialization tests for chunkserver list messages and compatibility tests with older list formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/chunkserver_list_entry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/cltocs.h -->
# sources/distributed-fs/lizardfs/src/protocol/cltocs.h

## Purpose
Defines typed serializers/deserializers for client-to-chunkserver packets.

## Important APIs, Types, And Functions
Supports prefetch, read, write init, write data prefix, write end, and test chunk messages. Packet versions distinguish standard/xor legacy chunk types from EC-capable `ChunkPartType` and `ChunkTypeWithAddress` chains. `writeData::kPrefixSize` defines the headerless prefix length for write data before payload bytes.

## Control Flow
Inline serializers call `serializePacket` or `serializePacketPrefix` with the correct command id and version. Deserializers verify packet version then unpack fields with `deserializeAllPacketDataNoHeader` or `deserializePacketDataNoHeader`.

## State And Persistence Behavior
No state. It defines wire encoding for read/write operations used by chunkserver clients and write paths.

## Dependencies And Integration Points
Depends on serialization macros, chunk part/address types, `protocol/packet.h`, and IDs from `MFSCommunication.h`. Integrated by chunk IO code, including mount write/read logic.

## Risks And Edge Cases
Correct packet version selection is critical for EC chunks. `writeData::serializePrefix` reserves `size` bytes of extra payload, so callers must append exactly matching data and CRC semantics. Prefix size constants must stay synchronized with field layout.

## Test Signals
`cltocs_unittest.cc` exercises read, write init, write data prefix, write end, and test chunk round trips and header ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/cltocs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/cltocs_unittest.cc -->
# sources/distributed-fs/lizardfs/src/protocol/cltocs_unittest.cc

## Purpose
Validates client-to-chunkserver packet serialization wrappers.

## Important APIs, Types, And Functions
Defines GoogleTests for `cltocs::read`, `writeInit`, `writeData`, `writeEnd`, and `testChunk`. Uses `verifyHeader`, `verifyHeaderInPrefix`, `removeHeaderInPlace`, in/out pair macros, and chunk type constants.

## Control Flow
Each test serializes representative fields into a byte vector, verifies the command header, removes the header, deserializes the body/prefix, and asserts all output fields match input.

## State And Persistence Behavior
No persistence. Tests operate on in-memory vectors.

## Dependencies And Integration Points
Depends on `protocol/cltocs.h`, GoogleTest, `common/lizardfs_version.h`, and unittest helper headers. Protects packet wrappers used by mount/chunkserver communication.

## Risks And Edge Cases
Tests cover one modern EC-style chunk type path but do not exhaust legacy overloads, malformed versions, truncated buffers, or payload data after write/read prefixes.

## Test Signals
Passing tests signal that selected CLTOCS packet IDs, field order, versions, and prefix-size calculations remain compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/cltocs_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/cltoma.h -->
# sources/distributed-fs/lizardfs/src/protocol/cltoma.h

## Purpose
Defines typed serializers/deserializers for newer client-to-master packets.

## Important APIs, Types, And Functions
Macro-generated packet wrappers cover credential updates, mknod/mkdir with umask, ACL get/set/delete across legacy/POSIX/RichACL versions, IO limits, quota set/delete/get, metadata server status/list, goal get/set/list, chunk health, chunkserver list variants, chunk info, hostname/admin operations, tape operations, truncate/truncate-end, flock/getlk/setlk and interrupts, lock management, whole-path lookup, recursive remove, paged getdir/reserved/trash, task management, snapshot, and defective-file listing. Manual namespaces cover fuse read chunk, write chunk, and write chunk end.

## Control Flow
Generated serializers pack fields with command ids and versions from `MFSCommunication.h`; deserializers verify versions and unpack in fixed order. Manual chunk functions wrap write/read chunk packets that include lock ids for modern write flows.

## State And Persistence Behavior
No runtime state; it defines stable wire formats for master operations that affect metadata, quotas, ACLs, locks, tasks, and chunk allocation.

## Dependencies And Integration Points
Depends on ACL, rich ACL, MooseFS string, small vector, lock info, quota, packet, and `MFSCommunication.h`. Used by mount/client master communication and tools.

## Risks And Edge Cases
This header has many compatibility surfaces. Version constants and overloads must align with master handlers. Some packet names share namespaces with multiple versions/overloads, so ambiguous calls are possible if argument types are not precise. Lock and quota structures carry complex nested serialization that needs separate compatibility tests.

## Test Signals
`cltoma_unittest.cc` covers core chunk write/read packets, chunk health, and ACL get/set/delete. Many other wrappers need targeted tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/cltoma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/cltoma_unittest.cc -->
# sources/distributed-fs/lizardfs/src/protocol/cltoma_unittest.cc

## Purpose
Validates selected client-to-master packet serialization wrappers.

## Important APIs, Types, And Functions
Tests `fuseReadChunk`, `fuseWriteChunk`, `fuseWriteChunkEnd`, `chunksHealth`, `fuseDeleteAcl`, `fuseGetAcl`, and `fuseSetAcl`. Uses in/out pair helpers, packet header helpers, and an `AccessControlList` sample.

## Control Flow
Each test serializes fields, verifies the command id, strips the header, deserializes, and compares outputs. ACL set additionally builds a POSIX ACL with mode and named group entry and compares full ACL equality.

## State And Persistence Behavior
No persistent state. Tests validate byte-vector serialization only.

## Dependencies And Integration Points
Depends on `protocol/cltoma.h`, GoogleTest, and unittest helpers. Protects master communication used by mount/client and administrative paths.

## Risks And Edge Cases
The test file covers a small fraction of `cltoma.h`. It does not test quotas, locks, admin commands, paged directory/trash/reserved listings, task/snapshot packets, rich ACLs, legacy ACLs, malformed buffers, or version mismatch handling.

## Test Signals
Passing tests provide confidence for chunk allocation/finish packet formats and basic ACL packet formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/cltoma_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/cstocl.h -->
# sources/distributed-fs/lizardfs/src/protocol/cstocl.h

## Purpose
Defines typed serializers/deserializers for chunkserver-to-client read/write response packets.

## Important APIs, Types, And Functions
`readData` serializes/deserializes read-data prefixes and defines modern and legacy prefix sizes. `readStatus` serializes chunk id plus status. `writeStatus` serializes chunk id, write id, and status.

## Control Flow
Read-data prefix serialization reserves CRC plus data bytes as extra payload, then writes version, chunk id, read offset, and read size. Prefix deserialization also extracts CRC. Status serializers use version 0 packet bodies with direct field unpacking.

## State And Persistence Behavior
No state. These wrappers define wire responses used by clients after chunkserver reads/writes.

## Dependencies And Integration Points
Depends on serialization macros, packet helpers, and IDs from `MFSCommunication.h`. Used by read/write data paths and chunkserver/client protocol handlers.

## Risks And Edge Cases
Callers must append/consume CRC and data consistently with prefix sizes. Legacy prefix size omits the version field, so compatibility code must know which format it is parsing. Status values are raw `uint8_t` LizardFS statuses and need correct higher-level error mapping.

## Test Signals
No direct `cstocl` unit test in subset; coverage should mirror `cltocs_unittest` with read data/status and write status round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/cstocl.h -->
