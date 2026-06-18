# sources/distributed-fs/ceph-client/drivers/firmware/xilinx/zynqmp-debug.c

## Purpose
`zynqmp-debug.c` implements a debugfs interface for invoking selected ZynqMP firmware power-management APIs from userspace. It is a diagnostic and bring-up tool, not a normal production control plane.

## Important APIs, types, and functions
`struct pm_api_info` maps firmware API ids to symbolic names. `pm_api_list[]` enumerates supported operations such as powerdown, wakeup, request/release node, reset, chip ID, pinctrl, ioctl, clocks, and query data. `debugfs_buf` is a page-sized global response buffer exposed by reads. `zynqmp_pm_ioctl()` is a local wrapper for `PM_IOCTL`.

`get_pm_api_id()` resolves an API name prefix or decimal API id. `zynqmp_pm_argument_value()` parses each string argument as a u64, returning zero on missing or invalid input. `process_api_request()` dispatches the selected API id to the corresponding exported ZynqMP PM helper and formats selected return data into `debugfs_buf`. `zynqmp_pm_debugfs_api_write()` parses a single write buffer, extracts up to five arguments, dispatches the request, and returns either the write length or an errno. `zynqmp_pm_debugfs_api_read()` returns the current `debugfs_buf`.

## Control flow and integration
`zynqmp_pm_api_debugfs_init()` creates `/sys/kernel/debug/zynqmp-firmware/pm` with mode `0660`; writes trigger PM operations and reads retrieve the last formatted result. `zynqmp_pm_api_debugfs_exit()` removes the tree. The header `zynqmp-debug.h` makes these calls no-ops when debug support is not reachable, letting the core firmware driver call init/exit conditionally without preprocessor spread.

## State and persistence behavior
Runtime state is the debugfs root dentry and one global `debugfs_buf`. The buffer is overwritten on each write and read by any opener, so it is not per-file or per-caller state. Firmware and hardware own the actual power, reset, pinctrl, clock, and ioctl side effects triggered by commands.

## Dependencies and integration points
The file depends on debugfs, user-copy helpers, string parsing, and `linux/firmware/xlnx-zynqmp.h` PM APIs. It integrates with the core ZynqMP firmware driver via `zynqmp_pm_api_debugfs_init/exit()` and is built only under `CONFIG_ZYNQMP_FIRMWARE_DEBUG`.

## Risks and test signals
Risks are significant because debugfs writes can power down nodes, alter clocks, assert resets, change pinctrl, and issue IOCTLs. There is no locking around the global response buffer, parsing invalid numeric arguments silently as zero can issue unintended default operations, and name matching uses prefix length rather than token equality. Test signals include debugfs file creation/removal, successful `PM_GET_API_VERSION` and `PM_GET_CHIPID`, permission checks, concurrent read/write behavior, and negative tests for invalid API names, oversized writes, and firmware errors.
