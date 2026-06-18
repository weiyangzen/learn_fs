# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/mdt.h

## Purpose

Declares metadata-file private structures, metadata block APIs, dirty helpers, and shadow-map APIs.

## Main Structures

- `struct nilfs_shadow_map`
  - Stores a saved bmap state, a shadow inode for page-cache copies, and a list of frozen buffers.
- `struct nilfs_mdt_info`
  - Holds metadata operation semaphore, blockgroup locks, entry sizing, persistent allocator cache, shadow map, and block-group geometry.

## Main APIs

- Metadata block access:
  - `nilfs_mdt_get_block()`
  - `nilfs_mdt_find_block()`
  - `nilfs_mdt_delete_block()`
  - `nilfs_mdt_forget_block()`
  - `nilfs_mdt_fetch_dirty()`
- Lifecycle:
  - `nilfs_mdt_init()`
  - `nilfs_mdt_clear()`
  - `nilfs_mdt_destroy()`
  - `nilfs_mdt_set_entry_size()`
- Shadow-map operations:
  - `nilfs_mdt_setup_shadow_map()`
  - `nilfs_mdt_save_to_shadow_map()`
  - `nilfs_mdt_restore_from_shadow_map()`
  - `nilfs_mdt_clear_shadow_map()`
  - `nilfs_mdt_freeze_buffer()`
  - `nilfs_mdt_get_frozen_buffer()`

## Inline Helpers and Macros

- `NILFS_MDT()` accesses `inode->i_private`.
- `nilfs_is_metadata_file_inode()` checks whether an inode carries metadata private state.
- `NILFS_MDT_GFP` defines default metadata page allocation flags.
- `nilfs_mdt_mark_dirty()` and `nilfs_mdt_clear_dirty()` manipulate `NILFS_I_DIRTY`.
- `nilfs_mdt_cno()` returns the current checkpoint number from the mounted NILFS object.
- `nilfs_mdt_bgl_lock()` returns a blockgroup lock pointer.

## Dependencies and Interactions

- Depends on `nilfs.h` for inode state definitions and `page.h` for buffer helpers.
- Used by metadata-specific files such as cpfile, sufile, ifile, dat, and by `inode.c` to identify metadata inodes.
