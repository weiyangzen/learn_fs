# Group Research: group_1072_linux_stable_sources_os_linux_linux_stable_fs_smb_client_connect_c__1c248795fabf

Scope: `Docs/research_subset_a`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/connect.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/connect.c

This file is the CIFS/SMB client connection orchestrator. It owns TCP session lifecycle, SMB session setup, tree connection setup, reconnect/failover, demultiplexing inbound SMB PDUs, superblock reuse matching, multiuser tcon links, mount/umount connection plumbing, socket creation, NetBIOS session setup, and protocol/session negotiation.

Main responsibilities:
- Maintains `TCP_Server_Info` state transitions across `CifsNew`, `CifsNeedNegotiate`, `CifsGood`, `CifsNeedReconnect`, and `CifsExiting`.
- Starts and stops the `cifsd` demultiplex thread via `cifs_get_tcp_session()` and `cifs_put_tcp_session()`.
- Reads SMB frames from sockets or SMB Direct, dispatches responses to matching MIDs, handles compound responses, oplock breaks, malformed PDUs, SMB transform headers, and credit updates.
- Implements reconnect paths through `cifs_reconnect()`, `cifs_reconnect_once()`, `cifs_signal_cifsd_for_reconnect()`, and `cifs_mark_tcp_ses_conns_for_reconnect()`.
- Under `CONFIG_CIFS_DFS_UPCALL`, reconnect can fail over across cached DFS targets using `reconnect_dfs_server()` and target hints.
- Matches and reuses TCP sessions, SMB sessions, tree connections, and superblocks only when transport, namespace, security, dialect, signing, user credentials, mount flags, prepath, and tree options are compatible.
- Creates IPC tcons for session-level operations and ordinary tcons for mounted shares.
- Handles SMB3 features during tcon setup: encryption, persistent/resilient handles, POSIX extensions, directory leasing, witness, fscache cookies, and multichannel interface polling.
- Builds mount context flows through `cifs_mount_get_session()`, `cifs_mount_get_tcon()`, and `cifs_mount()`.
- Manages multiuser `tcon_link` objects in a per-superblock red-black tree and prunes idle links.

Important flows:
- Initial mount: `cifs_setup_cifs_sb()` loads NLS and mount flags, `cifs_mount()` obtains server/session/tcon, checks DFS remoteness when appropriate, installs the master tlink, and schedules multichannel work if requested.
- TCP connect: `ip_connect()` tries port 445 first if no port is set, then port 139; `generic_ip_connect()` creates/binds/connects the socket and optionally runs `ip_rfc1001_connect()`.
- Receive path: `cifs_demultiplex_thread()` allocates buffers, reads RFC1002 headers, validates SMB response type, reads to MID, finds MID handlers, handles transformed responses, dispatches callbacks, and reconnects after repeated I/O timeouts.
- Reconnect: socket teardown marks submitted MIDs retryable, resets credits/session keys, marks affected sessions and tcons for reconnect, reconnects transport, then wakes waiters and schedules negotiation.
- Session setup: `cifs_get_smb_ses()` reuses compatible sessions or allocates a new one, negotiates protocol, performs session setup, supports alternate password retry, stores channel signing keys, and creates IPC.
- Tree setup: `cifs_get_tcon()` reuses compatible tcons or performs tree connect and applies share/mount options.

Concurrency and lifetime:
- Uses `cifs_tcp_ses_lock`, per-server `srv_lock`, per-session `ses_lock`/`chan_lock`, per-tcon `tc_lock`, MID queue locks, and workqueue cancellation to serialize state changes.
- Reference counts exist at each layer: server `srv_count`, session `ses_count`, tcon `tc_count`, and tlink `tl_count`.
- Demux cleanup wakes blocked requests and callbacks before freeing server memory.
- Multiuser tlink construction uses `TCON_LINK_PENDING` and `wait_on_bit()` to avoid duplicate per-UID tcon construction.

External dependencies:
- Calls dialect-specific operations through `server->ops`.
- Uses DFS helpers from `dfs.c`/`dfs_cache.c` when DFS upcall support is enabled.
- Uses DNS resolver helpers for reconnect hostname refresh.
- Uses SMB Direct helpers when RDMA is enabled.
- Integrates witness notifications, fscache, multichannel, keyring credentials, and optional legacy CIFS Unix extensions.

Research notes:
- This file is the central connection state machine for the SMB client.
- Reuse matching is deliberately conservative; small option differences prevent unsafe sharing.
- DFS support changes both mount and reconnect semantics because a logical path may reconnect to a different server/share.
- Error handling frequently converts transport loss into reconnect signals and MID callbacks rather than returning raw socket state to callers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/connect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/dfs.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/dfs.c

This file implements DFS-aware mount and tree-connect logic for the CIFS/SMB client when `CONFIG_CIFS_DFS_UPCALL` is enabled. It parses DFS referrals, walks nested DFS links, selects targets, updates mount context addressing, and performs DFS target tree connects.

Main responsibilities:
- Converts DFS referral targets into mount context data via `dfs_parse_target_referral()`.
- Resolves target hostnames with `dns_resolve_unc()`.
- Tracks a DFS root SMB session so later referrals can be requested through a valid IPC tcon.
- Walks referral chains with `dfs_ref_walk`, including nested interlinks up to `MAX_NESTED_LINKS`.
- Distinguishes non-DFS mounts from DFS mounts by probing referrals unless `nodfs` is set.
- Rebuilds session/tcon state when a DFS referral target changes the effective server/share.
- Stores `origin_fullpath` on DFS tcons and schedules periodic DFS cache refresh work.
- Implements DFS-aware `cifs_tree_connect()` that can tree-connect to a cached DFS target matching the current TCP session.

Important flows:
- `dfs_mount_share()` first resolves automount root destination when needed, obtains an initial session, probes for referral, and either falls back to ordinary tcon setup or switches into DFS connection mode.
- `__dfs_mount_share()` obtains a canonical origin path, walks referrals, verifies required server/session/tcon pointers, stores DFS origin metadata, and schedules `dfs_cache_work`.
- `__dfs_referral_walk()` iterates targets, parses each target into `ctx`, reconnects session/tcon, checks whether the resulting path is remote, and descends into interlinks when needed.
- DFS tree reconnect uses `tree_connect_dfs_target()` to parse target share/prefix, check whether target host matches the current server, update target hints, and issue the dialect `tree_connect`.

Concurrency and lifetime:
- DFS root session references are explicitly incremented during mount and transferred to `tcon->dfs_ses_list` once the final tcon is known.
- Connection references are released between target attempts with `cifs_mount_put_conns()`.
- `tcon->tc_lock` protects `origin_fullpath` updates.

External dependencies:
- Uses `dfs_cache_find()`, `dfs_cache_noreq_find()`, target iterators, and target hint updates from `dfs_cache.c`.
- Uses core mount helpers from `connect.c`.
- Uses DNS resolution from `dns_resolve.c`.

Research notes:
- The file is the bridge between logical DFS namespace traversal and normal CIFS mount/session/tcon construction.
- DFS interlinks are handled by descending the referral walk stack and restarting target iteration with a new referral path.
- DFS mounts force prefix-path handling and serverino auto-disable in `connect.c` after successful DFS connection.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/dfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/dfs.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/dfs.h

This header defines DFS referral-walk structures and inline helpers used by `dfs.c` and DFS-enabled connection paths.

Main contents:
- `DFS_INTERLINK(v)` identifies referrals that point to another DFS namespace link rather than a storage server.
- `struct dfs_ref` stores one referral-walk level: canonical path, full path, root session reference, target list, and current target iterator.
- `struct dfs_ref_walk` stores the active mount context and a fixed `MAX_NESTED_LINKS` stack of `dfs_ref` entries.
- Inline accessors and helpers manage referral-walk start/current/end positions, target iteration, target hint updates, descent, cleanup, and tcon session transfer.

Important helpers:
- `ref_walk_alloc()`/`ref_walk_init()` allocate and initialize a walk.
- `ref_walk_free()` frees all paths, target lists, and retained SMB sessions.
- `ref_walk_advance()` moves deeper into nested DFS referrals and returns `-ELOOP` if nesting exceeds the fixed stack.
- `ref_walk_next_tgt()` iterates targets and marks end-of-list with an `ERR_PTR(-ENOENT)` sentinel.
- `ref_walk_get_tgt()` converts the current target iterator into a `dfs_info3_param`.
- `ref_walk_set_tcon()` moves retained DFS root session references onto the final tcon’s `dfs_ses_list`.
- `dfs_get_path()` canonicalizes a path through the DFS cache helper.
- `dfs_get_referral()` fetches or refreshes a referral using the DFS root session when available.
- `dfs_put_root_smb_sessions()` releases root-session references stored on a list.
- `dfs_ses_refpath()` returns the canonical referral path for a DFS session.

Research notes:
- This header encodes DFS mount traversal state as a bounded stack, which is important for loop prevention.
- Cleanup is ownership-aware: once sessions are moved to `tcon->dfs_ses_list`, the walk no longer releases them.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/dfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/dfs_cache.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/dfs_cache.c

This file implements the CIFS DFS referral cache. It canonicalizes DFS paths, stores referral metadata and target lists, maintains target hints, exposes a procfs cache view/flush interface, refreshes expired referrals, and can force reconnects when refreshed targets no longer match an active DFS tcon.

Main data structures:
- `struct cache_entry`: hash-table entry keyed by canonical DFS path, with referral flags, TTL, expiry time, server type, path-consumed value, target count/list, and current target hint.
- `struct cache_dfs_tgt`: cached target node name and path-consumed value.
- Global cache state: 512-bucket hlist table, max 1024 entries, `htable_rw_lock`, slab cache, `dfscache_wq`, `dfs_cache_ttl`, cache codepage, and entry count.

Main responsibilities:
- Initialize/destroy DFS cache resources with `dfs_cache_init()` and `dfs_cache_destroy()`.
- Canonicalize paths into the cache codepage using `dfs_cache_canonical_path()`.
- Hash and compare paths case-insensitively using the cache NLS table.
- Lookup referrals by exact path or whole-component prefix for longer referral requests.
- Refresh missing, expired, or forced cache entries by issuing `get_dfs_refer` through an IPC session.
- Copy referral data into cache entries while preserving target hint ordering where possible.
- Return either a single `dfs_info3_param` referral or a complete `dfs_cache_tgt_list`.
- Update target hints without network I/O through `dfs_cache_noreq_update_tgthint()`.
- Parse target shares and merged prefix paths with `dfs_cache_get_tgt_share()`.
- Periodically refresh DFS sessions and tcon referrals through `dfs_cache_refresh()`.
- On forced remount refresh, mark the SMB connection for reconnect if the active target is no longer present.

Important flows:
- `dfs_cache_find()` canonicalizes the path, refreshes if necessary, then returns referral and/or target list data.
- `cache_refresh_path()` first looks under read lock, drops locks before network I/O, then reacquires write lock to add or update the entry.
- `dfs_cache_noreq_find()` reads an existing cache entry only and never sends referral requests.
- `refresh_tcon_referral()` checks whether the cached referral is missing/expired/forced, validates the root IPC session, fetches new refs, updates cache, and optionally reconnects.
- `dfs_cache_remount_fs()` force-refreshes a DFS mount, disables serverino assumptions, forces prefix-path use, and lets refresh logic decide whether reconnect is needed.

Concurrency and lifetime:
- `htable_rw_lock` protects cache table and entries.
- Network referral requests are performed outside the cache lock to avoid deadlocks with reconnect paths.
- Target hints are read/written with `READ_ONCE()`/`WRITE_ONCE()`.
- Target lists returned to callers are deep copies and must be freed by `dfs_cache_free_tgts()`.
- Cache purge favors removing single-target referrals first, then the oldest entry if still over limit.

External dependencies:
- Uses dialect `get_dfs_refer` operation through `cifs_ses`.
- Uses DNS resolution for target-share IP matching.
- Calls reconnect signaling when refreshed DFS targets require failover.

Research notes:
- The cache uses a minimum referral TTL of 120 seconds and tracks a global refresh cadence as the minimum observed cache TTL capped by configured/default TTL.
- Prefix lookup implements DFS referral matching for paths below an existing root/link referral.
- Forced refresh is used by remount to detect target-list changes and trigger failover.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/dfs_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/dfs_cache.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/dfs_cache.h

This header declares the DFS referral cache API and target-list iterator types.

Main contents:
- Exports `dfscache_wq` and `dfs_cache_ttl`.
- Defines `struct dfs_cache_tgt_list`, which owns a list of copied target iterators and a count.
- Defines `struct dfs_cache_tgt_iterator`, containing target name, path-consumed value, and list node.
- Provides initializer macros `DFS_CACHE_TGT_LIST_INIT` and `DFS_CACHE_TGT_LIST`.

Public API:
- Cache lifecycle: `dfs_cache_init()`, `dfs_cache_destroy()`.
- Lookup/refresh: `dfs_cache_find()`, `dfs_cache_noreq_find()`.
- Target hint and referral extraction: `dfs_cache_noreq_update_tgthint()`, `dfs_cache_get_tgt_referral()`.
- Target parsing: `dfs_cache_get_tgt_share()`.
- Path canonicalization: `dfs_cache_canonical_path()`.
- Remount and background refresh: `dfs_cache_remount_fs()`, `dfs_cache_refresh()`.

Inline helpers:
- `dfs_cache_get_tgt_iterator()` returns the first target iterator.
- `dfs_cache_get_next_tgt()` advances to the next target.
- `dfs_cache_free_tgts()` frees a copied target list.
- `dfs_cache_get_tgt_name()` returns an iterator’s name.
- `dfs_cache_get_nr_tgts()` returns target count.
- `dfs_cache_get_ttl()` returns the current refresh TTL.

Research notes:
- Callers receive owned target-list copies, not direct cache internals.
- The iterator order places the target hint first when available.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/dfs_cache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/dir.c

This file implements CIFS/SMB VFS dentry and directory-related operations: path construction, lookup, create/atomic open, mknod, tmpfile creation, negative/positive dentry validation, case-insensitive dentry operations, and silly-rename path generation.

Main responsibilities:
- Builds remote paths from dentries, optional DFS tree prefixes, mount prepaths, and CIFS path separators.
- Validates filename component length and rejects backslash in POSIX-disallowed mounts.
- Implements file creation and create+open through `__cifs_do_create()`, `cifs_do_create()`, `cifs_atomic_open()`, and `cifs_create()`.
- Supports legacy POSIX open when available, normal SMB open otherwise, and post-create inode metadata lookup.
- Handles fscache read-around requirements by requesting read access for write-only opens when needed.
- Uses cached parent directory handles to set SMB2 parent lease keys and invalidate cached dirents.
- Implements `cifs_lookup()` with cached negative lookup shortcuts, POSIX/Unix/standard inode query paths, and retry on `-EAGAIN`.
- Implements dentry revalidation via `cifs_d_revalidate()` for positive and negative dentries.
- Provides case-insensitive hash/compare operations using the mount NLS table.
- Implements SMB2+ `O_TMPFILE` by creating hidden temporary names with delete-on-close semantics and setting temporary/hidden attributes.
- Generates silly-rename full paths for deferred delete behavior.

Important flows:
- Path construction: `build_path_from_dentry()` delegates to optional-prefix helper and may prepend DFS tree name and prepath before converting separators.
- Create/open: `cifs_atomic_open()` checks forced shutdown, resolves tlink, validates name, creates lease key, records pending open, calls `cifs_do_create()`, instantiates/splices dentry, finishes open, creates `cifsFileInfo`, and starts fscache cookie use.
- Lookup: `cifs_lookup()` checks name validity, builds full path, optionally trusts valid cached directory negative state, queries inode info, renews parent timestamps on success, and returns `d_splice_alias()`.
- Revalidation: positive dentries call `cifs_revalidate_dentry()` and handle deleted/stale cases; negative dentries may remain valid if the parent cached directory is valid.
- Tmpfile: `cifs_tmpfile()` creates a unique hidden name under the parent, marks inode link count zero, instantiates the unhashed dentry, opens file state, then sets hidden/temporary attributes.

Concurrency and lifetime:
- Tcon links are acquired through `cifs_sb_tlink()` and released after each operation.
- Dentry path buffers are allocated with `alloc_dentry_path()` and freed after use.
- Pending opens are added before create/open and removed on failure.
- Cached directory handles are opened/closed around validation checks.

External dependencies:
- Calls server dialect operations for open, close, make_node, set_file_info, and lease-key handling.
- Uses inode query helpers from CIFS core.
- Integrates with fscache, cached directory support, POSIX extensions, and legacy CIFS Unix extensions.

Research notes:
- This file is the main VFS dentry bridge between Linux path semantics and SMB path/open operations.
- Negative dentry caching is conservative unless the parent directory cache is known valid.
- Case-insensitive operations depend on the mount codepage and CIFS uppercase conversion.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/dns_resolve.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/dns_resolve.c

This file implements hostname-to-IP resolution for CIFS/SMB DFS and reconnect paths using the kernel DNS resolver upcall.

Main responsibilities:
- `dns_resolve_name()` validates input, recognizes literal IPv4/IPv6 addresses without upcall, optionally expands NetBIOS names with a DNS domain, then resolves via `dns_query()`.
- `resolve_name()` performs the DNS resolver query in the current task network namespace and converts the returned string address into a `sockaddr`.

Important behavior:
- Literal IP addresses skip the DNS upcall and return success if `cifs_convert_address()` accepts them.
- If a DNS domain is supplied and the name looks like a NetBIOS name, the resolver first tries `<name>.<domain>`.
- If FQDN resolution fails, it falls back to resolving the original name.
- Failed conversion after a resolver result becomes `-EHOSTUNREACH`.

External dependencies:
- Uses `dns_query()` from the kernel DNS resolver.
- Uses CIFS address parsing and NetBIOS-name helpers from `cifsproto.h`.

Research notes:
- The helper is namespace-aware through `current->nsproxy->net_ns`.
- It is used by DFS target parsing, reconnect hostname refresh, and target/share matching.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/dns_resolve.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/dns_resolve.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/dns_resolve.h

This header declares the CIFS DNS resolver helper API.

Main contents:
- Declares `dns_resolve_name(const char *dom, const char *name, size_t namelen, struct sockaddr *ip_addr)`.
- Provides `dns_resolve_unc()`, an inline helper that extracts the hostname portion from a UNC path and resolves it.

Important behavior:
- `dns_resolve_unc()` rejects missing or too-short UNC paths.
- It uses `extract_unc_hostname()` and returns `-EINVAL` if no hostname can be extracted.
- Resolution is delegated to `dns_resolve_name()` with optional DNS domain.

Research notes:
- This is the small public interface used by DFS and connection code to avoid duplicating UNC hostname extraction.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/dns_resolve.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/export.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/export.c

This file contains CIFS exportfs hooks for optional NFSD export support.

Main responsibilities:
- Under `CONFIG_CIFS_NFSD_EXPORT`, defines `cifs_export_ops`.
- Uses `generic_encode_ino32_fh` for file handle encoding.
- Provides a stub `cifs_get_parent()` that currently logs and returns `-EACCES`.

Important behavior:
- Comments document that NFS-exporting CIFS mounts requires an explicit `fsid` and the CIFS mount should use `serverino` for stable inode numbers.
- The implementation is incomplete because mandatory export operation `fh_to_dentry` is not provided here.
- Parent lookup is explicitly not implemented.

Research notes:
- This file is a placeholder/partial exportfs integration point rather than full NFSD export support.
- The comments identify a future improvement: using routines that support 64-bit inode numbers instead of default 32-bit exportfs helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/export.c -->