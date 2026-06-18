# subset-b-009692 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/mem_handle.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/mem_handle.c

## Purpose
`mem_handle.c` implements the FSAL object operations for the in-memory MEM FSAL. It owns object allocation, directory indexing, file handle packaging, lookup/readdir, create/link/unlink/rename, attribute mutation, open/share state, read/write/commit/close, reference release, and wire/key conversion. This FSAL is primarily a test backend: it keeps its namespace and file data in process memory, optionally simulates async I/O completion, and uses Ganesha FSAL common helpers for share reservations and fd-lifetime accounting.

## Important APIs, Types, And Functions
The file operates on `struct mem_fsal_obj_handle` and `struct mem_dirent` from `mem_int.h`. Directories use two AVL trees: `avl_name` for name lookup and `avl_index` for cookie-ordered readdir. Files use `mh_file.share` and `mh_file.fd` to integrate with FSAL share reservation and fd LRU helpers. `mem_inode_number` is a process-global atomic source of file ids.

Core helpers are `mem_n_cmpf()`, `mem_i_cmpf()`, `mem_int_get_ref()`, `mem_int_put_ref()`, `mem_cleanup()`, `package_mem_handle()`, `mem_update_change_locked()`, `mem_insert_obj()`, `mem_dirent_lookup()`, `mem_readdir_seekloc()`, `mem_remove_dirent_locked()`, `mem_copy_attrs_mask()`, `mem_open_my_fd()`, and `_mem_alloc_handle()`. Public/exported or ops-vector functions include `mem_lookup()`, `mem_readdir()`, `mem_mkdir()`, `mem_mknode()`, `mem_symlink()`, `mem_readlink()`, `mem_setattr2()`, `mem_link()`, `mem_unlink()`, `mem_rename()`, `mem_open2()`, `mem_status2()`, `mem_reopen2()`, `mem_read2()`, `mem_write2()`, `mem_commit2()`, `mem_close2()`, `mem_handle_to_wire()`, `mem_handle_to_key()`, `mem_release()`, `mem_merge()`, `mem_handle_ops_init()`, `mem_lookup_path()`, and `mem_create_handle()`.

## Control Flow
Object creation flows through `mem_create_obj()` and `_mem_alloc_handle()`: allocate a variable-sized object, assign a fileid, insert it into the export object list under `mfe_exp_lock`, initialize type-specific state, initialize the generic FSAL handle, and either mark it as export root or insert a `mem_dirent` into the parent. Lookup locks the parent unless `op_ctx->fsal_private` already signals that readdir holds the lock, resolves `"."`/`".."` specially, and otherwise searches the name AVL tree. Readdir seeks by cookie in the index AVL tree, emits up to roughly two MDCACHE directory chunks, refs each emitted child, and returns the next cookie.

Mutation operations adjust directory entries and object attributes in local memory. `mem_link()` adds another dirent and increments link count. `mem_unlink()` rejects non-empty directories and open regular files, removes the dirent, decrements child link counts for non-directories, and updates parent change time. `mem_rename()` checks existing destination compatibility, unlinks an empty or compatible destination, removes the old dirent, may replace `m_name`, and inserts into the new directory; the source notes that this is not atomic.

Open and I/O split between stateful and stateless paths. `mem_open2_by_handle()` uses FSAL fd work helpers, checks share conflicts, reopens the per-state or global fd, updates fd LRU state, handles truncation, and validates exclusive-create verifiers. `mem_open2()` handles create-by-name, open-by-handle, attributes, global fd fallback, and share counter updates. `mem_read2()` and `mem_write2()` call `fsal_start_io()`, perform in-memory copy/synthesis, update atime/mtime/change, and either complete inline or submit `mem_async_complete()` to `mem_async_fridge`. Completion releases temporary share counters for stateless I/O and calls the upper callback.

## State And Persistence
All namespace and data state is process-local and disappears at module unload or restart. Regular file storage is bounded by `MEM.inode_size` in the object allocation; file size can grow beyond stored data, but reads outside stored bytes return synthetic `'a'` bytes. Object identity is carried by a fixed 58-byte `handle` built from fileid, basename, and CityHash64. `mem_create_handle()` can only revive handles that still exist in the in-process FSAL handle list; deleted or restarted objects become stale.

Reference counts are explicit and separate from directory membership. Every dirent holds a child ref; lookup/readdir hand refs to callers; `mem_release()` and `put_ref` eventually call `mem_cleanup()`. Export roots and objects still linked from directories are deliberately not deconstructed by `mem_cleanup()`. Directory child counts are atomic but the tree edits require object locks. Export object list edits require `mfe_exp_lock`.

## Dependencies And Integration Points
This file depends on Ganesha FSAL commonlib, fsal fd/share helpers, MDCACHE directory chunk config, Ganesha list and AVL utilities, CityHash64, LTTng tracepoints, op-context credentials/export state, and MEM globals from `mem_main.c`/`mem_int.h`. `mem_handle_ops_init()` is the integration point called by module init to populate the FSAL object ops vector. `mem_lookup_path()` and `mem_create_handle()` are wired by the MEM export ops implementation.

## Risks
The backend is intentionally non-persistent and not a full filesystem. Rename is documented as non-atomic, and attribute reads are often only weakly locked because the file treats MEM as non-production. Cookie generation uses `CityHash64(name)`, so cookie collisions are theoretically possible and could affect directory ordering/lookup by index. `package_mem_handle()` truncates names to the opaque handle budget after a hash and length, so uniqueness depends on hash behavior plus visible name prefix. The async decision uses `(random() % 1) == 1`, which is always false, so `MEM_RANDOM_OR_INLINE` appears to never choose async through that branch. In `mem_write2()`, the async path shadows `async_arg` with a new `gsh_malloc()` allocation and does not initialize `temp_fd`; that deserves focused testing or review. Error paths in read/write call `done_cb()` with success after `fsal_start_io()` failure because `status` is not propagated to the callback at `exit`.

## Test Signals
Useful tests are namespace create/lookup/readdir/unlink/rename sequences, hardlink link-count behavior, non-empty directory removal rejection, stale handle lookup after unlink, wire/key round trips through MDCACHE, `open2` share conflict and truncate behavior, stateless versus stateful read/write share counter cleanup, async read/write completion under all async modes, file sizes larger than `Inode_Size`, and concurrent lookup/readdir/mutation under thread sanitizer. The most important regression signals are refcount leaks/double-free assertions, fd LRU counter balance, `ERR_FSAL_STALE` for deleted handles, and callback status correctness on I/O setup failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/mem_handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/mem_int.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/mem_int.h

## Purpose
`mem_int.h` is the private interface for FSAL_MEM. It defines the in-memory export, object, dirent, state, module, async mode, and package/export/handle/upcall function contracts shared by MEM source files.

## Important APIs, Types, And Functions
`enum async_types` defines `MEM_INLINE`, `MEM_RANDOM_OR_INLINE`, `MEM_RANDOM`, and `MEM_FIXED` for test I/O completion behavior. `struct mem_fsal_export` embeds `struct fsal_export`, stores the export path/root handle, links into `MEM.mem_exports`, protects the per-export object list with `mfe_exp_lock`, and carries async delay/stall/type configuration. `struct mem_state_fd` prepends `struct state_t` so default state freeing can work and adds a per-state `struct fsal_fd`.

`struct mem_fsal_obj_handle` embeds `struct fsal_obj_handle`, cached POSIX attributes, fileid, fixed wire handle, type-specific unions for directory/file/node/symlink state, reverse dirent list, export list entry, owning export pointer, debug name, data capacity, export-root flag, explicit refcount, and flexible file data storage. `struct mem_dirent` links a child handle to a directory by name and cookie/index with AVL nodes and a reverse-list node. The header declares `mem_handle_ops_init()`, `mem_create_export()`, `mem_update_export()`, `str_async_type()`, `mem_clean_export()`, `mem_clean_all_dirents()`, `mem_up_pkginit()`, `mem_up_pkgshutdown()`, and the export lookup/create-handle methods.

## Control Flow
The header establishes the object ownership model used by `mem_handle.c` and `mem_export.c`. Export creation allocates `mem_fsal_export`, initializes the root lazily through `mem_lookup_path()`, and appends exports to `MEM.mem_exports`. Object operations use the embedded `fsal_obj_handle` for upper-layer dispatch and the private union for actual in-memory behavior. Directory traversal and mutation are expressed through `mem_dirent` entries in the parent AVL trees and child reverse lists.

## State And Persistence
All declared state is memory-resident. The only long-lived structures are module globals and export/object lists inside the running process. `V4_FH_OPAQUE_SIZE` fixes MEM file-handle size to 58 bytes. `mem_free_handle()` removes an object from the export object list, clears the owning export pointer and debug name, and frees the object; callers must hold `mfe_exp_lock` for write.

## Dependencies And Integration Points
The header depends on Ganesha AVL/list primitives, FSAL types, optional LTTng trace definitions, pthread rwlocks, and MEM-specific package globals. It is included by MEM handle, export, main, and upcall implementations. The `extern struct mem_fsal_module MEM` global is the module-wide control block registered with Ganesha.

## Risks
Correctness relies on lock ordering documented outside the type definitions: object locks for trees/reverse lists and export locks for object-list lifetime. Because `mem_fsal_obj_handle` has a flexible `data[0]` tail and file capacity is configured globally, callers must not assume data length follows file size. `mem_free_handle()` is inline and destructive, so misuse without the export write lock can corrupt the export object list.

## Test Signals
Compile-time signals include all MEM sources agreeing on struct layout, especially `mem_state_fd` with `state` first. Runtime signals include export cleanup freeing all object list entries, no stale reverse dirents after unlink/rename, and async/upcall configuration being visible across MEM source files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/mem_int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/mem_main.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/mem_main.c

## Purpose
`mem_main.c` is the module entry/exit and global configuration file for FSAL_MEM. It defines the MEM `fsal_module`, default static filesystem capabilities, module-level config block, async worker package lifecycle, and `MODULE_INIT`/`MODULE_FINI` hooks.

## Important APIs, Types, And Functions
The global `struct mem_fsal_module MEM` initializes FSAL capabilities such as POSIX attributes, unique handles, link and symlink support, readdir plus support, no lock support, max read/write sizes, and time support. `mem_items` exposes `Inode_Size`, `Up_Test_Interval`, `Async_Threads`, and `Whence_is_name`. `mem_block` registers those settings under the `MEM` config block. `mem_async_fridge` is the async I/O worker pool used by `mem_handle.c`.

`mem_async_pkginit()` creates a `fridgethr` worker pool named `MEM_ASYNC_fridge` when `Async_Threads` is nonzero. `mem_async_pkgshutdown()` stops, cancels on timeout, destroys, and clears the async fridge. `mem_init_config()` loads module config, starts the upcall test package, starts the async package, mirrors `whence_is_name` into fsinfo, and logs capabilities. `init()` registers the FSAL and wires module ops and handle ops. `finish()` shuts down upcalls, async workers, and unregisters the FSAL.

## Control Flow
On load, `init()` calls `register_fsal()`, assigns `create_export`, `update_export`, and `init_config`, initializes the module export list, seeds `MEM.next_inode`, and calls `mem_handle_ops_init()`. During configuration, `mem_init_config()` parses `MEM`, then starts optional background packages. On unload, `finish()` tears down background packages before unregistering the module; unregister failure is fatal and aborts.

## State And Persistence
Module config is held in the global `MEM` object for the process lifetime. `MEM.mem_exports` tracks live exports; `mem_up.c` iterates it for test upcalls. `mem_async_fridge` is process-global and shared by all MEM exports. No state persists across module reload or process restart.

## Dependencies And Integration Points
This file integrates with Ganesha module registration, config parsing, FSAL private helpers, fridgethr workers, MEM handle/export/upcall functions, and fsinfo display. `Inode_Size` directly controls allocation behavior in `mem_handle.c`; `Up_Test_Interval` controls `mem_up.c`; `Async_Threads` controls async read/write completions.

## Risks
Async initialization succeeds as a no-op when thread count is zero; callers must tolerate inline-only I/O. If `mem_up_pkginit()` succeeds but async init fails, the code returns failure without explicitly shutting down the upcall package in that path. Configuration allows very large per-file `Inode_Size` up to 0x200000, so tests that create many files can consume memory quickly.

## Test Signals
Exercise module load/config/unload with zero and nonzero `Async_Threads` and `Up_Test_Interval`, invalid config values, repeated init/shutdown, and export creation after config. Check that `whence_is_name` appears in fsinfo, async fridge is destroyed on unload, and no worker threads survive shutdown timeout paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/mem_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/mem_up.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/mem_up.c

## Purpose
`mem_up.c` implements FSAL_MEM upcall testing. When configured, it starts a looper thread that periodically selects random in-memory objects from each MEM export and sends FSAL upcalls for update, invalidate, and invalidate-close.

## Important APIs, Types, And Functions
The file owns static `mem_up_fridge`. `mem_invalidate()` builds a handle key and calls `up_ops->invalidate(..., FSAL_UP_INVALIDATE_CACHE)`. `mem_invalidate_close()` calls `up_ops->invalidate_close()` similarly. `mem_update()` changes the object ctime/change attributes, prepares an attrlist with `ATTR_CTIME` and `ATTR_CHANGE`, and calls `up_ops->update()`. `mem_rand_obj()` selects an object from an export object list while holding `mfe_exp_lock` for read. `mem_up_run()` is the looper callback. `mem_up_pkginit()` and `mem_up_pkgshutdown()` manage the looper fridge.

## Control Flow
`mem_up_pkginit()` is called from MEM config initialization. If `MEM.up_interval` is zero, no thread is created. Otherwise it initializes a single-thread `fridgethr_flavor_looper` with `thread_delay = MEM.up_interval` and submits `mem_up_run()`. Each run iterates `MEM.mem_exports`, picks up to three random objects per export, and calls update, invalidate, and invalidate-close independently when an object is available. Shutdown sends a stop command with timeout, cancels if needed, destroys the fridge, and clears the global pointer.

## State And Persistence
The upcall worker does not persist data; it mutates in-memory object ctime/change for update tests and sends cache invalidation signals. It relies on the live `MEM.mem_exports` list and each export's `mfe_objs` list. Random selection returns a pointer after dropping the export read lock, so object lifetime is protected only by the broader MEM ref/lifetime behavior.

## Dependencies And Integration Points
The file depends on `mem_int.h`, Ganesha FSAL upcall vectors, fridgethr, op-independent handle-to-key object ops, and the global `MEM` module. It is a test integration with upper cache invalidation paths rather than core filesystem serving behavior.

## Risks
`MEM.mem_exports` is noted in `mem_int.h` as lacking locking for serious use, and `mem_up_run()` iterates it without a module-level lock. `mem_rand_obj()` checks `glist_empty()` before taking `mfe_exp_lock`, then selects and returns an unrefed object pointer after unlocking; concurrent export cleanup could race in stress scenarios. `rand()` is used without explicit synchronization.

## Test Signals
Enable `Up_Test_Interval` and verify update/invalidate/invalidate-close callbacks reach MDCACHE without crashes. Combine with concurrent create/delete/export shutdown under sanitizer. Check that disabling the interval creates no thread and that shutdown handles both normal stop and timeout/cancel paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/mem_up.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/CMakeLists.txt

## Purpose
This CMake file builds and installs the `fsalproxy_v3` loadable FSAL module. It defines compile flags, source membership, dependencies, sanitizer integration, link libraries, version metadata, and install destination.

## Important APIs, Types, And Functions
The build target sources are `main.c`, `nlm.c`, `rpc.c`, and `utils.c`, plus `$<TARGET_OBJECTS:nfs_mnt_xdr>`. The target is declared as `add_library(fsalproxy_v3 MODULE ...)`. It links `ganesha_nfsd`, `${SYSTEM_LIBRARIES}`, and `${LDFLAG_DISALLOW_UNDEF}`. When `USE_LTTNG` is enabled, it adds dependency on `gsh_trace_header_generate` and includes generated trace file properties.

## Control Flow
CMake adds `-D__USE_GNU`, defines the source list, creates the module target, applies sanitizer settings, conditionally wires LTTng generation, links required libraries, sets `VERSION 4.2.0` and `SOVERSION 4`, and installs the module into `${FSAL_DESTINATION}` as component `fsal`.

## State And Persistence
There is no runtime state here. The persistent artifact is the built module and its install metadata. The source list controls what code is included in the loadable FSAL.

## Dependencies And Integration Points
The target depends on generated XDR object code for NFS mount protocol, Ganesha server symbols, system RPC/socket libraries from `${SYSTEM_LIBRARIES}`, and optional trace-generation artifacts. The disallow-undefined linker flag is important because FSAL modules are dynamically loaded but should still resolve against expected server symbols.

## Risks
Adding a new source file to FSAL_PROXY_V3 without updating this list will omit it from the module. LTTng-specific generated property inclusion depends on `${CMAKE_BINARY_DIR}/gsh_lttng_generation_file_properties.cmake` existing when `USE_LTTNG` is true. `-D__USE_GNU` can affect system header feature exposure globally for this target.

## Test Signals
Build with and without `USE_LTTNG`, with sanitizers enabled, and with undefined-symbol disallowance. Verify the module installs into the configured FSAL destination and dynamically loads in a Ganesha runtime config using `FSAL { Name = PROXY_V3; }`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/main.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/main.c

## Purpose
`FSAL_PROXY_V3/main.c` implements the Ganesha FSAL surface for a stateless NFSv3 proxy backend. It registers the PROXY_V3 module, parses global/export config, mounts a remote NFSv3 export via MOUNT v3, discovers service ports through portmapper, translates FSAL operations into NFSv3 RPCs, wraps remote file handles in FSAL object handles, and wires all supported object/export operations.

## Important APIs, Types, And Functions
The global `PROXY_V3` module advertises POSIX attributes, link/symlink support, NLM lock support, ACL allow, unique handles, and readdir-plus. Global config options include `maxread`, `maxwrite`, `num_sockets`, and `allow_lookup_optimization`; export config requires `Srv_Addr`. Accessors such as `proxyv3_sockaddr()`, `proxyv3_socklen()`, `proxyv3_nlm_port()`, `proxyv3_creds()`, and `proxyv3_readdir_preferred()` expose per-export RPC parameters to other files.

Handle helpers include `proxyv3_alloc_handle()`, `proxyv3_handle_release()`, `proxyv3_handle_to_wire()`, `proxyv3_wire_to_host()`, `proxyv3_create_handle()`, and `proxyv3_handle_to_key()`. Operation implementations cover lookup/getattr/setattr/root/path lookup, create/open, symlink/link/readlink, mkdir/mknode/readdir, read/write/commit, unlink/rename, dynamic fsinfo, close/status/reopen, and state allocation. `proxyv3_fill_fsinfo()` updates static fsinfo from remote FSINFO. `proxyv3_create_export()` performs remote mount and final export setup. `proxy_v3_init()` registers the module and object ops.

## Control Flow
Module init registers `PROXY_V3`, assigns `init_config` and `create_export`, initializes default object ops, and overrides the operations that the proxy supports. Global config setup initializes the custom RPC pool and NLM subsystem. Export creation allocates a `proxyv3_export`, initializes export ops, parses `Srv_Addr`, attaches the export, derives socket length/name, discovers mountd/nfsd/nlm ports, performs a MOUNT NULL probe, mounts `CTX_FULLPATH(op_ctx)` to get the root `fh3`, optionally probes NLM with NULL, and calls FSINFO to clamp max read/write and preferred readdir count.

Lookup uses either local optimization for `"."`/known `".."` or sends `LOOKUP3`. `proxyv3_lookup_path()` validates that the requested path begins with the export root, handles exact-root lookup through GETATTR on the root handle, and otherwise delegates a single lookup against `root_handle_obj`; the source notes full slash-splitting is still TODO. Create-like operations share `proxyv3_issue_createlike()`, which sends the RPC, requires both result handle and attributes despite NFSv3 optionality, converts parent weak-cache-consistency attributes, allocates the FSAL handle, and frees XDR output. I/O operations are synchronous wrappers around `READ3`, `WRITE3`, and `COMMIT3`, using the FSAL async callback interface only as an immediate completion callback.

## State And Persistence
The proxy stores remote NFSv3 file handles and fattr3 snapshots in `struct proxyv3_obj_handle`. Each handle owns a separately allocated `fh3.data.data_val` buffer. Optional parent pointers allow `".."` optimization but are not guaranteed for handles reconstructed from wire keys. The export stores the root handle bytes, discovered ports, preferred readdir size, and a cached root handle object. No remote state is persisted locally beyond process memory; the authoritative namespace/data lives on the backend NFSv3 server.

The proxy is mostly stateless for opens and closes. It maps NFSv4-style open-by-handle to GETATTR, create-by-name to CREATE3, returns closed/null status for `status2`, and returns `ERR_FSAL_NOT_OPENED` for close paths so upper layers do not manage a real fd. Lock state is delegated to NLM in `nlm.c`.

## Dependencies And Integration Points
The file depends on generated NFSv3/MOUNT/NLM XDR types, `proxyv3_fsal_methods.h`, `rpc.c` for transport, `utils.c` for status/attribute translation, `nlm.c` for locks, Ganesha FSAL common/config/init APIs, op-context credentials and export paths, and MDCACHE/object-handle contracts. It integrates with the backend through portmapper, MOUNT v3, NFS v3, and NLM v4 over TCP using AUTH_UNIX credentials derived from `op_ctx`.

## Risks
`proxyv3_lookup_path()` only handles root or one path component after the export prefix; nested path lookup is marked TODO. Export creation error paths after `fsal_attach_export()` often `gsh_free(export)` without detaching the export or freeing export ops, so failed mount/NLM setup can leak or leave partial registration. Several operations access `result.*res_u.resok` weak-cache data even when status is not OK, which can be invalid for failed NFSv3 replies. READLINK and READ/WRITE paths do not call `xdr_free()` on success, so decoded allocations require audit. The proxy assumes single-iovec read/write and rejects multi-iovec requests. It also assumes backend returns handles/attributes for create-like and readdirplus operations, falling back for some readdir cases but failing create-like operations that omit optional results.

## Test Signals
Run against Linux knfsd and at least one non-Linux NFSv3 server. Cover mount success/failure, portmapper unavailable, NLM unavailable, root and nested lookup, create modes, missing post-op attrs/handles, readdirplus fallback to LOOKUP/GETATTR, symlink/hardlink/mknod, READ/WRITE/COMMIT including unstable writes, remove versus rmdir, rename WCC attrs, wire-to-host/create-handle round trips, and FSINFO clamping. Fault injection should force RPC transport failure, NFS error statuses, short backend replies, and export creation failures after attach.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/nlm.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/nlm.c

## Purpose
`nlm.c` implements PROXY_V3 byte-range lock operations by translating Ganesha FSAL lock requests into NLM v4 RPCs against the backend NFSv3 server's lock manager.

## Important APIs, Types, And Functions
`proxyv3_nlm_init()` caches a client machine name and process id for NLM owner fields. `proxyv3_is_valid_lockop()` rejects unsupported async/blocking locks, non-POSIX locks, missing owners, missing TEST conflict output, and missing NLM port. `proxyv3_nlm_fill_common_args()` fills cookies and `nlm4_lock` fields from the remote fh3, Ganesha state owner, lock range, machine name, and pid. `proxyv3_nlm_commonrpc()` sends the RPC and maps NLM status through `nlm4stat_to_fsalstat()`.

Operation-specific helpers are `proxyv3_nlm_test()`, `proxyv3_nlm_lock()`, `proxyv3_nlm_cancel()`, and `proxyv3_nlm_unlock()`. `proxyv3_clear_conflicting_lock()` initializes conflict output to a whole-file exclusive lock when exact holder information is not available. The exported entry point is `proxyv3_lock_op2()`.

## Control Flow
`proxyv3_lock_op2()` casts the owner, determines whether the requested lock is exclusive, pre-clears conflict output if supplied, validates the request, and dispatches by `fsal_lock_op_t`. TEST sends `NLMPROC4_TEST` and, on `NLM4_DENIED`, fills `conflicting_lock` from `nlm4_holder`. LOCK sends nonblocking `NLMPROC4_LOCK`, preserving reclaim and using `state->state_seqid` as the NLM state. UNLOCK and CANCEL send their corresponding NLM calls. All calls use `proxyv3_nlm_call()` from `rpc.c` with current `op_ctx->creds`.

## State And Persistence
The file stores only process-global NLM client identity: `nlmMachineName` and `nlmSvid`. Actual lock ownership is represented by backend lockd state keyed by caller name, pid, file handle, owner bytes, and byte range. Cookies reuse the beginning of the remote fh3 and are capped at 32 bytes for Linux lockd compatibility.

## Dependencies And Integration Points
It depends on NLM XDR types, Ganesha `nlm_util.h`, `proxyv3_fsal_methods.h`, backend NLM port discovery from export setup, and the RPC transport wrappers. It is connected to Ganesha through `PROXY_V3.handle_ops.lock_op2`.

## Risks
Blocking locks are explicitly unsupported, so any path that reaches `FSAL_OP_LOCKB` is treated as a server fault. Cookie generation from file-handle bytes is simple and can collide for handles sharing a prefix. Crash/recovery behavior is only noted as a TODO; backend lockd may try to recover with this proxy as its client while Ganesha has separate client state. `state` is assumed non-NULL for LOCK because `state->state_seqid` is used. For non-TEST lock conflicts, exact holder data is unavailable and the code reports a whole-file write conflict.

## Test Signals
Exercise LOCK, UNLOCK, TEST conflict, reclaim, NLM unavailable, grace-period, deadlock, stale file handle, read-versus-write lock compatibility, and owner byte preservation. Recovery tests should restart the proxy while locks exist on the backend. Validate Ganesha client-visible errors produced from `NLM4_DENIED`, `NLM4_BLOCKED`, and `NLM4_DENIED_GRACE_PERIOD`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/nlm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/proxyv3_fsal_methods.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/proxyv3_fsal_methods.h

## Purpose
`proxyv3_fsal_methods.h` is the private PROXY_V3 interface shared by the module, RPC transport, NLM, and conversion utilities. It defines the module/export/object data structures and declares all cross-file helper APIs.

## Important APIs, Types, And Functions
`struct proxyv3_fsal_module` embeds the FSAL module and object ops vector, plus global `num_sockets` and `allow_lookup_optimization` config. `struct proxyv3_client_params` stores configured server address, derived sockaddr metadata, display name, discovered mountd/nfsd/nlm ports, and preferred READDIR size. `struct proxyv3_obj_handle` embeds `fsal_obj_handle`, remote `nfs_fh3`, cached `fattr3`, and optional parent pointer. `struct proxyv3_export` embeds `fsal_export`, client params, cached root object, and root handle bytes.

The header declares RPC setup and wrappers, port discovery, NLM locking, NFS/NLM status mapping, POSIX attribute-mask validation, fattr/sattr conversion, and weak-cache-consistency pre/post attr conversion.

## Control Flow
The header enforces the architecture: `main.c` owns FSAL dispatch and object/export lifetime, `rpc.c` owns transport, `nlm.c` owns locking, and `utils.c` owns translation. Other files obtain backend endpoint details through accessors rather than directly reaching into the export in most cases.

## State And Persistence
The declared structures keep only process-local proxy state. Remote file handles are copied into per-object allocations, and export root handle bytes are cached in the export. Parent pointers are optional and may be absent for reconstructed handles.

## Dependencies And Integration Points
The header includes Ganesha FSAL init/types and system socket definitions. It exposes the global `PROXY_V3` symbol used by module init and RPC buffer sizing. It also publishes conversion helpers that are tightly coupled to generated NFSv3/NLM typedefs.

## Risks
The optional parent pointer is `const` but points to separately allocated object handles whose lifetime is not explicitly refcounted by the child. `root_handle` is fixed at `NFS3_FHSIZE`, so callers must validate lengths before copying. Cross-file APIs rely heavily on `op_ctx` for export and credentials, which makes unit testing require a realistic Ganesha context.

## Test Signals
Compile all PROXY_V3 files together with strict warnings to catch signature drift. Unit-style tests should allocate/release handles and verify fh3 deep-copy ownership, parent pointer behavior for `".."`, and conversion helper prototypes against generated XDR types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/proxyv3_fsal_methods.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/rpc.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/rpc.c

## Purpose
`rpc.c` provides a custom TCP ONC RPC client for PROXY_V3. It avoids using standard client helpers because Ganesha's server-side RPC integration conflicts with making nested NFS client calls. It manages a reusable socket/buffer pool, AUTH_UNIX construction, XDR call/reply encoding, record markers, portmapper discovery, and program-specific wrappers for NFS v3, MOUNT v3, and NLM v4.

## Important APIs, Types, And Functions
Global state includes `global_xid`, `rpcMachineName`, `rpcLock`, `rpcNumSockets`, and `fd_entries`. `struct rpc_buf` is a growable byte buffer per pool entry. `struct fd_entry` tracks in-use/open state, endpoint identity, fd, and RPC buffer.

`proxyv3_rpc_init()` initializes hostname, mutex, socket pool, random XID seed, and one-time state. `proxyv3_openfd()` validates IPv4/IPv6 sockaddr inputs, binds a reserved client port under lock, sets the target port, and connects TCP. `proxyv3_fd_is_open()` probes a cached socket with nonblocking peek. `proxyv3_getfdentry()` and `proxyv3_getfd_blocking()` acquire a pool slot, reuse matching sockets, open new sockets, and back off when the pool is full. `proxyv3_release_fdentry()` returns or force-closes a slot. `proxyv3_call()` is the core RPC engine. Wrappers are `proxyv3_nfs_call()`, `proxyv3_mount_call()`, `proxyv3_nlm_call()`, and `proxyv3_find_ports()`.

## Control Flow
A call acquires an fd entry for host/port, creates AUTH_UNIX credentials from passed user credentials or defaults, XDR-encodes an RPC call into the entry buffer after a TCP record marker slot, writes the record marker and payload, destroys auth, reads the response marker and XID, validates the XID and length, resizes the buffer for the full reply, decodes `xdr_replymsg()` with the caller's decode function wired as accepted results, frees only reply wrapper allocations, releases the fd entry for reuse, and returns whether decode and RPC accept status succeeded.

Port discovery loops over MOUNT, NFS, and NLM pmap queries to `PMAPPORT`, using unauthenticated PMAP RPC calls and storing returned TCP ports.

## State And Persistence
State is process-global and lives until module unload/process exit. Sockets remain open across calls when reusable and are force-closed on transport/protocol errors. Buffers are lazily allocated based on current `PROXY_V3.module.fs_info.maxwrite + 512` and grow to larger replies as needed. The pool size is configured by `num_sockets`.

## Dependencies And Integration Points
The file depends on ONC RPC/XDR headers, portmap definitions, sockets, Ganesha allocation/logging, generated NFS/MOUNT/NLM constants, `PROXY_V3` fsinfo, and `proxyv3_fsal_methods.h`. All high-level PROXY_V3 filesystem and lock operations depend on these wrappers for backend communication.

## Risks
The transport uses blocking `connect`, `read`, and `write` without explicit timeouts, so backend stalls can tie up worker threads and pool entries. Partial `read()` returning zero is not specially handled in the reply-body loop and can spin if EOF occurs after the header. `inet_ntop()` is called with the whole sockaddr pointer rather than the address field, which can produce misleading diagnostics or fail. The code assumes single-fragment RPC replies by clearing the high record-marker bit and does not process multi-fragment records. If `xdr_callmsg()` or arg encoding fails, `xdr_destroy()` is not called on the XDR stream. Pool cleanup at module unload is absent in this file. Reserved-port binding serializes under `rpcLock` and can fail under privilege/container restrictions.

## Test Signals
Transport tests should simulate full and partial writes, short reads, EOF after header, mismatched XID, rejected RPC replies, auth failures, large READDIR replies requiring buffer growth, stale reusable sockets, pool exhaustion/backoff, IPv4/IPv6 addresses, unprivileged bind failure, and portmapper missing services. Integration tests should confirm all wrappers use the correct program/version/procedure numbers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/utils.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/utils.c

## Purpose
`utils.c` contains PROXY_V3 translation helpers for NFSv3/NLM statuses and NFSv3 attributes. It maps backend protocol results into Ganesha FSAL statuses, validates representable attribute masks, converts fattr3/pre/post attributes to FSAL attrlists, and converts FSAL setattr data into NFSv3 `sattr3`.

## Important APIs, Types, And Functions
`nfsstat3_to_fsal()` and `nfsstat3_to_fsalstat()` translate NFSv3 status codes. `nlm4stat_to_fsal()` and `nlm4stat_to_fsalstat()` translate NLM v4 statuses. `attrmask_is_posix()` validates that requested output attributes are limited to POSIX plus `ATTR_RDATTR_ERR`. `attrmask_valid()` validates setattr masks, including mutually exclusive client/server atime and mtime forms. `update_attrs_change()` derives FSAL change from max(mtime, ctime). `fattr3_to_fsalattr()`, `pre_attrs_to_fsalattr()`, `post_attrs_to_fsalattr()`, and `fsalattr_to_sattr3()` perform attribute conversion.

## Control Flow
Status conversion uses explicit switch statements and returns `ERR_FSAL_INVAL` with the original protocol status as minor only for unknown statuses. Attribute output conversion first validates the request mask, then copies `fattr3` directly into the FSAL attrlist because this codebase typedefs `fattr3` compatibly, updates change, and marks POSIX supported/valid. Weak-cache pre attrs expose ctime, mtime, size, and derived change only when present. Setattr conversion zeroes all optional fields, validates the mask, and sets NFSv3 option discriminants for mode, uid, gid, size, atime, and mtime.

## State And Persistence
No persistent state is stored. All functions are pure conversions except for logging.

## Dependencies And Integration Points
The file depends on generated NFSv3/NLM protocol types, FSAL conversion helpers such as `fsal2unix_mode()`, attrmask macros, Ganesha time helpers, and `proxyv3_fsal_methods.h`. `main.c` uses these helpers for nearly every NFSv3 operation, and `nlm.c` uses NLM status mapping.

## Risks
`attrmask_is_posix()` logs `ATTRS_NFS3` while allowing `ATTRS_POSIX | ATTR_RDATTR_ERR`, so diagnostics can be confusing. Direct `*fsal_attrs_out = *attrs` depends on the local typedef/layout contract; if generated protocol types diverge, conversion becomes unsafe. `NFS3ERR_REMOTE` maps to `ERR_FSAL_NAMETOOLONG`, which is semantically weak. `NFS3ERR_JUKEBOX` maps to `ERR_FSAL_LOCKED`, which may affect retry behavior. `fsalattr_to_sattr3()` currently ignores rawdev device-number payload even when `ATTR_RAWDEV` is allowed for mknod.

## Test Signals
Use table-driven tests for every NFSv3 and NLM status mapping. Validate accepted and rejected attr masks, especially mixed `ATTR_ATIME`/`ATTR_ATIME_SERVER` and mixed mtime forms. Round-trip representative fattr3 values into FSAL attrs, verify change derivation, and test mknod rawdev conversion expectations against backend behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V3/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/CMakeLists.txt

## Purpose
This CMake file builds and installs the `fsalproxy_v4` loadable FSAL module. It defines the module sources, optional handle-mapping sources, sanitizer integration, link libraries, optional sqlite dependency, version metadata, and install destination.

## Important APIs, Types, And Functions
The default source list is `handle.c`, `main.c`, `export.c`, and `xattrs.c`. When `PROXYV4_HANDLE_MAPPING` is enabled, `handle_mapping/handle_mapping.c` and `handle_mapping/handle_mapping_db.c` are appended. The target is declared as `add_library(fsalproxy_v4 MODULE ...)`, linked against `ganesha_nfsd`, `${SYSTEM_LIBRARIES}`, and `${LDFLAG_DISALLOW_UNDEF}`, and optionally `sqlite3`.

## Control Flow
CMake adds `-D__USE_GNU`, defines the source list, conditionally appends handle-mapping implementation, creates the module, applies sanitizers, links required libraries, adds sqlite when needed, sets `VERSION 4.2.0`/`SOVERSION 4`, and installs into `${FSAL_DESTINATION}`.

## State And Persistence
No runtime state is defined here. The optional handle-mapping build flag controls whether proxy v4 can persist or translate handles through sqlite-backed mapping code elsewhere.

## Dependencies And Integration Points
The module depends on Ganesha server symbols, system libraries, and optional sqlite. `export.c` references handle mapping under `PROXYV4_HANDLE_MAPPING`, so this build file must keep the conditional source and link dependency consistent with that preprocessor option.

## Risks
Mismatching `PROXYV4_HANDLE_MAPPING` with sqlite availability or source inclusion will break builds or runtime symbol resolution. New proxy v4 source files must be added here. Unlike the v3 build file, this file has no LTTng conditional block.

## Test Signals
Build both with and without `PROXYV4_HANDLE_MAPPING`, under sanitizer settings, and with undefined symbols disallowed. Verify the installed module loads and that sqlite is linked only in handle-mapping builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/export.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/export.c

## Purpose
`FSAL_PROXY_V4/export.c` implements export-level configuration, creation, operation wiring, and release for the NFSv4 proxy FSAL. It parses per-export remote server/RPC/security/handle-mapping options, initializes RPC synchronization primitives, attaches the export to the FSAL module, optionally initializes handle mapping, starts the proxy v4 RPC/session machinery, and cleans all export resources on release or failure.

## Important APIs, Types, And Functions
`proxyv4_export_params` declares export config. Core fields include `Retry_SleepTime`, mandatory `Srv_Addr`, `NFS_Service`, `NFS_SendSize`, `NFS_RecvSize`, `NFS_Port`, `Use_Privileged_Client_Port`, and `RPC_Client_Timeout`. Under `_USE_GSSRPC`, it also supports Kerberos principal/keytab/lifetime/security type/active settings. Under `PROXYV4_HANDLE_MAPPING`, it supports handle mapping enablement plus database/temp directory, database count, and hash table size.

`remote_commit()` validates configured send/receive sizes against module maxwrite/maxread plus RPC header space. `proxyv4_export_init()` initializes session/clientid/list/context locks and condition variables and sets `rpc_sock = -1`. `proxyv4_export_destroy()` destroys those primitives. `proxyv4_release()` detaches, frees export ops, stops the close thread, frees I/O contexts, destroys locks/conds, and frees the export. `proxyv4_export_ops_init()` wires export operations. `proxyv4_create_export()` is the exported constructor.

## Control Flow
Export creation allocates and zeroes `struct proxyv4_export`, initializes proxy-private synchronization state, calls `fsal_export_init()`, loads config through `proxyv4_export_param`, initializes export ops, sets FSAL/upcall pointers, stores the export in `op_ctx`, and attaches it to the module. If handle mapping is compiled in and enabled/configured, it calls `HandleMap_Init()`. It then calls `proxyv4_init_rpc(exp)` to establish the NFSv4 proxy connection/session. On any post-attach failure it closes proxy threads, frees I/O contexts, detaches the export, frees ops, destroys synchronization primitives, and frees the object.

At runtime, the export ops delegate path lookup, wire/host handle conversion, handle creation, dynamic fs info, supported attrs, and state allocation to proxy v4 handle/module helpers. Release reverses initialization and ensures no close thread or I/O context remains before freeing locks.

## State And Persistence
Per-export state includes parsed remote connection parameters, RPC/session coordination fields, socket state, I/O contexts, condition variables, mutexes, and optional handle-map settings. Persistence exists only when handle mapping is compiled/enabled and its sqlite-backed implementation stores mappings in configured directories; this file only initializes that subsystem.

## Dependencies And Integration Points
The file depends on FSAL config/commonlib, export manager APIs, `proxyv4_fsal_methods.h`, `nfs_exports.h`, and `export_mgr.h`. It integrates with handle-level proxy v4 functions (`proxyv4_lookup_path`, `proxyv4_wire_to_host`, `proxyv4_create_handle`, `proxyv4_get_dynamic_info`, `proxyv4_alloc_state`, `proxyv4_init_rpc`, `proxyv4_close_thread`, `free_io_contexts`) and optional `HandleMap_Init()`.

## Risks
The `_USE_GSSRPC` `KeytabPath` config line appears to concatenate the default string and struct/type tokens without a comma, which is suspicious and should be compile-checked in Kerberos builds. `remote_commit()` depends on `op_ctx->fsal_module` being set during config commit. Resource cleanup is careful after `err_cleanup`, but failures before attach rely on the `err_free` path only. Handle mapping initialization failure after attach correctly detaches, but any partial HandleMap state cleanup is delegated elsewhere or absent here. Configured send/receive size validation prevents too-small buffers but does not validate remote behavior until `proxyv4_init_rpc()`.

## Test Signals
Test export creation with valid config, missing/invalid `Srv_Addr`, too-small send/receive sizes, RPC init failure, and release after successful init. Build and run `_USE_GSSRPC` config parsing tests. Build with `PROXYV4_HANDLE_MAPPING` and test handle-map init success/failure and cleanup. Runtime tests should verify release drains close threads and I/O contexts without leaked mutex/cond resources.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/export.c -->
