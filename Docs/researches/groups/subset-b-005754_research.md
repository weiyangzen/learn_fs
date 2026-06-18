# Research Report: subset-b-005754

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/connect.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/connect.c

Purpose: implements the CIFS/SMB client connection lifecycle. It owns TCP/RDMA socket creation, RFC1001 session setup, demultiplex receive processing, reconnect and DFS failover, SMB negotiate/session setup, IPC tree setup, share tree connections, mount-time server/session/tcon acquisition, superblock matching, multiuser tcon construction, tlink pruning, and unmount teardown.

Important APIs and functions: externally used entry points include `cifs_signal_cifsd_for_reconnect`, `cifs_mark_tcp_ses_conns_for_reconnect`, `cifs_read_from_socket`, `cifs_discard_from_socket`, `cifs_read_iter_from_socket`, `dequeue_mid`, `cifs_handle_standard`, `cifs_enable_signing`, `cifs_ipaddr_cmp`, `cifs_match_ipaddr`, `cifs_find_tcp_session`, `cifs_get_tcp_session`, `cifs_put_tcp_session`, `cifs_setup_ipc`, `__cifs_put_smb_ses`, `cifs_get_smb_ses`, `cifs_put_tcon`, `cifs_put_tlink`, `cifs_match_super`, `cifs_setup_cifs_sb`, `cifs_mount_put_conns`, `cifs_mount_get_session`, `cifs_mount_get_tcon`, `cifs_is_path_remote`, `cifs_mount`, `cifs_umount`, `cifs_negotiate_protocol`, `cifs_setup_session`, `cifs_sb_master_tcon`, `cifs_sb_tlink`, and `cifs_tree_connect`. Key internal paths are `_cifs_reconnect`, `__cifs_reconnect`, DFS `reconnect_dfs_server`, `cifs_demultiplex_thread`, `match_server`, `match_session`, `match_tcon`, `cifs_get_tcon`, `generic_ip_connect`, and `ip_rfc1001_connect`.

Control flow: mount setup begins with `cifs_setup_cifs_sb`, then `cifs_mount` builds a `cifs_mount_ctx`. With DFS upcalls enabled it delegates to `dfs_mount_share`; otherwise it directly gets a server, session, and tree connection, verifies the path is not remote, optionally schedules multichannel setup, and installs the master tlink. Server acquisition first searches reusable TCP sessions with `match_server`; if none match, `cifs_get_tcp_session` allocates `TCP_Server_Info`, connects transport, starts the `cifsd` demultiplex thread, registers the session globally, and queues echo work. Session acquisition reuses or creates `cifs_ses`, negotiates protocol, performs session setup, stores DFS root-session ancestry when applicable, and creates an IPC tcon. Tcon acquisition reuses or creates a share tree connection, validates encryption, POSIX, persistent/resilient handle, witness, lease, cache, and Unix extension options, queries filesystem data, negotiates I/O sizes, and initializes fscache volume state. The receive thread reads RFC1002 headers, validates SMB responses, finds matching MIDs, dispatches standard or transform receive handlers, wakes request callbacks, handles oplock breaks, and triggers reconnect on malformed, timed-out, or dead connections. Reconnect tears down sockets and pending MIDs, marks sessions/tcons as needing reconnect, reconnects TCP/RDMA, moves to renegotiation, and wakes waiters.

State and persistence behavior: state is kernel-resident and refcounted across `TCP_Server_Info`, `cifs_ses`, `cifs_tcon`, `tcon_link`, and `cifs_sb_info`. TCP state includes socket/RDMA handles, destination/source addresses, hostname, DFS `leaf_fullpath`, DNS domain, credits, pending MID queue, echo/reconnect work, crypto material, sequence state, and transport status. Sessions track auth material, selected security type, channels, channel reconnect bitmaps, IPC tcon, DFS root session, charset, capabilities, and signing keys. Tcons track tree id, share options, cached directory handles, fscache cookies, DFS origin path, DFS session list, delayed DFS refresh work, witness registrations, and status. Superblocks own master tlinks and a per-fsuid rb-tree for multiuser tcons. Secrets and session keys are freed with sensitive zeroing where appropriate; superblock teardown is RCU-delayed after tlinks and prepath are released.

Dependencies and integration points: depends on Linux sockets, kthreads, workqueues, wait queues, keys, net namespaces, NLS, RDMA SMBDirect, SMB dialect operation tables, DFS cache and referral walking, SMB witness, fscache, cached directories, multichannel interface polling, tracepoints, and VFS superblock matching. It integrates with `dfs.c` for DFS mount resolution, `dfs_cache.c` for DFS failover targets, `dns_resolve.c` for hostname refresh, `dir.c` for path accessibility checks, protocol-specific SMB1/SMB2 operations, and filesystem context parsing.

Risks: locking spans global session lists, server locks, session locks, channel locks, tcon locks, and MID queues; ordering mistakes can deadlock reconnect, teardown, or multiuser tcon construction. Reconnect must wake and callback every pending MID exactly once while preserving retry semantics. DFS failover can change server/share targets, so inode number stability, prefix paths, target hints, and session/tcon reuse checks are subtle. Credential comparison and keyring-derived passwords affect session sharing and authentication fallback. Socket error handling includes RFC1001 fallback behavior where incorrect retry status could break mounts. Tlink pruning and unmount must not free active tcons. Encryption, signing, persistent handle, POSIX, witness, RDMA, and multichannel option checks are dialect-sensitive.

Test signals: exercise SMB1/SMB2/SMB3 mounts, IPv4/IPv6 and port 445/139 fallback, NetBIOS session init success/failure, signing/encryption negotiation, RDMA and TCP transports, keyring credentials, password rotation with `password2`, multichannel setup and reconnect, DFS root/link mount and failover, witness registration, persistent/resilient handles, POSIX extension mounts, fscache mounts, multiuser tlink creation/pruning, superblock reuse rejection/acceptance, echo timeout reconnect, malformed PDU handling, credit exhaustion reconnect, tree reconnect after `STATUS_NETWORK_NAME_DELETED`, and forced unmount cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/connect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/dfs.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/dfs.c

Purpose: implements DFS-aware mount and tree-connect logic for the CIFS client. It parses DFS target referrals into mount context data, walks nested DFS referrals, maintains the root IPC session needed for referral requests, mounts the selected DFS target, schedules referral cache refresh work, and overrides tree reconnects to use cached DFS targets.

Important APIs and functions: exported entry points are `dfs_parse_target_referral`, `dfs_mount_share`, and the DFS-enabled `cifs_tree_connect`. Internal helpers include `get_session`, `set_root_smb_session`, `parse_dfs_target`, `setup_dfs_ref`, `__dfs_referral_walk`, `dfs_referral_walk`, `__dfs_mount_share`, `update_fs_context_dstaddr`, `target_share_matches_server`, and `tree_connect_dfs_target`.

Control flow: `dfs_mount_share` optionally resolves the automount DFS root address, establishes an initial session, probes the root UNC for a referral, falls back to normal mounting if none exists or `nodfs` is set, and otherwise switches into DFS connection mode. `dfs_referral_walk` creates a `dfs_ref_walk`, seeds it with a referral for the source/root path, and `__dfs_referral_walk` iterates targets. Each target is parsed with `dfs_parse_target_referral`, current connections are dropped, a session and tcon are attempted for the target, and `cifs_is_path_remote` determines whether the path is still another DFS link. Interlinks advance the walk stack and fetch another referral until a final storage target is reached or nesting is exhausted. On success, `__dfs_mount_share` records the original full source path in `tcon->origin_fullpath`, transfers DFS root sessions to the tcon list, and queues cache refresh. DFS `cifs_tree_connect` uses `server->leaf_fullpath` to find cached targets and tries only those matching the connected server address before issuing `tree_connect`.

State and persistence behavior: state is transient during mount in `dfs_ref_walk`, but successful mounts persist `origin_fullpath`, DFS root session references, `leaf_fullpath` on TCP sessions, and delayed `dfs_cache_work` on the tcon. Target hints in `dfs_cache` are updated after successful target selection. `ctx->dfs_root_ses`, `ctx->leaf_fullpath`, and `ctx->dns_dom` are temporarily set around session acquisition so lower connection code can tag DFS-created sessions and servers.

Dependencies and integration points: depends on `dfs_cache` for canonical paths, referral lookup, target iteration, target hint updates, and target share/prefix parsing; on `dns_resolve` for target address resolution; on mount helpers from `connect.c`; on `cifs_is_path_remote` from `connect.c`; and on `smb3_parse_devname`/`cifs_build_devname`/`smb3_fs_context_fullpath` from context/path helpers. It integrates directly with tcon DFS session tracking and periodic DFS cache refresh.

Risks: referral path accounting relies on `path_consumed` and delimiter normalization; off-by-one handling can produce wrong prepaths or target UNC strings. Nested DFS link walking is bounded by `MAX_NESTED_LINKS`, but incorrect end-marker handling can loop or skip targets. Root session references are deliberately held across mount and transferred to tcons; missed puts leak sessions, while premature puts break future referral refresh. Tree reconnect only accepts targets whose share host matches the current server or IP, so DNS resolution failure behavior affects failover. DFS and non-DFS mount fallback must avoid creating incomplete superblocks.

Test signals: mount non-DFS shares with and without `nodfs`, DFS roots, DFS links with prefix paths, interlinks, referral targets with multiple delimiters, target failover ordering and hint updates, DFS automount address resolution, missing `dns_resolver` key handling, nested referrals up to the nesting limit, tree reconnect to cached DFS targets, and cleanup of root session references on unmount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/dfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/dfs.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/dfs.h

Purpose: defines the private DFS referral-walk interface used by SMB client mount code, plus small wrappers that bind CIFS mount state to DFS cache operations. It is the shared contract between `dfs.c`, `connect.c`, and DFS cache users.

Important APIs and types: defines `DFS_INTERLINK`, `struct dfs_ref`, `struct dfs_ref_walk`, and accessors such as `ref_walk_start`, `ref_walk_end`, `ref_walk_cur`, `ref_walk_path`, `ref_walk_fpath`, `ref_walk_tl`, and `ref_walk_ses`. Inline operations include `ref_walk_alloc`, `ref_walk_init`, `ref_walk_free`, `ref_walk_advance`, `ref_walk_next_tgt`, `ref_walk_get_tgt`, `ref_walk_set_tgt_hint`, `ref_walk_set_tcon`, `ref_walk_mark_end`, `dfs_get_path`, `dfs_get_referral`, `dfs_put_root_smb_sessions`, and `dfs_ses_refpath`. It declares `dfs_parse_target_referral` and `dfs_mount_share`.

Control flow: the header supports a stack-like DFS walk. `ref_walk_init` starts at the first slot. `ref_walk_next_tgt` lazily obtains or advances a DFS cache target iterator and marks the slot exhausted with an `ERR_PTR`. `ref_walk_advance` moves one level deeper and clears stale state in the destination slot. `ref_walk_descend` backs up toward the root when a level is exhausted. On successful mount, `ref_walk_set_tcon` moves session references from all traversed refs into the tcon's DFS session list. `ref_walk_mark_end` updates the previous level's target hint and marks it exhausted so walking resumes correctly after interlink expansion.

State and persistence behavior: `dfs_ref_walk` owns up to `MAX_NESTED_LINKS` temporary path strings, full-path strings, target lists, target iterators, and session references. `ref_walk_free` releases every slot and puts retained SMB sessions. `dfs_put_root_smb_sessions` later releases the sessions transferred to a tcon. The header itself persists no global state, but it encodes ownership transfer rules used by mount and unmount paths.

Dependencies and integration points: includes CIFS globals/prototypes, fs context data, DFS cache declarations, Unicode helpers, VFS namei, and errno. `dfs_get_path` canonicalizes paths through `dfs_cache_canonical_path`; `dfs_get_referral` selects either `ctx->dfs_root_ses` or the current mount session and calls `dfs_cache_find`; `dfs_ses_refpath` exposes `server->leaf_fullpath` to refresh paths.

Risks: most functions are inline ownership helpers, so misuse can leak or double-put path/session/target-list state. `DFS_INTERLINK` must match referral flag semantics. `ref_walk_descend` mutates the current pointer directly and assumes callers do not descend before start. `ref_walk_set_tcon` nulls moved sessions after list insertion; callers must not subsequently free them through the walk. `dfs_ses_refpath` returns `leaf_fullpath + 1`, so callers require UNC strings with a leading delimiter.

Test signals: build with `CONFIG_CIFS_DFS_UPCALL`, DFS walk leak checking with KASAN/KMEMLEAK, nested referral traversal, target iterator exhaustion, interlink end-marker behavior, root-session transfer on successful mounts, cleanup after failed mounts, and unmount releasing `dfs_ses_list`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/dfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/dfs_cache.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/dfs_cache.c

Purpose: implements the in-kernel DFS referral cache for CIFS/SMB. It canonicalizes DFS paths, stores referral metadata and target lists, resolves cache misses by issuing DFS referral requests over IPC, exposes `/proc/fs/cifs/dfscache`, refreshes referrals periodically, updates target hints for failover, and forces DFS reconnect when refreshed referrals no longer include the current target.

Important APIs and functions: exported entry points are `dfs_cache_init`, `dfs_cache_destroy`, `dfscache_proc_ops`, `dfs_cache_canonical_path`, `dfs_cache_find`, `dfs_cache_noreq_find`, `dfs_cache_noreq_update_tgthint`, `dfs_cache_get_tgt_referral`, `dfs_cache_get_tgt_share`, `dfs_cache_remount_fs`, and `dfs_cache_refresh`. Important internal helpers include `cache_entry_hash`, `dfs_path_equal`, `lookup_cache_entry`, `cache_refresh_path`, `get_dfs_referral`, `add_cache_entry_locked`, `update_cache_entry_locked`, `copy_ref_data`, `get_targets`, `setup_referral`, `parse_target_share`, `target_share_equal`, `is_ses_good`, `refresh_ses_referral`, and `refresh_tcon_referral`.

Control flow: initialization creates the `cifs-dfscache` workqueue, slab cache, hash table, default TTL, and UTF-8/default cache codepage. `dfs_cache_find` canonicalizes the caller path, calls `cache_refresh_path`, and returns either a single referral, a target list, or both. `cache_refresh_path` first looks under a read lock; if the entry is missing, expired, or force-refreshed it drops locks, requests fresh referrals through `server->ops->get_dfs_refer`, then takes the write lock and adds or updates the entry after rechecking for races. Target lists are copied out with the current hint first. No-request lookups use existing entries only and never refresh. Periodic `dfs_cache_refresh` refreshes referrals for every root session used by the tcon and then the tcon's own referral, rescheduling itself by the minimum observed TTL. Remount forces a referral refresh, disables `serverino`, enables prefix paths, and signals reconnect if the new target set does not include the current share/server.

State and persistence behavior: cache state is global to the CIFS module: a fixed 512-bucket hash table, max 1024 entries, atomic entry count, global minimum TTL, global cache codepage, and an rwsem. Each `cache_entry` stores canonical path, referral header flags, TTL, expiry time, server/referral type, path consumed, target list, and current target hint pointer. Entries are in-memory only and can be flushed by proc write of `0`, expiry, purge, destroy, or forced update. Target hints are updated with `WRITE_ONCE` and copied out in front of target lists to bias future reconnects.

Dependencies and integration points: depends on CIFS DFS referral protocol operations, SMB2/CIFS debug and Unicode helpers, NLS conversion, jhash, slab, procfs, workqueues, DNS resolution, tcon/session structures, and `dfs.h`. It is used by DFS mount walking, DFS tree reconnect, DFS-aware TCP reconnect, remount, and unmount-delayed refresh work.

Risks: cache lookup is case-insensitive and codepage-aware; conversion failures can make valid paths uncacheable. `cache_refresh_path` intentionally drops locks before I/O, so recheck logic must preserve consistency and avoid duplicate/stale entries. Updating target lists preserves the previous hint by target name; allocation failure during update can leave callers with errors while old metadata may have been partially freed if cleanup changes regress. `dfs_cache_noreq_update_tgthint` dereferences the current hint without checking for an empty target list, relying on cache invariants. TTL is clamped globally to the minimum of observed and default TTLs, which controls all scheduled refreshes. Refresh code may signal reconnect after referral changes, affecting active mounts and inode stability.

Test signals: DFS cache init/destroy, proc read and flush, canonicalization across NLS charsets and delimiters, case-insensitive lookup, prefix lookup for nested DFS paths, cache miss and expired-entry referral fetch, concurrent refresh races, target-list copy ordering with hints, cache max-entry purge, no-request lookup after cache flush, target share/prefix merging, forced remount refresh, referral change triggering reconnect, and delayed work rescheduling by TTL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/dfs_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/dfs_cache.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/dfs_cache.h

Purpose: declares the CIFS DFS referral cache API and target-list iterator model shared by mount, reconnect, remount, and refresh code.

Important APIs and types: declares global `dfscache_wq`, global atomic `dfs_cache_ttl`, `dfscache_proc_ops`, `struct dfs_cache_tgt_list`, and `struct dfs_cache_tgt_iterator`. Public functions include `dfs_cache_init`, `dfs_cache_destroy`, `dfs_cache_find`, `dfs_cache_noreq_find`, `dfs_cache_noreq_update_tgthint`, `dfs_cache_get_tgt_referral`, `dfs_cache_get_tgt_share`, `dfs_cache_canonical_path`, `dfs_cache_remount_fs`, and `dfs_cache_refresh`. Inline helpers include `DFS_CACHE_TGT_LIST_INIT`, `DFS_CACHE_TGT_LIST`, `dfs_cache_get_next_tgt`, `dfs_cache_get_tgt_iterator`, `dfs_cache_free_tgts`, `dfs_cache_get_tgt_name`, `dfs_cache_get_nr_tgts`, and `dfs_cache_get_ttl`.

Control flow: callers typically declare a stack `DFS_CACHE_TGT_LIST`, call `dfs_cache_find` or `dfs_cache_noreq_find`, iterate targets with `dfs_cache_get_tgt_iterator` and `dfs_cache_get_next_tgt`, and release copied target nodes with `dfs_cache_free_tgts`. Refresh work is queued on `dfscache_wq` and calls `dfs_cache_refresh`.

State and persistence behavior: target lists returned to callers are copied lists owned by the caller; freeing removes every iterator node and its duplicated name and resets `tl_numtgts`. The real persistent cache state lives in `dfs_cache.c`. The exported TTL controls refresh scheduling and is read atomically.

Dependencies and integration points: includes Linux NLS/list/uuid helpers and CIFS global structures. It is included by `dfs.h`, `dfs.c`, `connect.c`, and cache refresh/remount paths.

Risks: callers must initialize lists before use and free them on every path. `dfs_cache_get_next_tgt` assumes the iterator belongs to the given list. `dfs_cache_get_tgt_name` returns borrowed iterator storage. The header exposes globals, so module init/exit ordering must ensure `dfscache_wq` and `dfs_cache_ttl` are valid before scheduling or reading.

Test signals: compile coverage with DFS enabled, target-list iteration over empty/single/multiple targets, freeing partially populated lists after allocation failure, TTL reads after init, and all users freeing copied target lists after reconnect or mount attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/dfs_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/dir.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/dir.c

Purpose: implements CIFS dentry-facing VFS operations and file creation helpers. It builds SMB paths from dentries and prefix paths, validates component names, handles atomic create/open and plain create, supports mknod, lookup and dentry revalidation, provides case-insensitive dentry hashing/comparison, creates hidden delete-on-close tmpfiles, and builds sillyrename paths.

Important APIs and functions: exported or VFS-used functions include `cifs_build_path_to_root`, `build_path_from_dentry`, `__build_path_from_dentry_optional_prefix`, `build_path_from_dentry_optional_prefix`, `cifs_atomic_open`, `cifs_create`, `cifs_mknod`, `cifs_lookup`, `cifs_tmpfile`, `cifs_silly_fullpath`, `cifs_dentry_ops`, and `cifs_ci_dentry_ops`. Internal helpers include `renew_parental_timestamps`, `check_name`, `alloc_parent_path`, `__cifs_do_create`, `cifs_do_create`, `cifs_d_revalidate`, `cifs_ci_hash`, `cifs_ci_compare`, and `set_tmpfile_attr`.

Control flow: path construction starts from `dentry_path_raw`, optionally prepends the mount prepath, converts delimiters, and optionally prepends a DFS tree name. Create/open paths acquire a `tcon_link`, validate names, build the full path, request a lease key, register a pending open, and call `__cifs_do_create`. That helper tries legacy POSIX open when available, otherwise computes desired access/disposition/create options, optionally uses parent cached-directory lease keys, calls dialect `open`, queries inode info when needed, applies Unix/dynperm ownership/mode adjustments, and closes on failure. `cifs_atomic_open` splices or instantiates the inode, finishes the VFS open, switches direct-I/O file ops when needed, creates `cifsFileInfo`, and activates fscache cookies. `cifs_lookup` builds the path, uses cached directory negative knowledge where possible, queries POSIX/Unix/standard inode info, renews parental timestamps, and splices the result. Dentry revalidation refreshes positive dentries and handles DFS automount flags; negative dentries are retained only briefly or when parent cached-dir data proves absence. Tmpfile creation generates hidden `cifs_tmp` names, creates with delete access, marks the dentry as tmpfile, sets nlink zero, attaches file info, and sets hidden/temporary attributes.

State and persistence behavior: dentry timestamps are used as lightweight negative/parent cache signals. New inodes are instantiated into dentries and may receive lease keys, dynamic mode/uid/gid, fscache cookie use, and tmpfile zero-link state. Pending-open records bridge create/open races until `cifs_new_fileinfo` succeeds or the handle is closed. Tlink references pin the appropriate tcon for multiuser mounts. Case-insensitive dentry ops store hashes based on uppercased local-NLS characters. Tmpfile and sillyrename names use atomic counters and bounded retry loops.

Dependencies and integration points: depends on VFS dentry/inode/open/tmpfile APIs, CIFS superblock flags and tlinks from `connect.c`, SMB dialect operations (`open`, `close`, `make_node`, `set_file_info`, inode query helpers), legacy Unix extensions, SMB3 POSIX extensions, cached directory handles, fscache, DFS automount detection, lease/oplock handling, and path separator/remapping helpers.

Risks: path building must leave enough headroom in the page buffer for prepath and DFS prefix; wrong prefix handling breaks DFS and prefix-path mounts. Create/open has many dialect and option branches, and must close server handles on every post-open failure. Parent cached-dir lease use deliberately invalidates cached dirents after create. fscache write-only opens may temporarily request read access; fallback must invalidate cache when read access is denied. Dentry revalidation must return VFS-compatible values and avoid LOOKUP_RCU blocking. Case-insensitive comparison assumes upper/lowercase byte lengths match in the local codepage. Tmpfile creation must avoid name collisions and close handles on `finish_open` or dentry-name failures.

Test signals: path generation for root, prepath, DFS tree-prefix, POSIX path, and backslash-remapped mounts; create/open with `O_CREAT`, `O_EXCL`, `O_TRUNC`, direct I/O, fscache, leases, cached parent handles, Unix/POSIX extensions, and read-only mode; lookup positive/negative/cache-hit/cache-miss paths; DFS automount dentry revalidation; mknod dialect support; case-insensitive lookup under non-ASCII NLS; tmpfile create/collision/delete-on-close attributes; and sillyrename path collision exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/dns_resolve.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/dns_resolve.c

Purpose: provides CIFS DFS hostname-to-IP resolution through the kernel DNS resolver. It accepts UNC hostnames or DFS target hostnames, treats literal IPv4/IPv6 addresses as already resolved, optionally expands NetBIOS names with a DNS domain, and returns a populated socket address.

Important APIs and functions: the public function is `dns_resolve_name`. The internal helper `resolve_name` performs the `dns_query` upcall and converts the returned textual IP address with `cifs_convert_address`.

Control flow: `dns_resolve_name` validates inputs, tries `cifs_convert_address` directly, then if a DNS domain is present and the name is NetBIOS-style it allocates `name.domain` and resolves that first. If FQDN resolution fails or is not attempted, it resolves the original name. `resolve_name` calls `dns_query` in the current network namespace, logs failures or results, converts the returned string into `sockaddr`, frees the resolver string, and maps conversion failure to `-EHOSTUNREACH`.

State and persistence behavior: no persistent module state is kept here. The only allocated state is the temporary FQDN string and DNS resolver result string. Resolution runs in `current->nsproxy->net_ns`, so namespace selection follows the caller context.

Dependencies and integration points: depends on `linux/dns_resolver.h`, CIFS address conversion, NetBIOS name detection, debug logging, and network namespace context. It is called by DFS mount parsing, DFS target/server matching, and reconnect hostname refresh in `connect.c`.

Risks: DNS resolver upcalls can be unavailable or misconfigured, especially for DFS automounts. Domain suffixing is only attempted for NetBIOS names, so behavior differs between short and FQDN-like names. The returned IP string must be parseable by CIFS address conversion. Because current task namespace is used, callers must invoke it from the desired network namespace.

Test signals: literal IPv4 and IPv6 inputs skipping upcall, NetBIOS name plus domain resolving as FQDN first, fallback to original name, resolver failure mapping, conversion failure mapping to `-EHOSTUNREACH`, and DFS reconnect/mount paths in non-initial network namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/dns_resolve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/dns_resolve.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/dns_resolve.h

Purpose: declares the CIFS DNS resolver interface and provides a UNC-specific wrapper used by DFS and reconnect code.

Important APIs and functions: declares `dns_resolve_name` and defines inline `dns_resolve_unc`.

Control flow: `dns_resolve_unc` validates that a UNC-like string is at least three characters, extracts the hostname with `extract_unc_hostname`, rejects empty hostnames, and calls `dns_resolve_name` with the optional DNS domain and output socket address.

State and persistence behavior: the header owns no state. It passes caller-owned UNC strings and socket-address storage through to the resolver implementation.

Dependencies and integration points: includes Linux network declarations plus CIFS global/prototype helpers. Used by `dfs.c`, `dfs_cache.c`, and `connect.c` anywhere a UNC path or target must become an address for mount, target matching, or reconnect.

Risks: the wrapper assumes UNC parsing rules from `extract_unc_hostname`; malformed paths return `-EINVAL`. Callers must provide writable `sockaddr` storage large enough for IPv4 or IPv6 results. It does not set SMB ports, so callers such as DFS mount setup must apply ports separately.

Test signals: malformed UNC rejection, empty hostname rejection, slash and backslash UNC variants, IPv4/IPv6 literal UNC hosts, domain-suffixed NetBIOS UNC hosts, and callers setting the port after successful resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/dns_resolve.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/export.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/export.c

Purpose: provides the optional `CONFIG_CIFS_NFSD_EXPORT` exportfs operations table for exporting CIFS mounts through NFSD. The implementation is intentionally minimal and documents the constraints around server inode numbers and fsid usage.

Important APIs and functions: defines `cifs_get_parent` and `const struct export_operations cifs_export_ops` when `CONFIG_CIFS_NFSD_EXPORT` is enabled. The table uses `generic_encode_ino32_fh` for file-handle encoding and wires `.get_parent` to `cifs_get_parent`; mandatory decode operations are noted but not implemented in this file.

Control flow: when compiled in, exportfs can call `cifs_get_parent`, but it currently logs the request and returns `-EACCES`. File handle encoding is delegated to the generic 32-bit inode encoder.

State and persistence behavior: no state is stored by this file. Export behavior relies on stable server inode numbers from CIFS mount options; CIFS inode generation numbers are effectively zero.

Dependencies and integration points: depends on Linux exportfs, CIFS globals/debug, and CIFS filesystem declarations. It integrates only when the kernel config enables CIFS NFSD export support and an administrator configures CIFS paths for NFS export.

Risks: parent lookup and file-handle decode are incomplete, so practical NFSD export support is limited. Generic 32-bit inode handles can be insufficient for servers with 64-bit inode numbers. Exporting without `serverino` or a stable fsid can produce unstable or ambiguous NFS file handles.

Test signals: compile with and without `CONFIG_CIFS_NFSD_EXPORT`, verify `cifs_export_ops` linkage, attempted NFSD export returning access failure for parent lookup, and documentation/admin tests requiring `serverino` plus explicit fsid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/export.c -->
