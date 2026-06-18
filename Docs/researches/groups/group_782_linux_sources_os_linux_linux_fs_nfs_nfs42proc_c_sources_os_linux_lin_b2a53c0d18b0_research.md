# Group Research: group_782_linux_sources_os_linux_linux_fs_nfs_nfs42proc_c_sources_os_linux_lin_b2a53c0d18b0

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs42proc.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs42proc.c

This file implements the NFSv4.2 client procedure layer for operations beyond baseline NFSv4: `ALLOCATE`, `DEALLOCATE`, `ZERO_RANGE`, server-side `COPY`, `COPY_NOTIFY`, `OFFLOAD_CANCEL`, `OFFLOAD_STATUS`, sparse-file `SEEK`, pNFS `LAYOUTSTATS` and `LAYOUTERROR`, `CLONE`, and NFSv4.2 user extended attributes.

Key responsibilities:
- Converts VFS-facing operations into NFSv4.2 compound RPCs through `nfs4_call_sync()` or async `rpc_run_task()`.
- Selects and validates open/lock stateids with `nfs4_set_rw_stateid()`.
- Routes protocol errors through `nfs4_handle_exception()` and async errors through `nfs4_async_handle_error()`.
- Updates inode attributes, change attributes, delegation timestamps, and page cache state after server-side mutation.
- Clears server capability bits when operations return unsupported results.

Important flows:
- Fallocate family:
  - `_nfs42_proc_fallocate()` builds common fallocate args/results, requests cache-consistency attributes, sends the compound, traces it, removes SUID-related cache state when needed, and applies weak cache consistency updates.
  - `nfs42_proc_allocate()`, `nfs42_proc_deallocate()`, and `nfs42_proc_zero_range()` serialize write-side mutations with `nfs_start_io_write()` / `nfs_end_io_write()`, perform cache truncation/invalidation, and downgrade unsupported capabilities.
- Server-side copy:
  - `_nfs42_proc_copy()` flushes source writeback, blocks destination direct I/O, syncs the destination inode, sets source/destination stateids, sends `COPY`, verifies write/commit verifiers, handles async copy completion, commits unstable copy results, and updates destination cache state.
  - `handle_async_copy()` joins callback-completed copy state or registers pending copy state, waits with exponential timeout bounded by lease time, polls `OFFLOAD_STATUS`, restarts/cancels when required, and translates server copy failures into fallback-oriented errors.
  - `nfs42_proc_copy()` serializes destination copy with `inode_lock()`, handles source and destination recovery exceptions separately, responds to `OFFLOAD_NO_REQS` by switching sync mode, and triggers offload cancellation for inter-server failure cases.
  - `nfs42_proc_copy_notify()` builds inter-server source authorization, including a destination `NL4_NETADDR`, then returns the copy-notify stateid and source server list.
- Offload helpers:
  - `nfs42_do_offload_cancel_async()` sends async `OFFLOAD_CANCEL` using sequence callbacks and removes `NFS_CAP_OFFLOAD_CANCEL` if unsupported.
  - `nfs42_proc_offload_status()` polls async copy progress and maps copy stateid failures to `-EBADF` instead of broad state recovery.
- Sparse and clone operations:
  - `nfs42_proc_llseek()` implements `SEEK_HOLE` / `SEEK_DATA` through NFSv4.2 `SEEK`, mapping unsupported protocol status to `-EOPNOTSUPP`.
  - `nfs42_proc_clone()` wraps `CLONE`, sets read/write stateids, updates destination page cache and attributes, and clears clone capability on unsupported results.
- pNFS telemetry:
  - `nfs42_proc_layoutstats_generic()` asynchronously reports layout I/O stats while holding active inode/layout references until release.
  - `nfs42_proc_layouterror()` asynchronously reports layout/device errors, invalidates layout stateids on bad/revoked stateid classes, retries old stateids when appropriate, and clears `NFS_CAP_LAYOUTERROR` when unsupported.
- Extended attributes:
  - `nfs42_proc_getxattr()`, `nfs42_proc_setxattr()`, `nfs42_proc_listxattrs()`, and `nfs42_proc_removexattr()` implement NFSv4.2 user xattr RPCs with retry loops, page-backed buffers, xattr cache population/removal, and change-attribute updates.

Dependencies:
- Uses `nfs42.h` for operation-specific argument/result structures and xattr sizing.
- Uses `nfs4_fs.h` for stateid helpers, exception handling, procedure declarations, and xattr cache APIs.
- Uses `nfs4session.h` for sequence setup/completion.
- Uses `pnfs.h` for layout headers, layout segments, and pNFS state invalidation.
- Integrates with `delegation.h`, `internal.h`, `iostat.h`, and `nfs4trace.h`.

Concurrency and lifetime notes:
- Copy callback state is linked on client lists protected by `cl_lock`.
- Server-side copy sets `NFS_CLNT_SRC_SSC_COPY_STATE` and `NFS_CLNT_DST_SSC_COPY_STATE` on open states while the RPC is active.
- Async RPC payloads for offload cancel, layoutstats, and layouterror are freed by `rpc_call_ops` release callbacks.
- Layoutstats clears `NFS_INO_LAYOUTSTATS` with memory barriers after releasing layout-driver private data.
- Layouterror holds both an active inode reference and a pNFS layout segment reference.
- Fallocate paths use write-side NFS I/O serialization; copy uses destination inode locking.

Risk areas:
- Async server-side copy has subtle transitions between callback completion, polling, cancellation, restart, verifier validation, and VFS fallback.
- Correct page-cache invalidation is essential after allocate, deallocate, zero range, copy, and clone.
- Error translation deliberately distinguishes `-ENOTSUPP`, `-EOPNOTSUPP`, protocol status codes, and fallback-triggering errors.
- pNFS layoutstats/layouterror recovery depends on comparing layout stateids under inode lock and committing dirty data before retrying.
- Several async task-creation error paths return directly after allocating callback data; ownership must remain consistent with RPC setup expectations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs42proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs42xattr.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs42xattr.c

This file implements the client-side cache for NFSv4.2 user extended attributes. The cache is attached lazily to NFS inodes and stores both individual name/value xattrs and a special cached `listxattr` result.

Key structures:
- `struct nfs4_xattr_cache`: per-inode cache with 64 buckets, LRU/dispose nodes, entry count, listxattr lock, inode pointer, and special listxattr entry pointer.
- `struct nfs4_xattr_bucket`: spinlock-protected hash bucket with a `draining` flag and back-pointer to the cache.
- `struct nfs4_xattr_entry`: refcounted xattr or listxattr entry with hash node, LRU node, dispose node, name, value, size, bucket, and allocation flags.
- Global LRUs: one for cache objects, one for normal entries, and one for large entries whose values are separately allocated with `kvmalloc()`.

Main behavior:
- `nfs4_xattr_alloc_entry()` co-allocates the entry, name, and small value in one `kmalloc()` allocation, but uses an external `kvmalloc()` value for entries too large for one page.
- `nfs4_xattr_get_cache()` obtains or lazily creates a referenced inode cache. It unlinks stale caches when `NFS_INO_INVALID_XATTR` is set and avoids allocation while holding `inode->i_lock`.
- `nfs4_xattr_cache_get()` retrieves a named xattr, supporting length probes and `-ERANGE` for short caller buffers.
- `nfs4_xattr_cache_list()` retrieves the cached listxattr payload with the same length-probe behavior.
- `nfs4_xattr_cache_add()` replaces or inserts a named xattr and invalidates cached listxattr output.
- `nfs4_xattr_cache_remove()` removes a named xattr and invalidates cached listxattr output.
- `nfs4_xattr_cache_set_list()` stores listxattr output as a special entry not tied to a hash name.
- `nfs4_xattr_cache_zap()` unlinks the whole cache from an evicted or invalidated inode and discards its entries.

Shrinker design:
- The cache shrinker removes mostly empty cache structures after unlinking them from inodes.
- The normal entry shrinker reclaims ordinary cache entries.
- The large entry shrinker reclaims large entries more aggressively with `seeks = 1`.
- Shrinker isolation uses `trylock` because it can invert normal lock ordering; skipped objects are acceptable.

Locking and lifetime:
- Documented lock order is inode `i_lock` or bucket lock before the `list_lru` lock.
- Cache and entry lifetimes use `kref`.
- `ERR_PTR(-ESTALE)` in `cache->listxattr` marks a draining list cache so stale references cannot repopulate it.
- Cache unlinking requires `inode->i_lock`; bucket mutation requires the relevant bucket lock.
- Entry LRU membership and hash/list membership must be removed before the last `kref_put()`.

Risk areas:
- Refcount and LRU membership are tightly coupled; free callbacks warn if an entry remains on an LRU.
- Draining flags are the defense against racing writers repopulating stale caches.
- Large xattr memory pressure behavior depends on correct selection of `NFS4_XATTR_ENTRY_EXTVAL`.
- Shrinker callbacks deliberately skip locked objects; changing lock ordering here risks deadlock.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs42xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs42xdr.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs42xdr.c

This file contains NFSv4.2 XDR size accounting, encoders, and decoders for v4.2 compound operations. It is guarded as an include-style implementation header and defines operation-specific maximum sizes plus compound request/reply sizes.

Operations covered:
- `ALLOCATE`, `DEALLOCATE`, and `ZERO_RANGE`.
- `COPY`, `COPY_NOTIFY`, `OFFLOAD_CANCEL`, and `OFFLOAD_STATUS`.
- `READ_PLUS` and `SEEK`.
- pNFS `LAYOUTSTATS` and `LAYOUTERROR`.
- `CLONE`.
- `GETXATTR`, `SETXATTR`, `LISTXATTRS`, and `REMOVEXATTR`.

Key size definitions:
- Per-operation encode/decode limits such as `encode_copy_maxsz`, `decode_read_plus_maxsz`, and xattr encode/decode sizes.
- Compound totals such as `NFS4_enc_copy_sz`, `NFS4_dec_read_plus_sz`, and xattr-specific totals.
- Exported overhead constants `nfs42_maxsetxattr_overhead`, `nfs42_maxgetxattr_overhead`, and `nfs42_maxlistxattrs_overhead`, used by session setup to clamp xattr transfer sizes.

Encoder behavior:
- Encoders build standard compounds with header, `SEQUENCE`, `PUTFH`, operation-specific bodies, and optional `SAVEFH`, `COMMIT`, or `GETATTR`.
- `encode_copy()` supports intra-server copy and a single source server for inter-server copy.
- `encode_zero_range()` composes `DEALLOCATE` followed by `ALLOCATE`.
- `encode_read_plus()` prepares sparse read requests using stateid, offset, and count.
- `encode_layoutstats()` delegates layout-driver private encoding when `ld_private.ops` is present.
- Xattr encoders write names and page-backed values, with `LISTXATTRS` count following RFC 8276 reply-size semantics.

Decoder behavior:
- Basic decoders verify operation headers and then parse operation-specific payloads.
- `decode_write_response()` parses optional callback stateid, byte count, committed level, and verifier.
- `decode_copy()` special-cases `NFS4ERR_OFFLOAD_NO_REQS` to decode server sync/consecutive requirements.
- `decode_offload_status()` decodes copied byte count and optional completion status array.
- `decode_read_plus()` parses sparse data/hole segments, then processes them backwards to move data or zero-fill target reply pages.
- `decode_listxattrs()` prefixes returned names with `user.`, enforces name limits, maps `NFS4ERR_TOOSMALL` to `-ERANGE`, maps no-xattr to zero-length success, and turns max-size `-ERANGE` into `-E2BIG`.
- Mutating xattr decoders parse `change_info` and follow-up attributes.

Dependencies:
- Requires shared NFSv4 XDR helpers for compound headers, sequence, filehandle, stateid, verifier, commit, attributes, opaque strings, and XDR page manipulation.
- Uses constants from `nfs42.h`, NFSv4 protocol headers, xattr UAPI limits, and pNFS layout stats limits.

Risk areas:
- `READ_PLUS` buffer rewriting is delicate because segments are first decoded and then moved/zeroed into the receive page buffer.
- Xattr reply page length is intentionally separate from caller buffer length so successful oversized replies can still be cached.
- LISTXATTRS name sizing combines server count semantics with Linux `user.` prefixing and NUL terminators.
- Decoder status translation feeds directly into higher-level retry and fallback behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs42xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4_fs.h -->
# File Research: sources/os/linux/linux/fs/nfs/nfs4_fs.h

This is the central internal NFSv4 client header for filesystem-specific NFSv4 definitions, state structures, minor-version operation tables, and cross-file declarations.

Main content:
- Minor-version bounds derive from `CONFIG_NFS_V4_0` and `CONFIG_NFS_V4_2`.
- NFSv4 client state bits cover manager state, lease recovery, reclaim, session reset, delegation recall/expiration, migration, lease-moved recovery, and delayed delegation return.
- Sequence ID support is represented by `struct nfs_seqid_counter`, `struct nfs_seqid`, and `nfs_confirm_seqid()`.
- State-owner and state tracking structures include `struct nfs4_state_owner`, `struct nfs4_lock_state`, and `struct nfs4_state`.
- `struct nfs4_exception` carries state, inode, stateid, timeout/retransmit data, privileged/recovery/retry flags, and interruptibility for recovery loops.
- Operation vtables include minor-version ops, sequence slot ops, state recovery ops, state maintenance ops, and migration recovery ops.

Important declarations:
- NFSv4 procedure, state, recovery, session, migration, namespace, idmapping, and xattr functions.
- `nfs4_state_protect()` and `nfs4_state_protect_write()` helpers for SP4 machine credential protection.
- Procedure table declarations, fattr/statfs/pathconf/fsinfo/fs_locations bitmaps, stateid constants, and NFSv4.2 xattr overhead constants.
- Optional sysctl and NFSv4.2 xattr-cache declarations/stubs based on config.

Inline helpers:
- `is_ds_only_client()` and `is_ds_client()` identify pNFS data-server roles from exchange flags.
- Stateid helpers copy, compare full stateids, compare only the opaque portion, compare sequence freshness, handle wraparound increment, and check "match or older" semantics.
- `nfs4_valid_open_stateid()` and `nfs4_state_match_open_stateid_other()` provide small shared checks for open state recovery paths.
- SP4 helpers switch RPC client/credential to machine credentials for protected cleanup, pNFS cleanup, stateid operations, or writes; protected writes may force `NFS_FILE_SYNC` when commit is not machine-credential protected.

Role in this group:
- `nfs42proc.c`, `nfs42xattr.c`, `nfs4client.c`, `nfs4file.c`, `nfs4getroot.c`, `nfs4idmap.c`, `nfs4namespace.c`, `nfs4renewd.c`, and `nfs4session.c` all rely on this header for shared state and declarations.
- It defines the vocabulary and contracts for stateids, sessions, recovery, migration, and NFSv4.2 xattr caching.

Risk areas:
- State flags and stateid helper semantics are cross-cutting; small changes can affect open, lock, delegation, copy, pNFS, and recovery paths.
- Config-guarded stubs must match real function signatures and side-effect expectations.
- SP4 credential switching is security-sensitive and affects cleanup and write stability behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4client.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs4client.c

This file manages NFSv4 client objects, callback setup, NFSv4.1+ sessions, pNFS data-server clients, server records, referrals, trunking, and server migration updates.

Key client setup:
- `nfs4_alloc_client()` allocates and initializes an `nfs_client`, validates minor version, initializes NFSv4 locks/work/lists/waitqueues, creates the RPC client, derives callback address when needed, and creates idmap state.
- `nfs4_init_client()` initializes minor-version behavior, callback service, and server trunking discovery. If another usable client is found, it preserves clientid state, optionally adds a trunk transport, and returns the existing client.
- `nfs4_free_client()` shuts down NFSv4-specific resources and then frees the generic client.

Callback and session handling:
- `nfs_get_cb_ident_idr()` allocates v4.0 callback identifiers in the network namespace IDR.
- `nfs4_init_callback()` starts the callback service and sets up backchannel support for session clients.
- `nfs41_init_client()` allocates an NFSv4.1+ session and marks the client as session-initializing so callbacks can find it during create-session races.
- `nfs41_shutdown_client()` cleans pending callback copy state, pNFS DS clients, the session, and clientid.

pNFS data server support:
- `nfs4_find_or_create_ds_client()` maintains per-auth-flavor cloned RPC clients for DS I/O.
- `nfs4_shutdown_ds_clients()` tears those DS RPC clients down.
- `nfs4_set_ds_client()` creates or finds a DS `nfs_client` with MDS-derived owner identity, transport options, pNFS flags, and inherited TLS policy when applicable.

Trunking and client matching:
- `nfs4_match_client()` compares RPC ops, minor version, readiness, clientid, and owner-id compatibility, waiting for in-progress client initialization where necessary.
- `nfs41_walk_client_list()` searches for matching clientid/server-owner entries, treating session trunking as a clientid trunking subcase.
- `nfs4_detect_session_trunking()` verifies clientid, server owner major/minor IDs, and server scope before accepting session trunking.
- `nfs4_add_trunk()` adds a compatible transport to an existing client.

Server setup:
- `nfs4_set_client()` binds an `nfs_server` to a client, applies mount-derived transport flags, sets lease-check state, and links sysfs RPC client state.
- `nfs4_init_server()` copies mount context into a new server, selects the initial auth flavor, sets sizes/timeouts/cache parameters, and initializes the RPC client.
- `nfs4_server_common_setup()` allocates the delegation hash, rejects DS-only clients as metadata servers, initializes sessions, probes root filehandle and capabilities, clamps session sizes, inserts server list nodes, and installs destroy handling.
- `nfs4_create_server()` creates ordinary NFSv4 server records.
- `nfs4_create_referral_server()` creates referral server records, trying RDMA when available and otherwise TCP or TCP-TLS based on parent transport security.

Size limiting:
- `nfs4_session_limit_rwsize()` clamps `dtsize`, `rsize`, and `wsize` by negotiated forechannel sizes.
- `nfs4_session_limit_xasize()` clamps get/set/list xattr sizes using NFSv4.2 XDR overhead constants.

Migration:
- `nfs4_update_server()` switches the existing RPC client transport, computes a local client address, removes the server from lists, binds it to a new/updated `nfs_client`, preserves list membership on failure, and reprobes server capabilities after reinsertion.

Risk areas:
- Client matching/trunking is race-sensitive because the shared client list can contain initializing clients.
- Cleanup spans renewd, minor-version shutdown, callback service, idmap pipe state, DS clients, sessions, sysfs, RPC wait queues, and allocated server-owner strings.
- Referral and migration setup must preserve credentials, transport security policy, mount-derived auth/size options, and client owner identity.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4client.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4file.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs4file.c

This file defines NFSv4 file operations and wires NFSv4.2 file features into VFS operations when `CONFIG_NFS_V4_2` is enabled.

Core NFSv4 operations:
- `nfs4_file_open()` validates flags, strips create/exclusive flags, allocates an NFS open context, handles truncate-on-open by flushing cached pages, calls the protocol `open_context()` operation, drops stale dentries on selected lookup errors, installs the open context, opens fscache state, and enables direct I/O capability.
- `nfs4_file_flush()` flushes dirty writeback and reports writeback errors on close. If a write delegation does not require flush-on-close, it starts writeback without waiting for completion.
- `nfs4_setlease()` delegates lease handling to `nfs4_proc_setlease()`.

NFSv4.2 additions:
- `__nfs4_copy_file_range()` tries server-side copy only for NFSv4 file operations and copy-capable servers. It selects synchronous copy for small ranges, performs `COPY_NOTIFY` for inter-server copy, and retries `-EAGAIN`.
- `nfs4_copy_file_range()` falls back to `splice_copy_file_range()` for unsupported or cross-device style failures.
- `nfs4_file_llseek()` uses NFSv4.2 `SEEK` for `SEEK_HOLE` and `SEEK_DATA`, falling back to generic NFS seek when unsupported.
- `nfs42_fallocate()` supports allocate, punch-hole-keep-size, and zero-range modes for regular files, validates new size, and dispatches to NFSv4.2 procedure wrappers.
- `nfs42_remap_file_range()` implements clone/remap via `CLONE`, rejects dedupe and unsupported flags, validates clone block alignment, blocks direct I/O, syncs both inodes, calls clone RPC, and invalidates destination page cache on success.
- Server-side-copy pseudo-open helpers create and close read-only pseudo files around a source filehandle and server-provided stateid for inter-server copy support.

File operations table:
- `nfs4_file_operations` binds read/write, mmap prepare, open, flush, release, fsync, locks, splice, flag checking, leases, and, under NFSv4.2, copy, llseek, fallocate, and remap hooks.
- The table sets `FOP_DONTCACHE`.

Risk areas:
- Open path intentionally returns `-EOPENSTALE` after dropping dentries so VFS retries lookup/open correctly.
- Clone/remap must coordinate inode locking, direct I/O blocking, writeback synchronization, and destination cache invalidation.
- Server-side-copy pseudo-open manually constructs open state around a server-provided stateid and clears state flags on close.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4getroot.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs4getroot.c

This small file implements `nfs4_get_rootfh()`, the helper that retrieves and validates an NFSv4 root filehandle during server setup.

Behavior:
- Allocates an `nfs_fattr`.
- Calls `nfs4_proc_get_rootfh()` to fetch the server root filehandle and attributes.
- Verifies that the returned object has a valid type attribute and is a directory.
- Copies the returned fsid into `server->fsid`.
- Frees attributes before returning.

Dependencies:
- `nfs4_proc_get_rootfh()` from the NFSv4 procedure layer.
- `nfs_alloc_fattr()` and `nfs_free_fattr()`.
- `NFS_ATTR_FATTR_TYPE` and `S_ISDIR()` validation.

Risk areas:
- A non-directory root is converted to `-ENOTDIR`.
- Attribute allocation failure returns `-ENOMEM`.
- This helper is called during common server setup, so failures abort mount/referral setup early.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4getroot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4idmap.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs4idmap.c

This file implements NFSv4 UID/GID to owner/group string mapping and reverse mapping. It uses the kernel request-key infrastructure, with a legacy rpc_pipefs upcall fallback.

Core concepts:
- `struct idmap` stores rpc pipe directory state, pipe data, active legacy upcall data, a mutex, and the user namespace used for ID conversion.
- `id_resolver_cache` is a kernel credential with a `.id_resolver` thread keyring used while requesting idmapping keys.
- Two key types are registered: `id_resolver` for normal key-based resolution and `id_legacy` for rpc_pipefs-driven legacy upcalls.

Attribute-name helpers:
- `nfs_fattr_init_names()` attaches owner/group string storage to an `nfs_fattr`.
- `nfs_fattr_map_and_free_names()` maps owner/group strings to numeric uid/gid and frees cached strings.
- `nfs_fattr_free_names()` releases owner/group strings without mapping.

Numeric shortcut:
- `nfs_map_string_to_numeric()` treats non-domain strings without `@` as numeric IDs when parseable.
- `nfs_map_numeric_to_string()` formats numeric IDs for fallback and key descriptions.

Keyring flow:
- `nfs_idmap_init()` creates `.id_resolver`, registers both key types, configures resolver credentials, and stores them globally.
- `nfs_idmap_quit()` revokes the keyring, unregisters key types, and drops credentials.
- `nfs_idmap_get_desc()` builds descriptions such as `uid:name`, `gid:name`, `user:id`, or `group:id`.
- `nfs_idmap_request_key()` first tries the modern `id_resolver` in init user namespace cases, then falls back to legacy `id_legacy` with the per-client idmap as aux data.
- `nfs_idmap_get_key()` validates a key and copies its user payload into the caller buffer.

Legacy rpc_pipefs flow:
- `nfs_idmap_new()` creates per-client idmap state and an `idmap` pipe under rpc_pipefs.
- `nfs_idmap_delete()` removes the pipe object, destroys pipe data, releases the user namespace, and frees idmap state.
- `nfs_idmap_legacy_upcall()` prepares an `idmap_msg`, records one active upcall, queues it to the pipe, and completes request-key auth on failure or later downcall.
- `idmap_pipe_downcall()` validates the userspace response, checks it matches the outstanding request, instantiates the target key, sets cache timeout, and returns the downcall byte count.
- `idmap_release_pipe()` fails an outstanding upcall with `-EPIPE`.

Public mapping APIs:
- `nfs_map_name_to_uid()` maps owner names to `kuid_t`, using numeric shortcut or key lookup and validating with `uid_valid()`.
- `nfs_map_group_to_gid()` maps group names to `kgid_t`, using numeric shortcut or key lookup and validating with `gid_valid()`.
- `nfs_map_uid_to_name()` maps `kuid_t` to owner string, falling back to numeric output when named mapping fails or `NFS_CAP_UIDGID_NOMAP` is set.
- `nfs_map_gid_to_group()` maps `kgid_t` to group string with the same fallback behavior.

Namespace handling:
- ID conversion uses the idmap's user namespace if available, otherwise `init_user_ns`.
- Reverse mapping uses `from_kuid_munged()` / `from_kgid_munged()`.

Risk areas:
- Only one legacy upcall is active per idmap; `idmap_upcall_data` transitions use mutex, `xchg()`, and `cmpxchg()` patterns.
- Key payload length and userspace downcall validation are strict; malformed responses become `-EINVAL`, `-ENOKEY`, `-ENOSPC`, or `-EFAULT`.
- Numeric fallback behavior affects interoperability with servers that return numeric owner/group strings.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4idmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4idmap.h -->
# File Research: sources/os/linux/linux/fs/nfs/nfs4idmap.h

This header declares the NFSv4 idmapping interface used by client setup and attribute decode/update code.

Declarations:
- Lifecycle: `nfs_idmap_init()`, `nfs_idmap_quit()`, `nfs_idmap_new()`, and `nfs_idmap_delete()`.
- Attribute owner/group string helpers: `nfs_fattr_init_names()`, `nfs_fattr_free_names()`, and `nfs_fattr_map_and_free_names()`.
- Mapping APIs: `nfs_map_name_to_uid()`, `nfs_map_group_to_gid()`, `nfs_map_uid_to_name()`, `nfs_map_gid_to_group()`, and `nfs_map_string_to_numeric()`.
- External tunable: `nfs_idmap_cache_timeout`.

Role:
- Keeps idmap implementation details out of callers.
- Provides forward declarations for `nfs_client`, `nfs_server`, `nfs_fattr`, and `nfs4_string`.
- Includes UID/GID and NFS idmap UAPI definitions.

Risk areas:
- This header is a shared contract between idmap implementation, NFSv4 client setup, and XDR attribute decode/update paths.
- Signature drift would affect multiple translation and mount paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4idmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4namespace.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs4namespace.c

This file implements NFSv4 namespace handling: referral following, `WRONGSEC` security negotiation, server-name parsing, and transport replacement for migration.

Path helpers:
- `nfs4_pathname_len()` validates NFSv4 pathname components against `NAME_MAX` and total rendered length against `PATH_MAX`.
- `nfs4_pathname_string()` converts NFSv4 pathname components into a slash-prefixed POSIX path string.
- `nfs_path_component()` extracts the path part from `server:path`, including bracketed IPv6 address handling.
- `nfs4_path()` obtains a canonical NFS path and returns its export path component.
- `nfs4_validate_fspath()` verifies that a referral `fs_root` is a prefix of the current dentry path.

Server-name parsing:
- `nfs_parse_server_name()` tries `rpc_pton()`, then `rpc_uaddr2sockaddr()`, then DNS resolution through `nfs_dns_resolve_name()`.
- When a numeric address is parsed and a port is supplied, it applies the requested port.

Security negotiation:
- `nfs_find_best_sec()` selects the first server-provided security flavor that is locally supported and matches mount `sec=` constraints, then clones an RPC client with that auth flavor and verifies credentials can be acquired.
- `nfs4_negotiate_security()` calls `SECINFO` for a lookup name and returns a temporary RPC client using the chosen flavor. Callers must shut it down.

Referral handling:
- `try_location()` mutates the mount context for a single `fs_locations` entry, building hostname, export path, `fc->source`, server address, and port before trying `nfs4_get_referral_tree()`.
- It skips server names with IPv6 scope delimiters.
- `nfs_follow_referral()` validates the fs path prefix and iterates locations until one succeeds.
- `nfs_do_refmount()` obtains `fs_locations` for a referral dentry and follows them.
- `nfs4_submount()` re-lookups the mountpoint to get selected auth flavor and attributes, then either follows a referral or performs an ordinary submount.

Migration transport replacement:
- `nfs4_try_replacing_one_location()` allocates a `sockaddr_storage`, iterates usable server names in a location, resolves each name, builds a temporary hostname with `kmemdup_nul()`, and calls `nfs4_update_server()`.
- `nfs4_replace_transport()` iterates fs_locations and tries replacement until one succeeds.
- In this tree, transport replacement does not allocate or pass scratch pathname pages into `nfs4_try_replacing_one_location()`.

Risk areas:
- Referral path validation prevents mounting unrelated server paths from a malicious or stale `fs_locations` result.
- `fc->source`, hostname, export path, selected flavor, and server address fields are mutated during location attempts.
- Temporary cloned RPC clients from security negotiation must be shut down by callers.
- IPv6 scoped addresses are intentionally skipped in referral and migration server lists.
- Migration replacement depends on `nfs4_update_server()` preserving server list membership and reprobe behavior on failure/success.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4namespace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4renewd.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs4renewd.c

This file implements the NFSv4 lease renewal worker. It runs as delayed work in kernel workqueue context rather than as a dedicated kernel thread.

Main functions:
- `nfs4_renew_state()` checks whether renewal should stop, determines whether the client is close enough to lease timeout or has delegations requiring callback renewal pressure, obtains renewal credentials through minor-version ops, schedules async renewal, expires delegations when only delegation renewal lacks credentials, marks lease expired when timeout renewal lacks credentials, reschedules renewal work, and expires unreferenced delegations.
- `nfs4_schedule_state_renewal()` schedules the next renewal for roughly two-thirds of the lease period after the last renewal, with a minimum delay of five seconds, and sets `NFS_CS_RENEWD`.
- `nfs4_kill_renewd()` synchronously cancels delayed renewal work.
- `nfs4_set_lease_period()` caps lease period at one hour, stores it in jiffies under client lock, and caps RPC reconnect timeout to at most half the lease.

Dependencies:
- Minor-version `state_renewal_ops` for credential selection and scheduling renewal RPCs.
- Delegation helpers for detecting, expiring, and pruning delegations.
- Client lock protects lease time updates and renewal scheduling calculations.

Risk areas:
- Renewal timing determines whether client open/lock/delegation state survives server lease expiration.
- Credential absence has different consequences for lease timeout renewal versus delegation-only renewal.
- `NFS_CS_STOP_RENEW` must be honored during shutdown to avoid renewing after teardown starts.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4renewd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4session.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs4session.c

This file implements NFSv4.1+ session slot table management, dynamic slot resizing, session allocation/destruction, and session readiness checks.

Slot table setup:
- `nfs4_init_slot_table()` initializes highest-used state, spinlock, RPC wait queue, completion waitqueue, and drain completion.
- `nfs4_setup_slot_table()` prepares a standalone slot table and allocates initial slots.
- `nfs4_setup_session_slot_tables()` initializes forechannel and, when present, backchannel slot tables from session channel attributes.

Slot allocation and release:
- `nfs4_alloc_slot()` finds a free bit up to `max_slotid`, creates a slot if needed, marks it used, and updates `highest_used_slotid`.
- `nfs4_try_to_lock_slot()` attempts to allocate a specific slot already found by lookup.
- `nfs4_free_slot()` clears the used bit, recomputes `highest_used_slotid`, and completes table draining when no slots remain.
- `nfs4_lookup_slot()` finds or creates a slot without marking it used, returning `-E2BIG` if the slotid exceeds `max_slotid`.
- `nfs4_slot_wait_on_seqid()` lets callback-channel code wait until a slot sequence id is no longer in flight.

Waitqueue integration:
- `nfs41_assign_slot()` attaches a slot to RPC sequence args/results unless the table is draining and the task is not privileged.
- `nfs41_wake_and_assign_slot()` wakes one queued RPC task with a specific slot.
- `nfs41_wake_slot_table()` repeatedly allocates available slots and wakes waiters.

Dynamic resizing:
- `nfs41_set_target_slotid()` sets a new target highest slot id, resets derivative tracking, and wakes waiters.
- `nfs41_update_target_slotid()` consumes server sequence reply limits, filters target-slot outliers using first/second derivative checks, shrinks server slot storage when safe, updates max usable slotid, and wakes waiters.
- `nfs4_reset_slot_table()` resets sequence numbers, target/server slot limits, highest-used state, and derivative state.

Session lifecycle:
- `nfs4_alloc_session()` allocates a session, initializes fore/back channel slot tables, marks it initializing, and links it to the client.
- `nfs4_destroy_session()` obtains clientid credentials, sends `DESTROY_SESSION`, destroys the RPC backchannel, shuts down slot tables, and frees the session.
- `nfs4_init_session()` clears initializing state and checks readiness for normal MDS sessions.
- `nfs4_init_ds_session()` seeds DS lease time from the MDS lease, checks readiness, and verifies the client has a pNFS DS role.

Risk areas:
- Slot accounting must keep `used_slots`, `highest_used_slotid`, `max_slotid`, and slot sequence numbers consistent under `slot_tbl_lock`.
- Draining behavior must still allow privileged tasks while preventing ordinary slot assignment.
- Dynamic resizing avoids shrinking below in-use slots; mistakes can corrupt session sequencing.
- Destroying a session couples protocol teardown, backchannel teardown, waitqueue cleanup, and slot memory release.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4session.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4session.h -->
# File Research: sources/os/linux/linux/fs/nfs/nfs4session.h

This header defines NFSv4.1+ session and slot-table structures plus the public session-management interface used by NFSv4 procedure and client code.

Constants:
- Default forechannel slot table size: `NFS4_DEF_SLOT_TABLE_SIZE`.
- Default callback slot table size: `NFS4_DEF_CB_SLOT_TABLE_SIZE`.
- Maximum slot table size and slot id: `NFS4_MAX_SLOT_TABLE` and `NFS4_MAX_SLOTID`.
- Sentinel no-slot value: `NFS4_NO_SLOT`.

Main structures:
- `struct nfs4_slot` stores parent table, linked-list pointer, generation, slot number, current/last-acked/highest-sent sequence numbers, and privileged/sequence-done flags.
- `struct nfs4_slot_table` stores parent session, allocated slot list, used-slot bitmap, locks, wait queues, completion, max/server/target slot limits, derivative state for target changes, generation, and draining state.
- `struct nfs4_session` stores session id, flags, session state, SSV/hash data, forechannel/backchannel attributes, forechannel/backchannel slot tables, and parent client.

Public APIs:
- Slot table setup/shutdown: `nfs4_setup_slot_table()`, `nfs4_shutdown_slot_table()`, and `nfs4_setup_session_slot_tables()`.
- Slot allocation and lookup: `nfs4_alloc_slot()`, `nfs4_lookup_slot()`, `nfs4_try_to_lock_slot()`, `nfs4_free_slot()`, and `nfs4_slot_wait_on_seqid()`.
- Waiter assignment and wakeup: `nfs41_wake_and_assign_slot()` and `nfs41_wake_slot_table()`.
- Dynamic slot updates: `nfs41_set_target_slotid()` and `nfs41_update_target_slotid()`.
- Session lifecycle: `nfs4_alloc_session()`, `nfs4_destroy_session()`, `nfs4_init_session()`, and `nfs4_init_ds_session()`.

Inline helpers:
- `nfs4_slot_tbl_draining()` checks whether the table is draining.
- `nfs4_test_locked_slot()` tests whether a slot bit is in use.
- `nfs4_get_session()`, `nfs4_has_session()`, and `nfs4_has_persistent_session()` expose session presence and persistence.
- `nfs4_copy_sessionid()` copies session IDs.
- `nfs_session_id_hash()` computes a CRC32-derived session-id hash.

Risk areas:
- These structures are shared across the session sequencing, callback, recovery, and client lifecycle code.
- Bitmap dimensions and slot maxima must stay aligned with `NFS4_MAX_SLOT_TABLE`.
- Inline helpers encode assumptions that must match `nfs4session.c` locking and state transitions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4session.h -->