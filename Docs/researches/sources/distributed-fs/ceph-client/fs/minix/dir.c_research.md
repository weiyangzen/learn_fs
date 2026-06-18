# sources/distributed-fs/ceph-client/fs/minix/dir.c

## Purpose

`sources/distributed-fs/ceph-client/fs/minix/dir.c` implements Minix directory file operations and directory-entry manipulation. It reads directory entries, finds names, adds/removes links, initializes empty directories, checks directory emptiness, updates existing links, locates `..`, and resolves inode numbers by name. The source was read as a complete 458-line file for this report.

## Important APIs, Types, and Functions

Important exported objects/functions are `minix_dir_operations`, `minix_find_entry`, `minix_add_link`, `minix_delete_entry`, `minix_make_empty`, `minix_empty_dir`, `minix_set_link`, `minix_dotdot`, and `minix_inode_by_name`. Local helpers include `minix_readdir`, `minix_last_byte`, `dir_commit_chunk`, `minix_handle_dirsync`, `dir_get_folio`, `minix_next_entry`, and `namecompare`. The code handles both `struct minix_dir_entry` and `struct minix3_dir_entry`.

## Control Flow

Directory iteration aligns `ctx->pos` to the fixed Minix directory record size, maps each folio, walks entries up to the last valid byte, chooses v1/v2 or v3 entry layout, and emits nonzero inode entries. Lookup scans folios for a matching fixed-length name. Add-link scans existing pages and one possible expansion page for an empty slot or duplicate, prepares the directory chunk, writes the name and inode, commits the chunk, updates timestamps, and optionally syncs. Delete and set-link prepare and commit one directory record. `minix_make_empty` creates `.` and `..` in the first folio. `minix_empty_dir` accepts only valid `.` and `..` entries.

## State and Persistence Behavior

Directory entries are persistent on disk through the page cache and buffer-head writeback. `dir_commit_chunk` can grow `i_size`, updates the page cache, unlocks the folio, and marks the inode dirty. Dirsync paths call `filemap_write_and_wait` and `sync_inode_metadata`. Folio mappings are transient and must be released with `folio_release_kmap` or `folio_put`.

## Dependencies and Integration Points

It depends on Minix superblock fields `s_dirsize`, `s_namelen`, and `s_version`, folio/page-cache helpers, `minix_prepare_chunk`, generic directory/file operations, and VFS namei/inode code that calls these helpers from Minix `namei.c`.

## Risks and Edge Cases

Fixed-size directory entries require strict alignment and name truncation rules. The v3 directory format has a 32-bit inode and different name offset than v1/v2. Add-link operates beyond `i_size` while holding the target folio lock. Error paths must release kmap/folio locks correctly. `namecompare` rejects longer on-disk names when the lookup name is shorter. Dirsync failures must propagate after metadata changes.

## Test Signals

Run create/unlink/rename/mkdir/rmdir/link lookup tests on Minix v1/v2/v3 images, test maximum and near-maximum name lengths, directory expansion across folios, dirsync mounts, empty-directory checks with malformed `.`/`..`, fsck after directory mutation, and fault injection in `read_mapping_folio` or `minix_prepare_chunk`.
