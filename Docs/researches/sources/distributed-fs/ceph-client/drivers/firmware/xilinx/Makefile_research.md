# sources/distributed-fs/ceph-client/drivers/firmware/xilinx/Makefile

## Purpose
This Makefile maps Xilinx firmware Kconfig symbols to the objects compiled into the kernel. It is the build linkage for core ZynqMP firmware support, UFS helpers, crypto helpers, and optional debugfs support.

## Important rules
`obj-$(CONFIG_ZYNQMP_FIRMWARE) += zynqmp.o zynqmp-ufs.o zynqmp-crypto.o` builds the core firmware driver plus UFS and crypto extension files when the firmware interface is enabled. `obj-$(CONFIG_ZYNQMP_FIRMWARE_DEBUG) += zynqmp-debug.o` builds the debugfs command interface only when selected.

## Control flow and integration
The Makefile is declarative and follows standard kbuild `obj-*` expansion. It depends on `xilinx/Kconfig` for symbol selection and on public headers such as `linux/firmware/xlnx-zynqmp.h` for exported APIs used by these objects.

## State and persistence behavior
No runtime state exists here. Its persistent effect is object inclusion in the kernel build graph.

## Dependencies and integration points
The file integrates the firmware directory with kbuild. It assumes `zynqmp.o` exists as the core implementation that provides `zynqmp_pm_invoke_fn()` and register access helpers used by `zynqmp-ufs.o`, `zynqmp-crypto.o`, and `zynqmp-debug.o`.

## Risks and test signals
Risks include unresolved symbols if extension objects are built without the core implementation or if future files are added without matching Kconfig dependencies. Test signals are successful allmodconfig/allyesconfig builds, symbol export availability for UFS and crypto clients, and debug object inclusion only under `CONFIG_ZYNQMP_FIRMWARE_DEBUG`.
