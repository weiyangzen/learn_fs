# sources/distributed-fs/ceph-client/fs/ecryptfs/inode.c

## Purpose

`inode.c` implements eCryptfs inode operations and most namespace manipulation. It interposes upper inodes over lower inodes, maps plaintext names to encrypted lower names during lookup/create/symlink, initializes new encrypted files, handles link/unlink/mkdir/rmdir/mknod/rename, translates symlink targets, manages truncate and setattr sizing across encrypted headers, and forwards xattr, ACL, permission, and file-attribute operations.

## Important APIs, types, and functions

Externally visible functions are `ecryptfs_get_inode()`, `ecryptfs_initialize_file()`, `ecryptfs_truncate()`, `ecryptfs_setxattr()`, and `ecryptfs_getxattr_lower()`. The exported operation tables are `ecryptfs_symlink_iops`, `ecryptfs_dir_iops`, `ecryptfs_main_iops`, and `ecryptfs_xattr_handlers`. Key internal functions include `__ecryptfs_get_inode()`, `ecryptfs_inode_set()`, `ecryptfs_lookup()`, `ecryptfs_lookup_interpose()`, `ecryptfs_create()`, `ecryptfs_do_create()`, `ecryptfs_i_size_read()`, `ecryptfs_symlink()`, `ecryptfs_readlink_lower()`, `upper_size_to_lower_size()`, `__ecryptfs_truncate()`, and `ecryptfs_setattr()`.

## Control flow

Lookup encrypts the requested upper name when mount-wide filename encryption is enabled, then performs `lookup_noperm_unlocked()` in the lower parent. `ecryptfs_lookup_interpose()` stores the lower dentry, obtains or creates an upper inode using `iget5_locked()`, and for regular files reads enough metadata to initialize upper size. Inode setup copies lower attributes, sets operation tables by type, initializes special inodes when needed, and rejects lower files from unrelated lower superblocks or casefolded directories.

Create first creates the lower file, interposes the upper inode, then calls `ecryptfs_initialize_file()` to generate a new FEK and write eCryptfs metadata. Failure after lower creation unlinks the lower file and fails the new inode. Symlink creation encrypts/encodes the symlink target string with the same filename mechanism before calling lower `vfs_symlink()`. Directory and special-file operations mostly forward to lower VFS helpers and copy attributes back up.

Truncate converts upper logical sizes to lower physical sizes by adding header size and rounding to extents. Growing writes a single zero at the new final byte so write paths fill intermediate encrypted zeros. Shrinking zeros the remainder of the final page, updates the encrypted metadata i_size, then possibly truncates the lower inode. `setattr` ensures metadata is read and keys are valid before size changes, with passthrough fallback only when configured.

## State and persistence behavior

Persistent effects include lower namespace changes, eCryptfs header creation, lower encrypted symlink names, xattr writes/removals, ACL updates, file-attribute updates, and metadata i_size rewrites on truncate. Runtime state includes upper inode references to lower inodes, dentry lower pointers, crypt_stat initialization, and copied lower inode attributes.

## Dependencies and integration points

The file depends on VFS namei, fs_stack, xattr, ACL, fileattr, unaligned access, crypto metadata functions, lower file lifetime from `main.c`, file operation tables from `file.c`, dentry operations from `dentry.c`, and address-space operations from `mmap.c`. It is central to mount-root setup in `main.c` and to all upper filesystem operations.

## Risks

Size translation is security- and data-integrity-sensitive; off-by-one errors can truncate ciphertext, leak stale tail bytes, or corrupt header metadata. Filename encryption during lookup and symlink target creation must match readdir/readlink decoding exactly. Lower namespace locking uses modern start/end dentry helpers; regressions can race with concurrent lower changes. Passthrough mode changes failure handling for invalid metadata and needs careful coverage.

## Test signals

Tests should include lookup of encrypted and plaintext lower names, create rollback after metadata write failure, hard link size preservation, symlink target round trip, mkdir/rmdir/mknod/rename behavior, truncate grow and shrink across page/extent boundaries, xattr and ACL forwarding, fileattr forwarding, casefold lower directory rejection, lower attribute propagation, and passthrough versus non-passthrough invalid-header behavior.
