# sources/distributed-fs/ceph-client/drivers/net/can/kvaser_pciefd/Makefile

Purpose: this Makefile builds the Kvaser PCIe FD CAN driver as a composite object when `CONFIG_CAN_KVASER_PCIEFD` is enabled.

Important APIs, types, and functions: `obj-$(CONFIG_CAN_KVASER_PCIEFD) += kvaser_pciefd.o` declares the final object/module. `kvaser_pciefd-y = kvaser_pciefd_core.o kvaser_pciefd_devlink.o` combines the core PCI/CAN implementation with devlink support.

Control flow: Kbuild conditionally links the composite object from its two parts. There is no runtime behavior in the Makefile.

State and persistence: build configuration controls whether the driver is omitted, built-in, or built as a module. The `kvaser_pciefd-y` list is persistent build metadata for the composite object.

Dependencies and integration points: the file depends on the parent Kconfig symbol and the existence of `kvaser_pciefd_core.c`, `kvaser_pciefd_devlink.c`, and shared declarations in `kvaser_pciefd.h`.

Risks: adding new source files for PCI IDs, firmware handling, or devlink features requires updating the composite list. If `CONFIG_CAN_KVASER_PCIEFD` is enabled without one of the component objects, the build fails at Kbuild time.

Test signals: a kernel or module build with `CONFIG_CAN_KVASER_PCIEFD=m` should compile both component objects and link `kvaser_pciefd.ko`; built-in mode should include both objects in vmlinux.
