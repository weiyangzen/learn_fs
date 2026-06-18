# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/Makefile

Purpose: kbuild object list for the legacy Intel PRO/1000 `e1000` driver.

Important APIs, types, and functions: this file has no C APIs. It declares `obj-$(CONFIG_E1000) += e1000.o` and composes `e1000.o` from `e1000_main.o`, `e1000_hw.o`, `e1000_ethtool.o`, and `e1000_param.o`.

Control flow: build-time only. When `CONFIG_E1000` is enabled as built-in or module, kbuild descends into this directory and links the four listed objects into one driver object. `e1000_ethtool.o` is always part of the driver, so ethtool support is not optional within this Makefile.

State and persistence behavior: no runtime state and no persistent data. The file only affects generated build artifacts.

Dependencies and integration points: depends on the kernel Kconfig symbol `CONFIG_E1000`, normally selected from the Intel Ethernet Kconfig menu. It assumes the companion source files in the same directory provide the main PCI/netdev driver, hardware helper layer, ethtool hooks, and module parameter processing.

Risks: a missing object in `e1000-y` would compile out an essential part of the driver. Renaming files or splitting optional features requires this object list to remain synchronized with exported symbols such as `e1000_set_ethtool_ops()` from `e1000_ethtool.c` and core routines declared in `e1000.h`.

Test signals: build with `CONFIG_E1000=m` and `CONFIG_E1000=y`; verify `e1000.o` links all four objects, module load succeeds, and no unresolved symbols appear from ethtool, hardware, or parameter code.
