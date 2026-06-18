# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v5-irs.c

## Purpose

`irq-gic-v5-irs.c` implements GICv5 Interrupt Routing Service discovery and initialization. IRS blocks route SPIs and LPIs, provide Interrupt State Tables, map CPUs to IAFFIDs, expose SPI configuration operations, synchronize IRS state, and hand off to GICv5 ITS probing. The file supports both OF and ACPI firmware descriptions and initializes global GICv5 LPI domain data from the first IRS.

## Important APIs, Types, And Functions

The main driver state is `struct gicv5_irs_chip_data`, allocated per IRS and linked on `irs_nodes`. Per-CPU mappings are stored in `per_cpu_irs_data` and `cpu_iaffid`. File-local wrappers `irs_readl_relaxed()`, `irs_writel_relaxed()`, `irs_readq_relaxed()`, and `irs_writeq_relaxed()` access IRS MMIO.

IST setup is handled by `gicv5_irs_init_ist_linear()`, `gicv5_irs_init_ist_two_level()`, `gicv5_irs_l2_sz()`, `gicv5_irs_init_ist()`, and `gicv5_irs_iste_alloc()`. Public helpers include `gicv5_irs_cpu_to_iaffid()`, `gicv5_irs_lookup_by_spi_id()`, `gicv5_spi_irq_set_type()`, `gicv5_irs_syncr()`, `gicv5_irs_register_cpu()`, `gicv5_irs_remove()`, `gicv5_irs_enable()`, `gicv5_irs_its_probe()`, `gicv5_irs_of_probe()`, and `gicv5_irs_acpi_probe()`.

## Control Flow

OF probing iterates child nodes under the parent and initializes those compatible with `arm,gic-v5-irs`. `gicv5_irs_of_init()` allocates chip data, maps the `ns-config` register range, initializes base registers and cacheability with `gicv5_irs_init_bases()`, reads IAFFID width, parses CPU and `arm,iaffids` arrays, and calls `gicv5_irs_init()`. ACPI probing parses MADT GICv5 IRS subtables, reserves/maps IRS config space, initializes bases, parses GICC entries matching the current IRS ID to populate IAFFID mappings, and also calls `gicv5_irs_init()`.

`gicv5_irs_init()` validates LPI support, records the IRS SPI range, and for the first IRS initializes global virtual capability, priority bits, global SPI count, and the GICv5 LPI domain. `gicv5_irs_enable()` later initializes the IST on the first IRS. IST initialization reads IDR2 capabilities, chooses linear or two-level tables, caps ID bits by CPUIF support, chooses IST entry size and L2 table size, writes `IRS_IST_CFGR` and `IRS_IST_BASER`, waits for idle, and calls `gicv5_init_lpis()`. With two-level ISTs, `gicv5_irs_iste_alloc()` lazily allocates L2 tables for an LPI and asks the IRS to map the L2 entry.

CPU registration uses the previously parsed IAFFID and per-CPU IRS pointer. `gicv5_irs_register_cpu()` writes `IRS_PE_SELR`, waits for a valid PE selection, writes `IRS_PE_CR0_DPS`, and waits for completion. SPI type changes lock `spi_config_lock`, select the SPI, validate selection, write level/edge mode, and wait for the operation. `gicv5_irs_syncr()` writes `IRS_SYNCR` and waits on sync status. After IRSes are available, `gicv5_irs_its_probe()` invokes OF or ACPI GICv5 ITS probing.

## State And Persistence Behavior

Persistent state includes the global `irs_nodes` list, per-CPU IRS pointers, per-CPU IAFFID validity, and global GICv5 data updated by the first IRS. Per-IRS state stores MMIO base, fwnode, SPI range, flags, and a raw spinlock for SPI config. IST memory is allocated and intentionally ignored by kmemleak after hardware ownership. Two-level IST global metadata stores the L1 table address, L2 size, and L2 index bits. `gicv5_irs_remove()` tears down LPI domains, deinitializes LPIs, unmaps IRS MMIO, removes list entries, and frees chip data.

## Dependencies And Integration Points

The driver depends on GICv5 architecture helpers and global data from `arm-gic-v5.h`, OF and ACPI MADT parsing, kmemleak, cache maintenance helpers for non-coherent IRS blocks, and GICv5 ITS/LPI domain helpers such as `gicv5_init_lpi_domain()`, `gicv5_free_lpi_domain()`, `gicv5_init_lpis()`, `gicv5_deinit_lpis()`, `gicv5_its_of_probe()`, and `gicv5_its_acpi_probe()`. Firmware integration uses OF `reg-names = "ns-config"`, `cpus`, `arm,iaffids`, optional `dma-noncoherent`, and ACPI IRS/GICC fields including IRS ID, IAFFID, and non-coherent flags.

## Risks

Risks include incorrect IAFFID-to-CPU mapping, invalid firmware counts between CPUs and IAFFIDs, non-coherent cache maintenance mistakes, IST sizing errors, and lazy L2 allocation races. The code relies on irqdomain serialization for `gicv5_irs_iste_alloc()` rather than an internal lock. Linear IST allocation can approach kmalloc limits and caps LPI ID bits if necessary. ACPI parsing uses transient globals for the current IRS while scanning GICC entries, so future parallelization would need serialization. SPI configuration depends on correct IRS lookup and operation-status validity bits.

## Test Signals

Boot logs should show IRS detection, SPI ranges, IAFFID parsing warnings, global SPI counts, IST initialization failures, and LPI support checks. Tests should cover OF and ACPI probing, non-coherent IRS cache paths, CPU registration for every possible CPU, SPI type changes for edge and level variants, SPI lookup by ID, global sync, one-level and two-level IST initialization, lazy L2 IST allocation, GICv5 ITS handoff, and cleanup through `gicv5_irs_remove()`.
