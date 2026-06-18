# sources/distributed-fs/ceph-client/fs/fat/namei_msdos.c

## Purpose
`namei_msdos.c` implements the `msdos` filesystem variant: strict 8.3 name formatting, dentry hashing/comparison for formatted names, and VFS directory inode operations for create, lookup, unlink, mkdir, rmdir, and rename. It layers single-slot names on top of common FAT directory and inode helpers.

## Important APIs, Types, and Functions
- `msdos_format_name()` validates and converts user names into 11-byte FAT 8.3 names based on `check=`, `dotsOK`, and `nocase`.
- `msdos_find()` formats a user name, calls `fat_scan()`, and applies hidden-file dot semantics.
- `msdos_hash()` and `msdos_cmp()` ensure dentries compare in formatted-name space when possible.
- `msdos_add_entry()` builds one `msdos_dir_entry` and calls `fat_add_entries()`.
- `msdos_create()`, `msdos_mkdir()`, `msdos_unlink()`, `msdos_rmdir()`, and `msdos_rename()` implement the VFS operations.
- `msdos_init_fs_context()` registers msdos-specific fs_context operations and defaults.

## Control Flow
Lookup takes `sbi->s_lock`, formats the requested name, scans the directory, and builds or reuses a FAT inode by `sinfo.i_pos`. Create and mkdir format the target, reject formatted-name conflicts including dot-hidden aliases, create directory slots, build inodes, instantiate dentries, and flush if requested.

Remove operations check emptiness for rmdir, locate the slot, mark directory entries deleted, drop link counts, detach the inode from FAT hashes, and flush. Rename formats old/new names, handles hidden-dot attribute-only transitions, optionally validates replacement directories are empty, creates the destination entry if needed, moves `i_pos` by detach/attach, updates `..` for cross-directory directory moves, removes old slots, adjusts link counts, and has rollback/error paths that report corruption if on-disk recovery fails.

## State and Persistence
Persistent state is a single 8.3 directory entry per object. Hidden dotfiles are represented as `ATTR_HIDDEN` plus no leading dot in the formatted name when `dotsOK` is enabled. Rename changes directory entry location and possibly attributes, so inode hash state must be updated with `fat_detach()` / `fat_attach()`. Directory timestamps and link counts are updated through common helpers.

## Dependencies and Integration Points
This file uses `fat_scan()`, `fat_add_entries()`, `fat_remove_entries()`, `fat_alloc_new_dir()`, `fat_dir_empty()`, `fat_get_dotdot_entry()`, `fat_build_inode()`, `fat_flush_inodes()`, and shared attribute/getattr/setattr helpers. It registers a `file_system_type` named `msdos` that delegates mount setup to `fat_fill_super()`.

## Risks and Test Signals
Name validation depends on relaxed/normal/strict modes and must preserve DOS 0xE5/0x05 first-character semantics. Dot-hidden behavior can create conflicts between `foo` and `.foo`. Rename has multiple partial-persistence windows. Tests should cover 8.3 validation, `dotsOK`, case/no-case behavior, hidden transitions, create/mkdir/unlink/rmdir, cross-directory rename, replacement of empty directories, rollback after injected IO failure, and `msdos` mount registration.
