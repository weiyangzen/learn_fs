# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_vnops.c lines 1-9830

## Scope

This chunk covers the first 9,830 lines of illumos' NFSv4 vnode operations implementation. It is in subset A via `sources/os/illumos/illumos-gate`, and it is the main bridge between illumos VFS/vnode/page-cache entry points and NFSv4 COMPOUND operations for open, close, reads, writes, metadata, directory namespace operations, readdir, and the start of VM paging.

The chunk ends inside `nfs4_getapage()` at its local variable declarations. The rest of `nfs4_getapage()` plus later putpage, commit, mmap, lock, ACL, and pathconf code are cross-chunk responsibilities.

## APIs And Entry Points

- Vnode op table: `nfs4_vnodeops_template` registers NFSv4 implementations for open, close, read, write, ioctl, getattr/setattr/access, lookup/create/remove/link/rename/mkdir/rmdir/symlink/readdir/readlink, fsync, inactive, fid, rwlock/rwunlock, seek, page/mmap/pageio/dispose, security attributes, share locks, and vnode events.
- Exported or externally referenced vnode helpers in this chunk include `nfs4_getvnodeops()`, `nfs4_getattr()`, `nfs4_inactive()`, `nfs4_lookup()`, `nfs4_fid()`, `nfs4_rwlock()`, and `nfs4_rwunlock()`.
- NFSv4 compound argument helpers include `nfs4args_lookup_free()`, `nfs4args_lock_free()`, `nfs4args_lockt_free()`, `nfs4args_setattr()`, `nfs4args_setattr_free()`, `nfs4args_verify()`, `nfs4args_verify_free()`, `nfs4args_write()`, and `nfs4args_copen_free()`.
- Main protocol operations implemented here: `nfs4open_otw()`, `nfs4_reopen()`, `nfs4close_otw()`, `nfs4read()`, `nfs4write()`, `nfs4setattr()`, `nfs4openattr()`, `nfs4lookupvalidate_otw()`, `nfs4lookupnew_otw()`, `call_nfs4_create_req()`, `nfs4_remove()`, `nfs4_link()`, `nfs4rename_persistent_fh()`, `nfs4rename_volatile_fh()`, and `nfs4readdir()`.
- VM/page-cache entry points covered to the boundary: `nfs4_getpage()` is complete, and `nfs4_getapage()` begins at line 9823 but continues in the next chunk.

## Control Flow

### Initialization And Vnode Dispatch

The file starts with kernel, RPC, NFS, VM, and autofs dependencies, then declares many local helpers shared by later sections. `nfs4_vnodeops_template` maps illumos VOP names to NFSv4 functions. Several functions are intentionally non-static because ephemeral mount stub vnode ops call them from outside this source file.

### Open, Reopen, Close

`nfs4_open()` rejects wrong-zone access, bypasses OTW open for non-regular files via `nfs4_open_non_reg_file()`, obtains the parent vnode and file name, handles just-created vnodes and DNLC insertion, forces `FWRITE` for truncating opens, and delegates real NFSv4 open work to `nfs4open_otw()`. Shadow vnodes may be exchanged for master vnodes after success.

`nfs4open_otw()` builds several OPEN compounds:

- normal open: `PUTFH(dir), OPEN, GETFH, GETATTR(file)`;
- create without setgid repair: `PUTFH(dir), SAVEFH, OPEN(create), GETFH, GETATTR(file), RESTOREFH, GETATTR(dir)`;
- create with setgid repair: `PUTFH(dir), OPEN(create), GETFH, GETATTR(file), SAVEFH, PUTFH(dir), GETATTR(dir), RESTOREFH, NVERIFY(owner_group), SETATTR(owner_group)`.

It synchronizes open-owner sequence IDs, decides whether an OTW open is necessary for delegations and cached state, handles exclusive create verifiers, converts `vattr_t` to NFSv4 attributes against server-supported attribute masks, sends `rfs4call()`, starts recovery on recoverable errors, handles `OPEN_CONFIRM`, compares returned filehandles with cached vnodes, creates or updates rnodes via `makenfs4node()`, updates open streams and stateids, accepts delegations, updates directory caches, and handles exclusive-create follow-up `SETATTR`. Lost requests are captured by `nfs4open_save_lost_rqst()` for timeout/interruption/forced-unmount recovery.

`nfs4_reopen()` reopens an existing `nfs4_open_stream_t` during recovery or delegation transitions. It chooses `CLAIM_NULL`, `CLAIM_PREVIOUS`, or `CLAIM_DELEGATE_CUR`, can reuse recovered delegation state without OTW open, handles `NO_GRACE`, `GRACE`, `DELAY`, `FHEXPIRED`, `BAD_SEQID`, `WRONGSEC`, `EXPIRED`, and access fallback credentials, verifies that volatile/persistent filehandles still identify the same object, updates open stream stateids and delegation fields, or marks the rnode/open stream failed via `nfs4_fail_recov()`.

`nfs4_close()` releases local or network locks, flushes dirty pages with `nfs4_putpage_commit()` on final writer close, gathers delayed rnode errors, skips OTW close for non-regular files, and then calls `nfs4close_one()` for regular files. `nfs4close_otw()` sends `PUTFH, GETATTR, CLOSE`, updates open-owner seqids, saves lost close requests, starts recovery, invalidates cache on non-recoverable RPC errors, updates close stateid, invalidates the open stream, decrements the open-stream reference obtained at OPEN, and caches post-close attributes.

### Read And Write

`nfs4_read()` validates type, zone, offsets, recovery-error state, and then either bypasses VM caching for `VNOCACHE`/direct I/O or copies through segmap/VPM after `nfs4_validate_caches()`. It waits for cache purges and respects current `r_size`.

`nfs4_write()` validates type/zone/limits, serializes append writes by upgrading to writer lock, checks `RLIMIT_FSIZE`, increments delegation change for write delegations, and enters `r_lkserlock`. It writes either through direct `nfs4write()` with a temporary kernel buffer or through segmap/VPM and `writerp4()`. It throttles dirty-page creation using `r_awcount`, `r_gcount`, and `mi_max_threads`; forces synchronous release for `FSYNC`, `FDSYNC`, noac, swap, or out-of-space state; restores `uio` state on error; and updates local delegated mtime/ctime on success.

`nfs4write()` sends repeated `PUTFH, WRITE` compounds using the current write stateid from `nfs4_get_w_stateid()`. It handles stateid fallback (`OLD_STATEID`, `BAD_STATEID` on delegation), delegation return/reopen, recovery, server short/oversized writes, unstable write verifiers, kstats, attr-cache purge, `R4WRITEMODIFIED`, and local mtime/ctime updates.

`nfs4read()` sends repeated `PUTFH, READ` compounds using `nfs4_get_stateid()`. It supports direct copy into a caller `uio` or a mapped buffer, handles sync versus async stateid retry rules, delegation return on bad delegation stateid, recovery, EOF, kstats, and residual reporting.

### Metadata, Lookup, And Namespace

`nfs4_getattr()` provides fast `ATTR_HINT` answers for size/fsid/rdev from cached rnode fields, flushes dirty pages before mtime queries unless a write delegation makes local mtime authoritative, and then delegates to `nfs4getattr()`.

`nfs4setattr()` flushes dirty data first, optionally builds guarded size-changing compounds using `GETATTR, VERIFY(ctime), SETATTR, GETATTR`, converts vnode and ACL attributes to NFSv4 fattrs, chooses stateid for size changes, retries when ctime verification fails, handles stateid fallback and recovery, purges access and ACL caches on uid/gid/mode changes, invalidates pages after truncation, updates attr/ACL caches from final GETATTR, sets `r_size` on successful size change, and may issue a mode-repair SETATTR after uid/gid changes.

`nfs4_access()` maps VFS read/write/exec requests to NFSv4 access bits, checks read-only mounts, validates caches, tries cached access including adjusted credentials, sends `PUTFH, ACCESS[, GETATTR]`, handles recovery/stale filehandles, caches access results, and retries adjusted credentials for setuid-root semantics.

`nfs4_lookup()` and internal lookup helpers combine DNLC, access cache, directory change verification, referrals, `WRONGSEC` SECINFO, negative caching, `LOOKUPP`, `GETFH`, `GETATTR`, `makenfs4node()`, and `nfs4_make_dotdot()` to maintain close-to-open and directory coherency. `nfs4openattr()` handles xattr directory discovery/creation and caches unsupported xattr state.

Namespace mutations implement POSIX behavior over NFSv4 primitives: `nfs4_create()` uses guarded/exclusive open-create, `call_nfs4_create_req()` handles mkdir/symlink/mknod create compounds, `nfs4_remove()` renames open files to `.nfs*`, `nfs4_link()` creates shadow vnodes for alternate names, and `nfs4rename()` chooses persistent versus volatile filehandle rename flows while protecting active targets and directory `".."` caches.

### Readdir And VM Boundary

`nfs4_readdir()` manages `rddir4_cache` entries, EOF cookie shortcuts, synchronous fill, async readahead, copyout, and next-cookie updates. `nfs4readdir()` sends `PUTFH, READDIR` or adds `LOOKUPP, GETFH, GETATTR(parent)` to synthesize `".."` inode data, handles recovery and cookie verifiers, and preserves mount security flavor around stubs.

`nfs4_bio()` dispatches page I/O to `nfs4read()`/`nfs4write()`, rotates OTW credentials/open streams on `EACCES`, zero-fills EOF tails, maps full beyond-EOF reads to `NFS_EOF`, records stale/write errors, and releases open-stream references.

`nfs4_fid()` returns `EREMOTE`. `nfs4_rwlock()` chooses reader lock for reads and direct I/O without maps/pages, otherwise writer lock. `nfs4_seek()` accepts directory cookies and rejects negative non-directory seeks. `nfs4_getpage()` validates caches, throttles page creation, rejects user accesses beyond EOF, calls `pvn_getpages(nfs4_getapage, ...)`, retries after `NFS_EOF`, and purges stale filehandles on `ESTALE`.

## State And Dependencies

Key mutable state lives in `rnode4_t`: attributes, size, changeid, filehandle, server, delegation fields, open streams, created flag, unlinked-open rename state, symlink/xattr caches, readdir cookies/cache, delayed errors, async write counters, VM map counters, next readahead offset, and write verifiers.

`mntinfo4_t` supplies zone, mount flags, server, transfer sizes, async thread limits, attr-cache timing, filehandle expiry policy, recovery state, kstats, and security flavor state. NFSv4 state objects include open owners, open streams, stateids, delegation records, lost request records, recovery state, and bad-seqid entries.

Major dependencies include illumos VFS/vnode APIs, DNLC, VM/page-cache APIs, RPC/XDR compound dispatch, NFSv4 recovery and delegation helpers, shared filehandle/rnode creation helpers, credential adjustment, ACL/access-cache helpers, kstats, DTrace, and zone checks.

## Risks And Cross-Chunk References

Recovery correctness is the main risk: OTW paths must pair `nfs4_start_op/fop()` with `nfs4_end_op/fop()`, free XDR results, preserve open-owner sequence IDs, and avoid cache-purge/getattr recursion while recovery locks are held. Delegation stateid fallback, lost OPEN/CLOSE requests, volatile filehandle rename, guarded create retransmission behavior, unlink-open `.nfs*` semantics, and delayed page-write errors are especially sensitive.

Directory coherency depends on change attributes, DNLC purge/update, readdir-cache purge, access-cache refresh, and post-op dir attributes. Some mutating compounds intentionally treat the mutation as successful even when later GETATTR fails, then purge caches to force later validation.

`nfs4_getapage()` starts at line 9823 and continues in the next chunk. Later chunks must also cover putpage/commit, mmap/addmap/delmap, pageio/dispose, locking/share locking, ACL/security attributes, pathconf, directory-cache update internals, attr-cache update internals, and local lock recovery helpers.