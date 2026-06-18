# sources/distributed-fs/ceph-client/fs/ext2/dir.c

Purpose: Implements ext2 directory entry parsing, validation, lookup, iteration, insertion, deletion, empty-directory initialization/checking, and directory file operations.

Important APIs/types/functions: Exports `ext2_dir_operations`, `ext2_find_entry`, `ext2_inode_by_name`, `ext2_add_link`, `ext2_delete_entry`, `ext2_make_empty`, `ext2_empty_dir`, `ext2_dotdot`, and `ext2_set_link`. Key helpers include `ext2_check_folio`, `ext2_get_folio`, `ext2_readdir`, `ext2_prepare_chunk`, `ext2_commit_chunk`, `ext2_handle_dirsync`, `ext2_rec_len_from_disk`, and `ext2_rec_len_to_disk`.

Control flow: Directory reads map folios with `read_mapping_folio`, validate the page once with `ext2_check_folio`, then emit entries while honoring `i_version`-based seek-cookie revalidation. Lookup scans from `i_dir_start_lookup`, wrapping around pages. Add/link scans existing and one expansion folio, detects duplicates, uses a free entry or splits a large record, writes the new entry, clears the btree flag, updates times, and optionally syncs directory metadata. Delete merges the target record into the previous record when possible. `make_empty` creates `.` and `..`; `empty_dir` accepts only those entries.

State and persistence behavior: Directory contents persist as block-sized chunks of variable-length `ext2_dir_entry_2` records in page cache/buffer heads. Mutations increment inode version, update size for extension, dirty directory metadata, and sync on dirsync. `file->private_data` stores a per-open 64-bit directory version cookie used by `generic_llseek_cookie`.

Dependencies and integration points: Called by `namei.c` namespace operations and exportfs parent lookup. Uses `ext2_get_block` for block allocation, VFS `dir_emit`, folio/kmap APIs, file leases, ioctl/fasync hooks via `ext2_dir_operations`, and ext2 feature flag `EXT2_FEATURE_INCOMPAT_FILETYPE` for d_type.

Risks: Directory corruption checks must catch zero rec_len, unaligned entries, cross-block spans, bad names, and inode numbers beyond the superblock. Kmap release nesting is subtle because returned entries are mapped folio addresses. Insertion operates past `i_size` while holding the folio lock, so error paths must unlock and release correctly.

Test signals: Directory create/unlink/rename under large directories; readdir after concurrent changes and seeks; corrupted directory images; 64 KiB block rec_len conversion; dirsync mount behavior; filetype feature on/off; empty directory checks before `rmdir`.
