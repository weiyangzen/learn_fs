<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/can/Makefile

Purpose: this Makefile maps CAN Kconfig symbols to built objects and subdirectories. It is the build fan-out for the CAN driver tree.

Important APIs, types, and functions: key targets in this subset are `obj-$(CONFIG_CAN_AT91) += at91_can.o`, `obj-$(CONFIG_CAN_BXCAN) += bxcan.o`, `obj-$(CONFIG_CAN_CAN327) += can327.o`, `obj-$(CONFIG_CAN_CC770) += cc770/`, and `obj-$(CONFIG_CAN_C_CAN) += c_can/`. Common subdirectories such as `dev/`, `esd/`, `rcar/`, `rockchip/`, `spi/`, `usb/`, and `softing/` are included with `obj-y`.

Control flow: kbuild includes this file after Kconfig resolution. Built-in and modular values on each `CONFIG_CAN_*` symbol decide whether corresponding objects or subdirectories are compiled into vmlinux, a module, or not built. `subdir-ccflags-$(CONFIG_CAN_DEBUG_DEVICES) += -DDEBUG` adds debug logging to all nested CAN driver compilations when enabled.

State and persistence: the file has no runtime state; it shapes build artifacts and compiler flags.

Dependencies and integration points: it must match symbol names in `drivers/net/can/Kconfig` and nested Kconfig files. Directory targets delegate object selection to sub-Makefiles such as `c_can/Makefile` and `cc770/Makefile`.

Risks: stale object mappings cause selected Kconfig symbols to produce no module or to compile unexpected code. `obj-y` subdirectories are always visited, so their own Makefiles must guard individual objects correctly. Debug flags apply broadly and can change log volume across all CAN drivers.

Test signals: run `make drivers/net/can/` with representative configs, verify module names for `at91_can`, `bxcan`, `can327`, `c_can`, and `cc770`, and check that `CONFIG_CAN_DEBUG_DEVICES=y` adds debug messages without build breakage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/Makefile -->
