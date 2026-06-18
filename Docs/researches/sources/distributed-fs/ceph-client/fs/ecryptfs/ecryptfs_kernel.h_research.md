# sources/distributed-fs/ceph-client/fs/ecryptfs/ecryptfs_kernel.h

## Purpose

`ecryptfs_kernel.h` is the internal contract for the eCryptfs kernel module. It centralizes constants for the persistent file format, packet types, mount flags, per-inode crypto state, lower-object accessors, operation-table declarations, slab-cache globals, messaging structures, and cross-file function prototypes.

## Important APIs, types, and functions

Important constants include default IV and extent sizes, minimum header extent size, message buffer defaults, `ECRYPTFS_XATTR_NAME`, maximum key/cipher limits, the magic marker, file-size and marker byte counts, default cipher/key bytes, OpenPGP-inspired tag IDs 1/3/11 and eCryptfs tags 64-73, encrypted filename prefixes, and the versioning feature mask.

Core structures are `struct ecryptfs_crypt_stat`, `struct ecryptfs_inode_info`, `struct ecryptfs_mount_crypt_stat`, `struct ecryptfs_sb_info`, `struct ecryptfs_file_info`, `struct ecryptfs_global_auth_tok`, `struct ecryptfs_key_tfm`, `struct ecryptfs_message`, `struct ecryptfs_msg_ctx`, and `struct ecryptfs_daemon`. Inline helpers expose private data and lower-layer objects: `ecryptfs_file_to_lower()`, `ecryptfs_inode_to_lower()`, `ecryptfs_superblock_to_lower()`, `ecryptfs_dentry_to_lower()`, and `ecryptfs_lower_path()`. It also wraps key payload extraction for user and encrypted key types.

## Control flow

The header has no independent runtime control flow, but it shapes all eCryptfs paths. Mount code fills `ecryptfs_mount_crypt_stat`; inode allocation embeds `ecryptfs_inode_info`; open paths fill `ecryptfs_file_info`; crypto paths mutate `ecryptfs_crypt_stat`; messaging paths allocate `ecryptfs_msg_ctx` and `ecryptfs_daemon`; operation tables exported by `file.c`, `inode.c`, `dentry.c`, `super.c`, and `mmap.c` are declared here for setup in `main.c` and inode interposition.

## State and persistence behavior

The header defines the meaning of persistent metadata flags and packet tags. `ECRYPTFS_METADATA_IN_XATTR`, `ECRYPTFS_VIEW_AS_ENCRYPTED`, `ECRYPTFS_ENCRYPT_FILENAMES`, and related flags determine whether metadata lives in the lower header or xattr, how upper sizes are calculated, and how lower filenames are transformed. It also defines runtime-only state flags such as `ECRYPTFS_KEY_VALID`, `ECRYPTFS_KEY_SET`, and `ECRYPTFS_I_SIZE_INITIALIZED`.

## Dependencies and integration points

The header depends on kernel crypto, key, VFS, fs_stack, namespace, backing-device, scatterlist, hash, and public `linux/ecryptfs.h` definitions. It integrates every source file in the eCryptfs directory: crypto, keystore, inode, file, mmap, read/write, superblock, miscdev, messaging, kthread, debug, and main.

## Risks

Because this file is a shared ABI inside the module, flag-value changes can corrupt interoperability with existing encrypted files or userspace tools. Structure layout assumptions also interact with slab caches and key payload data. Inline lower-object accessors assume `private_data`, `d_fsdata`, and `s_fs_info` are initialized; calling them early or after release can crash. Compile-time messaging stubs return `-ENOTCONN` or `-ENOMSG`, so public-key operations must handle messaging-disabled builds.

## Test signals

Signals include building with and without `CONFIG_ECRYPT_FS_MESSAGING` and `CONFIG_ENCRYPTED_KEYS`, mounting with every supported flag combination, validating version mask export, exercising lower-object accessors through lookup/open/release/unmount, and running old-file compatibility tests that prove constants and flag mappings remain stable.
