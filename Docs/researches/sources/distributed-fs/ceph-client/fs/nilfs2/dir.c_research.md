# sources/distributed-fs/ceph-client/fs/nilfs2/dir.c

## Purpose
`dir.c` implements NILFS directory entry layout, lookup, iteration, link insertion/removal, `.`/`..` creation, and emptiness checks. It is ext2-derived but integrated with NILFS pagecache, transactions, dirty file accounting, and private-inode restrictions.

## Important APIs and functions
- Record helpers convert on-disk record lengths, compute chunk size, and find the last valid byte in a directory page.
- `nilfs_check_folio()` validates directory record structure, chunk alignment, name length, page boundaries, and disallowed private inode numbers before marking a folio checked.
- `nilfs_get_folio()` reads and maps a directory folio and validates it once.
- `nilfs_readdir()` implements directory iteration through `dir_emit()`.
- `nilfs_find_entry()`, `nilfs_inode_by_name()`, and `nilfs_dotdot()` implement lookup helpers for namei.
- `nilfs_set_link()`, `nilfs_add_link()`, and `nilfs_delete_entry()` mutate directory entries through `nilfs_prepare_chunk()` and `nilfs_commit_chunk()`.
- `nilfs_make_empty()` initializes new directories with `.` and `..`.
- `nilfs_empty_dir()` supports rmdir checks.
- `nilfs_dir_operations` wires readdir, ioctl, compat ioctl, fsync, and leases.

## Control flow
Reads map directory folios through the address_space using `nilfs_get_block()` indirectly. A folio is checked once and then iterated record by record using `rec_len`. Readdir advances `ctx->pos` by each record length and emits only entries with nonzero inode numbers.

Lookup starts at `i_dir_start_lookup` to improve locality, wraps over all pages, and detects impossible directory size versus block count. Add-link scans existing and one expansion page for an empty slot or splittable record, locks the folio, prepares the changed chunk, splits a live record if needed, writes the name/inode/type, commits the chunk, updates directory times, and marks the inode dirty. Delete-entry merges the target record into the previous record within the block-sized chunk and clears the target inode.

## State and persistence behavior
Directory blocks are file data blocks tracked by the inode bmap. Mutations dirty buffers and call `nilfs_set_file_dirty()` so segment construction writes the changed directory data. `IS_DIRSYNC` sets the NILFS transaction sync flag. Directory lookup state caches a starting page in `i_dir_start_lookup`.

## Dependencies and integration points
The file depends on `nilfs_get_block()`, `nilfs_set_file_dirty()`, `nilfs_mark_inode_dirty()`, NILFS directory on-disk structures/macros, VFS `dir_context`, folio mapping helpers, and ioctl/fsync routines from `ioctl.c` and `file.c`. Namei code outside this work item calls the exported helpers.

## Risks and invariants
Directory `i_size` must be chunk aligned. `rec_len` must be nonzero, at least minimal, 4-byte aligned, large enough for `name_len`, and not cross block chunks. Private NILFS inode numbers must not appear in user directories. Folio kmap pointers must be released with the same mapped address; the code has several error paths where pointer discipline matters.

## Test signals
Test readdir over corrupt and valid directories, lookup wraparound, add into empty and split records, delete first/non-first entries, directory expansion, `.`/`..` validation, rmdir emptiness, large-page record length conversion, and fsync/dirsync propagation.
