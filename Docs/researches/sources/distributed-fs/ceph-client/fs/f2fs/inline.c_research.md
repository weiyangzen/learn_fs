<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/inline.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/inline.c

## Purpose

`inline.c` implements F2FS inline data and inline dentry handling. Inline data stores small regular-file or symlink contents directly in the inode node page. Inline dentries store small directory entry sets in the inode node page. The file provides read, write, truncate, conversion, recovery, lookup, add/delete, empty-dir, readdir, and fiemap support for these inline layouts.

## Important APIs, Types, and Functions

- `support_inline_data()` and `f2fs_may_inline_data()` decide whether an inode can keep inline data, excluding atomic-write use, unsupported modes, oversize data, and post-read-required files such as encrypted/verity cases.
- `f2fs_sanity_check_inline_data()` validates that inline-data inodes do not also have data blocks or node children and flags invalid feature combinations.
- `f2fs_may_inline_dentry()` checks whether a directory can use inline dentries based on mount options and mode.
- `f2fs_do_read_inline_data()`, `f2fs_read_inline_data()`, and `f2fs_write_inline_data()` copy inline file data between page cache folios and inode node pages.
- `f2fs_truncate_inline_inode()` zeros inline bytes after a truncation point and clears `FI_DATA_EXIST` when truncating to zero.
- `f2fs_convert_inline_folio()` and `f2fs_convert_inline_inode()` reserve a real block, write inline data out-of-place, mark roll-forward state, clear inline data, and clear inline flags.
- `f2fs_recover_inline_data()` reconciles inline-data state during recovery when previous and next inode pages disagree.
- Inline directory functions include `f2fs_find_in_inline_dir()`, `f2fs_make_empty_inline_dir()`, `f2fs_try_convert_inline_dir()`, `f2fs_add_inline_entry()`, `f2fs_delete_inline_entry()`, `f2fs_empty_inline_dir()`, and `f2fs_read_inline_dir()`.
- Conversion helpers `f2fs_move_inline_dirents()`, `f2fs_add_inline_entries()`, `f2fs_move_rehashed_dirents()`, and `do_convert_inline_dir()` handle moving inline dentries into block-based directory pages.
- `f2fs_inline_data_fiemap()` reports inline extents to fiemap callers.

## Control Flow and State Behavior

Inline file reads fetch the inode folio, verify the inode still has inline data, then either copy inline bytes into page index 0 or zero nonzero pages. Inline writes fetch the inode folio, wait for node writeback, copy page-cache bytes into the inline region, clear page-cache dirty state, and set `FI_APPEND_WRITE` and `FI_DATA_EXIST` for recovery. Truncation waits for node writeback, zeros the tail in-place, dirties the inode folio, and clears existence state when all inline data is removed.

Conversion from inline data to block data grabs page-cache folio 0 and the inode folio under `f2fs_lock_op()`. If data exists, it reserves logical block 0, validates that the reserved address is `NEW_ADDR`, reads inline bytes into the folio, marks it dirty, writes it out-of-place with hot-data state, waits for writeback, marks the inode for append recovery, clears inline bytes, clears the inline marker in the node folio, decrements inline stats, and clears `FI_INLINE_DATA`. Corrupt non-`NEW_ADDR` mappings set `SBI_NEED_FSCK`, log a warning, call `f2fs_handle_error()`, and return `-EFSCORRUPTED`.

Inline recovery encodes a four-way policy: if both old and new states are inline, copy new inline bytes into the current inode page; if old is inline and new is not, remove inline data and recover blocks; if old is not inline and new is inline, truncate blocks and restore inline data; if neither is inline, leave block recovery to the normal path.

Inline directories use `make_dentry_ptr_inline()` to treat the inline region as a directory bitmap, dir_entry array, and filename area. Adding an entry searches for slots and either initializes a new inode plus dentry in-place or converts the directory if no room remains. Conversion for non-hashed inline directories reserves block 0, zeros the new dentry block, copies bitmap/dentries/names, clears inline state, updates depth and size, and releases backward-compatible inline-xattr reservation when possible. Rehashed directories copy inline data to a temporary buffer, clear inline state, then re-add entries through normal directory insertion; on failure they restore the inline buffer.

## Persistence, Locking, and Integration Points

Inline state is persisted in inode node pages via inline flags, inline data bytes, inline dentry bytes, inode size/depth, `i_inline_xattr_size`, and dnode block address 0 during conversion. The code coordinates with node writeback, page-cache folios, `f2fs_lock_op()`, dnode reservation, extent/block truncation, and recovery flags. It integrates with `file.c` truncation and fallocate conversion, `inode.c` sanity/recovery, directory lookup/insertion code, fiemap, and statistics counters.

## Risks and Edge Cases

Inline conversion has several corruption-sensitive points: inode folio and page-cache folio state must agree, reserved block 0 must be `NEW_ADDR`, unused dentry block bytes must be zeroed to avoid leaking memory, and rollback for rehashed directory conversion must restore inline bytes and size/depth. Inline data is incompatible with encryption/verity/compression post-read behavior and with atomic-write usage. Directory conversion must preserve names, hashes, inode numbers, file types, parent metadata, and xattr reservation compatibility.

## Test Signals

Tests should cover small regular files and symlinks staying inline, conversion when growing past inline capacity, truncate-to-zero and partial truncate, recovery across inline/block transitions, inline directory create/delete/readdir/empty checks, conversion of inline directories with and without hash levels, no-room insertion fallback, corruption detection for unexpected block address 0, fiemap reporting of inline extents, encrypted/verity/compressed rejection, and rollback after simulated conversion failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/inline.c -->
