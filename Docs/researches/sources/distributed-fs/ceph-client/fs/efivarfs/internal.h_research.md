<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/internal.h -->
# sources/distributed-fs/ceph-client/fs/efivarfs/internal.h

## Purpose
`internal.h` declares efivarfs-private data structures and cross-file helper prototypes shared by file, inode, superblock, and firmware variable code.

## Important APIs, types, and functions
Key types are `struct efivarfs_mount_opts`, `struct efivarfs_fs_info`, and `struct efivar_entry`. Important declarations include file and directory operation tables, `efivarfs_get_inode`, UTF-8 filename conversion, validation/removable checks, variable enumeration, and entry get/set/delete/size helpers. `efivar_entry()` converts from VFS inode to the containing entry.

## Control flow
The header has no runtime control flow, but it defines how the implementation units call each other: VFS operations manipulate `efivar_entry`; superblock population calls `efivar_init`; file operations call entry helpers; inode creation asks validation helpers whether variables should be removable.

## State and persistence
It defines runtime state: mount uid/gid options, superblock notifier ownership, per-variable open count, removed flag, and embedded `struct efi_variable`. Persistence remains in EFI firmware variables, accessed through declared helpers.

## Dependencies and integration points
It depends on Linux EFI, fs, notifier, and mutex-visible types. It is the integration contract between efivarfs VFS logic and the kernel EFIVAR namespace imported by `vars.c`.

## Risks and test signals
Risks include struct layout assumptions around `container_of`, missing prototypes after feature changes, and inconsistent use of `removed`/`open_count` across files. Test signals are all efivarfs build configurations and sparse/compiler checks for prototype drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/internal.h -->
