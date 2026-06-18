# sources/distributed-fs/ceph-client/drivers/misc/pvpanic/Makefile

Purpose: maps pvpanic Kconfig selections to object files.

Important build rules: `obj-$(CONFIG_PVPANIC_MMIO) += pvpanic.o pvpanic-mmio.o` and `obj-$(CONFIG_PVPANIC_PCI) += pvpanic.o pvpanic-pci.o`.

Control flow: each selected transport links the shared core `pvpanic.o` with the corresponding bus front end.

State and persistence: no runtime state; build-only file.

Dependencies and integration points: consumed by the kernel build system under `drivers/misc`.

Risks and test signals: selecting both transports may include `pvpanic.o` through two obj lines depending on build-system aggregation; build tests should cover MMIO only, PCI only, and both enabled as built-ins/modules to catch duplicate symbol or missing shared-core issues.
