# sources/distributed-fs/ceph-client/drivers/bus/Makefile

## Purpose
Maps bus-driver Kconfig symbols to built objects and subdirectories. It is the build-system companion to `drivers/bus/Kconfig`.

## Important APIs, Types, And Functions
The file uses kernel kbuild `obj-$(CONFIG_...)` assignments. In this subset, it builds `arm-cci.o`, `arm-integrator-lm.o`, `brcmstb_gisb.o`, `da8xx-mstpri.o`, and descends into `fsl-mc/` when `CONFIG_FSL_MC_BUS` is enabled. It always descends into `mhi/` with `obj-y += mhi/`, leaving that subtree to its own Kconfig and Makefile decisions.

## Control Flow
Kbuild expands each `obj-*` variable based on the resolved kernel configuration. Built-in, module, or omitted status follows the selected symbol type. Directory recursion gives sub-Makefiles control of composite objects such as the fsl-mc bus driver.

## State And Persistence
There is no runtime state. The output is persisted as build artifacts in the kernel build tree.

## Dependencies And Integration Points
This file must remain synchronized with `drivers/bus/Kconfig` and with source filenames. It integrates with kbuild, architecture defconfig choices, and subdirectory Makefiles for fsl-mc and MHI.

## Risks And Test Signals
Risks include stale object names, missing objects for new symbols, recursive directory inclusion under the wrong condition, or module/built-in mismatches. Test signals are clean kernel builds across relevant configs and checking that selected symbols produce expected `.o` files.
