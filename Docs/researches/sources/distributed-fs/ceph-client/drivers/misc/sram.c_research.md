# sources/distributed-fs/ceph-client/drivers/misc/sram.c

## Purpose
`sram.c` is the generic on-chip SRAM platform driver. It maps SRAM resources, parses reserved child regions from device tree, creates genalloc pools for allocatable SRAM, optionally exports reserved partitions as sysfs binary files, and supports platform-specific initialization for Atmel secure RAM and Tegra SYSRAM.

## Important APIs, Types, and Functions
Core helpers include `sram_add_pool()`, `sram_add_export()`, `sram_add_partition()`, `sram_free_partitions()`, `sram_reserve_regions()`, `sram_read()`, and `sram_write()`. Platform configuration is described by `struct sram_config` with `atmel_securam_config` and `tegra_sysram_config`. Driver entry points are `sram_probe()`, `sram_remove()`, and `sram_init()` registered as a `postcore_initcall()`.

## Control Flow
Probe reads match data and `no-memory-wc`, maps the whole SRAM unless the platform requires mapping only reserved child regions, creates a root gen_pool when applicable, enables an optional clock, and calls `sram_reserve_regions()`. Reservation parsing converts DT children to sorted `struct sram_reserve` blocks, detects out-of-range or overlapping regions, creates exported/pool/protect-exec partitions, and adds gaps between reserved blocks to the root pool. Platform `init()` runs after reservation setup; Atmel waits for SECUMOD RAM ready through regmap polling. Remove tears down sysfs exports and warns if pools still have allocated SRAM.

## State and Persistence
`struct sram_dev` holds mapped base, root pool, partition array, config, and flags. Each `struct sram_partition` holds its base, optional pool, sysfs binary attribute, mutex, and list hook. SRAM contents are persistent only as hardware RAM across power domains; the driver does not save or restore contents.

## Dependencies and Integration Points
The driver depends on platform resources, OF address parsing, `gen_pool`, sysfs bin attributes, memory-mapped IO, optional clocks, syscon/regmap for Atmel SECUMOD, and the optional `CONFIG_SRAM_EXEC` helper declared in `sram.h`. Device-tree properties include child `export`, `pool`, `protect-exec`, `label`, and top-level `no-memory-wc`.

## Risks and Edge Cases
Overlap detection reports "starts after current offset" even though it detects `block->start < cur_start`. Exported sysfs files permit raw root read/write of SRAM partitions, so DT exposure is security-sensitive. `map_only_reserved` platforms rely on every usable child being mapped separately to avoid speculative access faults. Removing with allocated gen_pool memory only logs an error; consumers must release allocations.

## Test Signals
Test root pool gap creation, sorted overlapping reservation rejection, child labels and sysfs bin file names, exported read/write locking, pool allocation/free accounting, `protect-exec` handoff, `no-memory-wc` mapping choice, Tegra map-only-reserved behavior, Atmel RAM-ready polling, and remove-time allocation warnings.
