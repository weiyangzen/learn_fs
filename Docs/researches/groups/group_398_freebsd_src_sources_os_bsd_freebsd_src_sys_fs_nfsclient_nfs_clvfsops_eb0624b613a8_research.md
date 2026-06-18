# Group Research: group_398_freebsd_src_sources_os_bsd_freebsd_src_sys_fs_nfsclient_nfs_clvfsops_eb0624b613a8

Static research for the listed FreeBSD NFS client VFS/vnode headers and NFS server FHA files in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clvfsops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clvfsops.c

## Purpose
Implements FreeBSD's new NFS client VFS operation layer for the `nfs` filesystem type. It handles mount option parsing, diskless root mounting, mount object construction, NFSv4 client/session setup, root vnode creation, statfs/fsinfo refresh, unmount cleanup, mount sync, VFS sysctl handling, forced dismount purge, NLM information extraction, and mount-option reporting.

## Main Interfaces
- Registers `nfs_vfsops` through `VFS_SET(nfs_vfsops, nfs, VFCF_NETWORK | VFCF_SBDRY)`.
- Exports `newnfs_iosize()` to clamp negotiated read/write/readdir sizes and update `f_iosize`.
- Exports `ncl_fsinfo()` for NFSv3 FSINFO probing and mount transfer-size loading.
- Exports `nfscl_retopts()` to format active mount options for user-visible reporting.
- Implements VFS operations: `nfs_mount`, `nfs_cmount`, `nfs_unmount`, `nfs_root`, `nfs_statfs`, `nfs_sync`, `nfs_sysctl`, and `nfs_purge`.

## Key Behavior
- Mount option parsing supports both legacy `nfs_args` and string options, including protocol version, TCP/UDP, cache timeouts, readahead, commit size, Kerberos security flavors, NFSv4 minor version, pNFS, `oneopenown`, TLS, `syskrb5`, and Linux-compatible `nconnect`.
- `mountnfs()` allocates and initializes `struct nfsmount`, copies variable-length Kerberos/mount-path/server-principal strings into trailing storage, initializes socket request state, connects to the server, obtains NFSv4 client/session state when needed, resolves NFSv4 path-based mounts, instantiates the root vnode, loads root attributes/fsinfo, marks ACL/named-attribute support, and enables extra TCP connections after a successful mount.
- NFSv4 path mounts can start with `nm_fhsize == 0`; `nfsrpc_getdirpath()` later fills the root file handle. `syskrb5` may use a fake root file handle until security negotiation allows real lookup.
- `nfs_statfs()` obtains the root vnode, refreshes NFSv3 FSINFO when missing, runs `nfsrpc_statfs()`, loads root attributes, updates mount fsinfo/statfs data, maps NFSv4 errors, and falls back to cached `mnt_stat` for fake-root `WRONGSEC` cases.
- `nfs_mountroot()` configures diskless network state, optional default route, diskless mount arguments, root hostname, and initial time-of-day before calling the same `mountnfs()` path.
- `nfs_unmount()` handles forced and normal unmount differently: forced unmount cancels outstanding RPCs and stops renewal early; successful teardown flushes vnodes, clears nfsiod ownership, waits for forced-dismount RPC cancellation, disconnects MDS/DS sessions, destroys auth/locks, releases credentials, and frees forced-unmount delegations.
- `nfs_sync()` walks dirty vnodes and calls `VOP_FSYNC`, but exits early for lazy syncs and forced dismounts.
- `nfs_sysctl()` exposes VFS query timeout state and tunable console timeout delay.

## Important State
- Allocates `M_NEWNFSREQ` and `M_NEWNFSMNT` memory types.
- Uses global diskless structures `nfs_diskless`, `nfsv3_diskless`, and `nfs_diskless_valid` when NFS root support is not compiled elsewhere.
- Per-mount state includes `nm_sockreq`, `nm_sess`, `nm_clp`, `nm_fh`, `nm_fhsize`, `nm_minorvers`, `nm_privflag`, `nm_newflag`, `nm_aconnect`, `nm_maxfilesize`, transfer sizes, attr/name cache timeouts, TLS certificate name, and trailing name/principal storage.
- Sysctls tune IP paranoia/no-connection defaults, server-down message delays, diskless status, and debug behavior when compiled.

## Dependencies
Depends on FreeBSD VFS mount/vnode APIs, kernel sockets/routing, diskless NFS boot data, RPCSEC TLS availability, NFS client RPC helpers, NFSv4 client/session state helpers, pNFS data-server session structures, nfsiod globals, and common NFS mount/socket abstractions from `nfs_mountcommon.h`.

## Risks and Edge Cases
- Mount option validation is security- and protocol-sensitive: `nconnect` and `syskrb5` are restricted to NFSv4.1/4.2, TLS requires kernel TLS RPC support, and mount updates cannot change protocol/security/lock strategy.
- Variable-length `struct nfsmount` trailing storage depends on exact size and offset calculations for Kerberos names, NFSv4 dirpath, and server principal.
- Switching an updated mount from TCP to UDP is explicitly warned as capable of hanging threads with large in-flight RPCs.
- Fake root file handles and `WRONGSEC` fallback intentionally let mounts/statfs proceed before the real root file handle is available.
- Unmount teardown must coordinate VFS vnode flushing, NFSv4 renewal, forced RPC cancellation, nfsiod queues, session lists, auth handles, and delegation structures without leaving `mnt_data` visible too long.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clvfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clvnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clvnops.c

## Purpose
Implements the FreeBSD new NFS client vnode operation layer for NFSv2, NFSv3, NFSv4, NFSv4.1, and NFSv4.2. It bridges VFS vnode operations to buffer-cache I/O, NFS RPC helpers, NFSv4 state/delegation/locking, pNFS data-server I/O, close-to-open coherency, namecache validation, extended attributes, and newer NFSv4.2 file operations.

## Main Interfaces
- Registers `newnfs_vnodeops` and `newnfs_fifoops`, with signal-deferred bypass wrappers around full nosig operation vectors.
- Implements normal vnode ops for access, lookup, open, close, getattr, setattr, read, readlink, create, mknod, remove, rename, link, symlink, mkdir, rmdir, readdir, strategy, fsync, advisory locks, ACLs, advise, allocate, deallocate, copy file range, ioctl seek-hole/data, extended attributes, and pathconf.
- Exports lower helpers used by bio/node code: `ncl_readlinkrpc()`, `ncl_readrpc()`, `ncl_writerpc()`, `ncl_removeit()`, `ncl_readdirrpc()`, `ncl_readdirplusrpc()`, `ncl_commit()`, and `ncl_flush()`.

## Key Behavior
- Access checks use NFSv3/v4 `ACCESS` RPCs with per-UID `n_accesscache` entries and KDTRACE probes. NFSv2 falls back to local mode checks plus a root-read probe to catch root-squash style denial.
- `nfs_open()` performs NFSv4 `OPEN` before cache validation, enforces close-to-open coherency by comparing cached mtime/change attributes, invalidates buffers when local or remote changes are detected, tracks direct I/O opens with `NNONCACHE`, records write credentials for later pageout, and flushes executable text mappings before execution.
- `nfs_close()` cleans dirty pages, flushes/commits modified buffers according to protocol and mount policy, updates NFSv4 change attributes, sends NFSv4 `CLOSE`, returns delayed write errors, and unwinds direct I/O state.
- `nfs_getattr()` prefers the attribute cache, can prime the access cache, overlays local delegation modify time, and maps NFSv4 protocol errors. `nfs_setattr()` validates supported flags, handles truncation through `ncl_meta_setsize()` and `ncl_vinvalbuf()`, rolls back size on RPC failure, and updates delegation/local modification time.
- `nfs_lookup()` integrates namecache hits, negative cache validation, parent directory mtime/ctime checks, named attribute directories, NFSv4 remove-in-progress waits, dot/dotdot locking rules, RPC lookup, vnode instantiation, stale-attribute suppression using `n_localmodtime`, and cache insertion with timestamps.
- Create-like operations issue protocol-specific RPCs, load parent/child post-op attributes when available, use lookup fallback when no file handle is returned, update namecache entries when safe, and mark parent directories modified.
- Remove and rename implement sillyrename for active unlinked files, cache purging, NFSv4 no-CTO delegation cleanup based on remove status, directory remove-in-progress serialization, and ENOENT-to-success retry handling for idempotent retransmit cases.
- Directory reading validates `DIRBLKSIZ` alignment, uses logical offset to NFS cookie maps, maintains EOF offset cache, supports `READDIRPLUS`, and purges namecache entries at offset zero when readdirplus will repopulate them.
- `ncl_flush()` is the central dirty-buffer write/commit engine. It gathers `B_DELWRI | B_NEEDCOMMIT` buffers, commits ranges with shared or per-buffer credentials, handles stale write verifiers, writes remaining dirty buffers, waits for output under signal/renew-thread constraints, performs pNFS layoutcommit, clears `NMODIFIED` when fully clean, and retries boundedly if buffers remain.
- Advisory locking routes non-v4 locks through lockd or local lockf depending on mount flags; NFSv4 locks call `nfsrpc_advlock()`, flush before unlocking write-locked ranges, wait/retry for blocking locks, and invalidate caches after acquiring locks for RFC3530 coherency.
- NFSv4 ACL operations call `nfsrpc_getacl()` and `nfsrpc_setacl()`, mapping unsupported/remote errors into VFS-visible results.
- NFSv4.2 support includes `VOP_ADVISE`, `VOP_ALLOCATE`, `VOP_DEALLOCATE`, server-side copy/clone with fallback to generic copy, `FIOSEEKDATA`/`FIOSEEKHOLE`, and RFC8276 user extended attributes.
- `nfs_pathconf()` probes server capabilities for pathconf values, ACL models, named attributes, clone block size, case-insensitivity, and seek-hole support; it fakes stable defaults for older protocols and unsupported names.

## Important State
- Sysctls tune access-cache timeout, access-cache priming, commit-on-close, clean-pages-on-close, direct I/O behavior, dirty-page retry, direct-I/O mmap allowance, and maximum allocate/deallocate RPC length.
- Uses `struct nfsnode` flags including `NMODIFIED`, `NWRITEERR`, `NNONCACHE`, `NDELEGMOD`, `NREMOVEINPROG`, `NREMOVEWANT`, `NNOLAYOUT`, `NWRITEOPENED`, `NHASBEENLOCKED`, `NDSCOMMIT`, `NMIGHTBELOCKED`, and `NNAMEDNOTSUPP`.
- Uses `struct nfsmount` flags/private flags for protocol version, no-CTO, pNFS, one-open-owner, no-copy, no-consecutive-copy, seek support/tested, no-xattr, no-advise, no-allocate, no-deallocate, and clone block size.
- Tracks local modification time (`n_localmodtime`) to reject stale RPC attributes that race with local size-changing operations.

## Dependencies
Depends on VFS vnode/namecache/locking APIs, buffer cache and VM pager APIs, `lockf`/lockd integration, NFS client RPC entry points from `nfs_clrpcops.c`, node and mount definitions in `nfsnode.h`/`nfsmount.h`, pNFS layout/data-server helpers, NFSv4 delegation/state helpers, KDTRACE macros, FreeBSD extattr/ioctl/pathconf APIs, and kernel credential handling.

## Risks and Edge Cases
- Cache coherency spans attribute stamps, mtime/change attributes, namecache timestamps, directory cookies, delegation state, dirty buffers, and close/open flushes; small changes can regress stale-data or excessive-RPC behavior.
- `ncl_flush()` has high deadlock and data-loss sensitivity because it interleaves buffer locking, commit RPCs, signal handling, async output waits, verifier recovery, pNFS layoutcommit, and vnode dirty-state clearing.
- NFSv4 named attribute handling changes lookup/create directory targets and disables namecache insertion; incorrect flag handling can return normal files for named-attribute paths or vice versa.
- Copy/clone has many fallbacks: intra-file clone constraints, cross-mount rejection, output credential retry, consecutive-copy fallback, stale verifier restart, and permanent mount disablement for unsupported server behavior.
- Extended attribute errors are protocol-specific and update a mount-wide `NOXATTR` flag on unsupported/illegal operation replies.
- Sillyrename intentionally approximates local unlink semantics over NFS but has race windows and depends on later inactive cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clvnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_kdtrace.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_kdtrace.h

## Purpose
Declares FreeBSD DTrace/KDTRACE probe IDs and probe-call macros for NFS client access-cache and attribute-cache events.

## Main Interfaces
- Declares access-cache probe IDs for flush done, get hit, get miss, and load done.
- Declares attribute-cache probe IDs for flush done, get hit, get miss, and load done.
- When `KDTRACE_HOOKS` is enabled, macros call hook function pointers from `<sys/dtrace_bsd.h>` only when the corresponding probe is registered.
- When `KDTRACE_HOOKS` is disabled, all macros compile to no-ops.

## Integration
Used by `nfs_clvnops.c` and related client cache code to instrument access-cache hits/misses/loads and attribute-cache invalidation/hits/misses/loads without adding runtime side effects when tracing is disabled.

## Risks
- Probe macro argument expressions must not be required for side effects, because the disabled path expands to nothing.
- The enabled path depends on the DTrace hook function pointer signatures matching the macro arguments exactly.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_kdtrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfsmount.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfsmount.h

## Purpose
Defines `struct nfsmount`, the per-mount state object for FreeBSD's new NFS client, plus mount-private flags, kernel-only new mount flags, and field/offset helper macros.

## Main Data
- Embeds `struct nfsmount_common nm_com` for shared NFS/NLM mount state such as lock, flags, state, timeout, hostname, mount pointer, and callback hooks.
- Stores root file handle, socket/RPC request state, timeout counters, negotiated read/write/readdir sizes, readahead, commit sizing, attr-cache lifetimes, write verifier, async I/O queue accounting, max file size, and namecache timeouts.
- Adds NFSv4/newnfs state: session list, client pointer, TLS certificate name, mount UID, client-id discriminator, NFSv4 fsid, minor version, `nconnect` additional clients, clone block size, and variable-length Kerberos/dirpath/server-principal storage.

## Main Macros And Flags
- `NFS_MAXNCONN` caps `nconnect` at 16.
- Field aliases expose common/socket fields as direct `nm_*` names, including `nm_nam`, `nm_sotype`, `nm_client`, `nm_mtx`, `nm_flag`, `nm_state`, `nm_mountp`, and callbacks.
- Private flags include forced dismount, cancel RPCs, I/O advise through MDS, disabled copy/consecutive-copy/seek/xattr/advise/allocate/deallocate, delegation-issued tracking, and fake-root-file-handle mode.
- New kernel-only mount flags include `NFSMNT_TLS` and `NFSMNT_SYSKRB5`.
- `NFSMNT_DIRPATH()` and `NFSMNT_SRVKRBNAME()` compute offsets into trailing variable-length name storage.
- `VFSTONFS(mp)` converts a mount to its `struct nfsmount`.

## Integration
Consumed by mount setup, VFS/vnode operations, RPC connection logic, NFSv4 state/session code, pNFS layout/data-server paths, lockd/NLM integration, and mount option reporting.

## Risks
- The trailing `nm_name[1]` allocation must be sized and indexed consistently with `nm_krbnamelen`, `nm_dirpathlen`, and `nm_srvkrbnamelen`.
- Additional `nconnect` RPC clients are protected through `nm_sockreq.nr_mtx`; users must preserve that lock discipline.
- Private flags are used as mount-wide capability disablement after protocol failures, so accidental setting can permanently degrade a mount until remount.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfsmount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfsnode.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfsnode.h

## Purpose
Defines `struct nfsnode`, the NFS client equivalent of an inode attached to each active vnode, plus structures for sillyrename, directory cookie maps, access-cache entries, flag bits, conversion macros, and client vnode helper prototypes.

## Main Data
- `struct sillyrename` stores deferred unlink state: task, credential, parent directory vnode, generated `.nfs...` name, and name length.
- `struct nfsdmap` maps logical directory offsets to NFS cookies in chunks of `NFSNUMCOOKIES`, with v3 and v4 cookie storage variants.
- `struct nfs_accesscache` caches an `ACCESS` result mode for one UID with a timestamp.
- `struct nfsnode` stores mutex-protected vnode state: file size, modification revisions, cached attributes, attr-cache timestamp, access cache, previous modify time, file handle pointer, vnode/parent pointers, lockf pointer, saved write error, special-file timestamps or directory cookie verifier, directory EOF or mtime, sillyrename pointer or cookie list, direct I/O count, NFSv4 change attribute, NFSv4 name metadata, write credential, cached open stateid, and last local modification time.

## Flags
Important `n_flag` bits cover directory cookie serialization, modified buffers, delayed write errors, create/truncate markers, size/cache invalidation, non-cacheable direct I/O, special-file access/update/change, delegation modification/recall, remove-in-progress waiters, node sleep lock, pNFS layout denial, write-open tracking, lock history, DS commit requirement, possible lock state, and openattr unsupported state.

## Interfaces
- `VTONFS(vp)` and `NFSTOV(np)` convert between vnode and nfsnode.
- `NFS_TIMESPEC_COMPARE()` compares timestamps.
- Kernel prototypes cover page I/O, write, inactive/reclaim, sillyrename removal, node lookup/creation, directory cookie mapping, directory invalidation, vnode lock upgrade helpers, and directory cookie lock/unlock.

## Integration
Used directly by `nfs_clvnops.c` for nearly every vnode operation and by node-cache, bio/page, NFSv4 state, pNFS, and directory-cookie code elsewhere in the client.

## Risks
- Several unions reuse the same storage for special-file timestamps, directory cookie verifier, directory EOF offset, sillyrename pointer, and cookie lists; callers must respect vnode type.
- Most fields are protected by `n_mtx`; missed locking can corrupt file size, cached attributes, flags, direct I/O counters, access cache, cookie state, and delayed write errors.
- `n_localmodtime` is a coherency guard against stale RPC attributes racing local size changes; bypassing it can install older size/mtime data.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfsnode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nlminfo.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nlminfo.h

## Purpose
Defines `struct nlminfo`, a small per-process/per-locking-context carrier for NLM-based advisory locking state.

## Main Data
- `msg_seq`: sequence counter for lock requests.
- `retcode`: return code from lock requests.
- `set_getlk_pid` and `getlk_pid`: PID bookkeeping for `F_GETLK`-style interactions.
- `pid_start`: process start time used to disambiguate lock ownership across PID reuse.

## Integration
Used by NFS/NLM locking code outside this group and populated through client mount/vnode information for lockd interactions.

## Risks
The structure is simple; correctness depends on external NLM/lockd code updating sequence, return code, and PID identity fields consistently.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nlminfo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_fha_new.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_fha_new.c

## Purpose
Implements the NFS server File Handle Affinity scheduler for NFSv2/v3 requests. FHA assigns incoming RPC requests to `nfsd` service threads based on file-handle identity, read/write offset locality, exclusive-vs-shared operation class, and per-file/per-thread load limits.

## Main Interfaces
- `fhanew_assign(SVCTHREAD *this_thread, struct svc_req *req)` chooses and locks the service thread that should receive a request.
- `fhanew_nd_complete(SVCTHREAD *thread, struct svc_req *req)` releases request accounting after the operation completes.
- VNET init/uninit functions allocate/destroy per-vnet FHA state.
- Sysctls under `vfs.nfsd.fha` expose enable, read-locality, write-locality, bin shift, max nfsds per file handle, max requests per nfsd, and a text stats dump.

## Key Behavior
- Initialization allocates `struct fha_params`, initializes `FHA_HASH_SIZE` slot mutexes, sets server name `nfsd`, and loads default tuning values from the header.
- Request extraction accepts only NFS program requests for versions 2 and 3. NFSv2 procedure numbers are translated to v3-style procedure numbers through `newnfs_nfsv3_procid`.
- File handles are parsed from the request XDR without blocking. The scheduler compresses a variable-length file handle into a 64-bit affinity key by XORing bytes into rotating 8-byte lanes.
- Read/write offsets are parsed for `READ` and `WRITE`; requests without meaningful offsets keep offset zero. Procedures are classified as shared or exclusive based on whether they can contend over file state.
- `fha_hash_entry_lookup()` finds or creates a per-file-handle hash entry under the appropriate slot mutex.
- Thread selection prefers an already-associated thread when exclusive operations are active, otherwise tries locality within `1 << bin_shift` bytes, respecting `max_reqs_per_nfsd`. If no locality match is available, it either attaches the current thread up to `max_nfsds_per_fh` or chooses the least-loaded existing thread.
- Assignment stores the file-handle entry and operation metadata in `svc_req` scratch fields, increments per-entry and per-thread counters, records the offset in `SVCTHREAD::st_p3`, and returns with the selected thread lock held.
- Completion decrements shared/exclusive and thread request counters, removes idle threads from the file-handle entry, and deletes the entry when no requests or threads remain.
- The stats sysctl walks all hash slots and prints file-handle entries, shared/exclusive counts, thread counts, thread offsets, and per-thread request counts.

## Important State
- Uses VNET-local `fhanew_softc` and `nfsfha_ctls`.
- `struct fha_hash_entry` tracks one affinity file handle, number of shared/read-write operations, number of exclusive operations, associated service threads, and its slot mutex.
- `SVCTHREAD` scratch fields are used for FHA state: `st_p2` is per-thread outstanding request count for an entry and `st_p3` is last offset; `svc_req` scratch fields hold the hash entry, lock type, and offset.

## Dependencies
Depends on FreeBSD RPC server thread/request structures, NFS XDR helpers (`NFSM_DISSECT_NONBLOCK`, `newnfs_realign`, `fxdr_hyper`), NFS procedure constants, VNET sysinit/sysuninit, sysctl/sbuf APIs, mutex/list primitives, and the shared header `nfs_fha_new.h`.

## Risks and Edge Cases
- FHA only applies to NFSv2/v3. NFSv4 or non-NFS RPCs fall back to the current service thread.
- Request parsing is best-effort; malformed or unsupported requests get a synthetic incrementing file-handle key and exclusive default behavior.
- The scheduler stores state in generic RPC scratch fields, so it depends on no other server layer reusing those fields for the same request/thread lifecycle.
- Hash entries are destroyed only when both operation counts and associated thread counts reach zero; accounting mismatches trigger assertions or leaks.
- Offset locality is only approximate because file handles are compressed into 64 bits and locality is measured by last thread offset rather than full per-stream history.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_fha_new.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_fha_new.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_fha_new.h

## Purpose
Declares the public data structures, defaults, constants, and entry points for the FreeBSD NFS server File Handle Affinity scheduler implemented in `nfs_fha_new.c`.

## Main Definitions
- `FHANEW_SERVER_NAME` sets the server name to `nfsd`.
- Default sysctl values enable FHA, read locality, and write locality; set bin shift to 22 bytes of locality distance; cap default threads per file handle at 8; and leave per-thread request limit unlimited.
- `FHA_HASH_SIZE` is 251 hash buckets.
- `struct fha_ctls` stores runtime tuning knobs.
- `struct fha_hash_entry` tracks one file-handle affinity key, shared/exclusive operation counts, associated service-thread list, and its protecting mutex.
- `struct fha_hash_slot` contains a list of entries and a mutex.
- `struct fha_info` carries extracted per-request affinity data: file-handle key, offset, lock type, read flag, and write flag.
- `struct fha_params` contains the hash table and server name.
- Declares `fhanew_assign()` and `fhanew_nd_complete()` for RPC server integration.

## Integration
Included by the NFS server FHA implementation and RPC/NFS server code that delegates service-thread choice and completion accounting to FHA.

## Risks
- Constants directly shape scheduler behavior and memory footprint; changing hash size or defaults affects contention and locality globally.
- `struct fha_hash_entry` embeds an RPC service-thread list, so thread lifecycle and completion accounting must match the implementation's expectations.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_fha_new.h -->