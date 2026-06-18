<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/file.c -->
# sources/distributed-fs/ceph-client/fs/efivarfs/file.c

## Purpose
`file.c` implements efivarfs regular-file operations. Each file represents one EFI variable, where the first four bytes exposed to userspace are EFI attributes and the remaining bytes are variable data.

## Important APIs, types, and functions
The exported table is `efivarfs_file_operations`. Important functions are `efivarfs_file_open`, `efivarfs_file_read`, `efivarfs_file_write`, and `efivarfs_file_release`. They operate on `struct efivar_entry` stored in `inode->i_private` and `file->private_data`.

## Control flow
Open stores the entry in private data and increments `open_count` under the inode lock. Reads rate-limit by user, fetch variable size, return EOF for uncommitted `-ENOENT` variables, allocate an attributes-plus-data buffer, call `efivar_entry_get`, and copy through `simple_read_from_buffer`. Writes require at least an attributes word, reject unknown attribute bits, copy payload data, lock the inode, reject removed variables, call `efivar_entry_set_get_size`, and then update inode size and timestamps. Release decrements `open_count`, marks zero-size last-close variables as removed, and recursively removes the dentry.

## State and persistence
Persistent state is firmware NVRAM variable content changed by SetVariable. Runtime inode size mirrors firmware state and uses zero size to signal a deleted or uncommitted variable. `removed` and `open_count` guard races between failed creates, deletes, and open files.

## Dependencies and integration points
It depends on `vars.c` firmware wrappers, inode locking, uaccess, per-user rate limiting, VFS removal helpers, and EFI attribute constants. It is called by VFS operations assigned in `inode.c`.

## Risks and test signals
Risks include firmware write failures after userspace sees a file, races between delete/create/write/release, attribute validation gaps, rate-limit latency, and size mismatch after append/delete semantics. Test signals include reading existing variables, creating then closing without data, deleting by zero-size SetVariable result, writes with invalid attributes, concurrent opens during unlink, and firmware returning `ENOENT`, `ENOSPC`, or write-protected errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/file.c -->
