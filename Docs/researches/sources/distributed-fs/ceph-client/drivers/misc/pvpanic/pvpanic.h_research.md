# sources/distributed-fs/ceph-client/drivers/misc/pvpanic/pvpanic.h

Purpose: small shared header between pvpanic core and bus front ends.

Important APIs and types: forward declares `struct attribute_group` and `struct device`, declares `devm_pvpanic_probe(struct device *dev, void __iomem *base)`, and exports `pvpanic_dev_groups`.

Control flow and integration: transport drivers include this header to map their hardware resource then delegate core registration and expose common sysfs groups.

State and persistence: no state.

Dependencies and risks: includes compiler types for `__iomem`. Any signature change must update both PCI/MMIO transports and the core. Build tests should compile both front ends independently.
