<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sysrq.h -->
# sources/distributed-fs/ceph-client/include/linux/sysrq.h

## Purpose
defines the Magic SysRq registration API and enable-mask categories for emergency kernel commands.

## Important APIs, Types, and Functions
The file is 84 lines and exports these visible symbol families: types/enums `sysrq_key_op`; macros/constants `SYSRQ_ENABLE_LOG`, `SYSRQ_ENABLE_KEYBOARD`, `SYSRQ_ENABLE_DUMP`, `SYSRQ_ENABLE_SYNC`, `SYSRQ_ENABLE_REMOUNT`, `SYSRQ_ENABLE_SIGNAL`, `SYSRQ_ENABLE_BOOT`, `SYSRQ_ENABLE_RTNICE`; function-like macros none; inline helpers `handle_sysrq`, `__handle_sysrq`, `register_sysrq_key`, `unregister_sysrq_key`, `sysrq_mask`; external prototypes `handle_sysrq`, `__handle_sysrq`, `register_sysrq_key`, `unregister_sysrq_key`, `sysrq_toggle_support`, `sysrq_mask`.

## Control Flow
Drivers or core code register `struct sysrq_key_op` handlers by key. `handle_sysrq()` and `__handle_sysrq()` dispatch a key, optionally checking the mask returned by `sysrq_mask()`. CONFIG_MAGIC_SYSRQ=n builds compile to inert stubs that reject registration.

## State and Persistence Behavior
Registered key operations and the enable mask are global kernel state. Individual operations may sync disks, remount filesystems, dump state, signal tasks, adjust RT priority, or reboot.

## Dependencies and Integration Points
It depends on errno/types and integrates with keyboard/serial console input, proc/sysctl sysrq mask control, crash/debug code, and reboot/sync/remount paths. Direct includes are `linux/errno.h`, `linux/types.h`.

## Risks and Edge Cases
SysRq handlers are emergency paths and may run in hostile contexts. Incorrect enable masks can expose destructive actions, and handlers must not assume normal scheduler or locking progress.

## Test Signals
Build with CONFIG_MAGIC_SYSRQ enabled and disabled, register/unregister test handlers, verify mask enforcement per category, and run selected non-destructive commands through keyboard and proc-trigger paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sysrq.h -->
