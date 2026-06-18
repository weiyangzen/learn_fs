<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/omap-gpmc.h -->
# sources/distributed-fs/ceph-client/include/linux/omap-gpmc.h

## Purpose
This header declares OMAP General Purpose Memory Controller helpers, NAND/OneNAND integration hooks, chip-select programming APIs, and timing calculation interfaces.

## Important APIs, types, and functions
It includes platform GPMC data, defines `GPMC_CONFIG_WP`, legacy IRQ-domain numbers, `struct gpmc_nand_ops`, `struct gpmc_onenand_info`, and forward declarations. APIs include `gpmc_omap_get_nand_ops()`, `gpmc_omap_onenand_set_timings()`, `gpmc_calc_timings()`, `gpmc_cs_write_reg()`, `gpmc_calc_divider()`, `gpmc_cs_set_timings()`, `gpmc_cs_program_settings()`, `gpmc_cs_request()`, `gpmc_cs_free()`, `gpmc_configure()`, and `gpmc_read_settings_dt()`.

## Control flow
Board/device code reads DT settings, calculates timings, requests a chip-select window, programs settings/timings, and uses NAND or OneNAND-specific hooks as needed. Disabled `CONFIG_OMAP_GPMC` stubs return `NULL` or `-EINVAL` for OMAP-specific NAND/OneNAND helpers, while common timing/programming declarations remain external.

## State and persistence
GPMC controller registers, chip-select allocation, timing registers, and NAND/OneNAND mode state persist in hardware/controller implementation. The header stores no state.

## Dependencies and integration points
It depends on OMAP GPMC platform data, DT settings, NAND/OneNAND platform data, device nodes, and memory-controller/register programming code.

## Risks and test signals
Risks include bad timing calculations, chip-select window conflicts, write-protect misconfiguration, legacy IRQ number assumptions, and disabled GPMC stubs in storage drivers. Test NAND/OneNAND probe, DT timing parsing, CS request/free collisions, sync read/write timing, IRQ-domain mapping, and OMAP GPMC disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/omap-gpmc.h -->
