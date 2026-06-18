# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/page.h

## Purpose

Declares NILFS-specific buffer state bits and page/buffer helper APIs.

## Main Definitions

- Extended buffer state bits start at `BH_PrivateStart`:
  - `BH_NILFS_Allocated`
  - `BH_NILFS_Node`
  - `BH_NILFS_Volatile`
  - `BH_NILFS_Checked`
  - `BH_NILFS_Redirected`
- Buffer flag helpers are generated for:
  - `nilfs_node`
  - `nilfs_volatile`
  - `nilfs_checked`
  - `nilfs_redirected`

## Main APIs

- Buffer acquisition and discard:
  - `nilfs_grab_buffer()`
  - `nilfs_forget_buffer()`
- Copying:
  - `nilfs_copy_buffer()`
  - `nilfs_copy_dirty_pages()`
  - `nilfs_copy_back_pages()`
- Dirty/page state:
  - `nilfs_folio_buffers_clean()`
  - `nilfs_clear_folio_dirty()`
  - `nilfs_clear_dirty_pages()`
  - `__nilfs_clear_folio_dirty()`
- Diagnostics and accounting:
  - `nilfs_folio_bug()`
  - `NILFS_FOLIO_BUG()`
  - `nilfs_page_count_clean_buffers()`
  - `nilfs_find_uncommitted_extent()`

## Dependencies and Interactions

- Included by `inode.c`, `mdt.c`, `recovery.c`, and `segbuf.c`.
- Provides the common buffer-state vocabulary used for delayed allocation, redirected metadata buffers, verified buffers, and node buffers.
