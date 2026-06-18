# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/dbgfs.c

## Purpose
`dbgfs.c` creates and removes Venus debugfs controls. It exposes firmware debug verbosity and, when fault injection is enabled, a software path to force SSR/system-error recovery testing.

## Important APIs
- `venus_dbgfs_init(struct venus_core *core)` creates `/sys/kernel/debug/venus`, adds `fw_level`, and conditionally adds `fail_ssr`.
- `venus_dbgfs_deinit(struct venus_core *core)` removes the debugfs tree.
- Declares `venus_ssr_attr` through `DECLARE_FAULT_ATTR()` when `CONFIG_FAULT_INJECTION` is set.

## Control Flow
Probe calls `venus_dbgfs_init()` after successful driver initialization. Remove calls `venus_dbgfs_deinit()` after tearing down HFI/V4L2 state. The IRQ thread consults `venus_fault_inject_ssr()` from `dbgfs.h`; if the fault attribute fires, it triggers HFI SSR.

## State And Persistence
Stores the debugfs root dentry in `core->root`. The `fw_level` file directly exposes global `venus_fw_debug`. Fault-injection state is kernel debugfs state and not persistent across module unload/reboot.

## Dependencies
Uses Linux debugfs and fault-injection APIs plus `core.h`.

## Risks
- Debugfs creation failures are not checked; this is conventional but means controls may be absent without failing probe.
- Writable `fw_level` and fault injection are debugging interfaces and should not be relied on for production control.

## Test Signals
With debugfs mounted, `venus/fw_level` should exist after probe and disappear after remove. With `CONFIG_FAULT_INJECTION`, writing to `venus/fail_ssr` should allow IRQ-thread-triggered SSR recovery paths to be exercised.
