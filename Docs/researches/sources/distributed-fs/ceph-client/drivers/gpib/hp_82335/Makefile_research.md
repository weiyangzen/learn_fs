# sources/distributed-fs/ceph-client/drivers/gpib/hp_82335/Makefile

Purpose: builds the HP 82335 GPIB adapter module when `CONFIG_GPIB_HP82335` is enabled. The module target is `hp82335.o`.

Important build API: `obj-$(CONFIG_GPIB_HP82335) += hp82335.o` is the kbuild binding. The resulting adapter registers the `hp82335` GPIB board interface.

Control flow and integration: `hp82335.o` depends on common GPIB exports and TMS9914 helper symbols. It is a legacy memory-mapped ISA-style adapter driver, so runtime configuration comes from user ioctls for base address and IRQ rather than PCI/platform discovery.

State and persistence: no runtime state in the Makefile. Its effect is build availability of the HP82335 board type.

Dependencies: Kconfig should require GPIB common, TMS9914 support, MMIO/legacy resource APIs, and IRQ support.

Risks: if TMS9914 helper code is not selected, module linking will fail. Build coverage alone does not validate required legacy base-address/IRQ configuration.

Test signals: build with `CONFIG_GPIB_HP82335=m`, inspect dependencies, load/unload, and select `hp82335` through the common board-type ioctl with configured base/IRQ.
