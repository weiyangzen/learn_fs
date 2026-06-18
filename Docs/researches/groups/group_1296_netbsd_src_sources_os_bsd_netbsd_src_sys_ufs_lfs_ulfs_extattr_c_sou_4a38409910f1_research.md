# Group Research: group_1296_netbsd_src_sources_os_bsd_netbsd_src_sys_ufs_lfs_ulfs_extattr_c_sou_4a38409910f1

Scope checked against `Docs/research_subset_a.md`: subset A includes the complete `sources/os/bsd/netbsd-src` source tree. All 18 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_extattr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_extattr.c

Read completely: 1584 lines.

Implements ULFS/LFS extended attributes using ordinary backing files, avoiding inode/on-disk format changes. Attribute backing files live under `.attribute/system/<name>` or `.attribute/user/<name>` below the mounted filesystem root. Each backing file has a file header followed by fixed-size per-inode slots indexed by inode number.

Core behavior:
- `ulfs_extattr_uepm_init()` / `ulfs_extattr_uepm_destroy()` manage per-mount EA state, mutex, enabled-attribute list, control credential, recursion count, and lifecycle flags.
- `ulfs_extattr_start()`, `ulfs_extattr_stop()`, and `ulfs_extattrctl()` implement mount-level EA lifecycle and privileged control.
- `ulfs_extattr_autostart()` discovers `.attribute/system` and `.attribute/user`, iterates regular files, opens them, and enables each as an attribute.
- `ulfs_extattr_autocreate_attr()` creates a missing backing file on first set, writes a `ulfs_extattr_fileheader`, then enables it.
- `ulfs_getextattr()`, `ulfs_listextattr()`, `ulfs_setextattr()`, and `ulfs_deleteextattr()` are vnode operation front ends that acquire the per-mount EA lock and dispatch to internal helpers.

Data layout:
- Backing files start with `struct ulfs_extattr_fileheader`: magic, version, and max value size.
- Per-inode slot offset is `sizeof(fileheader) + ino * (sizeof(attr_header) + uef_size)`.
- Per-inode headers use `struct ulfs_extattr_header`: flags, length, and inode generation.
- Header fields are byte-swapped when the backing file magic indicates opposite endian order.

Locking and access:
- Enabled attributes are tracked as `struct ulfs_extattr_list_entry` nodes on `ump->um_extattr.uepm_list`.
- The per-mount lock is a mutex with a manual recursion counter because inactive/close paths may re-enter EA code.
- Backing vnodes are locked shared for reads/lists and exclusive for writes/removes unless the backing vnode is the target vnode.
- `extattr_check_cred()` enforces namespace read/write authorization.
- Reads and writes require offset zero; writes replace the whole value and reject values above the backing file limit.
- Lists support both NUL-terminated names and `EXTATTR_LIST_LENPREFIX`.

Risks and notes:
- The file explicitly notes that value writes are not atomic with respect to header writes.
- The single per-mount lock serializes all EA operations and is called out as overly coarse.
- `ulfs_extattr_iterate_directory()` can return on `ulfs_readdir()` error without freeing `dirbuf`.
- `ulfs_extattr_list()` reads the attribute header before locking the backing vnode, despite the helper comment requiring caller locking.
- `ulfs_extattr_list()` can break on `uiomove()` error after locking a backing vnode, bypassing the later unlock.
- `ulfs_extattr_rm()` unconditionally unlocks the backing vnode on exit, even in same-vnode cases where it did not acquire that lock.
- Generation mismatches are treated as `ENODATA`, leaving stale backing slots for later cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_extattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_extattr.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_extattr.h

Read completely: 129 lines.

Defines the ULFS extended-attribute backing-file format, in-memory per-mount structures, command constants, and kernel prototypes used by `ulfs_extattr.c`.

Key definitions:
- `ULFS_EXTATTR_MAGIC`, `ULFS_EXTATTR_VERSION`, `.attribute`, `system`, and `user` define discovery and validation.
- `ULFS_EXTATTR_MAXEXTATTRNAME` fixes attribute names at 256 bytes including NUL.
- `ULFS_EXTATTR_ATTR_FLAG_INUSE` marks an active per-inode attribute slot.
- `ULFS_EXTATTR_UEPM_INITIALIZED` and `ULFS_EXTATTR_UEPM_STARTED` track per-mount state.
- `ULFS_EXTATTR_CMD_START`, `STOP`, `ENABLE`, and `DISABLE` define control operations.

Structures:
- `struct ulfs_extattr_fileheader` stores backing-file magic, version, and per-inode value capacity.
- `struct ulfs_extattr_header` stores per-inode flags, value length, and inode generation.
- `struct ulfs_extattr_list_entry` represents one enabled attribute, including namespace, name, backing vnode, file header, and byte-swap flag.
- `struct ulfs_extattr_per_mount` stores the mount lock, enabled list, held credential, recursion count, and flags.

Risks and notes:
- Permission constants are declared here but actual authorization is delegated to VFS/extattr checks.
- Compatibility depends on the fixed header/slot layout and correct byte-swap handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_extattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_extern.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_extern.h

Read completely: 160 lines.

Central external interface header for the ULFS layer inside NetBSD LFS. It forward-declares kernel structures and publishes vnode, directory, block mapping, quota, VFS, buffer-I/O, and snapshot entry points implemented across `sys/ufs/lfs`.

Major groups:
- Vnode operations: access, advlock, bmap, close, create, getattr, inactive, link, lookup, open, pathconf, print, readdir, readlink, remove, rmdir, setattr, strategy, whiteout, and special/fifo read/write/close variants.
- Block mapping: `ulfs_bmaparray()`, `ulfs_getlbns()`, and `ulfs_issequential_callback_t`.
- Inode helpers: `ulfs_reclaim()` and `ulfs_balloc_range()`.
- Directory helpers: `ulfs_dirbad()`, `ulfs_dirbadentry()`, `ulfs_direnter()`, `ulfs_dirremove()`, `ulfs_dirrewrite()`, `ulfs_dirempty()`, and `ulfs_blkatoff()`.
- Quota helpers: `ulfsquota_init()`, `ulfsquota_free()`, `lfs_chkdq()`, `lfs_chkiq()`, `lfsquota_handle_cmd()`, `lfs_qsync()`, and quota1/quota2 mount/unmount functions.
- VFS helpers: init/reinit/done, start, root, quotactl, and fhtovp.
- Vnode-init and I/O helpers: `ulfs_vinit()`, GOP allocation/update hooks, and `ulfs_bufio()`.
- Snapshot cleanup hook: `ulfs_snapgone()`.

Role:
- This header is the cross-module contract binding ULFS vnode operation code to LFS-specific allocation, quota, and mount code.
- `FORCE` is the shared quota-change flag allowing usage changes independent of limit enforcement.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_inode.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_inode.c

Read completely: 261 lines.

Implements ULFS inode inactive/reclaim handling and block preallocation for LFS vnode writes.

Functions:
- `ulfs_inactive()` handles last-reference processing. It ignores stale-handle inodes with mode zero, strips extended attributes for unlinked inodes, truncates unlinked file data to zero, decrements inode quota usage, clears mode/rdev on deleted inodes, marks inode state changed/updated, writes dirty updates, and asks VFS to recycle mode-zero inodes.
- `ulfs_reclaim()` performs final vnode reclaim cleanup: calls `lfs_update(... UPDATE_CLOSE)` twice, releases the device vnode, frees quota references, frees dirhash state when enabled, and leaves inode cleanup to vnode reclamation.
- `ulfs_balloc_range()` allocates disk blocks across an offset/length range while holding affected VM pages busy, preventing stale disk contents from becoming visible to racing readers.

Allocation path:
- Computes block-aligned and page-aligned ranges.
- Uses `VOP_GETPAGES()` with `PGO_NOBLOCKALLOC`, `PGO_PASTEOF`, and `PGO_GLOCKHELD`.
- Calls `GOP_ALLOC()` while pages are held.
- On success, clears `PG_RDONLY` for pages fully backed by disk blocks and marks pages dirty.
- Releases page busy state and frees the temporary page array.

Risks and notes:
- A comment questions whether the two `lfs_update(... UPDATE_CLOSE)` calls in `ulfs_reclaim()` are both needed.
- On allocation failure, pages are intentionally left cached because they may already contain dirty data.
- Correctness depends on holding pages busy across allocation to avoid stale block exposure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_inode.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_inode.h

Read completely: 232 lines.

Defines ULFS inode-facing macros, LFS resource thresholds, file-handle structures, dinode accessors, indirect block addressing constants, and vnode/inode conversion helpers.

Directory-operation and resource control:
- `MARK_VNODE()` and `UNMARK_VNODE()` map to LFS directory-operation vnode marking.
- Declares `lfs_set_dirop()` and `lfs_unset_dirop()`.
- Defines resource thresholds for buffers, bytes, pages, and directory operations: `LFS_MAX_*`, `LFS_WAIT_*`, `LFS_MAX_FSDIROP()`, and `LFS_STARVED_FOR_SEGS()`.
- Defines reserved-memory block types/counts for segment-writing paths: summaries, superblocks, inode blocks, clusters, clean blocks, and block I/O vectors.

Helpers and layout:
- `IS_IFILE()` identifies buffers belonging to the LFS ifile.
- `VPISEMPTY()` and `WRITEINPROG()` inspect vnode dirty/write state with LFS-specific fields.
- `VTOI()` and `ITOV()` convert between vnode and inode pointers.
- `struct ulfs_ufid` overlays NetBSD fid data with inode and generation.
- `struct lfid` adds an LFS identifier for exported LFS file handles.
- `DIP()`, `DIP_ASSIGN()`, and `DIP_ADD()` abstract ULFS1 32-bit vs ULFS2 64-bit dinode fields.
- `SHORTLINK()` selects inline symlink storage for the active dinode format.
- `S_INDIR()`, `D_INDIR()`, and `T_INDIR()` define logical block positions for single, double, and triple indirect metadata.
- `struct indir` describes logical block paths used by bmap/truncate code.

Risks and notes:
- Dinode macros depend on `ip->i_ump->um_fstype` matching the active dinode union.
- Resource thresholds are heuristic and tied to global buffer/page/vnode pressure.
- `ufid_ino` is explicitly 32-bit despite inode numbers being conceptually wider.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_lookup.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_lookup.c

Read completely: 1248 lines.

Implements ULFS directory lookup, directory-entry insertion/removal/rewrite, directory emptiness checks, corruption reporting, and directory block reads.

Lookup flow:
- `ulfs_lookup()` resolves a pathname component in a locked directory vnode.
- Checks execute permission and read-only mount constraints for delete/rename.
- Consults the name cache first and returns cached hits/misses.
- Requires an exclusive directory lock for uncached scans.
- Stores lookup side results in `dp->i_crap` and increments `i_crapcounter`; comments call this stale-result scheme undesirable.
- Uses `ulfsdirhash` when available for large directory lookup and free-slot search.
- Otherwise scans directory blocks linearly, optionally starting from cached `ulr_diroff` and doing a second pass from the beginning.
- Validates enough record structure for forward progress; full checks run when `lfs_dirchk` is enabled.
- Computes insertion/removal metadata: offsets, previous-entry distance, free slot size, record length, and end offset for truncation.

Directory update helpers:
- `ulfs_direnter()` writes a new directory entry using prior lookup results, allocating a new directory block or compacting an existing slot, updating dirhash state, writing synchronously, updating timestamps, and truncating trailing unused directory space when possible.
- `ulfs_dirremove()` removes an entry or replaces it with a whiteout, updates dirhash state, merges freed record length into the previous entry when possible, decrements the target inode link count, writes the buffer, and calls `ulfs_snapgone()` if a snapshot loses its last name.
- `ulfs_dirrewrite()` repoints an existing entry to a new inode/type, decrements the old inode link count, writes the buffer, marks parent flags, and handles last snapshot reference.
- `ulfs_dirempty()` scans a directory and returns true only when entries are empty/whiteout or valid `.` / `..`.

Support helpers:
- `ulfs_dirbad()` reports corrupt directory entries and panics on writable mounts.
- `ulfs_dirbadentry()` validates record length alignment, block fit, minimum size, name length, and NUL termination.
- `ulfs_direntry_assign()` fills inode, name length, type, name bytes, and trailing NUL without setting record length.
- `ulfs_blkatoff()` reads the filesystem block containing a directory offset, with optional read-ahead controlled by `ulfs_dirrablks`.

Risks and notes:
- Directory corruption on writable mounts is panic-worthy.
- Several comments note obsolete 4.2BSD artifacts and asymmetric link-count behavior.
- `ulfs_dirremove()` decrements link count before buffer write and comments that callers do not account for partial failure.
- In the `LFS_DIRHASH` block, `ulfs_dirremove()` uses `ip->i_lfs` even though `ip` may be null by signature.
- `ulfs_blkatoff()` allocates temporary read-ahead arrays per call.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota.c

Read completely: 1005 lines.

Provides the shared ULFS/LFS quota layer: quota syscall dispatch, inode quota attachment, dquot cache management, and quota1/quota2 mode selection.

Shared state:
- `lfs_dqlock` protects the dquot hash table and reference counts.
- `lfs_dqcv` coordinates quota open/close transitions.
- `dqhashtbl` caches `struct dquot` objects by quota vnode and id.
- `dquot_cache` allocates dquot objects.
- `lfs_quotatypes` names user and group quotas.

Inode integration:
- `ulfsquota_init()` initializes inode dquot pointers to `NODQUOT`.
- `ulfsquota_free()` releases all inode dquot references.
- `lfs_getinoquota()` avoids quota recursion on quota files, maps inode uid/gid to user/group dquots, drops stale dquots after ownership change, and lazily attaches missing dquots.
- `lfs_chkdq()` and `lfs_chkiq()` skip snapshots, then dispatch block/file accounting changes to quota1 or quota2 based on mount flags.

Quotactl dispatch:
- `lfsquota_handle_cmd()` dispatches stat, id/object type stat, quota on/off, get/put/delete, and quota2 cursor operations.
- Ordinary users may query their own quota; management/onoff/cursor operations use `kauth_authorize_system()`.
- Quota1 reports 32-bit, uniform-grace, needs-check restrictions; quota2 reports no restrictions.
- Delete and cursor operations are quota2-only.
- Quota on/off operations are quota1-only when quota2 is inactive.

Dquot cache:
- `lfs_dqinit()`, `lfs_dqreinit()`, and `lfs_dqdone()` initialize, resize, and destroy quota locks, CV, hash table, and pool cache.
- `lfs_dqget()` validates quota mode and quota vnode availability, checks cache, handles races after allocation, inserts a new dquot, and invokes `lfs_dq1get()` or `lfs_dq2get()`.
- `lfs_dqrele()` decrements references, syncs modified dquots before final release, removes final dquots from the hash, destroys their interlock, and returns them to the pool.
- `lfs_qsync()` dispatches sync to quota1 or quota2.

Risks and notes:
- Lock order is central: `dq_interlock -> lfs_dqlock` and `dq_interlock -> dqvp`.
- Several impossible dispatch cases panic with “no support ?”.
- Quota2 sync hooks are stubs because quota2 writes metadata buffers directly.
- Snapshot quota accounting is deliberately skipped to avoid deadlocks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota.h

Read completely: 146 lines.

Defines the common in-core quota object and prototypes shared by the generic dispatcher, quota1, and quota2.

Core structures:
- `struct dq2_desc` records the quota2 metadata location of an on-disk quota entry as logical block number plus block offset.
- `struct dquot` is the cached per-id quota object. It contains hash linkage, flags, type, refcount, id, mount pointer, per-dquot mutex, and a union for quota1 `struct dqblk` data or quota2 location data.

Flags and aliases:
- `DQ_MOD` marks dirty quota1 dquots.
- `DQ_FAKE` marks quota1 entries with no real limits.
- `DQ_WARN(ltype)` records warning state for block/file quota type.
- Shorthand macros expose quota1 fields (`dq_bhardlimit`, `dq_curblocks`, etc.) and quota2 location fields (`dq2_lblkno`, `dq2_blkoff`).
- `NODQUOT` is null.

Role:
- Bridges vnode/inode quota accounting to the two backing quota formats.
- Exposes generic dquot cache functions, quota1 accounting/sync/I/O handlers, and quota2 accounting/get/put/delete/cursor handlers.

Risks and notes:
- The documented lock ordering is essential to avoid deadlocks.
- The `struct dquot` union has different meanings in quota1 and quota2, so callers must dispatch by active quota mode.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota1.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota1.c

Read completely: 868 lines.

Implements deprecated quota1 support for ULFS/LFS. Quota1 stores fixed-size `struct dqblk` records in ordinary quota files indexed directly by user or group id.

Accounting:
- `lfs_chkdq1()` updates block usage. Negative changes subtract and clear warnings. Positive changes first check all relevant dquots against hard/soft limits unless `FORCE` or quota-nolimit authorization applies, then applies increments if all checks pass.
- `lfs_chkiq1()` applies the same pattern to inode/file usage.
- `chkdqchg()` and `chkiqchg()` enforce hard limits, soft-limit grace expiry, grace-timer initialization on crossing, and user-facing warnings/errors.

Mount/unmount:
- `lfsquota1_handle_cmd_quotaon()` opens a quota file, rejects non-regular files, serializes with quota open/close flags, marks mount and vnode quota/system state, stores a held credential, loads default grace times from id 0, and attaches dquots to currently writable vnodes.
- `lfsquota1_handle_cmd_quotaoff()` serializes closing, clears `ULFS_QUOTA`, detaches dquots from vnodes, flushes diagnostics, closes the quota vnode, releases the stored credential, and clears `MNT_QUOTA` if no quota files remain.
- `lfsquota1_umount()` flushes non-system vnodes and turns off each active quota type.

Quotactl handlers:
- `lfsquota1_handle_cmd_get()` reads a dquot, converts `dqblk` to block/file `quotaval` structures, and returns the requested object value.
- `lfsquota1_handle_cmd_put()` updates block/file limits, default grace values, soft-limit timers, fake-limit status, warning flags, and marks the dquot modified.

I/O and sync:
- `lfs_q1sync()` scans mount vnodes and synchronizes modified dquots.
- `lfs_dq1get()` reads the record at `id * sizeof(struct dqblk)` and treats a short empty read as zeroed quota data.
- `lfs_dq1sync()` writes the quota record back and clears `DQ_MOD`.

Risks and notes:
- Quota1 is limited to 32-bit on-disk limits/usage and maps unlimited to zero.
- Disabled legacy `setquota1()` and `setuse()` code remains under `#if 0`.
- Limit checks use legacy encoded semantics; conversion helpers normalize this for the modern quota API.
- Quota file operations intentionally avoid charging the quota file itself to prevent recursion/deadlock.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota1.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota1.h

Read completely: 105 lines.

Defines the legacy quota1 on-disk format and compatibility command constants.

Key constants:
- `MAX_IQ_TIME` and `MAX_DQ_TIME` define one-week default grace periods.
- `QUOTAFILENAME` and `QUOTAGROUP` preserve historical quota file/group names.
- `QCMD()`, `SUBCMDMASK`, `SUBCMDSHIFT`, and `Q_QUOTAON` through `Q_SYNC` define old `compat_50_quotactl` command encoding.

On-disk format:
- `struct dqblk` is the quota1 file record indexed by id.
- Stores 32-bit block hard/soft limits, current block usage, inode hard/soft limits, current inode usage, and 32-bit block/inode expiration times.

Risks and notes:
- The header explicitly marks quota1 as deprecated in favor of quota2.
- Zero represents no limit in the legacy format.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota1_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota1_subr.c

Read completely: 90 lines.

Implements conversion helpers between legacy quota1 `struct dqblk` records and modern `struct quotaval` block/file values.

Functions:
- `dqblk2q2e_limit()` maps legacy limit zero to `UQUAD_MAX` for unlimited; otherwise maps stored `lim` to `lim - 1`.
- `q2e2dqblk_limit()` maps `UQUAD_MAX` back to zero; otherwise stores `lim + 1`.
- `lfs_dqblk_to_quotavals()` fills block and file `quotaval` structures from a `dqblk`.
- `lfs_quotavals_to_dqblk()` writes a `dqblk` from block and file `quotaval` structures.

Risks and notes:
- Comments question whether `qv_grace` is handled correctly; the functions convert expire times but do not populate/store grace duration fields.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota1_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota2.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota2.c

Read completely: 1636 lines.

Implements quota2 support for ULFS/LFS. Quota2 stores quota metadata in special quota inodes referenced by the LFS superblock, with a header, default entry, free list, and hash chains of quota entries.

On-disk access:
- `getq2h()` reads and validates quota file block 0 as `struct quota2_header`.
- `getq2e()` reads a quota entry at logical block/offset and validates alignment and non-short reads.
- `quota2_walk_list()` walks linked lists of entries using callbacks for lookup/delete/cursor enumeration and writes modified buffers when callbacks change parent pointers.
- `quota2_q2ealloc()` allocates an entry from the free list, grows the quota file by a block when needed, initializes new entries with `lfsquota2_addfreeq2e()`, copies defaults, sets id, and inserts into the hash bucket.

Accounting:
- `getinoquota2()` attaches inode dquots, locks all relevant dquots, allocates on-disk entries when needed, and returns locked quota-entry buffers.
- `quota2_check()` handles both block and file accounting. Negative changes subtract usage; positive changes check hard/soft/grace state via `lfsquota_check_limit()`, issue warnings, set grace expiration on soft-limit crossing, and write usage updates if allowed.
- `lfs_chkdq2()` and `lfs_chkiq2()` dispatch block and file accounting.

Quotactl handlers:
- `lfsquota2_handle_cmd_get()` returns default or per-id quota values.
- `lfsquota2_handle_cmd_put()` updates default limits or allocates/updates a per-id entry.
- `lfsquota2_handle_cmd_del()` resets one object type from defaults and frees the quota entry if both object types match defaults and usage is zero.
- `quota2_fetch_q2e()` and `quota2_fetch_quotaval()` read per-id entries through dquot lookup.

Cursor support:
- Defines `struct ulfsq2_cursor` inside the public `quotakcursor` scratch area.
- Cursor operations open, close, rewind, skip idtype, check at-end, and get key/value batches.
- `lfsquota2_handle_cmd_cursorget()` uses two passes: scan hash chains under `lfs_dqlock` to produce keys, then fetch values through dquot lookup without holding the list lock.
- Cursor state tracks default emission, user/group completion, hash position, id position within a bucket, and whether the block half of an odd key/value pair was already returned.

Mount/unmount:
- `lfs_quota2_mount()` checks `lfs_use_quota2`, validates `lfs_quota_magic`, verifies configured quota inode numbers, gets quota vnodes, stores quota vnode/credential pointers, increments writecount, and sets `MNT_QUOTA`.
- `lfsquota2_umount()` closes active quota vnodes and clears quota pointers.
- `lfs_q2sync()` and `lfs_dq2sync()` are stubs because quota2 writes metadata buffers directly.

Risks and notes:
- Locking contract is explicit: entry data require dquot interlock; header/list pointers require global `lfs_dqlock`; order is `dq_interlock -> lfs_dqlock`.
- Corruption cases panic, including invalid header magic/type, truncated quota files, and misaligned entries.
- Cursor iteration returns `EDEADLK` if hash size changes or an entry disappears between key and value passes.
- `lfs_quota2_mount()` stores `l->l_cred` without an explicit credential hold in this file.
- User quota vnode writecount is incremented, but only the group quota vnode visibly gets `VV_SYSTEM` set here.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota2.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota2.h

Read completely: 129 lines.

Defines the quota2 on-disk metadata format and quota limit status codes.

Format:
- `struct quota2_val` stores hard limit, soft limit, current usage, grace expiration time, and grace duration.
- `N_QL` is 2, with `QL_BLOCK` and `QL_FILE`.
- `struct quota2_entry` stores block/file values, next-entry offset for hash/free lists, and owner id.
- `struct quota2_header` stores magic, quota type, hash geometry, default quota entry, free-list head, and a variable-length hash table.
- `Q2_HEAD_MAGIC` validates quota2 metadata.
- `FS_Q2_DO_TYPE(type)` maps quota type to LFS superblock quota flags.
- `off2qindex()` and `qindex2off()` translate between quota-entry offsets and indices after the variable-size header.

Limit status:
- `QL_S_ALLOW_OK`, `QL_S_ALLOW_SOFT`, `QL_S_DENY_GRACE`, and `QL_S_DENY_HARD` classify checks.
- `QL_F_CROSS` reports crossing a soft limit.
- `QL_STATUS()` and `QL_FLAGS()` split status bits.
- `lfsquota_check_limit()` is the shared checker.

Risks and notes:
- The implementation relies on filesystem-independent quota constants matching quota2 indices and uses `CTASSERT()` to enforce this.
- Block 0 layout depends on configured hash size because the header has a variable-length hash table.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota2_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota2_subr.c

Read completely: 130 lines.

Provides quota2 metadata construction, byte-swapping, and limit-check helpers shared by kernel and non-kernel quota2 tooling.

Functions:
- `lfsquota2_addfreeq2e()` turns free space in a quota block into a linked free list of `quota2_entry` records.
- `lfsquota2_create_blk0()` initializes quota block 0: clears the block, writes magic/type/hash geometry, sets default block/file hard and soft limits to unlimited, sets default grace to seven days, and initializes free entries after the hash table.
- `lfsquota2_ulfs_rwq2v()` byte-swaps all fields in a `quota2_val`.
- `lfsquota2_ulfs_rwq2e()` byte-swaps block/file values and owner id in a `quota2_entry`.
- `lfsquota_check_limit()` evaluates `cur + change` against hard and soft limits and grace expiry.

Risks and notes:
- `cur + change` is computed in unsigned arithmetic without explicit overflow guarding.
- `lfsquota2_ulfs_rwq2e()` does not swap `q2e_next`; callers handle list pointers directly.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota2_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quotacommon.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quotacommon.h

Read completely: 98 lines.

Defines quota constants and conversion helpers common to quota1 and quota2.

Shared definitions:
- `INITQFNAMES` supplies string names for user and group quota types.
- `quota_idtype_to_ulfs()` maps public `QUOTA_IDTYPE_USER/GROUP` values to `ULFS_USRQUOTA/ULFS_GRPQUOTA`.
- `quota_idtype_from_ulfs()` maps ULFS quota type constants back to public quota id types.
- Kernel builds declare `lfs_dqinit()`, `lfs_dqreinit()`, and `lfs_dqdone()`.

Risks and notes:
- Conversion helpers return `-1` for unsupported id types; callers must check before indexing quota arrays.
- Helpers are excluded for host tool builds with `HAVE_NBTOOL_CONFIG_H`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quotacommon.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_readwrite.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_readwrite.c

Read completely: 572 lines.

Implements LFS read and write vnode operations using ULFS-derived logic, with UBC paths for regular files and buffer-cache paths for directories, long symlinks, and the LFS ifile.

Read path:
- `lfs_read()` handles regular file reads through UBC, rejects offsets beyond max file size, handles EOF/resid zero cases, and routes directory reads and ifile reads to `lfs_bufrd()`.
- `lfs_bufrd()` reads directory/long-symlink/ifile data through `bread()`/`breadn()`, computes logical block and transfer sizes, avoids copying short-read garbage, and releases buffers.
- `ulfs_post_read_update()` marks access time unless `MNT_NOATIME` is set and forces `lfs_update()` for synchronous reads.

Write path:
- `lfs_write()` handles regular file writes through UBC.
- Enforces append-only behavior, max file size, ifile write prohibition, and zero-length no-op.
- Waits for LFS availability with `lfs_availwait()` and checks the vnode.
- Expands trailing fragments when extending across block boundaries using `ulfs_balloc_range()`.
- Chooses safe allocation with page initialization for holes/partial overwrites, or direct overwrite allocation with `GOP_ALLOC()`.
- Copies data with `ubc_uiomove()`, updates UVM vnode size, and flushes pages for synchronous writes.
- `lfs_bufwr()` writes directories and long symlinks through the buffer cache, reserves space, allocates blocks with `lfs_balloc()`, updates size, writes buffers, and unreserves on exit.

Post-write handling:
- `ulfs_post_write_update()` marks ctime/mtime and relatime atime.
- Clears setuid/setgid bits after successful writes unless authorization allows retaining them.
- On write error, truncates back to original size and restores the caller `uio` offset/resid.
- On synchronous successful writes, calls `lfs_update(... UPDATE_WAIT)`.
- Asserts vnode UVM size and inode size agree.

Risks and notes:
- Comments call out legacy/temporary issues: directory reads from userland, ifile buffer I/O, and simplistic async flushing.
- Regular file writes deny writes to the ifile even if flags are altered.
- Buffer-cache write path asserts directories are written synchronously and that no pages are cached for these vnode types.
- Correctness relies on `ulfs_balloc_range()` avoiding stale block exposure for holes and partial-block writes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_readwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_snapshot.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_snapshot.c

Read completely: 86 lines.

Contains only the ULFS snapshot last-name-removal hook for LFS.

Behavior:
- `ulfs_snapgone(struct inode *ip)` ignores its inode argument and immediately panics with `"reached ulfs_snapgone\n"`.

Context:
- The file is derived from FFS snapshot code but does not implement snapshot machinery for LFS.
- `ulfs_dirremove()` and `ulfs_dirrewrite()` call `ulfs_snapgone()` if an inode with `SF_SNAPSHOT` reaches link count zero.

Risks and notes:
- Any path that removes the last name from an LFS snapshot inode will panic.
- This appears to be an intentional unsupported-snapshot guard rather than functional snapshot cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_snapshot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_vfsops.c

Read completely: 288 lines.

Implements generic ULFS VFS helper operations used by LFS mounts.

Functions:
- `ulfs_start()` currently does nothing and returns success.
- `ulfs_root()` returns the root vnode via `VFS_VGET()` for `ULFS_ROOTINO`.
- `ulfs_quotactl()` handles quota control when quota support is compiled in: marks the mount busy, takes `mnt_updating`, dispatches to `lfsquota_handle_cmd()`, releases the lock, and unbusies the mount. Without quota support it returns `EOPNOTSUPP`.
- `ulfs_fhtovp()` converts an LFS file handle to a vnode after the filesystem validates it. It maps `ENOENT` to `ESTALE`, rejects mode-zero, generation-mismatched, or dead inodes, and returns the locked vnode on success.
- `ulfs_init()` initializes shared ULFS resources once, including quota, dirhash, and extattr subsystems when compiled.
- `ulfs_reinit()` rehashes quota state when enabled.
- `ulfs_done()` tears down shared resources once the init reference count reaches zero.

State and integration:
- `ulfs_initcount` reference-counts global ULFS subsystem initialization across mounts/modules.
- Pulls in LFS accessors, mount state, quota common code, optional dirhash, and optional extattr.
- Old quota command logic remains under disabled `#if 0`.

Risks and notes:
- `ulfs_initcount` is a plain static integer; callers are expected to serialize init/teardown.
- Quota control relies on `mnt_updating` plus `vfs_busy()` to stabilize the mount while passing it to kauth and quota handlers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_vfsops.c -->