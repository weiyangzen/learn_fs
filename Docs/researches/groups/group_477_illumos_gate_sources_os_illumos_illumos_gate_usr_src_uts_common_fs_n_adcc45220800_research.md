# Group Research: group_477_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_n_adcc45220800

Scope verified against `Docs/research_subset_a.md`: illumos source tree is in subset A. Read coverage: all five listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_client.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_client.c

## Purpose
Core support code for the illumos NFSv4 client. This file provides shared machinery used by the NFSv4 vnode layer, recovery layer, mount lifecycle, caching, async I/O, lease renewal, zone shutdown, shared filehandle management, and pathname tracking.

## Main Responsibilities
- Attribute-cache validation and invalidation.
- Page-cache flushing, dirty-page writeback, and truncation invalidation.
- Per-mount asynchronous request management and worker threads.
- Cross-zone-safe handling for async writeback and inactive processing.
- Mount kstats and recovery kstat setup.
- Zone lifecycle tracking for all NFSv4 mounts in a zone.
- NFSv4 client init/fini sequencing.
- Lease renewal thread and `RENEW` over-the-wire call.
- State reference accounting for open files requiring lease maintenance.
- Shared filehandle interning through a per-mount AVL tree.
- `nfs4_fname_t` tree management for reconstructing paths and component names.

## Attribute And Cache Flow
- `nfs4_validate_caches()` returns quickly if attributes are valid, otherwise fetches attributes via `nfs4_getattr_otw()`.
- `nfs4_getattr_cache()` copies cached vnode attributes only when `ATTRCACHE4_VALID()` succeeds.
- `nfs4_getattr_otw()` wraps `nfs4_getattr_otw_norecovery()` with `nfs4_start_fop()`, NFSv4 recovery handling, cache update, stale filehandle purge, and SECINFO restore checks.
- `nfs4_getattr_otw_norecovery()` constructs `{ CPUTFH, GETATTR }` and requests `NFS4_VATTR_MASK`, optionally OR-ing ACL attributes.
- `nfs4getattr()` returns the rnode cache view after forcing a refresh if needed, and always reports client-side `r_size`.
- `nfs4_attr_otw()` is a generic attribute fetch helper using a caller-provided tag and bitmap.

`nfs4_attr_cache()` is the central cache coherency routine. It compares returned attributes and change information with rnode state, handles directory `change_info4`, tracks `R4WRITEMODIFIED`, serializes purge activity using `r_serial`, avoids deadlocks with page-flush threads, caches attributes through `nfs4_attrcache_va()`, and purges data/name/access/ACL caches when mtime, ctime, size, or change attributes indicate stale state.

`nfs4_attrcache_va()` computes adaptive attribute timeout windows using mount `ac*min/ac*max` settings, honors `MI4_NOAC` and `VNOCACHE`, updates `r_attr`, `r_change`, mounted-on fileid, pathconf cache, `r_size`, and swap-like state. It handles `NFS4_GETATTR_NOCACHE_OK` by forcing immediate invalidation.

## Page And Data Cache Handling
- `nfs4_purge_stale_fh()` marks `R4STALE`, records an rnode error, invalidates pages, and purges caches on `ESTALE`.
- `nfs4_purge_caches()` purges DNLC entries, symlink/readlink cache, xattr dir vnode, pathconf cache, page cache, and readdir cache. Page purge may be synchronous or delegated to `nfs4_pgflush_thread()`.
- `nfs4_waitfor_purge_complete()` waits for `r_serial` or `R4PGFLUSH` activity while respecting interruptible mounts.
- `nfs4_flush_pages()` issues `VOP_PUTPAGE(..., B_INVAL)` and records `ENOSPC`/`EDQUOT`.
- `nfs4_purge_rddir_cache()` resets directory EOF/lookup state and purges cached readdir data.
- `writerp4()` performs page-sized chunks of user-data copy into cached pages, manages page creation, `R4MODINPROGRESS`, `r_size`, and `R4DIRTY`.
- `nfs4_putpages()` writes or invalidates dirty pages for whole-file or range requests, preserving `R4DIRTY` on failed non-forced flushes.
- `nfs4_invalidate_pages()` serializes truncation/invalidation with `R4TRUNCATE`, updates `r_truncaddr`, calls `pvn_vplist_dirty()` with invalidation flags, then wakes waiters.

## Async I/O Model
The file implements a per-mount async manager to avoid illegal cross-zone NFS operations. Global-zone pageout/fsflush can enqueue work for a mount in another zone; the per-mount manager/worker threads execute the work in the correct context.

Key pieces:
- `nfs4_async_manager()` creates async worker or pageop worker threads as queued demand appears, drains work during shutdown, and exits only when `MI4_ASYNC_MGR_STOP` is set.
- `nfs4_async_common_start()` is the worker loop. It round-robins across async queues, honors cluster counts, performs the requested operation, frees request arguments, and exits after timeout or async shutdown.
- `nfs4_async_start()` and `nfs4_async_pgops_start()` select the normal or pageops queue.
- `free_async_args4()` releases vnode/credential references and decrements rnode I/O counters.
- `nfs4_async_stop()` and `nfs4_async_stop_sig()` disable async work and wait for worker/inactive quiescence, with the latter interruptible for unmount.

Queued operations include:
- `nfs4_async_readahead()`
- `nfs4_async_putapage()`
- `nfs4_async_pageio()`
- `nfs4_async_readdir()`
- `nfs4_async_commit()`
- `nfs4_async_inactive()`

Fallback behavior is carefully constrained. For pageout/fsflush or cross-zone synchronous fallback, dirty pages are normally re-marked or unlocked with error rather than performing unsafe synchronous NFS I/O in the wrong context.

## Inactive Handling
`nfs4_inactive_thread()` processes `NFS4_INACTIVE` queue entries until the async manager is gone and no inactive work remains. `nfs4_async_inactive()` must hand off inactive work for correctness. If the inactive thread is already unavailable, it performs local cleanup, drops delegations, clears open streams, and adds the rnode to the free list without doing unsafe over-the-wire work.

## Mount Kstats And Diagnostics
- `nfs4_mnt_kstat_update()` fills `mntinfo` raw kstat data: protocol, version, flags, negotiated/current security flavor, transfer sizes, retrans/timeo, attribute cache timers, server response/failover/remap counts, and current server name.
- `nfs4_mnt_kstat_init()` installs per-mount I/O kstats, read-only mount kstats, and recovery kstats.
- `nfs4_write_error()` rate-limits write error console messages, suppresses forced-unmount/recovery-failed spam, prints user/group information for `ENOSPC`/`EDQUOT`, and prints the filehandle.
- `nfs4_safemap()` checks active byte-range locks; only whole-file locks are considered mmap-safe.
- `nfs4_map_lost_lock_conflict()` checks queued lost `LOCK`/`LOCKU` requests for unsafe mmap conflicts.
- `nfs4_lockcompletion()` toggles `VNOCACHE` based on lock safety and purges attributes after lock acquisition.

## Zone And Mount Lifecycle
The file registers zone-specific mount globals using `zone_key_create()`:
- `nfs4_mi_init()` allocates a per-zone `mi4_globals` list.
- `nfs4_mi_zonelist_add()` inserts a mount and takes `mi`/`vfs` holds to avoid zone shutdown races.
- `nfs4_mi_shutdown()` walks zone mounts, purges DNLC, stops async/inactive threads, marks mounts dead, waits for recovery, removes mounts from the zone list, releases holds, and marks per-zone NFSv4 servers dead so renew threads exit.
- `nfs4_mi_destroy()` frees globals immediately or defers if mounts still await `VFS_FREEVFS()`.
- `nfs4_mi_zonelist_remove()` removes a mount unless shutdown already marked it dead.
- `nfs_free_mi4()` performs final `mntinfo4_t` teardown: kstats, debug message queue, names/filehandles, servinfo, locks/cvs/rwlocks, open-owner hash buckets, freed open-owner list, state/lost-state lists, rnode/filehandle containers, and the `mi` allocation.
- `mi_hold()`/`mi_rele()` implement `mntinfo4_t` reference counting.

## Client Init/Fini And CPR
`nfs4_clnt_init()` initializes NFSv4 vnode/rnode/shadow/access/subr/ACL/idmap/callback/SECINFO subsystems, installs a CPR callback, creates zone mount keys, and initializes the special unsupported-xattr vnode. `nfs4_clnt_fini()` tears those down and removes the CPR callback.

`nfs4_client_cpr_callb()` records resume time on CPR resume. The renew thread uses this to detect that leases may need prompt renewal after suspend/resume.

## Lease Renewal And State Accounting
`nfs4_renew_lease_thread()` is per-server. It sleeps based on lease time, propagation delay, state reference count, and lease validity. It renews only when state exists and the lease is valid, exits when marked, and waits for outstanding over-the-wire calls before releasing server references.

`nfs4renew()` sends `{ RENEW }`, updates propagation delay, handles `NFS4ERR_CB_PATH_DOWN` by returning all delegations while treating the lease as renewed, invokes recovery when needed, and handles status-to-errno conversion.

State ref helpers:
- `nfs4_inc_state_ref_count()` / `_nolock()` bump server state refs and mount open-file count, initialize lease validity, and reset renewal time when the first state appears.
- `nfs4_dec_state_ref_count()` / `_nolock()` decrement counts and may remove a mount from the server on last close when `MI4_REMOVE_ON_LAST_CLOSE` is set.
- `inlease()` checks current lease validity against last renewal time.
- `nfs4_server_in_recovery()` reports whether server recovery lock is writer-held.

## Shared Filehandle Interning
The per-mount filehandle AVL tree ensures shared `nfs4_sharedfh_t` objects:
- `sfh4_createtab()` creates the AVL.
- `sfh4_get()` finds or creates a shared filehandle.
- `sfh4_put()` handles speculative allocation and insert under `mi_fh_lock`.
- `sfh4_hold()`/`sfh4_rele()` maintain refcounts and remove/free last references.
- `sfh4_update()` removes an object, updates the handle, reinserts it if no duplicate exists, and warns on duplicate handles for writable mounts.
- `sfh4_copyval()` and `sfh4_printfhandle()` expose/print handle contents.

## Filename Tree
`nfs4_fname_t` objects track path components and parent/child relationships:
- `fn_get()` returns an existing child with matching name and shared filehandle or removes stale mismatched children and creates a new entry.
- `fn_hold()`/`fn_rele()` refcount and recursively release parents without recursive C calls.
- `fn_name()` returns a copy of a single component.
- `fn_path()` walks parents and builds a filesystem-root-relative path.
- `fn_parent()` returns a held parent.
- `fn_move()` updates parent/name after rename, removing conflicting child entries under the new parent.

## Important Invariants
- Many cache functions require careful avoidance of deadlock between recovery, page flush, and start/end operation regions.
- `r_serial`, `R4PGFLUSH`, `R4INCACHEPURGE`, `R4MODINPROGRESS`, and `R4TRUNCATE` are coordination flags, not incidental state.
- Async request counters and vnode/credential references are paired in `free_async_args4()`.
- Zone shutdown owns a large part of mount/thread teardown; normal unmount must cooperate with that path.
- Shared filehandle and fname code assumes AVL uniqueness, but explicitly handles stale or duplicate cases caused by volatile filehandles or server-side rename behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_client.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_client_debug.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_client_debug.c

## Purpose
NFSv4 client recovery diagnostics and kstats. This file builds and manages per-mount recovery event/fact queues, formats user-visible diagnostic messages, deduplicates recent messages, and updates per-mount recovery counters.

## Main Data
- `rkstat_t`: named kstat counters for recovery conditions such as `badhandle`, `badowner`, `clientid`, `dead_file`, `delay`, `fail_relock`, `opens_changed`, `wrongsec`, and `lost_state_bad_op`.
- `rkstat_template`: initialization template for `mi_recov_kstat`.
- `nfs4_msg_max`: maximum queued recovery messages per mount.

## Event And Fact Construction
`set_event()` fills an `nfs4_revent_t` according to `nfs4_event_type_t`. It records affected rnodes, paths from `fn_path()`, pids, seqids, NFS status values, server names, and explanatory strings. It handles events such as bad seqid, bad filehandle, clientid recovery failure, dead file, recovery start/end, failed relock, failover/referral, lost state, changed open counts, lost locks, unexpected recovery action/error/status, and wrong security.

`set_fact()` fills `nfs4_rfact_t` entries for contextual facts including bad owner/domain mismatch, recovery error causes, renew expiration, server response transitions, delmap callback errors, and full send queues.

## Queue Interpretation
`successful_comm()` classifies whether a message represents successful server communication. `find_beginning()` walks backward through the mount message list to find the earliest relevant message for a fact sheet, bounded by roughly two lease periods or a default lease window. It includes logic to identify where communication was lost before recovery.

`get_facts()` walks backward from an event to collect not-yet-inspected facts into a summarized fact sheet, marking facts as inspected so repeated severe events do not repeatedly reuse the same historical context.

## Deduplication
`facts_same()` compares a new fact with recent facts within two lease periods. It compares type, recovery action, NFS status, reboot flag, op, time, errno, rnode pointer, server, mount point, and path strings.

`events_same()` compares a new event against the most recent prior event, skipping facts. It compares event type, mount, counters, status, pid, rnodes, tags, seqids, server, path strings, and mount point. This prevents repeated identical recovery noise from filling the queue or logs.

## Memory Management
- `free_event()` frees event path/string fields.
- `free_fact()` frees fact string fields.
- `nfs4_free_msg()` frees event/fact payload strings, server/mount strings, and the message itself.

## Logging
`queue_print_event()` formats recovery events into zone-aware `zcmn_err()` messages. It prints detailed messages for bad seqids, invalid filehandles, failed clientid recovery, dead files, failover, remap failures, lost state, failed relock, lost locks, unexpected recovery outputs, unrecoverable `WRONGSEC`, bad lost-state ops, and referrals. It calls `print_facts()` for severe file/lock-loss events.

`queue_print_fact()` formats standalone facts such as `NFSMAPID_DOMAIN` mismatch, operation error causing recovery action, lease expiration, server not responding/ok, all servers not responding/ok, delmap callback error, and send queue full.

`id_to_dump_queue()`, `id_to_dump_solo_event()`, and `id_to_dump_solo_fact()` control whether a new message dumps the whole queue, only itself, or stays queued silently.

## Kstats
`update_recov_kstats()` increments recovery kstat counters from events and facts. `nfs4_mnt_recov_kstat_init()` creates the per-mount named kstat under module `nfs`, installs the `rkstat_template`, handles zone visibility, and stores the kstat pointer on `mntinfo4_t`.

Small helpers:
- `nfs4_mi_kstat_inc_delay()`
- `nfs4_mi_kstat_inc_no_grace()`

## Public Queue APIs
`nfs4_queue_event()` allocates and initializes an event message, records server and mount path, deduplicates it against the last event, inserts it at the tail, dumps/logs as dictated by the event type, and trims the queue when `nfs4_msg_max` is reached.

`nfs4_queue_fact()` performs the analogous path for facts. It updates kstats, deduplicates recent facts, queues the fact, optionally prints standalone facts, and trims the queue.

## Notable Detail
In `events_same()`, the mount-point string comparison uses `strncmp(cur_msg->msg_mntpt, cur_msg->msg_mntpt, len)`, comparing the string to itself rather than `new_msg->msg_mntpt`. That makes the mount-point content check ineffective once both are non-NULL; other fields still participate in deduplication.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_client_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_client_secinfo.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_client_secinfo.c

## Purpose
NFSv4 client SECINFO and security-flavor negotiation. This file handles `NFS4ERR_WRONGSEC` by discovering server-supported security flavors and rotating the current `servinfo4_t` security data through candidate flavors until one works.

## Supported Security Flavors
`nfs4_secinfo_init()` builds a global `SECINFO4res` list of client-supported flavors:
- `AUTH_SYS`
- Kerberos RPCSEC_GSS with services none, integrity, privacy
- `AUTH_DH`
- `AUTH_NONE`

The Kerberos V5 OID is hard-coded. The file also hard-codes pseudo flavor mappings:
- krb5: `390003`
- krb5i: `390004`
- krb5p: `390005`

`nfs4_secinfo_fini()` frees the global support list.

`secinfo2nfsflavor()` maps RPCSEC_GSS mechanism/service pairs to these pseudo flavor numbers, returning zero when no known mapping exists.

## SECINFO Data Conversion
`secinfo_create()` converts wire `SECINFO4res` entries into `sv_secinfo_t` containing kernel `sec_data_t` entries:
- RPCSEC_GSS entries allocate and fill `gss_clntdata_t`, including mechanism bytes, service, qop, username `nfs`, and server instance name.
- AUTH_DH entries are included only if the server info has usable `sv_dhsec`; otherwise they are skipped.
- AUTH_SYS/AUTH_NONE and other simple flavors become direct `sec_data_t` entries.

`secinfo_free()` frees `sv_secinfo_t`, purges cached RPCSEC_GSS auth handles with `rpc_gss_secpurge()`, releases GSS mechanism storage, and avoids freeing shared AUTH_DH data.

## Current Security Selection
`secinfo_update()` replaces `svp->sv_secinfo`, frees the prior list unless saved for recovery, resets the index, sets `SV4_TRYSECINFO`, and points `sv_currsec` at the first candidate. If no usable security info remains, it clears trial state and current security.

`secinfo_check()` advances the current index. If another flavor exists, it sets `SV4_TRYSECINFO` and updates `sv_currsec`; otherwise it resets the index and clears trial state.

`save_mnt_secinfo()` saves the mount’s original current security choice before operations that may cross mount/security boundaries.

`check_mnt_secinfo()` restores saved security when operating on a stub vnode or mount root context, and frees stale saved lists otherwise.

## Root Security Negotiation
`secinfo_tryroot_otw()` uses the global client-supported SECINFO list and tries `PUTROOTFH` with each flavor. On `NFS4ERR_WRONGSEC`, it advances to the next flavor. Other recovery-worthy errors are returned as success to let the caller retry through normal recovery. Successful completion leaves `sv_currsec` set to the flavor that worked.

## Path-Based SECINFO
`comp_total()` counts pathname components, ignoring redundant slashes. `comp_getn()` extracts the nth path component and splits a mutable path buffer so the parent path can be used for LOOKUPs.

`nfs4secinfo_otw()` performs `{ PUTROOTFH, LOOKUP parent components..., SECINFO target-component }`.

It handles `WRONGSEC` at multiple points:
- If `PUTROOTFH` fails, it negotiates root security through `secinfo_tryroot_otw()`.
- If a LOOKUP fails with `WRONGSEC`, it backs up to the failing component, gets SECINFO for that component, updates current security, then retries the full target.
- If non-WRONGSEC recovery is needed and the caller is already the recovery thread, it schedules recovery and returns to the outer recovery loop; otherwise it returns an error.

On successful SECINFO, it updates `mi_curr_serv` security and rejects empty/unsupported server flavor lists with `EACCES`.

`nfs4_secinfo_path()` decides whether a mounted path needs SECINFO. For server root, SECINFO cannot name a component, so it uses the client-supported flavor list and tries candidates. For non-root paths it calls `nfs4secinfo_otw()`. On error, it clears current/saved secinfo state.

## Filehandle/Vnode SECINFO
`nfs4_secinfo_fh_otw()` sends `{ CPUTFH, CSECINFO }` for a parent filehandle and component name, then updates server security from the SECINFO result.

`nfs4_secinfo_vnode_otw()` wraps the filehandle SECINFO path for lookup-triggered `WRONGSEC`.

`nfs4_secinfo_vnode()` is recovery-oriented: if the vnode has a parent filehandle/name, use filehandle SECINFO; otherwise fall back to mount path SECINFO.

## Recovery Entry Point
`nfs4_secinfo_recov()` is called when the client receives `NFS4ERR_WRONGSEC`. If the mount used an explicit preferred flavor, it does not negotiate and returns the WRONGSEC errno. Otherwise it tries SECINFO with current credentials and, when configured with a non-root security uid, with a duplicated credential using that uid. It clears `MI4R_NEED_SECINFO` before returning.

## Important Invariants
- `svp->sv_lock` protects `sv_secinfo`, `sv_currsec`, `sv_save_secinfo`, and security trial flags.
- SECINFO lists may be temporarily saved across recovery and must not be freed while saved.
- Empty server SECINFO results or client-incompatible AUTH_DH-only results become `EACCES`.
- Root path security negotiation cannot use SECINFO directly because SECINFO requires a component name.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_client_secinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_client_state.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_client_state.c

## Purpose
NFSv4 client-side state owner and stateid management. This file maintains open owners, open streams, lock owners, seqid synchronization, stateid selection, open downgrade behavior, and lost OPEN resend logic.

## Global Stateids
Defines the special all-zero stateid `clnt_special0` and all-ones stateid `clnt_special1`, used by NFSv4 protocol paths that need special stateid values.

## Open Owner Management
Open owners are keyed by credentials in per-mount hash buckets:
- `lock_bucket()` hashes effective plus real uid into `mi_oo_list` and locks the bucket.
- `find_open_owner_nolock()` searches active owners, reactivates valid-but-zero-ref owners, lazily moves invalid owners to the freed-owner list, and falls back to `find_freed_open_owner()`.
- `find_open_owner()` wraps this under `mi_lock`.
- `create_open_owner()` allocates an owner, holds credentials, initializes seqid state, assigns a unique `oo_name`, and inserts it in the credential hash.
- `open_owner_hold()` and `open_owner_rele()` manage references. Zero refs mark the owner invalid but defer actual destruction/list movement to later lookup paths.
- `nfs4_free_open_owner()` maintains the mount’s LRU-ish freed open-owner cache, bounded by `mi_foo_max`.
- `nfs4_destroy_open_owner()` releases credentials and synchronization primitives.

This lazy-free approach keeps locking simpler while avoiding immediate churn for credentials that may reopen soon.

## Open Stream Management
Open streams represent a specific open owner’s open state for an rnode:
- `find_open_stream()` searches `rp->r_open_streams`, returns with `os_sync_lock` held, and increments the refcount.
- `create_open_stream()` allocates a stream, initializes share counters/stateid/delegation flags, holds the open owner, inserts into the rnode stream list, and returns locked.
- `find_or_create_open_stream()` requires open seqid synchronization and either bumps `os_open_ref_count` or creates a stream.
- `open_stream_hold()`/`open_stream_rele()` manage stream references and remove/free the stream on last reference.
- `nfs4_clear_open_streams()` removes all streams from an rnode and releases their open owners.

## Lock Owner Management
Lock owners are tracked per-rnode by pid:
- `find_lock_owner()` searches the rnode lock-owner list and optionally requires a valid server stateid.
- `create_lock_owner()` allocates a lock owner, gives it list and caller refs, assigns a unique lock owner name containing sequence number plus pid, inserts it in the rnode list, and returns with `lo_lock` held.
- `nfs4_rnode_remove_lock_owner()` removes a lock owner from the rnode list and releases the list reference.
- `nfs4_flush_lock_owners()` removes all lock owners from an rnode.
- `lock_owner_hold()`/`lock_owner_rele()` manage lifetime; last release asserts the owner is off-list and no seqid is in use, then destroys it.
- `nfs4_setlockowner_args()` fills protocol lock-owner arguments from an existing valid lock owner or makes up a new owner value for test-style operations.

## Seqid Synchronization
NFSv4 open/lock sequence ids are serialized per owner:
- `nfs4_start_open_seqid_sync()` waits on `oo_cv_seqid_sync` until no open seqid is in use, but returns `EAGAIN` if recovery is active and the caller is not the recovery thread.
- `nfs4_end_open_seqid_sync()` clears in-use state and signals waiters.
- `nfs4_start_lock_seqid_sync()` performs equivalent serialization for lock owners, records `lo_seqid_holder`, and detects recovery interference.
- `nfs4_end_lock_seqid_sync()` clears `NFS4_LOCK_SEQID_INUSE`, resets holder, and signals waiters.
- `nfs4_get_open_seqid()`, `nfs4_set_open_seqid()`, `nfs4_get_and_set_next_open_seqid()`, `nfs4_set_lock_seqid()`, and `nfs4_set_lock_stateid()` update protocol seqid/stateid fields under the required synchronization assumptions.

Debug builds include optional seqid fault injection.

## Stateid Selection
Stateid priority is:
1. delegation stateid when valid for the operation
2. lock stateid for the pid
3. open stateid for the credential/rnode
4. special zero stateid

Functions:
- `nfs4_get_deleg_stateid()`
- `nfs4_get_lock_stateid()`
- `nfs4_get_open_stateid()`
- `nfs4_get_w_stateid()` for write paths
- `nfs4_get_stateid()` for read/setattr paths, with async-read retry support that skips already-tried stateid classes
- `nfs4_init_stateid_types()` initializes retry tracking.
- `nfs4_save_stateid()` records a failed stateid in the appropriate slot so retries can skip it.

## Open Bypass And Delegations
`nfs4_is_otw_open_necessary()` decides whether an OPEN must go over the wire:
- If an existing open stream already has sufficient access/deny state, it increments local counters and bypasses OTW OPEN.
- If a delegation is held, it may create an open stream locally using the delegation stateid, provided requested access is covered.
- It refuses bypass when an open stream failed reopen or when delegation/access conditions are insufficient.
- On delegation bypass with state tracking, it increments server state refcount.

`get_dtype()` safely reads current delegation type while respecting pending delegation return.

## Lock Argument Setup
`nfs4_setup_lock_args()` fills `locker4` for `LOCK`:
- For a new lock owner, it embeds open-owner seqid + open stateid + initial lock seqid + clientid/owner.
- For an existing lock owner, it sends lock stateid and next lock seqid.

`nfs4_find_or_create_lock_owner()` returns a referenced lock owner with lock seqid synchronization started. For new lock owners it also finds the corresponding open owner/open stream and starts open seqid synchronization. Failure paths clean up temporary lock owners and references, returning protocol-style `NFS4ERR_DELAY` or `NFS4ERR_IO`.

## Credentials For Over-The-Wire Calls
`nfs4_get_otw_cred()` returns an owner-specific over-the-wire credential if present, otherwise the supplied cred, with a hold.

`nfs4_get_otw_cred_by_osp()` iterates valid open streams for an rnode to find an alternate over-the-wire credential, optimized to try the caller’s credential first.

## BAD_SEQID And Lost Requests
`nfs4_create_bseqid_entry()` packages owner/vnode/pid/tag/seqid data for BAD_SEQID recovery.

`nfs4open_dg_save_lost_rqst()` records a lost `OPEN_DOWNGRADE` request when the downgrade call returns timeout, interrupt, or forced-unmount style errors.

## OPEN_DOWNGRADE
`nfs4_open_downgrade()` performs the protocol downgrade when local close/share counts imply reduced access:
- Computes new share access/deny bits.
- Skips OTW downgrade when no downgrade is needed and just decrements local counters.
- Sends `{ CPUTFH, GETATTR, OPEN_DOWNGRADE }`.
- Bumps open seqid when required by response semantics.
- Retries with the original credential on access failure if an alternate OTW credential was used.
- Saves recovery credential/seqid when recovery is needed.
- Updates the open stateid, stream counters, downgrade access, and attribute cache on success.

## Lost OPEN Resend
`nfs4_resend_open_otw()` resends a previously lost OPEN during recovery, then repairs local state:
- Handles normal reopen and `CLAIM_DELEGATE_CUR`.
- Uses non-create OPEN even if the original lost request created a file, because the goal is to clean up possible server-side state.
- Starts open seqid synchronization and sends `{ CPUTFH, COPEN, GETFH, GETATTR }`.
- Creates a vnode if needed from the returned filehandle/attributes.
- On reopen, verifies the returned filehandle or fileid matches the original; persistent or no-expire-with-open mismatches fail recovery.
- Updates volatile filehandles when acceptable.
- Performs OPEN_CONFIRM if required.
- Finds or creates open streams, updates stateid/share counters/delegation state, accepts delegations, caches or purges attributes, and releases seqid synchronization.

## Important Invariants
- Callers must respect lock ordering among `mi_lock`, open-owner bucket locks, rnode stream locks, owner locks, and seqid condition variables.
- Open and lock seqid synchronization must bracket any operation using or modifying owner seqids.
- Open streams can outlive local opens while references, mmap state, pending close, or recovery work exist.
- Delegation bypass must still create enough local state for later close/recovery accounting.
- Lost request handling assumes FIFO saved lost requests and one operation over the wire per seqid.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_client_state.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_common.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_common.c

## Purpose
Small common NFSv4 client/server support module. It defines the loadable filesystem wrapper for `nfs4`, transfer-size defaults, mount option updates, seqid response rules, retryable RPC errors, and stringification helpers for diagnostics.

## Module Registration
- `nfs4_ctags[]` holds the global tag list initialized from `NFS4_TAG_INITIALIZER`.
- `vfw4` defines the NFSv4 VFS with name `nfs4`, init function `nfs4init`, and flags `VSW_CANREMOUNT | VSW_NOTZONESAFE | VSW_STATS`.
- `modlfs4` registers the module as `"network filesystem version 4"`.

## Transfer Sizes
Defaults:
- `nfs4_max_transfer_size`: 32 KiB
- `nfs4_max_transfer_size_cots`: 1 MiB
- `nfs4_max_transfer_size_rdma`: 1 MiB

Functions:
- `nfs4tsize()` returns the generic default.
- `nfs4_tsize()` chooses transfer size from client `knetconfig` semantics: COTS/COTS_ORD and RDMA get larger defaults.
- `rfs4_tsize()` performs analogous sizing from server transport request type.

## Mount Option Updates
`nfs4_setopts()` applies user mount arguments to `mntinfo4_t`:
- Sets flags for `NOAC`, `NOCTO`, local locking, and group-id inheritance.
- Purges attribute cache immediately for `NOAC`.
- Validates and applies retransmission count and timeout.
- Clamps read/write transfer sizes to requested `rsize`/`wsize`.
- Applies attribute-cache min/max options for regular files and directories, converting seconds to high-resolution time and clamping to maximums.
- Returns `EINVAL` for invalid negative/zero values where required.

## Seqid Response Semantics
`nfs4_need_to_bump_seqid()` inspects a compound response. If it contains a seqid-dependent operation (`CLOSE`, `OPEN`, `OPEN_CONFIRM`, `OPEN_DOWNGRADE`, `LOCK`, `LOCKU`), it decides whether the caller should advance the seqid after the response. It does not bump for status values such as stale clientid/stateid, bad stateid, bad seqid, bad XDR, old stateid, resource, or no filehandle. All other statuses for seqid-dependent operations cause a bump.

## Retryable RPC Errors
`nfs4_rpc_retry_error()` returns true for transient transport/network errors:
- `ETIMEDOUT`
- `ECONNREFUSED`
- `ENETDOWN`
- `ENETUNREACH`
- `ENETRESET`
- `ECONNABORTED`
- `EHOSTUNREACH`
- `ECONNRESET`

## Diagnostic String Helpers
`nfs4_stat_to_str()` maps many `nfsstat4` values to stable strings and falls back to `"Unknown error %d"`.

`nfs4_recov_action_to_str()` maps recovery actions such as stale, failover, clientid, open files, wrongsec, expired, bad stateid, badhandle, bad seqid, grace, delay, lost lock, lost state request, and moved.

`nfs4_op_to_str()` maps NFSv4 operation numbers to strings using `REAL_OP4(op)` so pseudo/client operation encodings still resolve to the underlying protocol operation. Unknown operations produce `"Unknown op %d"`.

## Notable Details
- `nfs4_stat_to_str()` returns `"NFSS4ERR_NOTEMPTY"` for `NFS4ERR_NOTEMPTY`, which appears to include an extra `S` compared with the enum spelling.
- The source contains duplicated unreachable/redundant lines in two places: a repeated negative `retrans` check in `nfs4_setopts()` and a second `return ("NFS4ERR_DQUOT");` immediately after the first.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_common.c -->