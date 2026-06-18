# subset-b-005692 Research: sources/distributed-fs/ceph-client/fs/nfs NFSv4/NFSv4.2 Client Paths

Grouped research for the source-tree-aligned files assigned to `subset-b-005692`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs42proc.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs42proc.c

## Purpose

`nfs42proc.c` implements the client-side NFSv4.2 procedure layer for operations that are exposed upward through VFS file operations, pNFS layout code, and xattr handlers. It prepares RPC argument/result structures, selects stateids, performs synchronous or asynchronous SUNRPC calls, handles NFSv4 recovery exceptions, updates inode/page-cache state after successful server-side mutations, and downgrades server capability bits when peers return unsupported-operation errors.

## Important APIs, Types, and Functions

The public API exported through `nfs42.h` includes `nfs42_proc_allocate`, `nfs42_proc_deallocate`, `nfs42_proc_zero_range`, `nfs42_proc_copy`, `nfs42_proc_copy_notify`, `nfs42_proc_llseek`, `nfs42_proc_layoutstats_generic`, `nfs42_proc_layouterror`, `nfs42_proc_clone`, `nfs42_proc_getxattr`, `nfs42_proc_setxattr`, `nfs42_proc_listxattrs`, and `nfs42_proc_removexattr`. These functions are invoked from `nfs4file.c`, `nfs4proc.c`, pNFS layout modules, and server-side-copy support.

The fallocate family is built around `_nfs42_proc_fallocate`, which fills `nfs42_falloc_args`, chooses a write stateid with `nfs4_set_rw_stateid`, asks for post-op attributes via `nfs4_bitmask_set`, performs `nfs4_call_sync`, updates suid/cache invalidation, and traces allocate/deallocate results. `nfs42_proc_allocate`, `nfs42_proc_deallocate`, and `nfs42_proc_zero_range` add capability checks, `nfs_start_io_write`/`nfs_end_io_write`, page-cache truncation or invalidation, and capability clearing on `-EOPNOTSUPP`.

The server-side copy path uses `_nfs42_proc_copy`, `handle_async_copy`, `process_copy_commit`, `nfs42_copy_dest_done`, `nfs42_proc_offload_status`, and `nfs42_do_offload_cancel_async`. It coordinates source and destination stateids, writeback synchronization, async CB_OFFLOAD completion lists, OFFLOAD_STATUS polling, optional COMMIT verifier checks, cancellation, and destination inode invalidation.

The pNFS reporting path is `nfs42_proc_layoutstats_generic` and `nfs42_proc_layouterror`. Their RPC callback operations validate layout stateids at prepare time, handle stale/bad/old layout stateids in done callbacks, destroy or invalidate layouts as needed, and release layout references in async completion.

The xattr procedure helpers translate VFS xattr requests to NFSv4.2 `GETXATTR`, `SETXATTR`, `LISTXATTRS`, and `REMOVEXATTR` RPCs. `_nfs42_proc_getxattr` caches successful replies through `nfs4_xattr_cache_add`; `_nfs42_proc_setxattr` and `_nfs42_proc_removexattr` request post-op attributes and change info; `_nfs42_proc_listxattrs` allocates scratch folio/page arrays and returns pagination state through cookie/eof.

## Control Flow

Most exported functions follow the same template: check a capability bit, acquire a lock/open context when a stateid is needed, optionally flush or synchronize local dirty data, call a private `_nfs42_proc_*` RPC helper, feed errors to `nfs4_handle_exception`, and loop while the exception says retry. The private helpers are narrow RPC marshalling/adaptation layers; the exported wrappers own policy, retries, capability fallback, and VFS-visible errno translation.

Copy is the most complex flow. `nfs42_proc_copy` obtains source and destination lock contexts, locks the destination inode, calls `_nfs42_proc_copy`, and retries or falls back based on `-EAGAIN`, `NFS4ERR_OFFLOAD_NO_REQS`, `NFS4ERR_OFFLOAD_DENIED`, `-ESTALE`, and same-server/inter-server status. `_nfs42_proc_copy` writes back the source range, obtains destination write state, blocks direct I/O, syncs the destination inode, sends COPY, then handles synchronous verifier checks, async CB_OFFLOAD wait or OFFLOAD_STATUS polling, commit fallback, page-cache invalidation, and atime invalidation.

`nfs42_proc_clone` is similar to copy but uses the `CLONE` operation with source/destination stateids and post-op destination attributes. `nfs42_proc_llseek` maps `SEEK_HOLE` and `SEEK_DATA` to NFSv4.2 `SEEK`, writes back from the requested offset onward before asking the server, and maps EOF-on-data to `NFS4ERR_NXIO`.

## State and Persistence Behavior

This file mutates in-memory client state, not durable local metadata. It updates `NFS_SERVER(inode)->caps` to stop retrying unsupported server features, sets and clears NFS state flags such as `NFS_CLNT_SRC_SSC_COPY_STATE`, `NFS_CLNT_DST_SSC_COPY_STATE`, and layout invalidation bits, maintains async copy objects on `nfs_client` callback lists, and invalidates page cache/inode attribute cache after remote mutation. Persistent data changes happen on the server through NFSv4.2 RPCs.

Cache side effects are significant. Allocate/zero/deallocate/clone/copy punch or truncate page-cache ranges so future reads refetch server data. Xattr get replies are populated into the xattr cache even for size probes or too-small caller buffers, while successful set/remove paths update change attributes and post-op inode attributes.

## Dependencies and Integration Points

The implementation depends on SUNRPC (`rpc_task`, `rpc_message`, `rpc_run_task`, callback ops), NFSv4 sequencing and recovery (`nfs4_call_sync`, `nfs4_handle_exception`, `nfs4_async_handle_error`, `nfs4_init_sequence`, `nfs41_sequence_done`), VFS inode/page-cache helpers, pNFS layout APIs, and NFS tracepoints. Procedure numbers and XDR handlers are provided by `nfs4_procedures[]` and `nfs42xdr.c`.

Primary callers include `nfs4file.c` for fallocate/copy/remap/llseek, `nfs4proc.c` for xattr VFS hooks and xattr cache integration, `pnfs.c` for layout stats, and layout drivers such as flexfiles for `LAYOUTERROR`.

## Risks and Edge Cases

Risk clusters include stale stateid recovery loops, verifier mismatch after COPY/COMMIT, async copy completion races with CB_OFFLOAD, cancellation behavior for inter-server copy, page-cache coherency after sparse-file operations, and capability-bit clearing that can disable features for a server after unsupported replies. Xattr paths must keep page allocation/freeing balanced across partial allocation failures and must respect negotiated `sxasize`/`lxasize`.

The copy path explicitly handles non-compliant async COPY servers that advertise async copy but not OFFLOAD_STATUS. Layout stats and error reporting invert some lock acquisition via async callbacks and must avoid using stale layout stateids.

## Test Signals

Useful tests are fallocate allocate/punch-hole/zero-range over NFSv4.2, sparse file `SEEK_HOLE`/`SEEK_DATA`, same-server and cross-server `copy_file_range`, async copy interruption and cancellation, clone/remap alignment handling, pNFS layoutstats/layouterror with stale layout stateids, and xattr get/set/list/remove including ERANGE/E2BIG and cache hit/miss behavior. Tracepoints such as `trace_nfs4_copy`, `trace_nfs4_fallocate`, `trace_nfs4_layoutstats`, and xattr tracepoints are direct observability hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs42proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs42xattr.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs42xattr.c

## Purpose

`nfs42xattr.c` implements the client-side cache for NFSv4.2 user extended attributes. It stores per-inode xattr name/value entries and listxattr results, integrates with inode cache invalidation, and registers memory shrinkers so cached xattr objects can be reclaimed under pressure.

## Important APIs, Types, and Functions

The file defines `struct nfs4_xattr_cache`, `struct nfs4_xattr_entry`, and `struct nfs4_xattr_bucket`. A cache is attached to `NFS_I(inode)->xattr_cache`, contains 64 hash buckets, has a special `listxattr` entry, tracks entry count in `nent`, and participates in `nfs4_xattr_cache_lru`. Entries contain the xattr name, value pointer, size, hash node, LRU node, reference count, and flags such as `NFS4_XATTR_ENTRY_EXTVAL` for separately allocated large values.

The exported cache API is `nfs4_xattr_cache_get`, `nfs4_xattr_cache_add`, `nfs4_xattr_cache_remove`, `nfs4_xattr_cache_set_list`, `nfs4_xattr_cache_list`, `nfs4_xattr_cache_zap`, `nfs4_xattr_cache_init`, and `nfs4_xattr_cache_exit`. These are declared in `nfs4_fs.h` and used by NFSv4.2 xattr RPC plumbing in `nfs42proc.c` and VFS xattr hooks in `nfs4proc.c`.

Core internals include `nfs4_xattr_get_cache`, `nfs4_xattr_discard_cache`, `nfs4_xattr_hash_add/find/remove`, `nfs4_xattr_set_listcache`, and shrinker callbacks `nfs4_xattr_cache_scan` and `nfs4_xattr_entry_scan`.

## Control Flow

Reads call `nfs4_xattr_get_cache(inode, 0)`, which returns a referenced valid cache or `NULL`. Name lookups hash by `jhash(name)` and take a bucket lock while finding and refcounting an entry. List lookups use `listxattr_lock` and the special list entry. Both return `-ENOENT` on misses, a length for size probes, `-ERANGE` for too-small caller buffers, or a copied value length.

Adds call `nfs4_xattr_get_cache(inode, 1)`, which may optimistically allocate a new cache without holding `i_lock`, then attach it under `i_lock` if the inode cache was not invalidated and another thread did not win the race. A new entry is allocated with name and, if small enough, value in one kmalloc object; large values are allocated by `kvmalloc`. Adding a named xattr invalidates the cached listxattr result, replaces an old same-name entry if present, and adds the entry to the small or large entry LRU.

Invalidation removes the cache from the inode under `i_lock`, marks buckets draining, removes all entries from LRUs/hash tables, marks list cache as `ERR_PTR(-ESTALE)`, and frees objects when final references drop. Shrinkers isolate caches or entries with trylocks to avoid deadlock against the normal lock order.

## State and Persistence Behavior

All state is volatile kernel memory. The cache mirrors server xattr values only while the inode's xattr validity remains acceptable. `NFS_INO_INVALID_XATTR` causes `nfs4_xattr_get_cache` to unlink and discard the old cache. The code carefully distinguishes the inode's pointer lifetime, cache kref lifetime, entry kref lifetime, and LRU membership lifetime.

The cache has no persistence across inode eviction, module unload, memory pressure reclamation, or explicit invalidation. `nfs4_xattr_cache_zap` is called from NFSv4 super/inode cleanup paths to detach and discard the whole cache.

## Dependencies and Integration Points

This file depends on Linux list LRU and shrinker APIs, slab caches, NFS inode state, spinlocks, krefs, xattr UAPI limits, and page-copy helpers. `nfs4proc.c` first attempts cache reads before calling `nfs42_proc_getxattr` or list RPCs, and updates/removes cache entries after successful remote mutation.

## Risks and Edge Cases

Important risks are lock ordering, refcount/LRU consistency, and stale cache exposure. The documented lock order is inode `i_lock` or bucket lock before list_lru internals; shrinker callbacks use trylocks because they invert lookup direction. The sentinel `ERR_PTR(-ESTALE)` prevents listxattr results from being added while a cache is draining.

Memory accounting and allocation behavior matter for large xattrs: small entries are packed into one page-sized allocation where possible, while large values use `kvmalloc` and a more aggressive shrinker. Bugs in `nent` tracking could prevent cache shrink or premature cache reclamation.

## Test Signals

Tests should exercise cache hits after successful `getxattr`, listxattr caching, invalidation after set/remove, inode eviction zap, memory pressure shrinkers for small and large xattrs, concurrent get/add/remove on the same inode/name, and ERANGE length-probe behavior. Kernel lockdep and KASAN/KCSAN are useful for lock/refcount races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs42xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs42xdr.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs42xdr.c

## Purpose

`nfs42xdr.c` supplies the XDR encode/decode implementation and size accounting for NFSv4.2 client procedures. It is included into the NFSv4 XDR/procedure table build and defines the compound request layouts for ALLOCATE, COPY, OFFLOAD_CANCEL, OFFLOAD_STATUS, COPY_NOTIFY, DEALLOCATE, ZERO_RANGE, READ_PLUS, SEEK, LAYOUTSTATS, LAYOUTERROR, CLONE, and NFSv4.2 xattr operations.

## Important APIs, Types, and Functions

The file defines maximum encode/decode sizes for each operation and compound call, plus exported overhead constants `nfs42_maxsetxattr_overhead`, `nfs42_maxgetxattr_overhead`, and `nfs42_maxlistxattrs_overhead`, used by session setup to cap xattr transfer sizes against negotiated channel limits.

Encoder helpers include `encode_fallocate`, `encode_copy`, `encode_copy_commit`, `encode_offload_cancel`, `encode_offload_status`, `encode_copy_notify`, `encode_read_plus`, `encode_seek`, `encode_layoutstats`, `encode_layouterror`, `encode_clone`, `encode_setxattr`, `encode_getxattr`, `encode_listxattrs`, and `encode_removexattr`. Compound encoders named `nfs4_xdr_enc_*` add COMPOUND headers, SEQUENCE, PUTFH/SAVEFH, operation-specific payloads, GETATTR or COMMIT when needed, reply page preparation, and op counts.

Decoder helpers include `decode_write_response`, `decode_nl4_server`, `decode_copy`, `decode_offload_status`, `decode_copy_notify`, `decode_read_plus`, `decode_seek`, `decode_setxattr`, `decode_getxattr`, `decode_listxattrs`, and the `nfs4_xdr_dec_*` compound wrappers.

## Control Flow

Each encoder follows the same compound pattern: initialize `compound_hdr` from the sequence minor version, encode COMPOUND and SEQUENCE, encode the relevant filehandle(s), encode the NFSv4.2 operation, optionally encode GETATTR or COMMIT, and finalize with `encode_nops`. Operations that return variable-length data, such as READ_PLUS, GETXATTR, and LISTXATTRS, call `rpc_prepare_reply_pages` so response data lands directly in caller-provided pages.

Decoders reverse the compound operation sequence. They decode COMPOUND, SEQUENCE, PUTFH/SAVEFH where present, then the operation body and follow-up GETATTR/COMMIT. `READ_PLUS` decodes all returned data/hole segments first, sets the page length, then processes segments backward so moving XDR subsegments into reply pages does not overwrite not-yet-processed data. Hole segments are zero-filled; data segments are moved from the XDR stream into the final page buffer.

COPY decoding handles a special `NFS4ERR_OFFLOAD_NO_REQS` response by decoding server requirements and returning that status to the procedure layer. LISTXATTRS translates NFS protocol edge cases: `NFS4ERR_TOOSMALL` becomes `-ERANGE`, `NFS4ERR_NOXATTR` becomes success with EOF and zero-length output, and a full-size caller buffer that still overflows becomes `-E2BIG`.

## State and Persistence Behavior

This file has no persistent state beyond static constants. It mutates only RPC request/response buffers and result structures supplied by procedure code. Correctness is nevertheless state-sensitive because sequence arguments/results, stateids, layout stateids, COPY stateids, cookies, EOF markers, and verifier fields are carried between `nfs42proc.c` and the wire.

## Dependencies and Integration Points

It depends on NFSv4 shared XDR helpers from `nfs4xdr.c`, `nfs42.h` argument/result structures, SUNRPC XDR stream APIs, pNFS layout-private encoder callbacks, xattr UAPI constants, and NFS procedure table macros. Its `nfs4_xdr_enc_*` and `nfs4_xdr_dec_*` functions are selected by `nfs4_procedures[]` entries for NFSv4.2 procedure IDs.

## Risks and Edge Cases

The highest-risk areas are size calculations, variable-length opaque data, and page-buffer placement. READ_PLUS must clip segments to the requested range and preserve EOF semantics if the server returns data beyond the requested window. GETXATTR validates the returned length against received page capacity before caching can occur. LISTXATTRS must add `user.` prefixes locally and enforce both `XATTR_NAME_MAX` and caller buffer bounds.

Network-location decoding supports only the first COPY_NOTIFY server when more than one is returned, logging a warning. `decode_write_response` validates callback-stateid array count and treats counts above one as remote I/O failure.

## Test Signals

Wire-level tests should cover sparse READ_PLUS data/hole mixes, COPY synchronous and async replies, OFFLOAD_STATUS no-completion and error-completion cases, COPY_NOTIFY with NETADDR, SEEK EOF behavior, xattr name/value boundary lengths, LISTXATTRS pagination and overflow, and malformed server lengths. RPC tracepoints plus packet capture can confirm compound op order and size accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs42xdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4_fs.h -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs4_fs.h

## Purpose

`nfs4_fs.h` is the central NFSv4 client-private header. It defines version bounds, client state flags, sequence/owner/state structures, minor-version operation tables, recovery hooks, stateid helpers, and cross-file function declarations used by NFSv4 procedure, state, namespace, client, file, idmap, xattr, and callback code.

## Important APIs, Types, and Functions

Key types include `enum nfs4_client_state`, `struct nfs4_minor_version_ops`, `struct nfs_seqid_counter`, `struct nfs_seqid`, `struct nfs4_state_owner`, `struct nfs4_lock_state`, `struct nfs4_state`, `struct nfs4_exception`, `struct nfs4_state_recovery_ops`, `struct nfs4_opendata`, `struct nfs4_sequence_slot_ops`, `struct nfs4_state_maintenance_ops`, and `struct nfs4_mig_recovery_ops`.

The header exposes procedure-layer APIs such as `nfs4_handle_exception`, `nfs4_call_sync`, `nfs4_init_sequence`, `nfs4_proc_get_rootfh`, `nfs4_proc_exchange_id`, `nfs4_proc_create_session`, `nfs4_proc_fs_locations`, `nfs4_proc_secinfo`, `nfs4_set_rw_stateid`, `nfs4_bitmask_set`, and state/recovery helpers. It also declares `nfs4_xattr_cache_*` functions under `CONFIG_NFS_V4_2`.

Inline helpers cover machine-credential state protection (`nfs4_state_protect`, `nfs4_state_protect_write`), pNFS data-server detection, stateid copy/match/newer/next checks, stateid sequence increment, and valid-open-state tests.

## Control Flow

As a header, it does not own a runtime control loop. Instead, it defines contracts used across the NFSv4 client: procedure code fills `nfs4_exception` and calls `nfs4_handle_exception`; state code maintains `nfs4_state` and `nfs4_state_owner`; client code invokes minor-version ops; and RPC code uses sequence slots and state protection wrappers before calls.

The minor-version operations table is a key dispatch point. It abstracts NFSv4.0 versus v4.1/v4.2 differences for initialization, shutdown, sequence slots, lease renewal, migration recovery, stateid matching, and root security discovery.

## State and Persistence Behavior

The header describes in-memory state that persists for the life of mounts, opens, locks, delegations, sessions, and recovery episodes. `nfs4_state` tracks open/lock stateids, open mode reference counts, delegation/open flags, and wait queues. `nfs4_state_owner` and `nfs_seqid_counter` enforce ordered once-only open/lock owner semantics. Client state bits schedule recovery and lease actions.

No local durable storage is defined here, but these structures represent server-side state that must be recovered after reboot, lease expiry, migration, session reset, delegation expiry, or stateid errors.

## Dependencies and Integration Points

The header includes Linux seqlock and file-lock primitives and is included by many NFSv4 implementation files. It connects `nfs4client.c`, `nfs4proc.c`, `nfs4state.c`, `nfs4renewd.c`, `nfs4namespace.c`, `nfs42proc.c`, `nfs42xattr.c`, and XDR/procedure code. It also exposes sysctl/module parameters such as idmapping disable flags, session slot limits, lost-lock recovery, and client ID uniquifier.

## Risks and Edge Cases

Because this header defines shared contracts, risks are ABI-like within the kernel module: state flag misuse, stale stateid comparison errors, incorrect machine-credential protection, or minor-version dispatch mismatches can break recovery and data consistency across many files. Stateid helpers must respect NFSv4 sequence wrap rules and special zero/current/invalid stateids.

The `CONFIG_NFS_V4` and `CONFIG_NFS_V4_2` guards are important: non-v4 builds replace some helpers with no-ops, and xattr cache APIs only exist for v4.2.

## Test Signals

Test signals are indirect: NFSv4.0 and v4.1/v4.2 mount/open/lock/recovery tests, session reset, delegation return, pNFS migration, stateid wrap behavior, machine credential cleanup/write paths, and xattr cache build coverage under `CONFIG_NFS_V4_2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4client.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs4client.c

## Purpose

`nfs4client.c` manages NFSv4 client and server objects: allocation, initialization, callback setup, session setup/shutdown, trunking discovery, pNFS data-server clients, referral server creation, mount server creation, size negotiation, and transport migration.

## Important APIs, Types, and Functions

Important public functions include `nfs4_alloc_client`, `nfs4_init_client`, `nfs41_init_client`, `nfs41_shutdown_client`, `nfs4_free_client`, `nfs4_match_client`, `nfs4_detect_session_trunking`, `nfs41_walk_client_list`, `nfs4_find_client_ident`, `nfs4_find_client_sessionid`, `nfs4_set_ds_client`, `nfs4_find_or_create_ds_client`, `nfs4_session_limit_rwsize`, `nfs4_session_limit_xasize`, `nfs4_create_server`, `nfs4_create_referral_server`, and `nfs4_update_server`.

`struct nfs4_ds_server` records per-auth-flavor RPC clients for pNFS data servers. Client initialization uses `struct nfs_client_initdata`; server creation uses `struct fs_context` and `struct nfs_fs_context`.

## Control Flow

`nfs4_alloc_client` starts with generic `nfs_alloc_client`, validates minor version bounds, initializes locks/lists/workqueues/client state, creates an RPC client preferring krb5i and falling back to AUTH_UNIX on invalid auth setup, derives a callback IP address if needed, creates idmapping state, and marks the idmap resource bit.

`nfs4_init_client` skips already-ready clients, runs minor-version-specific initialization, starts callbacks, performs server trunking discovery, and may replace a newly allocated client with an existing trunk-compatible one. If an existing client wins, the new client is marked unusable and released while the old client is returned.

Mount server creation flows through `nfs4_create_server` -> `nfs4_init_server` -> `nfs4_set_client` -> `nfs_init_server_rpcclient` -> `nfs4_server_common_setup`. Common setup allocates delegation hashes, rejects data-server-only clients as mount servers, initializes sessions, gets the root filehandle, probes server capabilities, limits negotiated read/write/xattr sizes, inserts the server into global lists, and installs a destroy callback.

Referral creation inherits user data from the parent server, tries RDMA where configured, then TCP or TCP-TLS based on parent security, and runs common setup. Transport migration uses `rpc_switch_client_transport`, computes a local callback address, temporarily removes the server from lists, attaches a new client with migration flags, drops the old client, reinserts lists, and reprobes the server.

## State and Persistence Behavior

This file creates and tears down long-lived in-memory `nfs_client` and `nfs_server` state. It maintains callback IDs, session pointers, pNFS data-server RPC clients, pending callback copy state, idmap resources, sysfs links, delegation hash tables, owner/trunking identity fields, and mount-time metadata. It also updates capability-derived I/O sizes and xattr size limits based on session channel attributes.

No durable client database is written here; server identity, client IDs, and sessions are negotiated with the server and recovered/recreated as needed.

## Dependencies and Integration Points

Dependencies include SUNRPC transports/auth/backchannel, rpc_pipefs, NFS callback service, NFS idmapping, pNFS, NFS sysfs, TLS/RDMA transport options, and generic NFS client/server allocation helpers. `nfs4super.c` and `nfs4proc.c` call these functions through the NFS subversion/procedure operation tables. pNFS layout drivers use `nfs4_set_ds_client` and `nfs4_find_or_create_ds_client` for data-server I/O.

## Risks and Edge Cases

Client matching/trunking is subtle: code waits for initializing clients before trusting IDs, compares client IDs, owner IDs, server owner major/minor IDs, and server scope, and must avoid loops when a server would attach to itself. Callback setup differs for v4.0 and v4.1+ sessions. pNFS data-server auth flavor cloning must avoid duplicate per-flavor clients under concurrency.

Size limiting subtracts XDR overhead from negotiated channel attributes; underflow or stale overhead constants would incorrectly cap read/write/xattr sizes. Transport migration has a quiescence requirement documented in comments and can leave the server on the old lists if reattachment fails.

## Test Signals

Tests should cover v4.0 and v4.1/v4.2 mounts, callback lookup by cb_ident/sessionid, session trunking with multiple addresses, referrals, migration, pNFS data-server access with matching MDS auth flavors, TCP/TCP-TLS/RDMA selection, nconnect/max_connect behavior, negotiated xattr size caps, and cleanup paths on failed client initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4file.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs4file.c

## Purpose

`nfs4file.c` defines NFSv4 VFS file operations and adapts Linux file operations such as open, flush, copy_file_range, llseek, fallocate, remap_file_range, leases, and server-side-copy helper hooks to NFSv4/NFSv4.2 procedure code.

## Important APIs, Types, and Functions

The primary exported object is `const struct file_operations nfs4_file_operations`. Core functions are `nfs4_file_open`, `nfs4_file_flush`, `nfs4_copy_file_range`, `nfs4_file_llseek`, `nfs42_fallocate`, `nfs42_remap_file_range`, `nfs42_ssc_register_ops`, and `nfs42_ssc_unregister_ops`. Under `CONFIG_NFS_V4_2`, this file calls `nfs42_proc_copy_notify`, `nfs42_proc_copy`, `nfs42_proc_llseek`, `nfs42_proc_deallocate`, `nfs42_proc_zero_range`, `nfs42_proc_allocate`, and `nfs42_proc_clone`.

The server-side-copy support uses `struct nfs4_ssc_client_ops` with `__nfs42_ssc_open` and `__nfs42_ssc_close` to fabricate a read-only file and NFS open context from a server-provided filehandle/stateid.

## Control Flow

`nfs4_file_open` handles cached positive dentries by allocating an NFS open context, preparing truncation attributes if `O_TRUNC`, calling the protocol `open_context`, rejecting stale lookup results by dropping the dentry and returning `-EOPENSTALE`, then attaching the open context and enabling direct I/O capability.

`nfs4_file_flush` is write-only sensitive. If no write delegation requires flush-on-close, it starts writeback and returns; otherwise it writes back all dirty data and checks writeback errors sampled before the flush.

For NFSv4.2, `nfs4_copy_file_range` first tries server-side copy. It rejects non-NFSv4 input, missing COPY capability, same-inode copy, and small inter-server copies. Cross-server copy performs COPY_NOTIFY before COPY. Unsupported or cross-device results fall back to `splice_copy_file_range`.

`nfs42_fallocate` accepts allocate, punch-hole keep-size, and zero-range modes for regular files and maps them to NFSv4.2 procedure calls after `inode_newsize_ok`. `nfs42_remap_file_range` maps clone/remap to `nfs42_proc_clone`, validates dedupe/advisory flags, swapfile state, clone block alignment, locks both inodes, blocks direct I/O, syncs source and destination inodes, and truncates destination page cache on success.

## State and Persistence Behavior

This file owns VFS-visible open contexts and file operation dispatch, but server-side state is created or mutated through lower procedure code. It attaches open contexts to files, initializes fscache file state, clears SSC pseudo-file state flags on close, and forces writeback or page-cache truncation before/after offloaded operations to maintain coherence.

## Dependencies and Integration Points

It depends on generic NFS read/write/mmap/fsync/lock/splice helpers, NFS delegation logic, fscache, pNFS/direct-I/O blockers, NFSv4 open/state owner helpers, and NFSv4.2 procedures. `nfs4proc.c` exposes `nfs4_file_operations` through the NFS RPC ops table, making this the VFS entry point for regular NFSv4 files.

## Risks and Edge Cases

Open must correctly distinguish stale cached dentries from valid positive dentries, especially around lookup/revalidation races. Copy and clone must not expose stale data: source dirty data is synchronized and destination cache is invalidated/truncated. Clone alignment follows `server->clone_blksize`, with the EOF exception for unaligned final ranges.

SSC pseudo-open constructs file/open/state objects manually, so leaks or incorrect state flags could affect server-side copy cleanup. `read_name_gen` is a simple static integer and only provides pseudo-file naming, not identity or synchronization.

## Test Signals

Tests should cover cached open retry via `-EOPENSTALE`, `O_TRUNC` open, close-to-open flush/writeback errors, `copy_file_range` same-server and cross-server fallback, fallocate modes and invalid modes, clone alignment/swapfile rejection, SEEK_HOLE/DATA fallback, and SSC open/close registration under NFSv4.2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4getroot.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs4getroot.c

## Purpose

`nfs4getroot.c` provides the small root-filehandle helper used during NFSv4 server setup. It retrieves the server pseudo-root filehandle, verifies it is a directory, and stores the root FSID on the `nfs_server`.

## Important APIs, Types, and Functions

The file exports `nfs4_get_rootfh(struct nfs_server *server, struct nfs_fh *mntfh, bool auth_probe)`. It allocates an `nfs_fattr`, calls `nfs4_proc_get_rootfh`, validates `NFS_ATTR_FATTR_TYPE` and `S_ISDIR(fattr->mode)`, copies `fattr->fsid` into `server->fsid`, and frees the attribute object.

## Control Flow

The control flow is linear: allocate fattr, call the NFSv4 procedure layer, return the negative RPC/procedure error if lookup fails, reject non-directory or missing-type results with `-ENOTDIR`, copy FSID on success, and release the fattr in all cases.

## State and Persistence Behavior

The only state mutation is `server->fsid`, an in-memory identity field used by the mounted `nfs_server`. The remote filehandle and attributes come from the server; nothing is persisted locally.

## Dependencies and Integration Points

`nfs4_server_common_setup` in `nfs4client.c` calls this before probing server capabilities and inserting the server into global lists. It depends on `nfs_alloc_fattr`, `nfs_free_fattr`, `nfs4_proc_get_rootfh`, and standard inode mode helpers.

## Risks and Edge Cases

The main risk is accepting a malformed root response. The helper requires a valid type attribute and a directory mode. Allocation failure returns `-ENOMEM`; procedure failure is logged with `dprintk`.

## Test Signals

Mount tests should cover a normal NFSv4 pseudo-root, auth probing, server errors from rootfh lookup, missing/invalid type attributes, and a server returning a non-directory root filehandle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4getroot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4idmap.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs4idmap.c

## Purpose

`nfs4idmap.c` maps between NFSv4 owner/group strings and Linux kuid/kgid values. It uses the kernel keyring id resolver, supports a legacy rpc_pipefs upcall path, handles user namespaces, maps numeric strings directly when possible, and provides helpers to map/free owner/group strings embedded in NFS file attributes.

## Important APIs, Types, and Functions

Public APIs include `nfs_idmap_init`, `nfs_idmap_quit`, `nfs_idmap_new`, `nfs_idmap_delete`, `nfs_fattr_init_names`, `nfs_fattr_free_names`, `nfs_fattr_map_and_free_names`, `nfs_map_string_to_numeric`, `nfs_map_name_to_uid`, `nfs_map_group_to_gid`, `nfs_map_uid_to_name`, and `nfs_map_gid_to_group`.

Important internal types are `struct idmap`, containing the rpc_pipefs object, pipe data, in-flight legacy upcall, mutex, and user namespace, and `struct idmap_legacy_upcalldata`, containing a pipe message, idmap message, auth key, and idmap pointer. The file registers key types `id_resolver` and `id_legacy`.

## Control Flow

Module initialization creates kernel credentials with a `.id_resolver` thread keyring, registers the modern and legacy key types, and stores credentials in `id_resolver_cache`. Per-client setup allocates `struct idmap`, records the RPC credential's user namespace, creates rpc_pipefs pipe data, registers a pipe directory object, and attaches it to `clp->cl_idmap`.

Name-to-ID mapping first accepts numeric strings without `@` via `nfs_map_string_to_numeric`. Otherwise it builds a key description like `uid:name` or `gid:name`, requests `id_resolver`, and falls back to `id_legacy` under `idmap_mutex`. ID-to-name mapping requests `user:id` or `group:id` unless `NFS_CAP_UIDGID_NOMAP` is set, then falls back to decimal numeric strings.

Legacy upcalls prepare an `idmap_msg`, store one in-flight upcall on the idmap, queue it to rpc_pipefs, and complete the key construction when userspace writes back a matching downcall. The downcall validates message size, status, name length, conversion type, ID/name match, instantiates the target key, and applies `nfs_idmap_cache_timeout`.

## State and Persistence Behavior

The id resolver keyring caches mapping results for `nfs_idmap_cache_timeout` seconds. Each `nfs_client` owns an `idmap` object and user namespace reference. At the attribute level, decoded owner/group strings live in `nfs_fattr` until mapped and freed; successful mapping sets numeric UID/GID validity bits.

No mapping database is persisted by this code. Persistent policy lives in userspace resolvers and kernel key cache entries.

## Dependencies and Integration Points

The file depends on Linux keyrings, request-key auth, rpc_pipefs, net namespaces, user namespaces, NFS tracepoints, and NFS attribute structures. `nfs4client.c` creates/deletes per-client idmaps. `nfs4xdr.c` calls mapping functions while encoding setattr owner/group and decoding owner/group attributes. `nfs4super.c` initializes and quits the idmap subsystem.

## Risks and Edge Cases

Concurrency is deliberately restricted in the legacy path: only one `idmap_upcall_data` can be in flight per idmap, protected by `idmap_mutex` and `xchg/cmpxchg` cleanup. Downcalls must match the outstanding request to prevent wrong key instantiation. User namespace conversion can fail with invalid kuid/kgid and returns `-ERANGE`.

Security-sensitive areas include key permissions, root invalidation flags, using kernel credentials for request_key, and validating userspace pipe data. Numeric owner strings without domains bypass userspace mapping.

## Test Signals

Tests should cover numeric owner/group strings, domain-qualified names through request-key, legacy rpc_pipefs upcalls/downcalls, failed downcalls, cache timeout behavior, user namespace ID validity, `NFS_CAP_UIDGID_NOMAP` fallback, module init/quit cleanup, and xdr owner/group encode/decode integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4idmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4idmap.h -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs4idmap.h

## Purpose

`nfs4idmap.h` declares the NFSv4 ID mapping interface shared by client setup, XDR attribute encoding/decoding, and file-attribute postprocessing. It keeps the mapping API independent via forward declarations for NFS client/server/fattr/string structures.

## Important APIs, Types, and Functions

The header declares subsystem lifecycle functions `nfs_idmap_init` and `nfs_idmap_quit`, per-client lifecycle functions `nfs_idmap_new` and `nfs_idmap_delete`, fattr owner/group string helpers `nfs_fattr_init_names`, `nfs_fattr_free_names`, and `nfs_fattr_map_and_free_names`, mapping calls `nfs_map_name_to_uid`, `nfs_map_group_to_gid`, `nfs_map_uid_to_name`, `nfs_map_gid_to_group`, numeric parser `nfs_map_string_to_numeric`, and external cache timeout `nfs_idmap_cache_timeout`.

## Control Flow

The header defines no runtime control flow. It establishes call boundaries: client/module lifecycle code owns idmap initialization and cleanup; XDR and attribute code call the mapping functions; fattr decode paths initialize owner/group string storage then map and free it after decoding.

## State and Persistence Behavior

State is opaque to the header. Implementations maintain keyring caches, per-client idmap objects, user namespace references, and temporary fattr strings. `nfs_idmap_cache_timeout` controls key cache lifetime and is exposed as a module/sysctl parameter elsewhere.

## Dependencies and Integration Points

It includes `linux/uidgid.h` and `uapi/linux/nfs_idmap.h`, and is consumed by `nfs4client.c`, `nfs4idmap.c`, `nfs4xdr.c`, and NFSv4 super/sysctl code. The API is NFSv4-specific but supports generic Linux kuid/kgid types.

## Risks and Edge Cases

The header's main risk is contract mismatch: callers must pass valid server/client idmap context and must free mapped owner/group strings exactly once. Numeric parsing returns a boolean success indicator rather than errno, so callers must preserve that convention.

## Test Signals

Build coverage under NFSv4, owner/group encode/decode tests, idmap module parameter tests, and fattr mapping/freeing paths validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4idmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4namespace.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs4namespace.c

## Purpose

`nfs4namespace.c` implements NFSv4 namespace-specific behavior: converting NFSv4 path components to POSIX paths, validating fs_locations referrals, negotiating security on WRONGSEC, following referrals by trying returned server locations, parsing server names, handling submounts, and replacing transports during filesystem migration.

## Important APIs, Types, and Functions

Public functions are `nfs_parse_server_name`, `nfs4_negotiate_security`, `nfs4_submount`, and `nfs4_replace_transport`. Internal helpers include `nfs4_pathname_len`, `nfs4_pathname_string`, `nfs_path_component`, `nfs4_path`, `nfs4_validate_fspath`, `nfs_find_best_sec`, `try_location`, `nfs_follow_referral`, `nfs_do_refmount`, and `nfs4_try_replacing_one_location`.

## Control Flow

Referral handling starts in `nfs4_submount`. The code re-lookups the mountpoint with `nfs4_proc_lookup_mountpoint` to obtain attributes and selected security flavor. If the attributes indicate an NFSv4 referral, `nfs_do_refmount` fetches `fs_locations`, validates that the server-provided `fs_root` is a prefix of the current dentry path, then iterates locations and their server lists. `try_location` updates the fs_context hostname/export path/source, parses a server address, sets the NFS port, and calls `nfs4_get_referral_tree` until one succeeds.

Security negotiation uses `nfs4_proc_secinfo` to fetch server-supported flavors for a lookup name, then searches them in server-returned order for a locally supported flavor allowed by the mount's `sec=` list. Candidate RPC clients are cloned with that auth flavor and tested by looking up credentials.

Transport replacement for migration iterates fs_locations, parses server addresses, duplicates hostnames, and calls `nfs4_update_server` for the first usable location. Name parsing tries numeric presentation format, universal address format, and DNS resolution, and optionally applies a port to numeric addresses.

## State and Persistence Behavior

Most mutations are to transient `fs_context` fields while preparing referral mounts: hostname, export path, source string, address, and selected flavor. Migration mutates the live `nfs_server` indirectly through `nfs4_update_server`, replacing its transport/client association. There is no durable local namespace state.

## Dependencies and Integration Points

The file depends on VFS dentry/mount/fs_context structures, SUNRPC client/auth/address helpers, NFS DNS resolution, NFSv4 procedure calls for SECINFO/FS_LOCATIONS/LOOKUP mountpoints, and `nfs4client.c` server update/referral creation paths. `nfs4proc.c` wires `nfs4_submount` into NFSv4 inode operations.

## Risks and Edge Cases

Path validation prevents following referrals whose `fs_root` does not prefix the current mounted path, but it depends on correct path rendering and length checks. IPv6 scoped addresses containing a scope delimiter are skipped. `nfs_find_best_sec` must shut down cloned RPC clients when credential setup fails. Referral iteration overwrites fs_context strings as it tries locations, so allocation failures and partial updates need careful cleanup by the mount context owner.

Migration transport replacement assumes the server is quiescent, as documented in `nfs4_update_server`. DNS and universal-address parsing failures are treated as unusable locations rather than fatal until all options are exhausted.

## Test Signals

Tests should cover referrals with multiple locations/servers, invalid fs_root prefixes, DNS and IPv6 literal parsing, secinfo negotiation with mount `sec=` filtering, WRONGSEC recovery, submounts without referral attributes, migration to a new address, failed cloned auth credentials, and exhausted fs_locations returning `-ENOENT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4namespace.c -->
