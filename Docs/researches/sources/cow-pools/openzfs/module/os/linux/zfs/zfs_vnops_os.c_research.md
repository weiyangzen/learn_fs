# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_vnops_os.c

## Read Coverage
Read completely: 4,440 lines, 113,842 bytes.

## Purpose
`zfs_vnops_os.c` is the Linux-specific ZPL operation layer for OpenZFS. It implements exported inode/vnode-style helpers for open/close, lookup, create, tmpfile, remove, mkdir/rmdir, readdir, getattr/setattr, rename, symlink/readlink, link, page-cache writeback/fault reads, dirty inode handling, mmap permission checks, space freeing, and file-handle generation.

## Major Responsibilities
- Implements namespace operations over ZFS directories: lookup, create, tmpfile, remove, mkdir, rmdir, rename, symlink, hard link, and directory iteration.
- Bridges Linux inode/page-cache behavior with ZFS DMU/SA/ZIL state through page update, mapped-read, page fault read, dirty inode, and writeback helpers.
- Enforces ZFS security and metadata policy: ACL checks, FUID support, ephemeral ID validation, readonly/immutable/append-only/nounlink flags, project inheritance, project quota, xattr namespace boundaries, and Linux idmapped mount translation.
- Coordinates ZFS transactions and ZIL logging for namespace and metadata mutations.
- Supports Linux rename extensions: `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, and `RENAME_WHITEOUT`.
- Handles O_TMPFILE creation and later linking from the unlinked set with txg durability semantics.
- Updates Linux inode state from znode/SA state after ZFS metadata mutations.
- Exports the Linux operation helpers consumed by ZPL wrapper files such as `zpl_inode.c`, `zpl_file.c`, and related Linux glue.

## Key Data and Interfaces
- Uses `znode_t` and embedded Linux `struct inode` as paired filesystem/inode state.
- Uses `zfsvfs_t` for mounted dataset state, including objset, ZIL, sync mode, xattr mode, UTF-8/case handling, quota objects, and teardown guards.
- Uses `zfs_dirlock_t` for directory-entry locking and `z_rangelock` for file data/page-cache ranges.
- Uses SA attributes (`SA_ZPL_*`) and bulk SA updates for inode metadata, timestamps, flags, project IDs, link counts, symlink data, and xattr pointers.
- Uses DMU transactions with explicit holds and follows the file header’s ordering rules: enter filesystem, take locks, create/hold tx, assign nonblocking when ZPL locks are held, log before unlocking, commit, then optionally `zil_commit()`.
- Uses Linux page-cache APIs such as `find_lock_page()`, `kmap()`, `flush_dcache_page()`, `clear_page_dirty_for_io()`, `set_page_writeback()`, `end_page_writeback()`, `truncate_inode_pages_range()`, and `truncate_setsize()`.
- Uses Linux VFS idmapping helpers through `zidmap_t`, `zfs_uid_to_vfsuid()`, `zfs_gid_to_vfsgid()`, and inode namespace helpers.

## Control Flow Highlights
- The opening programming-rules block is central: it documents mount verification, delayed `zrele()`, range-lock-before-transaction ordering, `DMU_TX_NOWAIT` with ZPL locks, ZIL logging before unlock, unconditional tx commit, and post-unlock synchronous commits.
- `zfs_open()` enforces append-only write opens and upgrades existing async ZIL records to sync when the first `O_SYNC` open appears.
- `zfs_lookup()` has a fast path for simple non-xattr lookups, handles `.` and empty names, enters xattr directories through `zfs_get_xattrdir()`, enforces directory execute permission, validates UTF-8, and returns held znodes.
- `zfs_create()` handles existing-file open/truncate separately from new object creation; new creation validates FUID/ACL/version state, quotas, xattrs, UTF-8, directory permissions, transaction holds, `zfs_mknode()`, link insertion, ZIL create logging, and sync mode.
- `zfs_tmpfile()` creates an unlinked regular object and inserts it into the unlinked set so it can later be linked or destroyed.
- `zfs_remove()` decides between immediate deletion and deferred unlinked-set removal based on link count, inode references, cached data, file size threshold, xattr state, and external ACL state.
- `zfs_setattr()` is the central metadata mutation path. It handles truncation/extension, uid/gid/project changes, xattr directory propagation, ACL chmod/chown behavior, optional attributes, timestamp updates, quota checks, SA layout upgrades for project IDs, FUID synchronization, and ZIL setattr logging.
- `zfs_rename()` establishes deterministic source/target dirent locking, checks project inheritance and access, prevents directory cycles via parent-lock tree walk, supports exchange and whiteout variants, logs the exact rename flavor, and includes recovery code for partially changed link state.
- `zfs_putpage()` deliberately drops the page lock before taking the range lock, then rechecks page state to avoid Linux page-lock/range-lock inversions. It redirties failed writeback pages and uses ZIL callbacks for synchronous page-clean completion.
- `zfs_getpage()` takes a range lock around page fault reads to avoid races with direct I/O or block cloning that may temporarily clear dbuf data.
- `zfs_fid()` encodes object number and nonzero generation in short ZFS file handles.

## Important Functions
- `zfs_open()` and `zfs_close()` maintain append-only and sync-open semantics.
- `update_pages()` and `mappedread()` keep mmap/page-cache contents coherent with DMU reads.
- `zfs_write_simple()` provides a small kernel-buffer write wrapper around common `zfs_write()`.
- `zfs_zrele_async()` avoids synchronous final `iput()` in unsafe transaction/lock contexts.
- `zfs_lookup()`, `zfs_get_name()`, and `zfs_readdir()` implement lookup, reverse-name lookup, and directory enumeration.
- `zfs_create()`, `zfs_tmpfile()`, `zfs_remove()`, `zfs_mkdir()`, `zfs_rmdir()`, `zfs_rename()`, `zfs_symlink()`, and `zfs_link()` implement namespace mutation.
- `zfs_getattr_fast()` and `zfs_setattr()` expose and mutate Linux inode metadata.
- `zfs_setattr_dir()` propagates ownership/project changes into hidden xattr directory entries.
- `zfs_putpage()`, `zfs_getpage()`, `zfs_dirty_inode()`, and `zfs_inactive()` integrate Linux page-cache and inode lifecycle events with ZFS SA/DMU/ZIL state.
- `zfs_map()` enforces mmap restrictions for immutable, readonly, append-only, and quarantined files.
- `zfs_space()` calls `zfs_freesp()` for file hole punching/truncation-like operations.
- `zfs_fid()` produces exportable ZFS file IDs.

## Invariants and Assumptions
- Every operation that touches live ZFS state must enter the filesystem and verify znodes before using SA handles.
- Final `zrele()`/`iput()` can trigger `zfs_zinactive()` and new transactions, so release timing is part of transaction correctness.
- Directory-entry locks, range locks, parent/name locks, ACL locks, and znode locks must follow the ordering implied by the header comment and operation-specific retry loops.
- ZIL records must be generated while the mutation ordering locks are still held.
- Xattr directory contents must not be linked or renamed into ordinary namespace entries or vice versa.
- Project-inheriting directories constrain hard links and renames to matching project IDs.
- `O_TMPFILE` objects remain in the unlinked set until linked and require txg sync semantics rather than ordinary ZIL link replay.
- Page writeback must preserve dirty data on errors and must not unlock a synchronously written page as clean until its ZIL/txg durability condition has been met.
- Linux inode fields are refreshed after ZFS metadata mutations through `zfs_znode_update_vfs()`.

## Risks and Edge Cases
- `zfs_setattr()` has a large blast radius: ACLs, FUIDs, uid/gid, project IDs, hidden xattr directories, SA upgrades, immutable/read-only policy, timestamps, truncation, and quotas all interact.
- Rename is concurrency-sensitive because it combines dirent locks, directory name locks, parent locks, optional target removal, exchange/whiteout creation, and rollback-style repair paths.
- `zfs_remove()` immediate-delete decisions can be invalidated by concurrent references, xattr changes, ACL changes, or cached page state.
- Page writeback has explicit lock-inversion hazards with `zfs_read()`, `zfs_write()`, truncation, and page fault handling.
- Fault reads must hold range locks because direct I/O and block cloning can transiently clear dbuf data.
- Linux lazytime/dirty-inode behavior means atime may be deferred and later persisted through inactive or dirty-inode handling.
- Case-insensitive/case-preserving rename and lookup behavior depends on UTF-8 normalization flags and exact-match handling.
- Error cleanup for failed namespace changes must preserve link counts, unlinked-set state, inode hash state, and ZIL replay consistency.

## Testing Signals
Useful coverage should include:
- Lookup of ordinary names, empty names, `.`, missing entries, xattr directories, invalid UTF-8, case-insensitive names, and hidden `.zfs` interactions through callers.
- Create/open existing/truncate paths, exclusive create, xattr-directory create restrictions, ACL inheritance, FUID/ephemeral IDs, project quotas, and sync-always behavior.
- O_TMPFILE creation, later link, failed link restoration, and txg sync behavior under normal and failmode-continue pools.
- Remove of small files, large files, files with cached pages, files with xattrs, files with external ACLs, open-but-unlinked files, and directories passed to remove.
- Mkdir/rmdir with permissions, non-empty directories, current-working-directory removal, project inheritance, and case-insensitive flags.
- Rename same-name no-op, case-only rename, directory cycle prevention, cross-superblock rejection, project mismatch rejection, `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, and `RENAME_WHITEOUT`.
- `setattr` for size changes, uid/gid changes, project ID and project-inherit toggles, chmod under restricted ACL mode, immutable/append/nounlink flags, birthtime, AV flags, xattr directory propagation, quota failures, and SA project-ID upgrade.
- Page fault reads, mmap writes, async writeback, sync writeback, writeback failure redirtying, EOF partial pages, concurrent truncate/free-range, and direct I/O/block clone races.
- Dirty inode and inactive processing with lazytime atime, unlinked files, readonly remounts, and rollback-held teardown locks.
- Export file-handle generation and lookup paired with `zfs_vget()`.

## Overall Assessment
This file is the Linux operational core of the OpenZFS ZPL. Its complexity is concentrated at boundaries: Linux VFS semantics, ZFS transactions, ZIL replay requirements, SA metadata layout, ACL/security policy, project quotas, namespace locking, and page-cache coherency. Changes here should be treated as high risk unless backed by tests that combine concurrency, mmap/page writeback, rename, xattr, quota, ACL, tmpfile, and sync-write workloads.
