# sources/distributed-fs/ceph-client/fs/ecryptfs/main.c

## Purpose

`main.c` owns module parameters, mount option parsing, filesystem registration, superblock setup, lower-file lifetime management, slab cache lifecycle, sysfs version export, and module init/exit sequencing. It is the top-level integration point that turns eCryptfs operation tables and crypto/key machinery into a mountable stacked filesystem.

## Important APIs, types, and functions

Important exported globals are `ecryptfs_verbosity`, `ecryptfs_message_buf_len`, `ecryptfs_message_wait_timeout`, and `ecryptfs_number_of_users`. Important functions include `__ecryptfs_printk()`, `ecryptfs_get_lower_file()`, `ecryptfs_put_lower_file()`, `ecryptfs_parse_param()`, `ecryptfs_validate_options()`, `ecryptfs_get_tree()`, `ecryptfs_init_fs_context()`, `ecryptfs_kill_block_super()`, `ecryptfs_init_kmem_caches()`, `ecryptfs_free_kmem_caches()`, `do_sysfs_registration()`, `ecryptfs_init()`, and `ecryptfs_exit()`.

The mount parser recognizes `sig`, `ecryptfs_sig`, cipher options, key-byte options, passthrough, xattr metadata, encrypted view, FNEK signature, filename cipher/key bytes, unlink sigs, mount-auth-token-only, and check-dev-ruid.

## Control flow

Mount context initialization allocates `struct ecryptfs_fs_context` and `struct ecryptfs_sb_info`, initializes mount crypto state, and installs `ecryptfs_context_ops`. Each parsed mount parameter mutates mount crypto state or context booleans. Validation requires at least one auth-token signature, fills default ciphers/key sizes, validates cipher support, initializes cached key TFMs, and resolves global auth tokens from the keyring.

`ecryptfs_get_tree()` validates the source, rejects FIPS mode, allocates an anonymous superblock, installs super/xattr/dentry operations, resolves the lower directory path, rejects stacking on eCryptfs and idmapped lower mounts, optionally checks lower root uid against the mounting user, mirrors lower superblock flags, forces read-only for lower read-only or encrypted-view mounts, checks stack depth, interposes the root inode, stores lower root dentry and mount, and returns the root.

Lower-file lifetime uses an atomic per-inode count plus mutex. First `ecryptfs_get_lower_file()` opens a lower file with `ecryptfs_privileged_open()`; final `ecryptfs_put_lower_file()` waits for upper writeback, closes the lower file, and clears the pointer.

Module init checks extent size against page size, creates all slabs, registers sysfs `/sys/fs/ecryptfs/version`, starts the helper kthread, initializes messaging, initializes crypto, and registers the filesystem. Exit reverses those steps.

## State and persistence behavior

Persistent filesystem state is not written directly here, but mount options determine all later metadata placement, filename encryption, and passthrough semantics. Runtime state includes mount-wide auth-token lists, lower mount reference, slab caches, sysfs kobject, cached lower files per inode, and module parameters that affect logging and messaging capacity/timeouts.

## Dependencies and integration points

The file depends on fs_context/fs_parser, keyrings, FIPS status, path lookup, stacked filesystem helpers, sysfs, slab, module registration, and all eCryptfs operation tables and init functions. It coordinates `crypto.c`, `keystore.c`, `messaging.c`, `kthread.c`, `super.c`, `inode.c`, `file.c`, and `dentry.c`.

## Risks

Mount option validation is security critical because missing or invalid auth tokens should fail before files are exposed. Encrypted-view forces read-only; missing that would allow writes through a ciphertext view. Lower-file refcount imbalance can leak files or close them under active I/O. Init/exit order must match dependency order, especially messaging before public-key operations and slab caches before object allocation. FIPS mode disables the module because the implementation uses non-FIPS-approved primitives.

## Test signals

Tests should cover all mount options and aliases, missing sig rejection, invalid cipher/key-size rejection, FNEK filename mount validation, xattr and encrypted-view flag effects, check-dev-ruid permissions, lower read-only propagation, FIPS rejection, eCryptfs-on-eCryptfs rejection, idmapped lower mount rejection, stack-depth checks, sysfs version contents, lower-file refcount open/release behavior, and init failure unwinding at each stage.
