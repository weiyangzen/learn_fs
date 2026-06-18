# Group Research: DragonFlyBSD VFS Kernel Helpers, Mounting, Lookup, Journaling, Locking, and Quota

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_helper.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_helper.c

## Summary
Provides reusable helper routines for filesystem VOP implementations: UNIX permission checks, flag changes, create/chmod/chown semantics, and an optional VM-backed read shortcut.

## Main Responsibilities
- Implements standard access checking in `vop_helper_access()`.
- Implements inode flag update rules in `vop_helper_setattr_flags()`, including jail and securelevel handling.
- Provides create owner, chmod, and chown helpers for filesystems.
- Implements `vop_helper_read_shortcut()` to satisfy reads directly from valid resident VM pages when `LWBUF_IS_OPTIMAL`.

## Important Behavior
Write access is denied on read-only mounts for regular filesystem objects and denied for immutable files. UID 0 bypasses normal mode checks after those write restrictions. Chmod/chown helpers enforce privilege, group membership, sticky-bit, and SUID/SGID clearing rules.

The read shortcut avoids normal VOP read/buffer-cache paths only when a vnode has a VM object, a known file size, no `UIO_NOCOPY`, and fully valid resident pages. It uses `uiomove_nofault()` and falls back to normal read handling on faults or missing/invalid pages.

## Risks
Quota hooks are explicitly absent in `vop_helper_chown()`. The read shortcut depends on VM object/page state and is compiled to a no-op when `LWBUF_IS_OPTIMAL` is unavailable.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_helper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_init.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_init.c

## Summary
Initializes the VFS subsystem and manages filesystem/vnode operation-vector registration.

## Main Responsibilities
- Initializes VFS globals, namei object cache, vnode subsystem, mount subsystem, vnode locking, and namecache.
- Adds/removes vnode operation vectors with default-op filling.
- Maintains registered filesystem types in `vfsconf_list`.
- Registers/unregisters filesystems and handles VFS module load/unload events.

## Important Behavior
`vfs_add_vnodeops()` can either install a static template or allocate a mount-specific copy, then fills NULL VOP slots from `vop_default`. When journal or coherency operations are present, mount vnode dispatch is redirected through those layered ops.

`vfs_register()` rejects duplicate filesystem names, assigns a type number, re-numbers matching `vfs.<fstype>` sysctl nodes, asserts core mount/root/unmount ops, fills missing optional VFS methods with standard defaults, conditionally adds VFS quota accounting methods, then calls filesystem init.

## Risks
Registration mutates the filesystem’s provided `vfsops` vector in place. Unregister refuses active filesystem types via `vfc_refcount`, but otherwise assumes the registered `vfsconf` and ops remain valid.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_jops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_jops.c

## Summary
Implements the VOP shim layer for DragonFlyBSD’s mount-level VFS journaling. It attaches journal vnode operations to a mount, manages journal instances, and wraps mutating VOPs to emit redo and optional undo records.

## Main Responsibilities
- Handles `MOUNTCTL_*_VFS_JOURNAL` requests in `journal_mountctl()`.
- Attaches/detaches journal vnode ops and per-mount stream-id bookkeeping.
- Installs, restarts, removes, destroys, and reports status for per-mount journals.
- Builds per-operation `jrecord_list` transactions across all attached journals.
- Wraps mutating VOPs: setattr, write, putpages, ACL/extattr set, create, mknod, link, symlink, whiteout, remove, mkdir, rmdir, rename.

## Important Behavior
A mount may have multiple journals. `jreclist_init()` allocates a distinct stream id, creates one `jrecord` per journal, and reports whether any journal wants reversible undo data. `jreclist_done()` pops transaction records, commits or aborts based on VOP error, frees extra records, and releases the stream id.

Wrapped VOPs generally journal after the underlying filesystem operation succeeds. Reversible journals write undo data first for selected operations, such as write overwrite ranges, remove targets, rename overwrite targets, rmdir attributes, and setattr attributes. Redo records include credentials, paths, vnode references, vattrs, UIO data, page lists, or symlink payloads depending on operation.

## Risks
Several areas are explicitly partial: resync returns `EINVAL`, ACL redo/undo is mostly stubbed, extattr undo is not implemented, mmap modification handling is called out as unresolved, and hardlink/path identity handling has XXX notes. Append-write offset reconstruction is described as a hack. `journal_restart()` also has an explicit “XXX lock the jo” note.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_jops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_journal.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_journal.c

## Summary
Provides the low-level journaling transport and record serialization machinery used by `vfs_jops.c`: FIFO reservation, worker threads, stream commit/abort, subrecord nesting, and helpers for serializing VFS objects.

## Main Responsibilities
- Creates/destroys journal writer and optional full-duplex reader threads.
- Manages the per-journal circular memory FIFO.
- Reserves, extends, pads, commits, and aborts raw journal stream records.
- Builds nested logical journal records with `jrecord_*` APIs.
- Serializes paths, vnode attributes, credentials, vnode references, page lists, UIOs, and preimage file data.

## Important Behavior
Records are first reserved as incomplete so the writer thread cannot flush past them. Commit writes trailers and sets begin magic last with memory barriers. If a record cannot grow in place, `journal_extend()` commits the current segment and continues the logical stream in a new raw record.

The writer thread batches complete records and writes them to `jo->fp`. In non-full-duplex mode it treats written bytes as acknowledged. In full-duplex mode the reader thread consumes acknowledgement records and advances `xindex`, allowing restart from the last acknowledged point.

`jrecord_push()` and `jrecord_pop()` support nested records even when FIFO pressure makes parent pointers stale; the stream format tolerates unknown nested record sizes in that case.

## Risks
The file contains many forward-looking XXXs: partial write/nonblocking I/O handling, failure notification, checksum disabled, permanent versus temporary failure policy, SMP thread teardown interlocks, and acknowledgement protocol maturity. `copyin()`/XIO copy paths inside `jrecord_data()` do not propagate copy errors to callers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_journal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_lock.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_lock.c

## Summary
Implements vnode lifecycle, reference handling, activation/inactivation state transitions, VX locking, vnode allocation, recycling, and pressure reclamation.

## Main Responsibilities
- Initializes per-CPU-ish vnode active/inactive lists.
- Tracks active, cached, and inactive vnode counts.
- Implements `vref()`, `vrele()`, `vhold()`, `vdrop()`, and `vfinalize()`.
- Implements VX lock helpers used for reclamation and deactivation.
- Reactivates vnodes with `vget()` and releases locked vnodes with `vput()`.
- Allocates/reuses vnodes in `allocvnode()` and frees pressure candidates through `freesomevnodes()`.

## Important Behavior
Vnodes move among `VS_ACTIVE`, `VS_INACTIVE`, `VS_CACHED`, and `VS_DYING` under carefully documented lock requirements. `vrele()` has a fast lockless decrement path for non-final references, but on a finalizing 1-to-0 transition it acquires the VX lock and calls `vnode_terminate()`.

`cleanfreevnode()` first tries to rebalance active cached vnodes into inactive state, then scans inactive lists for reclaimable candidates. It avoids recycling vnodes with unexpected aux refs, active namecache topology, active real refs, or lock contention. Reusable vnodes are transitioned to `VS_DYING` and returned VX-locked.

## Risks
This is highly concurrency-sensitive code with many invariants around `v_refcnt`, `v_auxrefs`, namecache references, and list state. Several comments note races or limitations, including object races in deactivation weighting and an abandoned alternative `vrele()` implementation that was not safe.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_lock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_lookup.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_lookup.c

## Summary
Contains legacy lookup support, mainly `relookup()`, for old API rename paths.

## Main Responsibilities
- Exposes `varsym_enable` sysctl for variant symlink handling used elsewhere.
- Implements `relookup()` for re-looking up a single pathname component under old VOP lookup semantics.

## Important Behavior
`relookup()` requires `CNP_LOCKPARENT` and `CNP_PDIRUNLOCK` on entry. It locks the directory vnode, rejects empty names and `..`, calls `VOP_OLD_LOOKUP()`, and handles `EJUSTRETURN` as a valid create-missing result unless the operation is read-only.

On success, the directory parent remains locked and the target vnode is locked if it exists. On error, it unlocks the parent if needed and releases any target vnode.

## Risks
This is intentionally old API support for narrow rename conditions. It panics on dot-dot lookups and relies on caller-provided component-name flags being exactly as expected.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_mount.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_mount.c

## Summary
Implements mount structure initialization, mount-list management, mount busy interlocks, vnode-to-mount association, mount vnode scans, vnode flushing, background vnode reclamation, and BIO sync hooks.

## Main Responsibilities
- Initializes mount globals and dummy mount in `vfs_mount_init()`.
- Allocates normal and special vnodes with `getnewvnode()` / `getspecialvnode()`.
- Implements `vfs_busy()` / `vfs_unbusy()` unmount interlocks.
- Allocates root mounts and initializes generic mount structures.
- Maintains mount list and RB lookup by fsid.
- Runs `vnlru` kernel thread to free vnode pressure.
- Scans mount vnode lists with `vmntvnodescan()`.
- Flushes vnodes during unmount with `vflush()`.
- Registers and invokes `bio_ops` sync callbacks.

## Important Behavior
Mount list scans are removal-safe via active scan descriptors. Each scanned mount can be held and optionally busied before callback execution. `vmntvnodescan()` similarly tracks active vnode scans so vnode removal can advance scan cursors safely.

`vflush()` scans all vnodes on a mount with VX locks, finalizes candidates, forcibly detaches when requested, and reports `EBUSY` for still-referenced vnodes unless force-close rules apply. Device vnodes are protected from force-close.

The `vnlru` thread periodically synchronizes vnode counts, frees excess cached/inactive vnodes, and runs namecache hysteresis cleanup.

## Risks
`mountlist_exists()` is documented as a best-effort pointer validity check for quota/PFS use and explicitly does not guarantee the same mount pointer will be used later. Many functions rely on mount tokens and vnode scan interlocks; misuse by callbacks can break assumptions.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_mount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_nlookup.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_nlookup.c

## Summary
Implements DragonFlyBSD’s newer namecache-based pathname lookup API. It resolves paths into `nchandle` objects rather than old-style parent/leaf vnode lock combinations, improving parallelism and simplifying filesystem lookup contracts.

## Main Responsibilities
- Initializes and cleans up `nlookupdata` for normal, `*at`, raw, and early-root contexts.
- Performs full pathname resolution in `nlookup()`.
- Handles `.`, `..`, jail/root boundaries, mount crossings, symlink expansion, and generation-number retries.
- Provides mount glue lookup via `nlookup_mp()`.
- Reads symlink contents with `nreadsymlink()`.
- Checks pathname and target access through `naccess()` and `naccess_lva()`.
- Registers long-term nlookup statistics collection.

## Important Behavior
Intermediate path components require execute/search permission. Last components can request create, delete, rename, open, truncate, exclusive-create, parent-dvp reference, shared locks, no-cross-mount behavior, and other semantics via `NLC_*` flags.

Lookup uses namecache locks rather than directory vnode locks. Intermediate elements are optimized with shared or unlocked cache operations when possible; unresolved entries are locked and resolved. Symlinks allocate a path buffer, concatenate remaining path text, and restart lookup. Mount crossings resolve mount root namecache glue with `VFS_ROOT()` under `vfs_busy()`.

`naccess()` can short-circuit world-searchable directories using `NCF_WXOK`, refresh namecache permission/cache-control flags from `VOP_GETATTR_LITE()`, enforce read-only mount write restrictions, and feed final checks to `naccess_lva()`.

## Risks
The code is intentionally complex and generation-sensitive; many branches retry when namecache generations change or parent directories disappear. There are diagnostic comments around broken chroot/jail traversal, autofs/NFS retry behavior, stale entries, and lock cycling. Access decisions depend on cached namecache flags being refreshed correctly.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_nlookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_quota.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_quota.c

## Summary
Implements optional VFS-level in-memory space accounting and quota-like limit checks by mount, UID, and GID.

## Main Responsibilities
- Maintains per-mount UID and GID accounting trees keyed by ID chunks.
- Enables accounting via `vfs.quota_enabled`.
- Initializes per-mount accounting in `vq_init()`.
- Accounts byte deltas through `vfs_stdaccount()`.
- Implements `sys_vquotactl()` commands for usage export/import and limit setting.
- Selects a valid accounting mount for vnodes with `vq_vptomp()`.
- Checks whether a write is within global, UID, and GID limits with `vq_write_ok()`.

## Important Behavior
Accounting stores total bytes plus per-UID/per-GID chunk arrays in red-black trees. Updates are protected by `mp->mnt_acct.ac_spin`. The userland control interface uses proplib dictionaries and arrays with commands such as `get usage all`, `set usage all`, `set limit`, `set limit uid`, and `set limit gid`.

`vq_write_ok()` treats limit `0` as unlimited. It checks mount-wide limit first, then UID limit, then GID limit.

## Risks
`vq_done()` is a TODO and does not free accounting trees. The code comments call out UID/GID duplication and a potentially stale `v_pfsmp` pointer, mitigated only by `mountlist_exists()`. `sys_vquotactl()` has limited validation and several paths return without releasing all proplib objects.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_quota.c -->