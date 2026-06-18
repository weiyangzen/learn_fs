# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_debug.h

## Purpose

`mtu3_debug.h` declares optional MTU3 debugfs and trace-debug helpers while providing no-op stubs when debugfs or tracing is disabled.

## Important APIs, Types, and Functions

`struct mtu3_regset` wraps a named `debugfs_regset32`, and `struct mtu3_file_map` maps debugfs file names to `seq_file` show functions. When `CONFIG_DEBUG_FS` is enabled, prototypes expose `ssusb_dev_debugfs_init()`, `ssusb_dr_debugfs_init()`, `ssusb_debugfs_create_root()`, and `ssusb_debugfs_remove_root()`. When tracing is enabled, `mtu3_dbg_trace()` is available; otherwise it is an inline no-op.

## Control Flow

The header has no runtime control flow. Compile-time conditionals decide whether callers link to `mtu3_debugfs.c` and `mtu3_trace.c` or compile to empty operations.

## State and Persistence Behavior

The header defines only helper structures for runtime debugfs state; no persistence exists. Debugfs dentries are owned by `ssusb_mtk` and removed recursively by the implementation.

## Dependencies and Integration Points

It depends on debugfs declarations and forward-declares `struct ssusb_mtk`. It is included by platform, core, and dual-role code to avoid scattering `#ifdef CONFIG_DEBUG_FS` at call sites.

## Risks and Test Signals

Risks include callers assuming debugfs side effects in builds where calls are stubbed, and trace debug calls silently disappearing without `CONFIG_TRACING`. Test signals include compiling with debugfs and tracing both enabled and disabled, and verifying probe/remove succeeds without unresolved symbols in all combinations.
