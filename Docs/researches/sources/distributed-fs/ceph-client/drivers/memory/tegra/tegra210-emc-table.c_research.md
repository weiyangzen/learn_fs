# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210-emc-table.c

## Purpose
This file registers reserved-memory operations for Tegra210 EMC timing tables. It maps firmware-provided timing-table memory into the EMC driver's address space, classifies the first table as nominal and the second matching table as derated, stores table counts, and unmaps the table on release.

## Important APIs, Types, And Functions
The main callbacks are `tegra210_emc_table_init()`, `tegra210_emc_table_device_init()`, and `tegra210_emc_table_device_release()`, grouped in `tegra210_emc_table_ops`. `RESERVEDMEM_OF_DECLARE()` binds these ops to reserved-memory nodes compatible with `nvidia,tegra210-emc-table`. `TEGRA_EMC_MAX_FREQS` limits scanning to 16 timing entries. The code consumes `struct tegra210_emc_timing` and writes into `struct tegra210_emc` fields `nominal`, `derated`, and `num_timings`.

## Control Flow
When the EMC core calls `of_reserved_mem_device_init_by_name()` for `nominal` or `derated`, the reserved-memory framework invokes `device_init`. The callback `memremap()`s the region write-back, counts entries until a zero revision or 16 entries, warns and ignores excess tables after nominal and derated are already assigned, requires derated entry count to match nominal count, and stores the mapped pointer in `rmem->priv`. Release checks that the pointer corresponds to either active table and calls `memunmap()`. Node init only logs base and size.

## State And Persistence
The persistent state is the mapping pointer stored in both `struct tegra210_emc` and `rmem->priv`. `emc->num_timings` is set from the nominal table and reused to validate derated tables. The timing contents are not copied; the core uses the mapped reserved-memory region directly. State persists for the device lifetime and is released by `of_reserved_mem_device_release()` from the EMC core.

## Dependencies And Integration Points
It depends on the reserved-memory framework, `memremap()`/`memunmap()`, the Tegra210 EMC timing struct definition, and the core driver's call order. It assumes only two named tables are meaningful: nominal first, derated second. The core later validates monotonic rates/voltages, selects timing entries, and builds clock configs from these mapped arrays.

## Risks
The table scanner trusts the reserved-memory size and scans up to 16 `struct tegra210_emc_timing` entries without deriving the bound from `rmem->size`; if firmware reserves too small a region, this can read beyond the mapping. If the nominal table has zero valid entries, core validation/current-rate matching will fail later. Excess tables are only warned and left mapped until release. Because data is used in place, corruption of reserved memory or ABI mismatch with `struct tegra210_emc_timing` can directly destabilize EMC programming.

## Test Signals
Tests should cover nominal-only and nominal-plus-derated reserved-memory nodes, derated count mismatch returning `-EINVAL`, excess table warnings, clean unmap on driver remove/failure, and core probe failure when no current-rate timing exists. Firmware/DT validation should ensure reserved-memory size is at least `num_entries * sizeof(struct tegra210_emc_timing)` and table revisions terminate with zero within 16 entries.
