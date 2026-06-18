# sources/distributed-fs/ceph-client/fs/btrfs/scrub.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/scrub.h` declares the Btrfs scrub interface used by the rest of the filesystem. It is the public local header for starting a device scrub or device-replace scrub, pausing/resuming active scrubs around transactions, canceling all or one-device scrub work, and querying live scrub progress. The source was read as a complete 22-line file for this report.

## Important APIs, Types, and Functions

The header forward-declares `struct btrfs_fs_info`, `struct btrfs_device`, and `struct btrfs_scrub_progress` so users do not need the full scrub implementation internals. `btrfs_scrub_dev(fs_info, devid, start, end, progress, readonly, is_dev_replace)` starts the actual scan/copy operation for a device physical range. `btrfs_scrub_pause(fs_info)` and `btrfs_scrub_continue(fs_info)` provide filesystem-wide pause coordination. `btrfs_scrub_cancel(fs_info)` cancels all active scrub work on the filesystem, while `btrfs_scrub_cancel_dev(dev)` cancels the scrub attached to one device. `btrfs_scrub_progress(fs_info, devid, progress)` returns live progress for a device if one is currently being scrubbed.

## Control Flow

Callers include ioctl/sysfs/device-replace paths rather than this header itself. A normal run calls `btrfs_scrub_dev`, which resolves the target device, installs a scrub context on `dev->scrub_ctx`, validates superblocks, enumerates device extents, and returns a final `btrfs_scrub_progress` copy if requested. Transaction or freeze-sensitive paths call `btrfs_scrub_pause` before work that needs scrub quiescence and `btrfs_scrub_continue` afterward. Cancel paths set the filesystem-wide or device-local cancel flag and block until the running scrub clears.

## State and Persistence Behavior

This header owns no storage and defines no persistent data. Its declarations expose functions that operate on state stored in `struct btrfs_fs_info`, `struct btrfs_device`, and `struct btrfs_scrub_progress`: pause/cancel atomics and wait queues, the per-device `scrub_ctx` pointer, device-replace state, and progress counters. The only caller-visible persisted output is the copied progress structure and the return code from each operation.

## Dependencies and Integration Points

The only direct include is `<linux/types.h>` for `u64` and `bool`-compatible kernel types used in prototypes. The declarations integrate `scrub.c` with Btrfs ioctl handling, transaction pause coordination, filesystem freeze behavior, device replace, and progress reporting. Because the implementation is intentionally hidden, callers should treat `struct btrfs_scrub_progress` as the stable progress contract and avoid depending on `struct scrub_ctx`.

## Risks and Edge Cases

The main contract risk is semantic rather than syntactic: callers must pass a valid device id/range, choose `readonly` consistently with filesystem/device writability, and set `is_dev_replace` only for the device-replace path because it changes writeback and missing-device handling. Pause and cancel functions can wait; they must not be called from contexts that cannot sleep. Progress returns `-ENOTCONN` when the device exists but has no active scrub, so callers must distinguish idle from missing-device `-ENODEV`.

## Test Signals

Compile coverage should ensure all scrub users include this header without requiring implementation-only types. Functional tests should start scrub through the public caller path, query progress during and after the run, cancel globally and by device, pause around transaction-heavy operations, and run both read-only and repair-capable scrub. Device-replace tests should verify the same `btrfs_scrub_dev` declaration supports source-device copying with `is_dev_replace=true`.
