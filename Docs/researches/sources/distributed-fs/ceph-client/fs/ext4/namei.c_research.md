# sources/distributed-fs/ceph-client/fs/ext4/namei.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ext4/namei.c` implements ext4 directory and namespace operations. It covers directory block reads and checksums, htree indexed lookup and insertion, linear directory scanning, casefolded and encrypted filename matching, directory entry creation/deletion, create/mknod/tmpfile/mkdir/rmdir/unlink/symlink/link, normal rename, whiteout rename, exchange rename, and inode operation tables. The source was read as a complete 4249-line file.

## Important APIs, Types, and Functions

The exported or externally used directory helpers include `ext4_dirblock_csum_verify()`, `ext4_handle_dirty_dirblock()`, `ext4_htree_fill_tree()`, `ext4_fname_setup_ci_filename()`, `ext4_search_dir()`, `ext4_find_dest_de()`, `ext4_insert_dentry()`, `ext4_generic_delete_entry()`, `ext4_init_dirblock()`, `ext4_init_new_dir()`, `ext4_empty_dir()`, `__ext4_unlink()`, `__ext4_link()`, `ext4_get_parent()`, and the operation tables `ext4_dir_inode_operations` and `ext4_special_inode_operations`.

Important htree types are `struct dx_root`, `struct dx_node`, `struct dx_entry`, `struct dx_countlimit`, `struct dx_frame`, `struct dx_map_entry`, and `struct dx_tail`. Directory mutation centers on `add_dirent_to_buf()`, `__ext4_add_entry()`, `ext4_dx_add_entry()`, `make_indexed_dir()`, `do_split()`, `ext4_delete_entry()`, and `ext4_rename*()` helpers. Filename matching flows through `struct ext4_filename`, `ext4_fname_setup_filename()`, `ext4_fname_prepare_lookup()`, `ext4_match()`, fscrypt helpers, and Unicode casefold helpers.

## Control Flow

Directory block reads go through `ext4_read_dirblock()`, which rejects reads past `i_size`, handles simulated failures, distinguishes htree index blocks from leaf blocks, verifies metadata checksums when enabled, and returns buffer heads only after format checks appropriate to the expected block type. Lookup first tries inline data, then htree lookup for indexed directories, then a readahead-assisted linear scan. Htree lookup uses `dx_probe()` to validate the root, compute or reuse filename hash, walk index levels by binary search, detect cycles, and return a leaf frame. `ext4_dx_find_entry()` scans the selected leaf and follows hash continuations with `ext4_htree_next_block()`.

Insertion starts in `__ext4_add_entry()`. Inline directories are tried first. Indexed directories use `ext4_dx_add_entry()`, which locates a leaf, tries direct insertion, splits full leaves with `do_split()`, and may split or grow index levels. Non-indexed directories scan blocks for space, convert a single-block directory to htree with `make_indexed_dir()` when the dir_index feature is available, or append a new block with `ext4_append()`. `add_dirent_to_buf()` obtains journal access, inserts the dirent, updates directory ctime/mtime and i_version, updates the dx flag, and dirties the checksummed directory block.

Creation operations allocate a new inode inside an ext4 journal handle, set inode operations and address-space operations, then attach it using `ext4_add_nondir()` or directory-specific setup. `ext4_mkdir()` initializes `.` and `..` through inline or block-backed directory initialization and updates parent directory link counts. `ext4_unlink()` and `ext4_rmdir()` find and delete dirents, update timestamps and link counts, add zero-link inodes to the orphan machinery, and track fast-commit unlink records. Symlink creation prepares fscrypt disk names, chooses fast symlink storage or an allocated data block, then inserts the entry. Hard links increment link count, add a dirent, and remove tmpfiles from the orphan list when first linked.

Rename builds `struct ext4_renament` records for source and destination. Normal rename validates source and target, optionally creates a whiteout inode, prepares `..` updates for moved directories, replaces or creates the target dirent, deletes or whiteouts the old entry, updates link counts and timestamps, and either tracks fast-commit operations or marks directory renames ineligible. `ext4_cross_rename()` handles `RENAME_EXCHANGE` by swapping two existing dirents and updating both `..` entries and parent link counts when directory-ness differs.

## State and Persistence Behavior

Persistent state includes directory data blocks, inline directory data, htree index roots/nodes, directory block checksum tails, dirent hash fields for casefolded encrypted directories, inode link counts, inode timestamps, inode versions, `i_size` and `i_disksize` for directories and symlinks, orphan list membership for failed or unlinked inode cleanup, and fast-commit tracking records. Metadata updates are journaled with JBD2 write access before mutation and dirty metadata calls afterward. Checksum setters are called through `ext4_handle_dirty_dirblock()` and `ext4_handle_dirty_dx_node()` before buffers are committed.

In-memory state includes lookup start hints (`i_dir_start_lookup`), htree frames and temporary hash maps for splitting, fscrypt filename buffers, casefold buffers, inline-data state flags, and dentry cache effects such as `d_splice_alias()`, `d_instantiate_new()`, `d_tmpfile()`, and CI dentry invalidation.

## Dependencies and Integration Points

The file integrates VFS inode operations with ext4 inode allocation, JBD2, ext4 inline data, fscrypt, fsverity-adjacent encryption context checks, Unicode casefolding, quota initialization, fast commits, orphan handling, buffer-head directory I/O, htree readdir storage, project quotas, and ext4 error reporting. It also consumes mount features including metadata checksums, dir_index, filetype, large directory depth, hash-in-dirent, inline data, and fast commit.

## Risks and Edge Cases

Directory code is corruption-sensitive. It must reject invalid rec_len loops, bad checksum tails, htree count/limit mismatches, htree cycles, invalid `.` or `..`, bad inode numbers, and incompatible encryption contexts. Htree insertion must keep leaf blocks balanced, maintain continuation hash bits, and update checksums for both leaves and index nodes. Inline directory conversion during rename can move the dirent being deleted, so rename has a forced reread path. Casefolded encrypted lookup can fall back to linear search when hashes cannot be trusted, and negative dentry caching is avoided for current CI limitations.

Namespace operations have multi-object consistency risks: link counts, orphaning, parent `..`, fast commit records, and directory block updates must stay transactionally aligned. Whiteout rename has rollback logic that resets the source entry and orphans the whiteout if later work fails. Directory renames disable fast commit because replay cannot update `..` entries.

## Test Signals

Relevant signals include fstests for encrypted, casefolded, inline, indexed, metadata-checksummed, and large directories; lookup of hash-collision names; readdir htree ordering; directory split and index growth; mkdir/rmdir link-count limits; unlink orphan recovery; tmpfile link; fast symlink and long symlink paths; normal, whiteout, no-replace, and exchange renames; cross-directory directory renames; project quota inheritance failures; and fault injection for directory block EIO/CRC, journal access failures, inode allocation ENOSPC, and inline-to-block conversion.
