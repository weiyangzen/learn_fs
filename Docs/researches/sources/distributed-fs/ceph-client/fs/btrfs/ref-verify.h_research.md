# sources/distributed-fs/ceph-client/fs/btrfs/ref-verify.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/ref-verify.h` exposes the Btrfs reference verifier interface and compiles it away outside `CONFIG_BTRFS_DEBUG`. The source was read as a complete 58-line file.

## Important APIs, Types, and Functions

When `CONFIG_BTRFS_DEBUG` is enabled, the header declares `btrfs_build_ref_tree()`, `btrfs_free_ref_cache()`, `btrfs_ref_tree_mod()`, and `btrfs_free_ref_tree_range()`. It also defines `btrfs_init_ref_verify()`, which initializes `fs_info->ref_verify_lock` and `fs_info->block_tree`. When debug support is disabled, all functions are static inline no-ops or zero-return stubs.

## Control Flow

The header controls build-time dispatch. Debug builds call the real verifier in `ref-verify.c`; non-debug builds preserve call sites without runtime cost or state changes.

## State and Persistence Behavior

In debug builds, initialization prepares in-memory verifier state inside `struct btrfs_fs_info`. In non-debug builds, no verifier state is initialized. No persistent filesystem data is defined or modified by this header.

## Dependencies and Integration Points

The header depends on Linux integer and rb-tree type declarations, and on spinlock declarations only for debug builds. It is included by Btrfs mount/setup and delayed-ref code that should remain source-compatible whether the verifier is compiled in or not.

## Risks and Edge Cases

The main risk is semantic drift between real debug functions and no-op stubs. Callers must not rely on side effects from verifier functions in production builds. Debug initialization must run before any verifier mutation path uses `fs_info->ref_verify_lock` or `fs_info->block_tree`.

## Test Signals

Compile both `CONFIG_BTRFS_DEBUG=y` and non-debug configurations. Debug boot/mount smoke tests should confirm `btrfs_init_ref_verify()` precedes `btrfs_build_ref_tree()` and delayed-ref modification calls; non-debug builds should verify call sites compile and optimize to stubs.
