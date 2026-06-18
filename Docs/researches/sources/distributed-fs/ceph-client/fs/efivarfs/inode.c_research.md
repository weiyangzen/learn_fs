<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/inode.c -->
# sources/distributed-fs/ceph-client/fs/efivarfs/inode.c

## Purpose
`inode.c` provides efivarfs inode creation, directory operations, unlink, immutable flag support, and setattr behavior. It maps valid efivarfs filenames into EFI variable vendor/name pairs.

## Important APIs, types, and functions
Important functions are `efivarfs_get_inode`, `efivarfs_create`, `efivarfs_unlink`, `efivarfs_valid_name`, `efivarfs_fileattr_get`, `efivarfs_fileattr_set`, and `efivarfs_setattr`. It exports `efivarfs_dir_inode_operations` and assigns private file inode operations internally.

## Control flow
`efivarfs_get_inode` creates a new inode with mount uid/gid, timestamps, and immutable state based on whether the variable is removable; regular files get efivarfs file ops and directories get simple directory ops. Create validates `VariableName-GUID` naming, rejects Linux random seed variables, parses the GUID, checks the removable whitelist, fills `struct efivar_entry`, stores it in `i_private`, and makes a persistent dentry without immediately committing firmware data. Unlink calls `efivar_entry_delete` and then `simple_unlink`. File attributes expose only immutable toggling; setattr copies metadata changes without allowing i_size updates.

## State and persistence
Inode state stores `struct efivar_entry`, mode, uid/gid, immutable flag, and open/delete bookkeeping. Firmware persistence occurs through delete/write helpers, not inode allocation alone. Immutable defaults protect non-whitelisted firmware variables from accidental deletion or modification.

## Dependencies and integration points
It depends on EFI GUID parsing, variable validation/whitelist logic in `vars.c`, VFS simple directory helpers, file attributes, and mount options from superblock fs info.

## Risks and test signals
Risks include accepting malformed UTF-8-to-UCS2 names as variable names, immutable flag bypasses, create/unlink races with firmware state, and size updates through setattr. Test signals include filename validation, GUID case handling, `chattr +/-i`, unlink of protected and removable variables, create followed by write/release, and rejection of random-seed GUID variables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/inode.c -->
