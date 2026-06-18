# sources/distributed-fs/ceph-client/security/landlock/fs.h

## Purpose

`fs.h` declares Landlock filesystem LSM blob types and public filesystem helpers. It ties inode, file, and superblock objects to Landlock state.

## Important APIs, Types, and Functions

`struct landlock_inode_security` stores an RCU weak pointer to the inode's Landlock object. `struct landlock_file_security` stores `allowed_access`, optional audit `deny_masks` and `fown_layer`, and the `fown_subject` credential snapshot used for signal scope. `struct landlock_superblock_security` tracks pending inode references during unmount cleanup. Accessors `landlock_file()`, `landlock_inode()`, and `landlock_superblock()` index LSM blobs. `landlock_add_fs_hooks()` and `landlock_append_fs_rule()` are exported to setup/syscall code.

## Control Flow

Setup registers filesystem hooks through `landlock_add_fs_hooks()`. Syscall code adds path rules through `landlock_append_fs_rule()`. Enforcement code populates file and inode blobs through hooks in `fs.c`.

## State and Persistence Behavior

Inode object pointers are weak and RCU-protected; rules hold strong references. File security state persists for the lifetime of an open file and is intentionally used for later operations. Superblock state persists until unmount cleanup completes.

## Dependencies and Integration Points

The header depends on Linux fs structures, RCU, Landlock credentials, rulesets, and setup blob sizes. It must match `landlock_blob_sizes` in `setup.c`.

## Risks and Test Signals

Blob layout mismatches corrupt LSM state. File `allowed_access` semantics are user-visible for descriptor passing. Test with open/truncate/ioctl after policy changes, unmount of inodes referenced by rules, and audit-enabled fowner signal scenarios.
