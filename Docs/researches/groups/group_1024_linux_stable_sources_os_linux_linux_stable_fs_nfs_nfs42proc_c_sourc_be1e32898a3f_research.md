# Group Research: group_1024_linux_stable_sources_os_linux_linux_stable_fs_nfs_nfs42proc_c_sourc_be1e32898a3f

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux-stable`, which is included in subset A. Each listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs42proc.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs42proc.c

This file implements the NFSv4.2 client-side procedure layer for operations above the basic NFSv4 protocol: `ALLOCATE`, `DEALLOCATE`, `ZERO_RANGE`, `COPY`, `COPY_NOTIFY`, `OFFLOAD_CANCEL`, `OFFLOAD_STATUS`, `SEEK`, pNFS `LAYOUTSTATS` / `LAYOUTERROR`, `CLONE`, and user xattr RPC wrappers.

Key responsibilities:
- Converts VFS-facing operations into NFSv4.2 compound RPC calls through `nfs4_call_sync()` or async `rpc_run_task()`.
- Acquires correct open/lock stateids with `nfs4_set_rw_stateid()`.
- Routes NFSv4 state recovery through `nfs4_handle_exception()`.
- Maintains local page cache and inode metadata after server-side mutation.
- Degrades server capability bits when operations return unsupported errors.

Important flows:
- Fallocate family:
  - `_nfs42_proc_fallocate()` builds shared fallocate RPC args/results and updates inode attributes.
  - `nfs42_proc_allocate()`, `nfs42_proc_deallocate()`, and `nfs42_proc_zero_range()` wrap capability checks, write serialization, page-cache truncation/invalidation, and capability fallback.
- Server-side copy:
  - `nfs42_proc_copy()` drives retry and exception handling for intra-server and inter-server copy.
  - `_nfs42_proc_copy()` flushes source writes, syncs destination, sets source/destination stateids, sends `COPY`, optionally verifies commit verifiers, waits for async completion, and updates destination cache state.
  - `handle_async_copy()` manages callback-completed copy state, timeout polling via `OFFLOAD_STATUS`, restart/cancel logic, and translated completion errors.
  - `nfs42_proc_copy_notify()` prepares inter-server copy source authorization and server location data.
- Clone:
  - `nfs42_proc_clone()` validates capability and state, then `_nfs42_proc_clone()` sends `CLONE`, updates destination size/cache, and refreshes attributes.
- SEEK:
  - `nfs42_proc_llseek()` implements `SEEK_HOLE` / `SEEK_DATA` with NFSv4.2 `SEEK`, falling back to `-EOPNOTSUPP` for callers.
- pNFS telemetry:
  - `nfs42_proc_layoutstats_generic()` asynchronously reports layout device I/O stats.
  - `nfs42_proc_layouterror()` asynchronously reports layout/device errors and handles bad/old layout stateids.
- Extended attributes:
  - `nfs42_proc_getxattr()`, `nfs42_proc_setxattr()`, `nfs42_proc_listxattrs()`, and `nfs42_proc_removexattr()` wrap NFSv4.2 xattr operations, retry on recoverable state/session errors, update change attributes, and populate or invalidate the xattr cache.

Notable dependencies:
- `nfs42.h` for operation argument/result structures.
- `nfs4_fs.h` for stateid, exception, and NFSv4 procedure declarations.
- `nfs4session.h` for sequence/session handling.
- `pnfs.h` for layout state and pNFS segment references.
- `delegation.h`, `internal.h`, `iostat.h`, and `nfs4trace.h`.

Concurrency and lifetime notes:
- Copy callback state is linked on client lists protected by `cl_lock`.
- Async RPC data for offload, layoutstats, and layouterror is released through `rpc_call_ops`.
- Layoutstats holds active inode/layout references until release.
- Layouterror holds both an active inode reference and pNFS layout segment reference.
- `inode_lock()` protects destination copy operations in `nfs42_proc_copy()`.
- `nfs_start_io_write()` / `nfs_end_io_write()` serialize fallocate-style write mutations.

Risk areas:
- Server-side copy has several subtle transitions between callback completion, polling, cancellation, fallback, and retry.
- Correct page-cache invalidation is essential after clone/copy/zero/deallocate.
- `-ENOTSUPP`, `-EOPNOTSUPP`, and NFS protocol errors are intentionally translated in different paths; changing these translations can affect VFS fallback behavior.
- pNFS layout error/stat paths rely on stateid comparison to decide whether to invalidate layouts or retry.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs42proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs42xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs42xattr.c

This file implements the client-side cache for NFSv4.2 user extended attributes. The cache is attached lazily to NFS inodes and stores individual xattr name/value pairs plus a special cached `listxattr` result.

Key structures:
- `struct nfs4_xattr_cache`
  - Per-inode cache object.
  - Contains 64 hash buckets, an LRU node, a dispose list node, entry count, listxattr lock, inode pointer, and special `listxattr` entry pointer.
- `struct nfs4_xattr_bucket`
  - Spinlock-protected hash bucket with `draining` flag.
- `struct nfs4_xattr_entry`
  - Refcounted xattr value entry with hash node, LRU node, dispose node, name, value, size, bucket pointer, and flags.
- Global LRUs:
  - `nfs4_xattr_cache_lru` for cache objects.
  - `nfs4_xattr_entry_lru` for normal entries.
  - `nfs4_xattr_large_entry_lru` for entries whose values require separate `kvmalloc()` storage.

Main behavior:
- Entries are allocated by `nfs4_xattr_alloc_entry()`.
  - Small values are co-allocated with the entry/name in one `kmalloc()` allocation.
  - Large values are stored via `kvmalloc()` and placed on the large-entry LRU.
  - Values can be copied either from a direct buffer or from RPC reply pages.
- `nfs4_xattr_get_cache()` obtains or creates a referenced per-inode cache.
  - It handles `NFS_INO_INVALID_XATTR` by unlinking and discarding stale caches.
  - It avoids allocations under `inode->i_lock` via optimistic allocation and race resolution.
- Public cache entry points:
  - `nfs4_xattr_cache_get()` retrieves a named xattr.
  - `nfs4_xattr_cache_list()` retrieves cached list output.
  - `nfs4_xattr_cache_add()` adds/replaces a named entry and invalidates list cache.
  - `nfs4_xattr_cache_remove()` removes a named entry and invalidates list cache.
  - `nfs4_xattr_cache_set_list()` caches `listxattr` output.
  - `nfs4_xattr_cache_zap()` unlinks and discards the entire inode cache.

Shrinker design:
- There are three shrinkers:
  - Cache shrinker: frees cache structures only when they are small/mostly empty.
  - Entry shrinker: reclaims normal entries.
  - Large entry shrinker: reclaims large entries more aggressively with `seeks = 1`.
- Shrinker isolation uses `trylock` paths because it inverts ordinary lock ordering.
- Discarding a cache marks listcache as stale and all buckets as draining before unlinking entries.

Locking and lifetime:
- Documented lock order is inode `i_lock` or bucket lock before list_lru lock.
- Cache and entry lifetimes are protected by `kref`.
- `ERR_PTR(-ESTALE)` in `cache->listxattr` marks a draining list cache and prevents new listcache insertion into stale cache state.
- Cache unlink requires `inode->i_lock`.

Risk areas:
- Refcount and LRU membership must stay synchronized. Free callbacks warn if an entry remains on an LRU.
- Shrinker paths deliberately use `trylock`; missed reclamation is acceptable, but incorrect locking could deadlock.
- The stale-cache/draining flags prevent racing writers from repopulating invalid cache objects.
- Large xattr memory pressure behavior depends on correct `NFS4_XATTR_ENTRY_EXTVAL` flag selection.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs42xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs42xdr.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs42xdr.c

This file contains NFSv4.2 XDR size accounting, encoders, and decoders for v4.2 compound operations. It is included as the v4.2 XDR implementation and defines operation-specific maximum sizes and compound request/reply sizes.

Operations covered:
- `ALLOCATE`
- `COPY`
- `OFFLOAD_CANCEL`
- `OFFLOAD_STATUS`
- `COPY_NOTIFY`
- `DEALLOCATE`
- `ZERO_RANGE`
- `READ_PLUS`
- `SEEK`
- `LAYOUTSTATS`
- `LAYOUTERROR`
- `CLONE`
- `GETXATTR`
- `SETXATTR`
- `LISTXATTRS`
- `REMOVEXATTR`

Key size definitions:
- Per-operation encode/decode max sizes.
- Compound request/reply sizes such as `NFS4_enc_copy_sz`, `NFS4_dec_read_plus_sz`, and xattr-specific sizes.
- Exported overhead constants:
  - `nfs42_maxsetxattr_overhead`
  - `nfs42_maxgetxattr_overhead`
  - `nfs42_maxlistxattrs_overhead`
  These are used to constrain xattr sizes by session channel limits.

Encoder highlights:
- Encoders build compound sequences: compound header, `SEQUENCE`, `PUTFH`, operation, optional `SAVEFH`, optional `COMMIT`, optional `GETATTR`, then `encode_nops()`.
- `encode_copy()` supports intra-server copy and one source server for inter-server copy.
- `encode_zero_range()` composes `DEALLOCATE` then `ALLOCATE`.
- `encode_read_plus()` prepares reply pages with room for read-plus segment overhead.
- `encode_getxattr()` and `encode_listxattrs()` prepare reply pages for variable-sized xattr data.
- `encode_layoutstats()` allows layout-driver private encoding via `ld_private.ops`.

Decoder highlights:
- Basic operation decoders verify op headers and parse operation payloads.
- `decode_write_response()` handles optional callback stateid, byte count, committed level, and verifier.
- `decode_copy()` special-cases `NFS4ERR_OFFLOAD_NO_REQS` to decode server sync/consecutive requirements.
- `decode_offload_status()` decodes partial byte count and optional completion status.
- `decode_read_plus()` parses multiple sparse data/hole segments, then moves data or zero-fills target reply pages.
- `decode_listxattrs()` prefixes returned names with `user.`, enforces name length limits, handles `NFS4ERR_TOOSMALL` as `-ERANGE`, maps no-xattr to zero-length success, and turns max-size `-ERANGE` into `-E2BIG`.
- Mutating xattr decoders parse `change_info` and follow-up attributes.

Risk areas:
- `READ_PLUS` segment processing is delicate: it decodes segments first, then processes them backward while reshaping the XDR page buffer.
- Xattr page lengths and reply lengths are intentionally decoupled from caller buffer lengths to allow caching of oversized successful replies.
- LISTXATTRS sizing follows RFC 8276 count semantics and adds cookie/names-count overhead.
- Many decoders return protocol-level errors directly or translate selected protocol errors; this affects higher-level fallback behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs42xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4_fs.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4_fs.h

This is the central internal NFSv4 client header for filesystem-specific NFSv4 definitions, state structures, minor-version operations, and cross-file declarations.

Main content:
- Minor version bounds:
  - `NFS4_MIN_MINOR_VERSION`
  - `NFS4_MAX_MINOR_VERSION`
- NFSv4 client state bits:
  - Lease recovery, reclaim, session reset, server-scope mismatch, delegation expiration, callback recall states, migration states, and manager scheduling bits.
- Sequence ID support:
  - `struct nfs_seqid_counter`
  - `struct nfs_seqid`
  - `nfs_confirm_seqid()`
- State-owner and state tracking:
  - `struct nfs4_state_owner`
  - `struct nfs4_lock_state`
  - `struct nfs4_state`
  - State flags for open modes, delegation, reclaim, recovery failure, lock notification, and server-side-copy roles.
- `struct nfs4_exception`
  - Carries state, inode, stateid, timeout, retransmit count, privilege/delay/recovery/retry flags, and interruptibility for recovery loops.
- Operation vtables:
  - `struct nfs4_minor_version_ops`
  - `struct nfs4_sequence_slot_ops`
  - `struct nfs4_state_recovery_ops`
  - `struct nfs4_state_maintenance_ops`
  - `struct nfs4_mig_recovery_ops`

Important declarations:
- NFSv4 procedure, state, recovery, session, migration, namespace, idmapping, and xattr functions.
- `nfs4_state_protect()` helpers for SP4 machine credential protection.
- Session and trunking declarations.
- XDR procedure table and v4.2 xattr overhead constants.
- Optional sysctl and xattr-cache stubs based on config.

Inline helpers:
- Data-server role checks:
  - `is_ds_only_client()`
  - `is_ds_client()`
- Stateid operations:
  - `nfs4_stateid_copy()`
  - `nfs4_stateid_match()`
  - `nfs4_stateid_match_other()`
  - `nfs4_stateid_is_newer()`
  - `nfs4_stateid_is_next()`
  - `nfs4_stateid_match_or_older()`
  - `nfs4_stateid_seqid_inc()`
- Open-state validity checks.
- Stubs for non-NFSv4 builds.

Role in this group:
- `nfs42proc.c`, `nfs42xattr.c`, `nfs4client.c`, `nfs4file.c`, `nfs4getroot.c`, `nfs4idmap.c`, `nfs4namespace.c`, `nfs4renewd.c`, and `nfs4session.c` all rely on this header for shared state and declarations.
- It defines the common state/recovery vocabulary used throughout these files.

Risk areas:
- State flags and stateid helper semantics are cross-cutting; small changes can affect open, lock, delegation, copy, and recovery paths.
- Config-guarded stubs must match real function signatures closely enough to keep callers correct across build options.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4client.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4client.c

This file manages NFSv4 client objects, callback setup, sessions, pNFS data-server clients, server records, referrals, trunking, and server migration updates.

Key client setup:
- `nfs4_alloc_client()` allocates and initializes an `nfs_client`.
  - Validates minor version.
  - Initializes locks, renewal work, data-server list, wait queues, migration generation, pending callback stateids.
  - Creates RPC client, derives callback IP address if needed, and creates idmap state.
- `nfs4_init_client()` initializes minor-version behavior, callback service, and server trunking discovery.
- `nfs4_free_client()` shuts down NFSv4-specific resources then frees the generic client.

Callback and session handling:
- `nfs_get_cb_ident_idr()` allocates v4.0 callback identifiers.
- `nfs4_init_callback()` starts callback service and sets up backchannel for sessions.
- `nfs41_init_client()` allocates an NFSv4.1+ session and marks the client as session-initializing.
- `nfs41_shutdown_client()` cleans callback copy state, pNFS DS clients, session, and clientid.

pNFS data server support:
- `nfs4_find_or_create_ds_client()` clones per-auth-flavor RPC clients for DS I/O.
- `nfs4_shutdown_ds_clients()` tears those clients down.
- `nfs4_set_ds_client()` creates or finds a DS `nfs_client` with MDS-derived identity, transport parameters, and pNFS flags.
- TLS policy may be inherited from MDS if available.

Trunking and client matching:
- `nfs4_match_client()` checks version, minor version, readiness, clientid, and owner-id compatibility.
- `nfs41_walk_client_list()` searches for matching clientid/server-owner entries.
- `nfs4_detect_session_trunking()` verifies clientid, server owner major/minor IDs, and server scope before accepting session trunking.
- `nfs4_add_trunk()` adds a transport to an existing client when trunking succeeds.

Server setup:
- `nfs4_set_client()` binds an `nfs_server` to a client, sets init flags, handles transport constraints, and sysfs linkage.
- `nfs4_init_server()` copies mount context into a new server and initializes RPC client flavor.
- `nfs4_server_common_setup()` allocates delegation hash, initializes session, probes root filehandle, probes server capabilities, applies session size limits, inserts server into lists, and installs destroy callback.
- `nfs4_create_server()` creates normal NFSv4 server records.
- `nfs4_create_referral_server()` creates referral server records, trying RDMA then TCP/TLS paths.

Size limiting:
- `nfs4_session_limit_rwsize()` clamps `dtsize`, `rsize`, and `wsize` by negotiated forechannel sizes.
- `nfs4_session_limit_xasize()` clamps get/set/list xattr sizes using v4.2 overhead constants.

Migration:
- `nfs4_update_server()` switches RPC transport, computes local client address, replaces the client association, preserves list membership, and reprobes the server.

Risk areas:
- Client matching/trunking is sensitive to initialization races; `nfs4_match_client()` can wait for another client to finish initialization while walking the shared list.
- Resource cleanup spans callback, idmap, sessions, DS clients, sysfs, and RPC wait queues.
- Referral and migration setup must preserve credentials, transport security policy, and mount-derived size/security options.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4client.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4file.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4file.c

This file defines NFSv4 file operations and wires NFSv4.2 file features into VFS operations when `CONFIG_NFS_V4_2` is enabled.

Core NFSv4 operations:
- `nfs4_file_open()`
  - Validates flags.
  - Allocates an NFS open context.
  - Handles truncate-on-open by flushing cached pages.
  - Calls NFS protocol `open_context()`.
  - Drops stale dentries on mismatch or selected lookup errors so VFS retries.
  - Sets open context and fscache state on success.
- `nfs4_file_flush()`
  - Flushes writeback and checks writeback errors.
  - If write delegation does not require flush-on-close, starts writeback only.
- `nfs4_setlease()` delegates lease handling to `nfs4_proc_setlease()`.

NFSv4.2 additions:
- `nfs4_copy_file_range()`
  - Attempts server-side copy, falls back to splice copy on unsupported or cross-device style errors.
- `__nfs4_copy_file_range()`
  - Requires NFSv4 file operations and copy capability on both files.
  - Uses synchronous copy for small copies.
  - For inter-server copy, obtains `COPY_NOTIFY` first.
  - Retries on `-EAGAIN`.
- `nfs4_file_llseek()`
  - Uses NFSv4.2 `SEEK` for `SEEK_HOLE` / `SEEK_DATA`, otherwise falls back to generic NFS llseek.
- `nfs42_fallocate()`
  - Supports allocate, punch-hole keep-size, and zero-range modes.
  - Checks regular file and new size.
  - Dispatches to allocate/deallocate/zero-range procedure wrappers.
- `nfs42_remap_file_range()`
  - Implements clone/remap via NFSv4.2 `CLONE`.
  - Rejects dedupe.
  - Validates clone block alignment.
  - Blocks direct I/O, syncs both inodes, calls clone RPC, and truncates destination page cache on success.
- Server-side-copy pseudo-open support:
  - `__nfs42_ssc_open()` creates a pseudo read-only file from a source filehandle and supplied stateid.
  - `__nfs42_ssc_close()` clears SSC state flags.
  - `nfs42_ssc_register_ops()` and `nfs42_ssc_unregister_ops()` register/unregister common SSC ops.

File operations table:
- `nfs4_file_operations` includes read/write, mmap prepare, open, flush, release, fsync, lock/flock, splice, flag checking, lease, and v4.2 copy/llseek/fallocate/remap hooks when enabled.

Risk areas:
- Open path intentionally returns `-EOPENSTALE` after dropping dentries so VFS retries correctly.
- Remap/clone must coordinate inode locking, direct I/O blocking, writeback synchronization, and destination cache invalidation.
- Server-side-copy pseudo-open manually constructs open state around a server-provided stateid; state flags must be reset on close.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4getroot.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4getroot.c

This small file implements `nfs4_get_rootfh()`, the helper that retrieves and validates an NFSv4 root filehandle during server setup.

Behavior:
- Allocates an `nfs_fattr`.
- Calls `nfs4_proc_get_rootfh()` to fetch the server root filehandle and attributes.
- Verifies that the returned object has a valid type attribute and is a directory.
- Copies the returned fsid into `server->fsid`.
- Frees attributes before returning.

Dependencies:
- `nfs4_proc_get_rootfh()` from the NFSv4 procedure layer.
- `nfs_alloc_fattr()` / `nfs_free_fattr()`.
- `NFS_ATTR_FATTR_TYPE` and `S_ISDIR()` validation.

Risk areas:
- A non-directory root is converted to `-ENOTDIR`.
- Attribute allocation failure returns `-ENOMEM`.
- This function is called during common server setup, so failures abort mount/referral setup early.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4getroot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4idmap.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4idmap.c

This file implements NFSv4 UID/GID to owner/group string mapping and reverse mapping. It uses the kernel keyring request-key infrastructure, with a legacy rpc_pipefs upcall fallback.

Core concepts:
- `struct idmap`
  - Holds rpc pipe directory object, rpc pipe, active legacy upcall data, mutex, and user namespace.
- `id_resolver_cache`
  - Kernel credentials with a `.id_resolver` thread keyring used for idmapping key lookup.
- Two key types:
  - `id_resolver` for normal key-based resolution.
  - `id_legacy` for rpc_pipefs-driven legacy upcalls.

Attribute-name helpers:
- `nfs_fattr_init_names()` associates owner/group string storage with an `nfs_fattr`.
- `nfs_fattr_map_and_free_names()` maps owner/group names to numeric uid/gid and frees cached strings.
- `nfs_fattr_free_names()` releases owner/group strings without mapping.

Numeric shortcut:
- `nfs_map_string_to_numeric()` treats non-domain strings without `@` as numeric IDs when parseable.
- `nfs_map_numeric_to_string()` formats numeric IDs for fallback or key descriptions.

Keyring flow:
- `nfs_idmap_init()` creates `.id_resolver`, registers key types, and stores resolver credentials.
- `nfs_idmap_quit()` revokes the keyring, unregisters key types, and drops credentials.
- `nfs_idmap_get_desc()` builds descriptions like `uid:name`, `gid:name`, `user:id`, or `group:id`.
- `nfs_idmap_request_key()` first tries modern `id_resolver`; if unavailable, uses legacy `id_legacy` with aux idmap data.
- `nfs_idmap_get_key()` requests and validates a key, then copies user payload data.

Legacy rpc_pipefs flow:
- `nfs_idmap_new()` creates per-client idmap state and an `idmap` pipe under rpc_pipefs.
- `nfs_idmap_delete()` removes pipe state and releases namespace references.
- `nfs_idmap_legacy_upcall()` prepares an `idmap_msg`, queues it to the pipe, and waits for downcall completion through request-key auth.
- `idmap_pipe_downcall()` validates user response, verifies it matches the outstanding request, instantiates the key, and sets timeout.
- `idmap_release_pipe()` fails an outstanding upcall with `-EPIPE`.

Public mapping APIs:
- `nfs_map_name_to_uid()`
- `nfs_map_group_to_gid()`
- `nfs_map_uid_to_name()`
- `nfs_map_gid_to_group()`

Namespace handling:
- ID conversion uses the idmap’s user namespace if present, otherwise `init_user_ns`.
- Name-to-ID validates resulting kuid/kgid with `uid_valid()` / `gid_valid()`.
- ID-to-name falls back to numeric strings when named mapping fails or server advertises `NFS_CAP_UIDGID_NOMAP`.

Risk areas:
- Only one legacy upcall is active per idmap; `idmap_upcall_data` is protected with mutex/xchg/cmpxchg style transitions.
- Key payload length validation is strict; bad user responses become `-EINVAL` or `-ENOKEY`.
- Numeric fallback behavior affects interoperability with servers that return numeric owner strings.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4idmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4idmap.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4idmap.h

This header declares the NFSv4 idmapping interface used by NFS client setup and attribute decoding code.

Declarations:
- Lifecycle:
  - `nfs_idmap_init()`
  - `nfs_idmap_quit()`
  - `nfs_idmap_new()`
  - `nfs_idmap_delete()`
- Attribute owner/group string helpers:
  - `nfs_fattr_init_names()`
  - `nfs_fattr_free_names()`
  - `nfs_fattr_map_and_free_names()`
- Mapping APIs:
  - `nfs_map_name_to_uid()`
  - `nfs_map_group_to_gid()`
  - `nfs_map_uid_to_name()`
  - `nfs_map_gid_to_group()`
  - `nfs_map_string_to_numeric()`
- External tunable:
  - `nfs_idmap_cache_timeout`

Role:
- Keeps idmap implementation details out of users.
- Provides forward declarations for `nfs_client`, `nfs_server`, `nfs_fattr`, and `nfs4_string`.
- Includes UID/GID and UAPI idmap definitions.

Risk areas:
- This is a shared contract between idmap implementation, NFSv4 client setup, and XDR attribute decode/update code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4idmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4namespace.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4namespace.c

This file implements NFSv4 namespace handling: referral following, security negotiation after `WRONGSEC`, server-name parsing, and transport replacement for migration.

Path helpers:
- `nfs4_pathname_len()` validates and computes POSIX path length from NFSv4 pathname components.
- `nfs4_pathname_string()` converts NFSv4 path components to a slash-prefixed string.
- `nfs_path_component()` extracts the path part from `server:path`, including bracketed IPv6 handling.
- `nfs4_path()` obtains a canonical NFS path and returns the export path component.
- `nfs4_validate_fspath()` verifies that a referral fs_root is a prefix of the current dentry path.

Server-name parsing:
- `nfs_parse_server_name()` tries:
  - `rpc_pton()`
  - `rpc_uaddr2sockaddr()`
  - DNS resolution through `nfs_dns_resolve_name()`
- Applies port when requested.

Security negotiation:
- `nfs_find_best_sec()` selects the first locally supported server-provided security flavor that matches mount `sec=` constraints.
- It clones an RPC client with that auth flavor and verifies credentials can be acquired.
- `nfs4_negotiate_security()` calls `SECINFO` and returns a temporary RPC client with the selected auth flavor.

Referral handling:
- `try_location()` attempts a single fs_locations entry across its server list.
  - Builds hostname, export path, and `fc->source`.
  - Skips scoped IPv6 names.
  - Resolves address and tries `nfs4_get_referral_tree()`.
- `nfs_follow_referral()` validates fs path and iterates fs_locations.
- `nfs_do_refmount()` gets fs_locations for a referral dentry and follows it.
- `nfs4_submount()` re-lookups a mountpoint, determines selected auth flavor, and either follows referral or performs ordinary submount.

Migration transport replacement:
- `nfs4_try_replacing_one_location()` tries servers from a location and calls `nfs4_update_server()`.
- `nfs4_replace_transport()` iterates fs_locations and tries replacement until one succeeds.

Risk areas:
- Referral path validation prevents mounting unrelated server paths.
- `fc->source`, hostname, export path, and server address fields are mutated during location attempts.
- Temporary cloned RPC clients from security negotiation must be shut down by callers.
- IPv6 scoped addresses are intentionally skipped in referral/migration server lists.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4namespace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4renewd.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4renewd.c

This file implements the NFSv4 lease renewal worker. It is not a kernel thread; it runs as delayed work in kernel workqueue context.

Main functions:
- `nfs4_renew_state()`
  - Checks whether renewal should stop.
  - Computes whether the client is close enough to lease timeout.
  - Adds delegation callback renewal pressure when delegations are present.
  - Obtains state renewal credentials through minor-version ops.
  - Schedules async renewal via `sched_state_renewal()`.
  - Expires all delegations if only delegation renewal is needed but no credentials exist.
  - Marks lease expired when timeout renewal has no credentials.
  - Reschedules renewal work and expires unreferenced delegations.
- `nfs4_schedule_state_renewal()`
  - Schedules the next renewal at roughly two-thirds of the lease period after last renewal, with a minimum delay of 5 seconds.
  - Sets `NFS_CS_RENEWD`.
- `nfs4_kill_renewd()`
  - Cancels delayed renewal work synchronously.
- `nfs4_set_lease_period()`
  - Caps lease period at one hour.
  - Stores lease in jiffies.
  - Sets RPC reconnect timeout to at most half the lease.

Dependencies:
- Minor-version `state_renewal_ops`.
- Delegation helpers for detecting, expiring, and pruning delegations.
- Client lock protects lease time update and scheduling calculations.

Risk areas:
- Renewal timing determines whether client state survives server lease expiration.
- Credential absence is handled differently depending on whether renewal is needed for lease timeout or only delegations.
- `NFS_CS_STOP_RENEW` must be honored to avoid renewing during shutdown.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4renewd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4session.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4session.c

This file implements NFSv4.1+ session slot-table management and session lifecycle helpers.

Slot table basics:
- `nfs4_init_slot_table()` initializes lock, wait queues, completion, and highest-used state.
- Slots are linked in a list and tracked in a bitmap.
- `nfs4_alloc_slot()` finds a free bitmap slot up to `max_slotid`, creates the slot if needed, marks it used, and updates highest-used slot id.
- `nfs4_free_slot()` clears a used slot and recalculates `highest_used_slotid`, completing drain when no slots remain.
- `nfs4_lookup_slot()` returns an existing or newly created slot if within max slot id.
- `nfs4_try_to_lock_slot()` marks a specific slot used if available.

Slot sequence wait:
- `nfs4_slot_seqid_in_use()` checks whether a slot/sequence pair is still in flight.
- `nfs4_slot_wait_on_seqid()` waits for that sequence to complete, primarily for callback channel coordination.

Sizing and reset:
- `nfs4_grow_slot_table()` ensures enough slots exist.
- `nfs4_shrink_slot_table()` frees retired slots above new size.
- `nfs4_reset_slot_table()` resets sequence numbers and slot limits.
- `nfs4_realloc_slot_table()` grows/resets table with a cap at `NFS4_MAX_SLOT_TABLE`.
- `nfs41_set_target_slotid()` and `nfs41_update_target_slotid()` adapt client target slot limits based on server SEQUENCE replies.
- Outlier filtering uses first and second derivative tracking to avoid abrupt target-slot changes.

RPC wait queue integration:
- `nfs41_assign_slot()` attaches an allocated slot to RPC sequence args/results unless draining and non-privileged.
- `nfs41_wake_and_assign_slot()` wakes one waiter with a specific slot.
- `nfs41_wake_slot_table()` allocates and assigns slots to waiting tasks until no more work can be woken.

Session lifecycle:
- `nfs4_alloc_session()` allocates a session and initializes forechannel/backchannel slot tables.
- `nfs4_setup_session_slot_tables()` initializes or resets forechannel and backchannel tables using negotiated channel attributes.
- `nfs4_destroy_session()` sends `DESTROY_SESSION`, destroys backchannel, releases slot tables, and frees session.
- `nfs4_init_session()` clears initializing state and checks readiness.
- `nfs4_init_ds_session()` initializes DS session lease timing from MDS lease and verifies DS role.

Risk areas:
- Slot-table locks protect bitmap, highest-used, and dynamic sizing fields.
- Drain completion depends on accurate `highest_used_slotid` maintenance.
- Dynamic resizing must respect server highest slot id, target highest slot id, and local maximum.
- Session readiness maps some initialization failures to `-EPROTONOSUPPORT` to allow fallback to other NFS versions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4session.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4session.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4session.h

This header defines NFSv4.1+ session and slot-table data structures and declares the slot/session helper APIs.

Constants:
- `NFS4_DEF_SLOT_TABLE_SIZE` = 64
- `NFS4_DEF_CB_SLOT_TABLE_SIZE` = 16
- `NFS4_MAX_SLOT_TABLE` = 1024
- `NFS4_MAX_SLOTID`
- `NFS4_NO_SLOT`

Structures:
- `struct nfs4_slot`
  - Parent table, linked-list next pointer, generation, slot number, sequence numbers, privileged flag, and sequence-done flag.
- `struct nfs4_slot_table`
  - Parent session, slot list, used-slot bitmap, lock, RPC wait queue, sequence wait queue, max/highest slot fields, target/server slot fields, derivative tracking, completion, and state bits.
- `struct nfs4_session`
  - Session ID, flags, session state, hash/SSV fields, forechannel/backchannel attributes and slot tables, and parent client.

Enums:
- Slot table state:
  - `NFS4_SLOT_TBL_DRAINING`
- Session state:
  - `NFS4_SESSION_INITING`
  - `NFS4_SESSION_ESTABLISHED`

Declared APIs:
- Slot table setup/shutdown, allocation, lookup, locking, freeing, waiting, wake/assign.
- Target slotid update and dynamic resize helpers.
- Session slot table setup, allocation, destruction, initialization, and DS initialization.

Inline helpers:
- `nfs4_slot_tbl_draining()`
- `nfs4_test_locked_slot()`
- `nfs4_get_session()`
- `nfs4_has_session()`
- `nfs4_has_persistent_session()`
- `nfs4_copy_sessionid()`
- `nfs_session_id_hash()`

Role:
- Shared contract between session management, sequence processing, callback handling, and NFSv4.2 procedure code.

Risk areas:
- `SLOT_TABLE_SZ` must be large enough for the maximum slot table bitmap.
- Inline state checks are widely used; semantic changes affect session recovery, callback routing, and RPC scheduling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4session.h -->