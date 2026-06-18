# sources/distributed-fs/ceph-client/fs/f2fs/dir.c

## Purpose

`dir.c` implements F2FS directory lookup, insertion, deletion, empty-directory checks, inode metadata initialization for directory entries, and readdir. It handles both inline dentries and regular dentry blocks, integrates fscrypt and Unicode casefolding, uses F2FS hash-directory layout, and updates parent/child metadata when links are created or removed.

The file provides the directory file operations table `f2fs_dir_operations`, with `iterate_shared` backed by `f2fs_readdir()` and fsync/ioctl delegated to shared F2FS handlers.

## Important APIs, Types, And Functions

Filename setup is handled by `f2fs_setup_filename()`, `f2fs_prepare_lookup()`, `__f2fs_setup_filename()`, `f2fs_init_casefolded_name()`, `f2fs_free_casefolded_name()`, and `f2fs_free_filename()`. These combine fscrypt name preparation, optional casefolded-name allocation, and F2FS dirhash calculation into `struct f2fs_filename`.

Hash-directory geometry helpers include `dir_blocks()`, `dir_buckets()`, `bucket_blocks()`, and `dir_block_index()`. Lookup helpers include `find_in_block()`, `f2fs_match_name()`, `f2fs_find_target_dentry()`, `find_in_level()`, `__f2fs_find_entry()`, `f2fs_find_entry()`, `f2fs_parent_dir()`, and `f2fs_inode_by_name()`.

Insertion and metadata setup are handled by `f2fs_do_make_empty_dir()`, `make_empty_dir()`, `f2fs_init_inode_metadata()`, `init_dent_inode()`, `f2fs_update_parent_metadata()`, `f2fs_room_for_filename()`, `f2fs_has_enough_room()`, `f2fs_update_dentry()`, `f2fs_add_regular_entry()`, `f2fs_add_dentry()`, `f2fs_do_add_link()`, and `f2fs_do_tmpfile()`.

Link removal and directory scanning are handled by `f2fs_drop_nlink()`, `f2fs_delete_entry()`, `f2fs_empty_dir()`, `f2fs_fill_dentries()`, and `f2fs_readdir()`.

## Control Flow

Lookup begins with `f2fs_find_entry()` or `f2fs_prepare_lookup()`. The name is prepared through fscrypt and optionally casefolded; encrypted no-key names can carry a predecoded hash. `__f2fs_find_entry()` searches inline dentries first when present. For regular directories, it walks hash levels up to `i_current_depth`, and `find_in_level()` selects the bucket from the hash, reads each dentry block with `f2fs_find_data_folio()`, and searches populated bitmap slots with `f2fs_find_target_dentry()`. If casefold compatibility fallback is enabled, a failed hash lookup in a casefolded directory retries with a linear scan.

Creation enters through `f2fs_do_add_link()`. It prepares the filename and, when the task differs from the last lookup task, rechecks the on-disk dentry to avoid lookup/create races from stackable filesystems. `f2fs_add_dentry()` tries inline insertion first under `i_xattr_sem`; if that returns `-EAGAIN`, `f2fs_add_regular_entry()` finds or allocates a regular dentry block at the appropriate hash level. It initializes child inode metadata if an inode is supplied, writes the dentry bitmap/name/inode/type fields, marks the dentry page dirty, records parent inode number in the child, updates the child inode page for new inodes, and updates parent depth/link/time metadata.

Directory inode initialization for new directories calls `make_empty_dir()`, which either uses inline dentry helpers or allocates the first data folio and writes `.` and `..` entries via `f2fs_do_make_empty_dir()`. `f2fs_init_inode_metadata()` also initializes ACLs, security xattrs, fscrypt context, directory-entry name information in the inode page, orphan handling for tmpfile link, and link counts.

Deletion through `f2fs_delete_entry()` updates request time, optionally records strict-fsync transition state, handles inline entries if needed, clears the dentry bitmap slots, marks the dentry folio dirty, and if the entire dentry block becomes empty, truncates the hole and clears page-cache dirty state. Parent times are updated and the victim inode link count is decremented through `f2fs_drop_nlink()`, which adds zero-link inodes to the orphan list.

`f2fs_readdir()` prepares fscrypt readdir state, handles inline directories through inline helpers, otherwise scans dentry blocks according to `ctx->pos`. It performs page-cache readahead for directory data pages, skips holes using `next_pgofs`, and delegates entry emission to `f2fs_fill_dentries()`. That function validates name lengths and bitmap slot boundaries, converts encrypted disk names to user names when needed, emits entries with `dir_emit()`, and optionally readaheads inode node pages for found entries.

## State And Persistence Behavior

Directory contents persist as inline dentry data inside inode pages or as regular dentry data blocks. Each dentry is represented by a bitmap slot range, `struct f2fs_dir_entry`, and name bytes. `f2fs_update_dentry()` sets the hash, name length, name bytes, target inode number, file type, and occupied slot bits; continuation slots have `name_len` cleared to avoid readdir garbage.

Directory hash growth is tracked by `F2FS_I(dir)->i_current_depth`, updated when insertion requires a deeper level. `chash` and `clevel` are transient hints that speed creation after lookup found room in a bucket.

Child inode metadata persists a copy of the disk name in `i_name`, parent inode number through `f2fs_i_pino_write()`, link counts, ACL/security/fscrypt context, and special encrypted-casefold hash suffix or `LOST_PINO` fallback for roll-forward recovery.

Deletion clears bitmap bits and may punch/truncate an empty dentry block. Link count updates, orphan list changes, and parent ctime/mtime changes persist through dirty inode/node pages and checkpoint/recovery mechanisms.

## Dependencies And Integration Points

`dir.c` depends on fscrypt, Unicode normalization/casefolding, generic VFS directory iteration, F2FS inline directory helpers, data folio helpers from `data.c`, inode/node metadata helpers, ACL and xattr initialization, orphan handling, tracepoints, and the page cache.

It integrates with mount options controlling lookup behavior (`LOOKUP_PERF`, `LOOKUP_COMPAT`, `LOOKUP_AUTO`), fsync behavior (`FSYNC_MODE_STRICT`), directory readahead (`sbi->readdir_ra`), and fault injection. It also interacts with checkpoint/recovery through orphan inodes, roll-forward name information, and transition-directory inode tracking.

## Risks And Edge Cases

Casefold plus encryption is the most complex name path. No-key encrypted names may provide only a decoded hash, strict Unicode encoding can reject invalid names, and encrypted casefolded filenames need special roll-forward recovery support because keys may be unavailable during recovery.

Hash-directory fallback behavior changes lookup coverage. In compatibility/auto modes, casefolded directories may perform a linear scan after hash lookup failure, which is slower but preserves compatibility with older hash behavior.

Dentry bitmap integrity is critical. `f2fs_fill_dentries()` detects zero name lengths after valid entries, slot overruns, and names longer than `F2FS_NAME_LEN`, then marks the filesystem needing fsck and reports corruption. Insert/delete paths must keep bitmap slots and continuation `name_len` fields coherent.

Creation has a deliberate race recheck when the creating task is not the task that performed lookup. Regressions there can allow duplicate dentries under stackable filesystem races.

Empty dentry block truncation in `f2fs_delete_entry()` changes both page-cache and block mapping state; it must correctly clear dirty accounting and private folio state after `f2fs_truncate_hole()`.

## Test Signals

Useful coverage includes lookup/create/unlink/rename workloads across inline and non-inline directories, encrypted directories with and without keys, casefolded directories under all lookup modes, strict Unicode rejection, tmpfile linking, directory fsync in strict mode, and recovery after fsync-created encrypted casefolded names.

Readdir tests should include holes in directory data, corrupted dentry name lengths, interrupted scans, encrypted name conversion, and readdir readahead. Consistency signals include correct link counts for `.`/`..`, parent times and depth updates, no duplicate dentries after racing create, and fsck-needed marking on detected corrupt dirents.
