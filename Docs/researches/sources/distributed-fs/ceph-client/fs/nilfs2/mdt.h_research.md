# sources/distributed-fs/ceph-client/fs/nilfs2/mdt.h

## Purpose

`mdt.h` defines the common in-memory contract for NILFS2 metadata files. These files are ordinary-looking inodes from the VFS perspective, but their private state is specialized around metadata block access, persistent allocation entries, per-blockgroup locking, and the segment constructor's shadow-copy mechanism. The header is shared by concrete metadata files such as the DAT, checkpoint file, segment usage file, and ifile.

## Important APIs, Types, and Functions

`struct nilfs_mdt_info` is the private `inode->i_private` payload for metadata inodes. It contains `mi_sem` for read/write metadata operations, `mi_bgl` for blockgroup-scoped locking, entry layout fields (`mi_entry_size`, `mi_first_entry_offset`, `mi_entries_per_block`), a persistent allocator cache, optional `mi_shadow`, and grouping geometry.

`struct nilfs_shadow_map` carries the shadow bmap state, a shadow inode whose page cache holds copied metadata pages, and a list of frozen buffers. This is central to garbage collection and rollback-style DAT handling.

The main exported helpers are `nilfs_mdt_get_block()`, `nilfs_mdt_find_block()`, `nilfs_mdt_delete_block()`, `nilfs_mdt_forget_block()`, `nilfs_mdt_fetch_dirty()`, initialization/destruction helpers, entry sizing, and the shadow-map operations. Inline helpers identify metadata inodes, mark or clear `NILFS_I_DIRTY`, retrieve the current checkpoint number with `nilfs_mdt_cno()`, and get a per-blockgroup spinlock with `nilfs_mdt_bgl_lock()`.

## Control Flow

Callers initialize a metadata inode with `nilfs_mdt_init()`, set its entry format with `nilfs_mdt_set_entry_size()`, then access metadata blocks through `nilfs_mdt_get_block()` or lookup-only variants. Concrete metadata files layer their own entry indexing on top of these calls. Segment construction and metadata mutation mark dirty state through `nilfs_mdt_mark_dirty()`, and later the log writer detects metadata work with `nilfs_mdt_fetch_dirty()`.

Shadow-map flow is explicit: setup, save original metadata pages/bmap into the shadow state, use frozen buffers while the operation proceeds, then either restore, clear, or destroy the shadow map. This lets GC prepare complex changes without permanently committing partial DAT state.

## State and Persistence Behavior

The header models volatile metadata-file state. Persistence occurs indirectly when dirty metadata blocks are collected into NILFS logs and checkpoint/super-root records. `mi_sem` protects logical metadata updates, while `mi_bgl` narrows allocator-style contention. Dirty state is stored in `NILFS_I(inode)->i_state`, not the VFS inode's generic dirtiness alone.

The shadow map deliberately separates tentative metadata state from the original mapping. `nilfs_mdt_restore_from_shadow_map()` can roll back in-memory metadata after failed GC preparation, while later log construction persists only the selected dirty buffers.

## Dependencies and Integration Points

`mdt.h` depends on `nilfs.h`, `page.h`, buffer heads, and blockgroup locks. It is consumed by allocator-like metadata modules (`sufile.c`, `cpfile.c`, `dat.c`, `ifile.c`, palloc helpers) and by the segment constructor in `segment.c`, which queries metadata dirtiness and clears metadata dirty flags after super-root completion.

## Risks and Edge Cases

Metadata-file identity is inferred from non-NULL `inode->i_private`; code that sets private data incorrectly can make normal inodes look like metadata files. Entry layout must match on-disk metadata sizes, or block/offset calculations in concrete metadata files will corrupt entries. Shadow-map handling is a rollback-sensitive path: leaked frozen buffers or forgotten restore/clear calls can leave stale pages or incorrect bmap state.

## Test Signals

Useful coverage includes metadata inode initialization/destruction, missing metadata blocks, dirty flag propagation into segment construction, shadow-map save/restore after injected allocation failures, and blockgroup lock use under concurrent metadata updates. GC tests should exercise DAT shadow-map rollback and successful commit paths.
