# sources/distributed-fs/ceph-client/fs/btrfs/verity.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/verity.h` declares the Btrfs fs-verity integration points and provides disabled-configuration stubs. The file was read as a complete 35-line header for this report.

## Important APIs, Types, and Functions

When `CONFIG_FS_VERITY` is enabled, the header includes `<linux/fsverity.h>`, declares `extern const struct fsverity_operations btrfs_verityops`, and exposes `btrfs_drop_verity_items()` and `btrfs_get_verity_descriptor()`. When the option is disabled, it provides inline stubs: dropping verity items succeeds as a no-op and descriptor lookup returns `-EPERM`.

## Control Flow

There is no executable control flow beyond compile-time selection. Enabled builds route superblock fs-verity operations to `verity.c`; disabled builds let callers compile while making descriptor access fail and cleanup harmless.

## State and Persistence Behavior

The header owns no state. It gates access to persistent descriptor/Merkle items and runtime fs-verity operations based on kernel configuration.

## Dependencies and Integration Points

The header forward declares `struct inode` and `struct btrfs_inode`. It is included by Btrfs superblock setup and inode/orphan code that must either use real fs-verity support or compile cleanly without it.

## Risks and Edge Cases

Callers must handle `-EPERM` from the disabled stub and must not assume `btrfs_verityops` exists unless `CONFIG_FS_VERITY` is enabled. Cleanup paths can safely call `btrfs_drop_verity_items()` in both configurations, but only enabled builds remove actual on-disk verity metadata.

## Test Signals

Build coverage with `CONFIG_FS_VERITY=y` and disabled configurations should verify both branches. Runtime fs-verity tests apply only to enabled builds; disabled builds should reject descriptor operations cleanly while preserving normal Btrfs behavior.
