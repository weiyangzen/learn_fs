# Group Research:

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/connect.c -->
# File Research: sources/os/linux/linux/fs/smb/client/connect.c

## Purpose
Implements the CIFS/SMB client connection, session, tree-connect, mount, reconnect, socket receive, and per-superblock tcon-link lifecycle machinery. This is the central transport/session orchestration file for SMB mounts.

## Main Interfaces
- TCP/session lifecycle: `cifs_get_tcp_session()`, `cifs_put_tcp_session()`, `cifs_find_tcp_session()`.
- SMB session lifecycle: `cifs_get_smb_ses()`, `__cifs_put_smb_ses()`, `cifs_setup_session()`, `cifs_setup_ipc()`.
- Tree connection lifecycle: `cifs_mount_get_tcon()`, `cifs_put_tcon()`, `cifs_tree_connect()` in non-DFS builds.
- Mount/unmount: `cifs_setup_cifs_sb()`, `cifs_mount()`, `cifs_umount()`, `cifs_mount_put_conns()`.
- Reconnect: `cifs_reconnect()`, `cifs_signal_cifsd_for_reconnect()`, `cifs_mark_tcp_ses_conns_for_reconnect()`.
- Receive path: `cifs_read_from_socket()`, `cifs_read_iter_from_socket()`, `cifs_discard_from_socket()`, `cifs_handle_standard()`, `dequeue_mid()`.
- Multiuser tcon resolution: `cifs_sb_tlink()`, `cifs_sb_master_tcon()`.

## Control Flow
Initial mount setup builds a `cifs_sb_info`, resolves or creates a TCP transport, negotiates protocol, creates or reuses an SMB session, and then creates or reuses a tree connection. `cifs_mount()` has separate DFS and non-DFS implementations under `CONFIG_CIFS_DFS_UPCALL`; DFS builds delegate referral traversal to `dfs_mount_share()`, while non-DFS builds directly connect session and tcon, then reject remote DFS paths if DFS upcalls are unavailable.

The demultiplex thread `cifs_demultiplex_thread()` owns socket/RDMA receive processing. It reads RFC1002 headers, validates SMB response framing, finds matching MID entries, handles transformed/encrypted responses through dialect operations, invokes callbacks, returns credits, detects server timeout statuses, and schedules reconnects when needed.

Reconnect flow marks TCP sessions, SMB sessions, channels, and tcons as needing reconnect, aborts the socket/RDMA transport, retries IP or DFS target reconnect, resets credits, transitions through `CifsNeedNegotiate`, and wakes waiters. DFS reconnect uses cached referral target lists and updates target hints after a successful target selection.

## State And Synchronization
The file coordinates several shared state machines:
- `TCP_Server_Info::tcpStatus` under `srv_lock`.
- session status and multichannel reconnect bitmaps under `ses_lock` and `chan_lock`.
- pending MIDs under `mid_queue_lock`.
- request credits under `req_lock`.
- global TCP/session/tcon lists under `cifs_tcp_ses_lock`.
- per-superblock tcon links in an rbtree under `tlink_tree_lock`.

Lifetime is reference-counted through `srv_count`, `ses_count`, `tc_count`, and `tcon_link::tl_count`. Teardown carefully cancels delayed work, wakes wait queues, drains pending MIDs, releases sockets/RDMA state, and defers superblock cleanup with RCU.

## Integration Points
- Depends on dialect-specific `server->ops` callbacks for negotiate, session setup, tree connect/disconnect, echo, open protocol checks, DFS referrals, interface query, transforms, message validation, and credit handling.
- Calls DNS helpers from `dns_resolve.h` for reconnect hostname refresh.
- Calls DFS cache and traversal helpers when `CONFIG_CIFS_DFS_UPCALL` is enabled.
- Integrates SMB Direct through `smbdirect.h`.
- Integrates witness notifications through `cifs_swn.h`.
- Integrates fscache setup through `cifs_fscache_get_super_cookie()`.

## Notable Behaviors
- Existing TCP sessions are reusable only when protocol, hostname/address/port, source address, namespace, signing/security, RDMA, echo interval, offload, retransmission, and sharing options match.
- Existing SMB sessions are reusable only when security type, credentials, domain/user identity, charset, DFS root session, and channel limits match.
- Existing tcons are reusable only when tree name or DFS origin path, encryption, snapshot time, handle timeout, lease behavior, delete semantics, and POSIX extension state match.
- RFC1002 negative session responses during negotiate can trigger a one-shot reconnect with NetBIOS session establishment.
- Multiuser mounts lazily construct per-fsuid tcons and prune idle links from the superblock rbtree.
- Multichannel setup is queued asynchronously after successful mount to avoid blocking the core mount path.

## Risks And Review Focus
- Lock ordering and refcounting are subtle across TCP/session/tcon teardown, reconnect work, demux callbacks, and multichannel references.
- Reconnect status transitions must keep MIDs, waiters, credits, channels, sessions, and tcons consistent.
- DFS failover can change target server/share and therefore disables server inode assumptions and forces prefix-path behavior.
- Socket receive error handling must avoid leaving pending MIDs without callbacks.
- Credential handling uses sensitive frees; any new password/session-key field must follow the same pattern.
- Mount reuse matching is security-sensitive because incorrect reuse can cross credentials, signing, encryption, or DFS boundaries.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/connect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/dfs.c -->
# File Research: sources/os/linux/linux/fs/smb/client/dfs.c

## Purpose
Implements DFS-aware mount traversal and DFS-aware tree reconnect logic for the CIFS/SMB client. It follows DFS referrals, connects to target shares, records origin paths for failover, and reconnects tcons to suitable DFS targets.

## Main Interfaces
- `dfs_parse_target_referral()` converts a DFS referral target into an SMB mount context.
- `dfs_mount_share()` performs DFS-aware mount setup.
- `cifs_tree_connect()` provides the DFS-enabled tree-connect implementation.

## Control Flow
`dfs_mount_share()` starts by optionally resolving the DFS root address for automounts, obtains an initial session, probes for a DFS referral unless `nodfs` is set, and either falls back to ordinary tcon setup or switches into DFS connection mode. DFS traversal uses `dfs_ref_walk` to walk nested referrals up to `MAX_NESTED_LINKS`, trying each target from the DFS cache until a session, tcon, and non-remote path check succeed.

`__dfs_mount_share()` stores the original DFS full path in `tcon->origin_fullpath`, attaches DFS root sessions to the tcon, and schedules the DFS cache refresh worker.

The DFS version of `cifs_tree_connect()` handles IPC normally, then checks whether the TCP server has a `leaf_fullpath` with a cached DFS referral. If so, it parses target shares, filters targets to those matching the current server hostname/IP, updates the DFS target hint, tree-connects to the selected share, and updates the superblock prepath for DFS links.

## State And Synchronization
- Temporarily mutates `ctx->leaf_fullpath`, `ctx->dns_dom`, and `ctx->dfs_root_ses` while obtaining sessions.
- Keeps extra references to DFS root sessions so future referrals can use IPC tcons safely.
- Stores DFS origin path under `tcon->tc_lock`.
- Uses DFS cache target hints to bias future reconnects toward recently successful targets.

## Integration Points
- Calls `dfs_cache_find()`, `dfs_cache_get_tgt_referral()`, `dfs_cache_get_tgt_share()`, and `dfs_cache_noreq_update_tgthint()`.
- Calls `dns_resolve_unc()` and `match_target_ip()` to resolve referral hostnames.
- Calls generic mount helpers from `connect.c`: `cifs_mount_get_session()`, `cifs_mount_get_tcon()`, `cifs_mount_put_conns()`, and `cifs_is_path_remote()`.
- Uses `smb3_parse_devname()` and `smb3_fs_context_fullpath()` to translate referral targets into normal mount context fields.

## Notable Behaviors
- DFS automounts resolve the root UNC before the first session setup, then clear `dfs_automount`.
- Interlink referrals can trigger descent into a nested referral path.
- DFS mounts force later reconnect behavior by setting `ctx->dfs_conn` and re-establishing the session.
- Tree reconnect prefers cached referrals but falls back to the last `tcon->tree_name` when no referral is cached.
- If DFS target prefix paths differ, `cifs_update_super_prepath()` updates the mounted prefix for link targets.

## Risks And Review Focus
- `dfs_ref_walk` cleanup and session reference ownership are critical; missed puts would leak root sessions.
- Context fields are temporarily borrowed and restored, so future changes to `smb3_fs_context` need care.
- Target matching must avoid connecting a tcon to a referral target that does not correspond to the active TCP server.
- Nested DFS traversal must preserve `-ELOOP` behavior and avoid infinite interlink loops.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/dfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/dfs.h -->
# File Research: sources/os/linux/linux/fs/smb/client/dfs.h

## Purpose
Declares DFS traversal structures, helpers, and public DFS mount interfaces used by the CIFS client when DFS upcalls are enabled.

## Main Contents
- Defines `DFS_INTERLINK(v)` to identify referrals that are referral servers but not storage servers.
- Defines `struct dfs_ref`, holding one referral path, full path, root session, target list, and current target iterator.
- Defines `struct dfs_ref_walk`, a bounded stack of referral levels for nested DFS traversal.
- Provides inline traversal helpers for allocation, initialization, cleanup, target iteration, descending/advancing, target hint updates, and tcon session-list transfer.
- Declares `dfs_parse_target_referral()` and `dfs_mount_share()`.
- Provides `dfs_get_path()` and `dfs_get_referral()` wrappers around DFS cache canonicalization and lookup.
- Provides `dfs_put_root_smb_sessions()` and `dfs_ses_refpath()`.

## Control Flow
The header models DFS walking as a small stack. Each level owns its canonical DFS path, user-visible full path, root session reference, and copied target list. `ref_walk_next_tgt()` iterates targets at the current level; `ref_walk_advance()` descends to a deeper level for interlinks; `ref_walk_descend()` backs up when a branch fails.

## State And Ownership
`__ref_walk_free()` releases owned strings, target lists, and session references. `ref_walk_set_tcon()` transfers session references from the walk into `tcon->dfs_ses_list` by linking sessions to the tcon and nulling the walk’s session pointers so cleanup will not put them.

## Integration Points
Included by `dfs.c`, `connect.c`, and DFS cache users. It depends on `dfs_cache.h`, CIFS session/tcon definitions, mount context data, and CIFS Unicode remapping helpers.

## Risks And Review Focus
- The traversal stack is bounded by `MAX_NESTED_LINKS`; changes must preserve loop protection.
- Ownership transfer in `ref_walk_set_tcon()` is easy to break because it intentionally prevents `ref_walk_free()` from putting transferred sessions.
- `dfs_get_referral()` chooses `ctx->dfs_root_ses` when available, otherwise the current mount session; this selection matters for referral IPC routing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/dfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/dfs_cache.c -->
# File Research: sources/os/linux/linux/fs/smb/client/dfs_cache.c

## Purpose
Implements the in-kernel DFS referral cache for CIFS/SMB: canonical path handling, referral lookup/fetch/update, target iteration copies, `/proc` inspection and flushing, TTL scheduling, remount refresh, and background refresh work.

## Main Interfaces
- Cache lifecycle: `dfs_cache_init()`, `dfs_cache_destroy()`.
- Lookup APIs: `dfs_cache_find()`, `dfs_cache_noreq_find()`.
- Target APIs: `dfs_cache_get_tgt_referral()`, `dfs_cache_get_tgt_share()`, `dfs_cache_noreq_update_tgthint()`.
- Path normalization: `dfs_cache_canonical_path()`.
- Refresh/remount: `dfs_cache_remount_fs()`, `dfs_cache_refresh()`.
- `/proc` operations: `dfscache_proc_ops`.

## Data Model
`struct cache_entry` stores a canonical DFS path, referral header flags, TTL, expiration time, server type, referral flags, path-consumed length, a target list, target count, and a target hint. `struct cache_dfs_tgt` stores one referral target name and its path-consumed value.

The cache is a 512-bucket hash table with a maximum of 1024 entries. Hashing and equality are case-insensitive using the cache codepage, normally UTF-8.

## Control Flow
`dfs_cache_find()` canonicalizes the caller’s path, then calls `cache_refresh_path()`. If an entry is present and fresh, it is returned under the read lock. If missing, expired, or force-refreshed, the code drops the cache lock, issues `get_dfs_refer()` over IPC, then reacquires the write lock to add or update the entry.

`lookup_cache_entry()` supports exact matching and longest component-prefix matching for link referral behavior. On success, callers can copy a single referral via `setup_referral()` and/or copy all targets into an external `dfs_cache_tgt_list`.

Background refresh walks DFS sessions attached to a tcon, refreshes their referral paths, refreshes the tcon referral, and requeues itself using the global minimum cache TTL.

## State And Synchronization
- Uses `htable_rw_lock` to protect hash table entries and target lists.
- Uses `READ_ONCE`/`WRITE_ONCE` for target-hint access.
- Uses `atomic_t cache_count` and `atomic_t dfs_cache_ttl`.
- Drops the cache lock before network referral requests to avoid reconnect/cache deadlocks.
- Uses `dfscache_wq` for delayed refresh work.

## Integration Points
- Calls dialect `get_dfs_refer()` through `ses->server->ops`.
- Uses `dns_resolve_unc()` to compare target share hosts with active TCP server addresses.
- Uses `cifs_signal_cifsd_for_reconnect()` when forced refresh shows the current tcon should move to a different DFS target.
- Uses `cifs_setup_ipc()` to ensure referral refresh has an IPC tcon.
- Uses `cifs_autodisable_serverino()` and prefix-path flags during DFS remount.

## Notable Behaviors
- TTL is clamped to at least 120 seconds, and global refresh TTL tracks the minimum observed entry TTL.
- When the cache reaches its size limit, it purges single-target referrals first, then the oldest remaining entry.
- Target hints are preserved across referral updates where possible and moved to the front of copied target lists.
- `/proc/fs/cifs/dfscache` write accepts only `0` to flush the cache.
- `dfs_cache_get_tgt_share()` merges target prefix paths with the remaining DFS referral path.

## Risks And Review Focus
- Cache entries store `refs[0].path_name` by ownership transfer; referral cleanup must not double-free it.
- Lock release around referral fetch is necessary but introduces races handled by rechecking under write lock.
- Prefix matching must stay component-aware to avoid matching partial path components.
- Target hint updates assume the cached target still exists; missing checks here could dereference unexpected state if changed carelessly.
- Refresh paths can trigger reconnects, so lock ordering with session/tcon reconnect code is important.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/dfs_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/dfs_cache.h -->
# File Research: sources/os/linux/linux/fs/smb/client/dfs_cache.h

## Purpose
Declares the DFS cache public API, target-list structures, workqueue/TTL globals, and inline target-list utilities.

## Main Contents
- Exposes `dfscache_wq` and `dfs_cache_ttl`.
- Defines `DFS_CACHE_TGT_LIST_INIT()` and `DFS_CACHE_TGT_LIST()` stack helpers.
- Defines `struct dfs_cache_tgt_list` and `struct dfs_cache_tgt_iterator`.
- Declares cache lifecycle, lookup, target parsing, canonicalization, remount, refresh, and proc operation interfaces.
- Provides inline helpers to get the first/next target, free copied target lists, get target names, count targets, and read TTL.

## Integration Points
Used by `dfs.c`, `dfs.h`, `dfs_cache.c`, and DFS reconnect logic in `connect.c`. The target-list API intentionally copies cache data so callers can iterate without holding cache internals longer than needed.

## Risks And Review Focus
- `dfs_cache_free_tgts()` relies on `tl_numtgts` and list state being initialized correctly.
- Callers must treat `dfs_cache_tgt_iterator` names as owned by the copied target list and not by the cache.
- The TTL helper returns the global atomic value, which is a cache-wide scheduling hint rather than a per-entry TTL.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/dfs_cache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/dir.c -->
# File Research: sources/os/linux/linux/fs/smb/client/dir.c

## Purpose
Implements CIFS/SMB VFS dentry and directory-name operations: path construction, lookup, create, atomic open, mknod, tmpfile creation, negative dentry revalidation, case-insensitive dentry hashing/comparison, and silly-rename path generation.

## Main Interfaces
- Path builders: `cifs_build_path_to_root()`, `build_path_from_dentry()`, `build_path_from_dentry_optional_prefix()`, `__build_path_from_dentry_optional_prefix()`.
- Create/open: `cifs_atomic_open()`, `cifs_create()`, `cifs_tmpfile()`.
- Lookup and node creation: `cifs_lookup()`, `cifs_mknod()`.
- Dentry operations: `cifs_dentry_ops`, `cifs_ci_dentry_ops`.
- Misc path helper: `cifs_silly_fullpath()`.

## Control Flow
Path builders combine raw dentry paths with optional superblock prepaths and optional DFS tree-name prefixes, converting separators according to mount flags. `check_name()` rejects overly long path components and disallows backslashes when POSIX paths are not enabled.

Create/open flows use `cifs_sb_tlink()` to obtain the right tcon, generate lease keys when supported, record pending opens, and call `__cifs_do_create()`. That helper tries legacy POSIX open when enabled and applicable, otherwise uses dialect `open()` with SMB create options, requested access, create disposition, optional parent lease key, fscache read-for-write behavior, and mode handling. It then queries inode information and validates the resulting inode type.

Lookup builds the full path and queries inode metadata using POSIX, Unix, or normal CIFS inode-info paths depending on negotiated extension support. Negative dentry handling can rely on a fully cached parent directory when case-insensitive lookup is forced.

`cifs_tmpfile()` creates a hidden temporary SMB2+ file with delete-on-close semantics, gives it a generated name, instantiates an unhashed dentry, and marks temporary/hidden attributes.

## State And Synchronization
- Uses tcon links from the superblock to support multiuser mounts.
- Uses pending-open tracking around network creates.
- Updates parental dentry timestamp caches after successful lookups.
- Dentry revalidation may force inode revalidation by clearing `CIFS_I(inode)->time`.
- Case-insensitive dentry ops hash and compare via the mount codepage and `cifs_toupper()`.

## Integration Points
- Calls dialect operations for open, close, make-node, set-file-info, and lease-key handling.
- Uses inode metadata helpers from the CIFS client for Unix, POSIX SMB3.11, and normal SMB queries.
- Uses fscache helpers to request and invalidate cache state.
- Uses cached directory handles from `cached_dir.h` for negative lookup optimization and parent lease keys.
- Uses DFS automount flagging through `cifs_d_automount` in dentry ops.

## Notable Behaviors
- Write-only opens may request read access when fscache is enabled so partial writes can fill cache gaps; if access is denied, the code retries without read and invalidates cache.
- `O_TMPFILE` is supported only for SMB2 and later.
- Parent directory cached handles can supply parent lease keys to SMB2 create and are invalidated before use.
- Dentry revalidation sets `DCACHE_NEED_AUTOMOUNT` if refreshed inode attributes reveal an automount/DFS entry.
- Negative dentries are dropped for create and rename-target lookups to preserve caller spelling and case semantics.

## Risks And Review Focus
- Path construction is sensitive to DFS prefixing, prepath ownership, POSIX path flags, and separator conversion.
- Create error paths must close remote handles, remove pending opens, release tlinks, and free open info exactly once.
- Cached-directory negative lookup assumptions depend on mount case-sensitivity behavior.
- Temporary and silly names use bounded retry loops; failure handling must preserve VFS expectations for unhashed or negative dentries.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/dns_resolve.c -->
# File Research: sources/os/linux/linux/fs/smb/client/dns_resolve.c

## Purpose
Implements CIFS DNS resolver upcalls for converting SMB/DFS hostnames to socket addresses.

## Main Interfaces
- `dns_resolve_name()` resolves a hostname or address string into `struct sockaddr`.

## Control Flow
`dns_resolve_name()` first validates inputs and tries `cifs_convert_address()` so numeric IPv4/IPv6 addresses skip DNS upcall. If the name appears to be NetBIOS-style and a DNS domain is supplied, it constructs `name.domain` and tries that first. If that fails or does not apply, it calls `resolve_name()` on the original name.

`resolve_name()` uses `dns_query()` in the current network namespace, then converts the returned string IP address into a socket address with `cifs_convert_address()`.

## State And Synchronization
The file is stateless. It allocates temporary strings for FQDN construction and for the DNS resolver result, freeing both before return.

## Integration Points
- Used by DFS mount/referral logic and reconnect hostname refresh.
- Depends on the kernel DNS resolver key/upcall infrastructure.
- Uses CIFS address parsing and NetBIOS-name helpers from `cifsproto.h`.

## Risks And Review Focus
- DNS upcall failures propagate as negative errno values and can affect DFS mount/reconnect failover.
- FQDN construction length is bounded by `CIFS_MAX_DOMAINNAME_LEN`; changes to domain handling should preserve this bound.
- The function treats failed numeric conversion as a signal to try DNS, but failed DNS result is terminal.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/dns_resolve.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/dns_resolve.h -->
# File Research: sources/os/linux/linux/fs/smb/client/dns_resolve.h

## Purpose
Declares CIFS DNS resolver helpers for hostname and UNC resolution.

## Main Contents
- Declares `dns_resolve_name()`.
- Defines inline `dns_resolve_unc()`, which extracts the hostname from a UNC path and resolves it.

## Integration Points
Included by DFS cache, DFS mount, and connection reconnect code. `dns_resolve_unc()` depends on `extract_unc_hostname()` to parse the server component from a UNC string before delegating to `dns_resolve_name()`.

## Risks And Review Focus
- `dns_resolve_unc()` rejects UNC strings shorter than three characters or without a hostname.
- Callers must pass a writable `struct sockaddr` storage area large enough for IPv4 or IPv6 results.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/dns_resolve.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/export.c -->
# File Research: sources/os/linux/linux/fs/smb/client/export.c

## Purpose
Provides CIFS hooks for exportfs/NFSD export support when `CONFIG_CIFS_NFSD_EXPORT` is enabled.

## Main Interfaces
- Defines `cifs_export_ops` under `CONFIG_CIFS_NFSD_EXPORT`.
- Uses `generic_encode_ino32_fh` for file-handle encoding.
- Provides stub `cifs_get_parent()`.

## Control Flow
The only implemented parent lookup function logs a debug message and returns `-EACCES`. The comments explain that full NFS export support would require mandatory export operations such as `fh_to_dentry`, and that CIFS exports require an explicit `fsid` plus stable server inode numbers via `serverino`.

## Integration Points
Included by CIFS filesystem registration code when export support is configured. Relies on Linux exportfs helpers and CIFS inode/debug definitions.

## Risks And Review Focus
- Export support is incomplete: `get_parent()` denies access and `fh_to_dentry` is not implemented here.
- The current encoder is 32-bit inode based even though CIFS/server inode numbers may be 64-bit; comments note this could be improved.
- CIFS-as-NFS-export correctness depends on stable server inode numbers and explicit export `fsid`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/export.c -->