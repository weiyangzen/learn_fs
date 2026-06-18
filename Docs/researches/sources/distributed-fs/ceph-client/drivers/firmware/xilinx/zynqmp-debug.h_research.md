# sources/distributed-fs/ceph-client/drivers/firmware/xilinx/zynqmp-debug.h

## Purpose
`zynqmp-debug.h` declares the ZynqMP firmware debugfs init/exit hooks and supplies no-op inline stubs when the debug object is not built or reachable.

## Important APIs
The exported internal hooks are `zynqmp_pm_api_debugfs_init()` and `zynqmp_pm_api_debugfs_exit()`. Under `IS_REACHABLE(CONFIG_ZYNQMP_FIRMWARE_DEBUG)` they are real functions implemented in `zynqmp-debug.c`; otherwise they are static inline empty functions.

## Control flow and integration
The header lets core firmware code call debug init/exit unconditionally while kbuild decides whether calls resolve to the real debugfs implementation or compile away. This keeps debug support optional without changing the call site.

## State and persistence behavior
The header stores no state. When debug support is enabled, state is owned by `zynqmp-debug.c`; when disabled, there are no side effects.

## Dependencies and integration points
It depends on Kconfig reachability for `CONFIG_ZYNQMP_FIRMWARE_DEBUG` and is included by ZynqMP firmware code that wants optional debugfs support.

## Risks and test signals
Risks are limited to configuration mismatch: using `IS_REACHABLE()` is important for built-in/module combinations. Test signals are successful builds with debug enabled and disabled, no unresolved symbols in modular configurations, and debugfs tree absence when disabled.
