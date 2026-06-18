<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/can/c_can/Makefile

Purpose: this Makefile builds the Bosch C_CAN/D_CAN shared core and optional bus-specific front ends.

Important APIs, types, and functions: `obj-$(CONFIG_CAN_C_CAN) += c_can.o` builds a composite object from `c_can_ethtool.o` and `c_can_main.o`. `obj-$(CONFIG_CAN_C_CAN_PLATFORM) += c_can_platform.o` and `obj-$(CONFIG_CAN_C_CAN_PCI) += c_can_pci.o` add the platform and PCI wrappers.

Control flow: kbuild links `c_can_ethtool.o` and `c_can_main.o` into `c_can.o`, exporting shared helpers such as `alloc_c_can_dev()` and `register_c_can_dev()` for the wrappers. Bus wrappers compile only when their child Kconfig symbols are selected.

State and persistence: this file has no runtime state; it controls build composition and module contents.

Dependencies and integration points: symbol names must match `c_can/Kconfig`. The composite core must be available before platform/PCI wrappers can reference its exported functions.

Risks: object-list drift can omit the ethtool ops or core entry points from the module. Building wrappers without the parent would produce unresolved symbols, so Kconfig nesting and Makefile symbols must stay in sync.

Test signals: build `CONFIG_CAN_C_CAN=m` with each wrapper enabled/disabled, inspect that `c_can.ko` contains `c_can_main` and `c_can_ethtool` code, and run module dependency checks for wrapper modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/Makefile -->
