# Group Research: group_1244_netbsd_src_sources_os_bsd_netbsd_src_sys_fs_nfs_client_nfs_clstate__6bc45d0be84c

Scope: `Docs/research_subset_a.md`  
Files read completely: 3/3

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clstate.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clstate.c

## Purpose

Implements NetBSD/FreeBSD-derived NFSv4 client-side state management: client IDs, open owners, lock owners, opens, byte-range locks, delegations, callbacks, recovery, lease renewal, and pNFS layout/device state.

The file is the core NFSv4 state machine behind vnode open/close/lock paths and callback service behavior. It maintains in-kernel state that mirrors server-granted stateids and repairs or discards that state when the server reports stale, expired, or recalled state.

## Main Data Model

- Global client list: `nfsclhead`, protected by `NFSCLSTATEMUTEX`.
- Per-mount client state: `struct nfsclclient`, linked from `nfsmount::nm_clp`.
- Open owners: `struct nfsclowner`, keyed by POSIX process-derived owner bytes.
- Opens: `struct nfsclopen`, keyed by file handle under an open owner.
- Lock owners: `struct nfscllockowner`, keyed by lock owner bytes under an open.
- Byte locks: `struct nfscllock`, maintained as ordered, non-overlapping byte ranges.
- Delegations: `struct nfscldeleg`, hashed by file handle and LRU-tracked in `nfsc_deleg`.
- pNFS layouts: `struct nfscllayout`, hashed by MDS file handle and LRU-tracked.
- pNFS file layout segments: `struct nfsclflayout`, split by read/read-write layout lists.
- pNFS device info: `struct nfscldevinfo`, referenced by file layout entries.

The comments at the top define the design choice: open owners and lock owners map to POSIX process identity, trading extra owner structures for natural operation serialization.

## Key Entry Points

- `nfscl_open()` finds or creates an open owner/open, optionally using a delegation.
- `nfscl_deleg()` inserts or finds a delegation for a file handle.
- `nfscl_getstateid()` chooses a delegation, lock, open, or zero stateid for I/O.
- `nfscl_getcl()` finds/creates a clientid and performs SetClientID/session setup as needed.
- `nfscl_getbytelock()` prepares local/server byte-range lock state before LOCK RPCs.
- `nfscl_relbytelock()` updates local lock state before LOCKU RPCs.
- `nfscl_checkwritelocked()` checks whether local state says a process holds a write lock.
- `nfscl_getclose()` decrements open counts on close.
- `nfscl_doclose()` performs server CLOSEs later, usually during vnode inactive handling.
- `nfscl_docb()` handles NFSv4 callback compounds.
- `nfscl_renewthread()` renews leases and performs deferred cleanup, delegation return, layout return, and recovery.
- `nfscl_initiate_recovery()` marks a client for state recovery.
- `nfscl_hasexpired()` handles server-side state expiration.
- `nfscl_umount()` terminates renew state and tears down client state on unmount.
- `nfscl_layout()`, `nfscl_getlayout()`, `nfscl_adddevinfo()`, and `nfscl_layoutcommit()` maintain pNFS layout/device state.

## Open And Delegation Flow

`nfscl_open()` allocates possible owner/open objects before taking global state locks, avoiding sleeping allocation while mutating lists. It then:

1. Gets the NFSv4 client with `nfscl_getcl()`.
2. Builds an owner name from the current process.
3. Checks for a usable delegation if `usedeleg` is set.
4. Selects either delegation-local owner lists or normal client owner lists.
5. Calls `nfscl_newopen()` to insert missing owner/open state.
6. Marks whether an actual server OPEN is required via `NFSCLOPEN_DOOPEN`.

Delegation-local opens are tracked separately under the delegation and later migrated to server state when a delegation is recalled.

## Stateid Selection

`nfscl_getstateid()` prioritizes:

1. Valid delegation stateid for matching file and access mode.
2. Matching lock owner stateid, except for data-server I/O.
3. Matching open owner/open stateid.
4. Any open that satisfies the requested access mode.
5. Zero stateid for non-DS fallback when no open state is needed.

It waits while recovery is active, so I/O does not consume stale or transitional state.

## Clientid Lifecycle

`nfscl_getcl()` creates the per-mount client object and fills:

- owner list
- delegation queue/hash
- layout queue/hash
- device list
- callback identifier
- client identity bytes from host UUID plus mount-specific value

It then acquires an exclusive NFSv4 state lock if SetClientID/session setup is required. It retries transient `STALECLIENTID`, `BADSESSION`, `STALEDONTRECOVER`, and `CLIDINUSE` conditions. Existing client state uses reference counts instead of exclusive locking.

`nfscl_clientrelease()` and `nfscl_clrelease()` release either an exclusive lock or a reference, depending on current lock state.

## Byte-Range Locking

`nfscl_getbytelock()` creates lock owner and lock range objects, checks delegation-local eligibility, checks local conflicts, merges the requested lock into local state, and decides whether the server RPC is needed.

`nfscl_updatelock()` is the core interval-list algorithm. It keeps lock ranges sorted by offset, non-overlapping, and merged when possible. It handles:

- full absorption of existing ranges
- trimming front or back of an existing range
- splitting an existing range into two
- unlock ranges
- same-type contiguous/overlapping merge

`nfscl_localconflict()` and `nfscl_checkconflict()` detect conflicts from other owners when byte ranges overlap and at least one side is a write lock or the new operation is unlock-like.

## Cleanup, Expiry, And Recovery

`nfscl_cleanup_common()` marks open owners defunct after a process exits, or frees empty owners immediately. `nfscl_cleanupkext()` periodically scans for dead processes and empty lock owners, moving releasable lock owners to a temporary list for `ReleaseLockOwner`.

`nfscl_expireclient()` handles `NFSERR_EXPIRED`. It merges delegation-local opens back into normal client lists, discards delegation locks, tries to reopen state that has no unrecoverable locks/share-deny state, and frees unrecoverable opens.

`nfscl_recover()` handles stale clientid/stateid/session cases. It:

1. Exclusively locks client state and marks recovery in progress.
2. Drops all pNFS layouts.
3. Re-establishes the clientid/session.
4. Marks outstanding queued requests `R_DONTRECOVER`.
5. Marks delegations as needing reclaim.
6. Reclaims opens and then locks.
7. Reclaims standalone delegations by synthetic opens.
8. Closes extra opens and returns extra delegations.
9. Sends `RECLAIM_COMPLETE` for NFSv4.1+.
10. Clears recovery flags and wakes waiters.

## Renew Thread

`nfscl_renewthread()` is the background maintenance loop. It:

- renews the MDS lease and DS sessions
- triggers recovery when stale/bad session errors occur
- handles total recall when callback path is down
- frees defunct empty open owners
- processes delegation recalls
- trims old delegations over the high-water mark
- processes layout recalls and stale layouts
- sends layout commits before layout return when required
- frees unused pNFS device info
- returns cleaned/recalled delegations
- periodically releases lock owners for exited processes
- exits only after `NFSCLFLAGS_UMOUNT`

This makes the renew thread both the lease-renewal worker and deferred state garbage collector.

## Callback Handling

`nfscl_docb()` parses callback COMPOUND requests and implements:

- `CB_GETATTR`: returns delegated size/change attributes.
- `CB_RECALL`: marks matching delegations for recall and wakes the renew thread.
- `CB_LAYOUTRECALL`: marks matching pNFS layouts for recall by file, fsid, or all.
- `CB_SEQUENCE`: validates NFSv4.1 callback session sequencing and caches replies.

Unsupported or illegal callback ops are mapped through `nfscl_errmap()`, which restricts errors to protocol-allowed callback error sets.

## Delegation Return Paths

`nfscl_recalldeleg()` moves delegation-local state back to server state. For write delegations it flushes dirty vnode data before returning. It then:

- moves local opens to normal open-owner state with `nfscl_moveopen()`
- replays local byte-range locks with `nfscl_relock()`
- returns errors that should trigger recovery if stale/bad session state is encountered

`nfscl_removedeleg()` and `nfscl_renamedeleg()` are used by remove/rename paths to locate and return relevant delegations, waiting for outstanding delegation I/O and recalling local state first when necessary.

## pNFS Layout Handling

`nfscl_layout()` creates or updates a file layout, merges new file-layout extents into read or read-write lists, and returns a referenced layout.

`nfscl_getlayout()` finds a layout usable for a given offset. It returns either a shared referenced layout when a matching layout segment exists, or an exclusive layout lock when the caller must fetch more layout state.

`nfscl_layoutrecall()` records ordered layout recalls. It orders file recalls before fsid/all recalls and compares wrapping sequence IDs with `nfscl_seq()`.

`nfscl_layoutreturn()` issues `LAYOUTRETURN` for each recall entry. `nfscl_dolayoutcommit()` issues `LAYOUTCOMMIT` for written read-write layout ranges and disables future commits if the server returns `NFSERR_NOTSUPP`.

## Integration Points

This file depends heavily on:

- RPC helpers: `nfsrpc_setclient`, `nfsrpc_openrpc`, `nfsrpc_lock`, `nfsrpc_closerpc`, `nfsrpc_renew`, `nfsrpc_delegreturn`, `nfsrpc_layoutreturn`, `nfsrpc_layoutcommit`.
- vnode/nfsnode helpers: `nfscl_ngetreopen`, `ncl_flush`, `VTONFS`, `NFSTOV`.
- NFSv4 lock helpers: `nfsv4_lock`, `nfsv4_unlock`, `nfsv4_getref`, `nfsv4_relref`.
- mount state from `struct nfsmount`.
- global request queue `nfsd_reqq` for marking stale in-flight requests.
- NFS statistics counters in `nfsstatsv1`.

## Concurrency Notes

- Global state mutations use `NFSCLSTATEMUTEX`.
- Client state has a lock/reference object used for exclusive recovery/setup versus shared users.
- Open owner and lock owner rwlocks serialize operation sequences per owner.
- Delegation/layout I/O uses `nfslock_usecnt` plus `NFSV4LOCK_WANTED` sleeps.
- Several functions intentionally drop `NFSCLSTATEMUTEX` around RPCs and reacquire afterward.

## Risks And Edge Cases

- Many operations rely on correct lock dropping/reacquiring around RPCs; mistakes can cause stale pointers or state races.
- Recovery paths intentionally discard state if reclaim fails, meaning byte locks can be lost.
- `nfscl_updatelock()` is compact but subtle; off-by-one or inclusive/exclusive range assumptions are high risk.
- Delegation recall flush errors from the renew thread can defer recall completion.
- Callback compound parsing must maintain exact XDR cursor state.
- pNFS layout recall ordering depends on sequence wrap logic that the source itself notes as uncertain.
- Some diagnostics use `printf` and panic on invariants that “should never happen.”

## Verification Ideas

- Unit-style tests for `nfscl_updatelock()` interval merge/split/unlock behavior.
- Recovery tests covering stale clientid, bad session, expired state, and no-grace reclaim.
- Callback tests for illegal op/error mapping and `CB_SEQUENCE` reply cache behavior.
- Delegation recall tests with dirty write delegation data and local locks.
- pNFS layout recall/return tests for file/fsid/all recalls and sequence wrap ordering.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clstate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clsubs.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clsubs.c

## Purpose

Provides small support routines for the NFS client module: initialization, module uninitialization policy, directory cookie locking and lookup, vnode lock upgrade/downgrade helpers, attribute-cache validation, and write-verifier commit reset.

## Key Entry Points

- `ncl_init()` initializes async I/O daemon state, the new nfsiod task, and the nfsnode hash table.
- `ncl_uninit()` currently returns `EOPNOTSUPP`; NFS client module unload is explicitly unsupported.
- `ncl_dircookie_lock()` and `ncl_dircookie_unlock()` serialize access to per-directory cookie maps with `NDIRCOOKIELK`.
- `ncl_upgrade_vnlock()` upgrades a shared vnode lock to exclusive and returns the old lock mode.
- `ncl_downgrade_vnlock()` restores the original shared lock when needed.
- `ncl_getattrcache()` validates and returns cached vnode attributes.
- `ncl_getcookie()` maps logical directory offsets to NFS directory cookies.
- `ncl_invaldir()` invalidates directory cookie/verifier state.
- `ncl_clearcommit()` clears `B_NEEDCOMMIT` and `B_CLUSTEROK` on delayed-write buffers after a write verifier change.

## Attribute Cache Logic

`ncl_getattrcache()` computes a timeout based on cached mtime age, mount attribute-cache limits, vnode type, and whether local modifications require flushing. It returns `ENOENT` on cache miss and updates `nfsstatsv1.attrcache_misses`.

On cache hit it:

- updates `np->n_size` and pager size when cached size differs
- preserves locally changed atime/mtime when `NCHG`, `NACC`, or `NUPD` are set
- copies cached attributes into the caller’s `vattr`
- records DTrace attr-cache hit/miss probes

The call to `nfscl_mustflush(vp)` is deliberately made before locking the node mutex.

## Directory Cookie Handling

`ncl_getcookie()` stores NFS readdir cookies in linked `struct nfsdmap` blocks. It treats offset zero or negative offsets as the null cookie. For positive offsets it converts the logical offset to a cookie index based on `NFS_DIRBLKSIZ`, walks/extends the cookie block list, and optionally allocates new blocks when `add` is true.

`ncl_invaldir()` resets EOF offset, cookie verifier, and the first cookie map’s effective cookie count. It does not free all cookie blocks; it invalidates the logical contents.

## Commit Verifier Handling

`ncl_clearcommit()` walks all vnodes on a mount and scans dirty buffer queues. For unlocked dirty buffers marked both `B_DELWRI` and `B_NEEDCOMMIT`, it clears `B_NEEDCOMMIT` and `B_CLUSTEROK`.

This supports server reboot/write verifier changes: unstable writes must be rewritten before later COMMITs can be trusted.

## Integration Points

- Uses `nfscl_mustflush()` from NFSv4 state/delegation logic.
- Uses `ncl_nhinit()` to initialize nfsnode state.
- Uses async daemon globals `ncl_iodwant`, `ncl_iodmount`, `ncl_numasync`, and `ncl_iodmax`.
- Uses vnode/buffer iteration macros and buffer object locks.
- Updates global NFS statistics and DTrace probes.

## Concurrency Notes

- Directory cookie lock is a flag protected by `np->n_mtx` and `msleep`/`wakeup`.
- Attribute cache reads and size adjustments are protected by `np->n_mtx`.
- Commit clearing uses mount vnode iteration plus per-vnode buffer-object locks.
- Vnode lock upgrade/downgrade helpers assert expected starting lock state.

## Risks And Edge Cases

- `ncl_uninit()` leaves unload unsupported, so cleanup paths under `#if 0` are not active.
- Directory cookie invalidation only resets the first map’s end marker; stale allocated maps remain but are logically unreachable until rebuilt.
- Attribute cache timeout behavior depends on local modification flags and delegation flush policy.
- `ncl_clearcommit()` skips locked buffers, so later passes must handle them.

## Verification Ideas

- Attribute-cache tests for modified regular files, directories, zero `n_attrstamp`, and delegation no-flush behavior.
- Directory cookie tests for offset zero, negative offset, sparse lookup without add, and multi-map allocation.
- Write verifier reset tests with locked/unlocked dirty buffers and `B_CLUSTEROK` clearing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clsubs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clvfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clvfsops.c

## Purpose

Implements VFS operations and mount lifecycle for the new NFS client: mount, old `cmount`, unmount, root vnode lookup, statfs, sync, mount sysctl, forced purge, diskless-root mounting, mount option parsing, and option reporting.

It registers the `nfs` VFS with network and server-boundary flags and wires NFS client initialization/uninitialization through `ncl_init()` and `ncl_uninit()`.

## VFS Registration

The file defines `nfs_vfsops` with:

- `vfs_init = ncl_init`
- `vfs_mount = nfs_mount`
- `vfs_cmount = nfs_cmount`
- `vfs_root = nfs_root`
- `vfs_statfs = nfs_statfs`
- `vfs_sync = nfs_sync`
- `vfs_uninit = ncl_uninit`
- `vfs_unmount = nfs_unmount`
- `vfs_sysctl = nfs_sysctl`
- `vfs_purge = nfs_purge`

It declares module dependencies on `nfscommon`, `krpc`, `nfssvc`, and `nfslock`.

## Mount Sizing

`newnfs_iosize()` clamps read, write, and readdir sizes according to protocol version and transport:

- NFSv4: up to `NFS_MAXBSIZE`
- NFSv3 UDP: up to `NFS_MAXDGRAMDATA`
- NFSv3 TCP: up to `NFS_MAXBSIZE`
- NFSv2: up to `NFS_V2MAXDATA`

It then sets `mnt_stat.f_iosize` to at least page size and `NFS_DIRBLKSIZ`.

## Diskless Root Support

The file supports older and newer diskless boot structures:

- `nfs_convert_oargs()` converts old mount args into `nfs_args`.
- `nfs_convert_diskless()` populates `nfsv3_diskless` from old `nfs_diskless`.
- `nfs_mountroot()` configures the boot network interface, optional MTU, optional default gateway, builds the `server:path` root string, and calls `nfs_mountdiskless()`.
- `nfs_mountdiskless()` duplicates the server sockaddr and delegates to `mountnfs()`.

This path assumes it runs once early in boot before normal concurrent NFS client activity.

## Mount Option Parsing

`nfs_mount()` accepts both old `nfs_args` and newer string options. It filters valid options through `nfs_opts`, then handles:

- cache options: `noac`, `actimeo`, `acregmin/max`, `acdirmin/max`
- transport: `tcp`, `udp`, `mntudp`, `conn`, `noconn`, `resvport`
- protocol: `nfsv3`, `nfsv4`, `minorversion`
- security: `sec=krb5`, `krb5i`, `krb5p`, `principal`, `gssname`, `allgssname`
- behavior: `soft`, `hard`, `intr`, `rdirplus`, `nocto`, `noncontigwr`, `pnfs`
- sizing/retry: `rsize`, `wsize`, `readdirsize`, `readahead`, `wcommitsize`, `timeo`, `timeout`, `retrans`
- name cache: `nametimeo`, `negnametimeo`
- addressing: `from`, `hostname`, `addr`, `fh`, `dirpath`

`nfs_mount_parse_from()` parses `server:path`, bracketed IPv6-style syntax, or deprecated `path@server`, but actual address parsing is IPv4-only via `inet_pton(AF_INET)` and hardcoded port 2049. In the `from` path it currently forces NFSv4 over TCP with no initial filehandle, so `mountnfs()` resolves the directory path.

## Mount Update Behavior

For `MNT_UPDATE`, `nfs_mount()` preserves protocol version, security flavor, lockd strategy, and related immutable flags. It warns if an update changes TCP to UDP because outstanding large TCP RPCs can hang after transfer-size mismatch. Updates call `nfs_decode_args()` and do not enter `mountnfs()`.

## Common Mount Initialization

`mountnfs()` allocates and initializes `struct nfsmount`, including variable trailing storage for Kerberos names, directory path, and server principal. It:

1. Initializes buffer queues and per-mount unique client value.
2. Stores mount user ID for Kerberos state operations when non-root.
3. Copies name/path/security strings into trailing storage.
4. Holds mount credentials and initializes socket request mutexes.
5. Installs helper callbacks `nfs_getnlminfo` and `ncl_vinvalbuf`.
6. Sets default timeouts, retry counts, readahead, and write commit size.
7. Decodes final mount args with `nfs_decode_args()`.
8. Connects the RPC socket with `newnfs_connect()`.
9. For NFSv4.1+, gets a clientid early with `nfscl_getcl()`.
10. For NFSv4 path mounts without a filehandle, resolves the mount directory with `nfsrpc_getdirpath()`.
11. Creates and pins the root nfsnode/vnode.
12. Loads root attributes or fallback attributes.
13. Sets NFSv4 lease/renew values and starts the renew thread for v4.1.
14. Loads NFSv3 fsinfo if applicable.
15. Marks `MNT_NFS4ACLS` when supported attributes advertise ACLs.

On failure, it disconnects the socket, frees credentials/auth, destroys mutexes, removes/free client state if allocated, frees sessions, and releases `nfsmount` plus server sockaddr.

## Argument Normalization

`nfs_decode_args()` applies mount flags to `nfsmount`:

- sets/clears read-only mount flag
- forces sensible TCP timeout/retry behavior
- clears `NFSMNT_NOCONN` for TCP
- clears `RDIRPLUS` for NFSv2
- calculates whether socket reconnect/rebind is required
- clamps timeout/retry values
- rounds read/write sizes down to powers of two above `NFS_FABLKSIZE`
- enforces attr-cache min/max ordering
- clamps readahead
- adjusts write commit size
- reconnects UDP sockets when needed
- stores hostname without trailing path component

## Statfs And Fsinfo

`nfs_statfs()` obtains the root vnode, optionally fetches NFSv3 fsinfo, calls `nfsrpc_statfs()`, refreshes root attributes, loads fsinfo and statfs data into the mount, recomputes I/O size, and maps NFSv4 errors through `nfscl_maperr()`.

`ncl_fsinfo()` is the exported helper for fetching and loading NFSv3 transfer parameters and root attributes.

## Unmount

`nfs_unmount()` handles forced and normal unmount:

- forced unmount cancels outstanding requests and stops NFSv4 renewal first
- flushes vnodes, retrying forced `vflush()` up to 30 times
- normal unmount stops NFSv4 state after vnode flush
- detaches async nfsiod assignments for this mount
- disconnects socket and frees mount credentials, address, auth, mutexes, sessions, and `nfsmount`

## Root, Sync, Sysctl, Purge

`nfs_root()` regets the root nfsnode by mount filehandle, loads NFSv3 fsinfo if still missing, forces `VDIR` when vnode type is unset, and marks `VV_ROOT`.

`nfs_sync()` walks mount vnodes and calls `VOP_FSYNC()` on dirty, unlocked vnodes unless the sync is lazy or forced unmount is underway.

`nfs_sysctl()` supports:

- `VFS_CTL_QUERY`: reports `VQ_NOTRESP` when mount state has `NFSSTA_TIMEO`
- `VFS_CTL_TIMEO`: gets/sets initial timeout warning delay with superuser check

`nfs_purge()` cancels in-flight RPC requests so forced unmount can proceed.

## NLM Integration

`nfs_getnlminfo()` extracts lock-manager information from an NFS vnode:

- filehandle and length
- server sockaddr
- whether the mount is NFSv3
- cached file size
- timeout as timeval

This is installed in `nfsmount::nm_getinfo`.

## Option Reporting

`nfscl_retopts()` serializes active mount options into a caller-provided buffer. It reports protocol version, minor version, pNFS, transport, reserved port, connection mode, hard/soft, interruptibility, close-to-open behavior, noncontiguous writes, lockd state, rdirplus, security flavor, attr-cache timeouts, name-cache timeouts, I/O sizes, readahead, write commit size, timeout, and retransmit count.

## Integration Points

- Calls state code in `nfs_clstate.c`: `nfscl_getcl()`, `nfscl_start_renewthread()`, `nfscl_clientrelease()`, `nfscl_umount()`.
- Calls vnode/node code: `ncl_nget()`, `nfscl_loadattrcache()`, `ncl_vinvalbuf()`.
- Calls RPC code: `newnfs_connect()`, `newnfs_disconnect()`, `nfsrpc_fsinfo()`, `nfsrpc_statfs()`, `nfsrpc_getattrnovp()`, `nfsrpc_getdirpath()`.
- Uses global async I/O daemon assignment arrays under `ncl_iod_mutex`.
- Uses diskless boot data from `nfsdiskless.h`.

## Concurrency Notes

- Mount updates mutate `nfsmount` fields and may reconnect sockets under transport locks.
- `mountnfs()` starts renewal only after mount success is effectively committed.
- `nfs_statfs()` uses `vfs_busy()` around root vnode/statfs work.
- `nfs_unmount()` carefully coordinates forced request cancellation, state teardown, vnode flush, nfsiod detachment, and socket destruction.
- `nfs_sync()` restarts vnode iteration when `vget()` races.

## Risks And Edge Cases

- `from` parsing is IPv4-only despite bracket syntax handling.
- Hardcoded NFS port 2049 in `nfs_mount_parse_from()`.
- Update from TCP to UDP is allowed but explicitly warned as potentially hanging threads.
- Root attribute fallback fabricates permissive directory attributes when getattr fails.
- Error cleanup in `mountnfs()` must stay aligned with every initialized field.
- `nfs_sync()` has a documented racy dirty-buffer count check.
- `nfscl_printopt()`/`nfscl_printoptval()` can truncate silently when buffers are too small.

## Verification Ideas

- Mount option parser tests for old `nfs_args`, `from`, explicit `addr`/`fh`, invalid numeric values, security names, and update immutability.
- Failure-injection tests for each `mountnfs()` stage to verify cleanup.
- Diskless-root tests for interface setup, gateway setup, and root path construction.
- Forced unmount tests with outstanding RPCs and assigned nfsiod workers.
- Statfs tests with missing fsinfo, NFSv4 error mapping, and fallback root attributes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clvfsops.c -->