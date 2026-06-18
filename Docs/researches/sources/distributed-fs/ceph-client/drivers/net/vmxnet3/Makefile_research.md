# sources/distributed-fs/ceph-client/drivers/net/vmxnet3/Makefile

## Purpose
Builds the VMware vmxnet3 Ethernet NIC driver as a kernel object when `CONFIG_VMXNET3` is enabled. It identifies the driver object and the compilation units that make up the module.

## Important APIs, Types, And Functions
The file uses standard Kbuild variables. `obj-$(CONFIG_VMXNET3) += vmxnet3.o` makes the object conditional on the kernel config option. `vmxnet3-objs := vmxnet3_drv.o vmxnet3_ethtool.o vmxnet3_xdp.o` declares the composite object members: the main driver, ethtool support, and XDP support.

## Control Flow
There is no runtime control flow. During kernel build, Kbuild evaluates `CONFIG_VMXNET3`; if built-in or module-enabled, it compiles the listed object files and links them into `vmxnet3.o` according to normal kernel build rules.

## State And Persistence Behavior
The file contains no runtime state and persists no data. Its only persistent effect is build-system metadata: changing the object list changes what source files are included in the built driver.

## Dependencies And Integration Points
Depends on the kernel Kbuild system and the `CONFIG_VMXNET3` Kconfig symbol defined elsewhere. It integrates with the vmxnet3 source directory by naming `vmxnet3_drv.o`, `vmxnet3_ethtool.o`, and `vmxnet3_xdp.o`; any source split or new feature file must be reflected here to be linked.

## Risks
The main risk is object-list drift. Adding code in a new `.c` file without updating `vmxnet3-objs` produces unresolved symbols or missing functionality; removing or renaming a source file without updating the list breaks the build. Incorrectly changing `obj-$(CONFIG_VMXNET3)` can alter built-in/module behavior for the driver.

## Test Signals
Build signals are sufficient: `make M=drivers/net/vmxnet3` or a full kernel build with `CONFIG_VMXNET3=m/y` should compile and link `vmxnet3.o`. Runtime smoke testing requires the linked module to expose the expected vmxnet3 driver functionality, including ethtool and XDP paths that come from the separate object files.
