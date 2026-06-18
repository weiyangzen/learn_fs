# sources/distributed-fs/ceph-client/include/linux/irqchip/arm-gic-v5.h

## Purpose
`arm-gic-v5.h` defines the emerging ARM GICv5 register, table, global-state, and helper interfaces for IRS, ITS, IWB, PPIs/SPIs/LPIs/IPIs, and virtualization-capable interrupt routing.

## Important APIs, types, and functions
It defines INTID/hwirq type fields, architected PPI IDs, table attribute encodings, IRS/ITS/IWB register offsets and bitfields, table entry layouts, `struct gicv5_chip_data`, `struct gicv5_irs_chip_data`, wait helpers `gicv5_wait_for_op*_s`, probe/init/remove functions for IRS/ITS/LPI domains, SPI type setting, IAFFID lookup, and config structures for VPE, dev tables, and ITTs.

## Control flow
GICv5 code probes IRS and ITS instances from firmware, configures global domains, allocates interrupt state tables, maps SPIs to IRS ranges, initializes LPIs, waits for register operations to become idle, and exposes virtualization state through VPE/table structures.

## State and persistence
State is runtime hardware configuration: global domains, SPI counts, CPU/IRS priority and ID widths, IRS list entries, LPI/IST/ITT/devtab memory, SPI config locks, and VPE residency flags.

## Dependencies and integration points
It depends on I/O polling, cache flushing, SMP/sysreg arch headers, irqdomains, fwnodes, ACPI/OF probing, KVM, and LPI/MSI management.

## Risks and test signals
Risks include timeout logic, new bitfield/table encoding errors, wrong page-size support selection, IAFFID mapping mistakes, SPI range overlap, and virtualization table lifetime bugs. Tests should cover OF and ACPI probe, IRS enable/remove, LPI init/deinit, SPI type programming, timeout paths, CPU registration, and table invalidation/sync.
