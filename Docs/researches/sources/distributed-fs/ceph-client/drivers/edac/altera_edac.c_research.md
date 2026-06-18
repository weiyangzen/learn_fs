# sources/distributed-fs/ceph-client/drivers/edac/altera_edac.c Research

## Purpose
This driver provides EDAC support for Altera/Intel SoCFPGA memories: SDRAM controllers, L2 cache, OCRAM, and several Arria10/Stratix10 peripheral ECC blocks such as Ethernet, NAND, DMA, USB, QSPI, and SDMMC. It uses both EDAC memory-controller and EDAC device frameworks and handles legacy Cyclone5/Arria5 style devices as well as Arria10/Stratix10 ECC-manager interrupt aggregation.

## Important APIs, Types, and Functions
SDRAM support is driven by `struct altr_sdram_prv_data` tables `c5_data` and `a10_data`, `altr_sdram_mc_err_handler()`, `altr_sdr_mc_err_inject_write()`, `get_total_mem()`, `a10_init()`, `a10_unmask_irq()`, and `altr_sdram_probe()`. Generic EDAC-device support uses `struct edac_device_prv_data`, `altr_edac_device_handler()`, `altr_edac_device_trig()`, `altr_edac_device_probe()`, and `altr_create_edacdev_dbgfs()`. Arria10/Stratix10 support uses `altr_init_memory_port()`, `altr_init_a10_ecc_block()`, per-device setup tables, `altr_edac_a10_irq_handler()`, `altr_edac_a10_device_add()`, `a10_eccmgr_irqdomain_map()`, `s10_edac_dberr_handler()`, and `altr_edac_a10_probe()`.

## Control Flow
When SDRAM support is enabled, `altr_sdram_probe()` obtains the SDRAM syscon regmap, verifies ECC is already enabled, computes memory size from DT `memory` nodes, clears counts, registers an EDAC MC, requests SDRAM IRQs, enables ECC interrupts, and optionally exposes a debugfs injection trigger. The legacy ECC-manager parent `altr_edac_probe()` populates child platform devices for simple L2/OCRAM nodes. `altr_edac_device_probe()` maps each child register resource, runs the per-device dependency setup callback, requests SB/DB IRQs, registers an EDAC device, and creates debugfs injection hooks.

For Arria10/Stratix10, `altr_edac_a10_probe()` obtains the system-manager regmap, masks sensitive pending IRQs, creates a 64-entry IRQ domain, chains shared SBE/DBE parent IRQs, registers a Stratix10 panic notifier on 64-bit builds, reports sticky previous-boot UE state, and walks child nodes. Each matching child is registered through `altr_edac_a10_device_add()`, which maps the child resource, validates parent availability, runs device setup, requests logical IRQs, registers EDAC state, and links the device into the ECC-manager list. The chained handler reads system-manager SBE or DBE status and dispatches set bits through the IRQ domain.

## State and Persistence
Per-device state lives in `struct altr_sdram_mc_data`, `struct altr_edac_device_dev`, and the top-level `struct altr_arria10_edac`. Persistent hardware state includes ECC enable bits, pending interrupt status, sticky Stratix10 UE value/address registers, initialized ECC memory contents, and ECC-manager masks. EDAC core persists counters and sysfs/debugfs visibility. The driver also changes system state by refusing suspend for SDRAM EDAC and by panicking on selected uncorrectable errors.

## Dependencies and Integration Points
The driver depends on platform device-tree compatibles, syscon/regmap access to SDRAM and system-manager registers, IRQ domains, chained IRQ handlers, EDAC core APIs, debugfs when `CONFIG_EDAC_DEBUG` is enabled, genalloc SRAM pools for OCRAM injection, cache flush support for L2 injection, ARM SMCCC calls for Stratix10 secure register/ECC notification paths, and panic notifiers. Kconfig gates each peripheral block through `CONFIG_EDAC_ALTERA_*` symbols and related subsystem dependencies.

## Risks and Edge Cases
Many paths assume firmware or bootloader initialized memory and enabled ECC before Linux probes; enabling ECC after memory is live can cause immediate CE/UE events. Several UE paths call `panic()`, so false-positive DBE routing or stale status can be fatal. Debugfs injection intentionally corrupts ECC-protected data and must remain debug-only. The Arria10/Stratix10 path has architecture-specific IRQ parsing branches and a FIXME around compatibles for SDMMC. Resource cleanup uses devres groups and extra synthetic devices for SDMMC PortB, which are easy to regress. Sticky UE registers are cleared at probe after reporting previous-boot errors.

## Test Signals
Build matrix coverage should enable `EDAC_ALTERA` plus each `EDAC_ALTERA_*` option on suitable ARM/ARM64 SoCFPGA configs. Runtime tests need DT nodes for the SDRAM controller, ECC manager, and child ECC blocks; successful signals include EDAC MC/device registration, parent IRQ-domain dispatch, CE/UE counter increments, debugfs `altr_trigger` operation under `CONFIG_EDAC_DEBUG`, and correct previous-boot UE logging on Stratix10. Suspend attempts should fail with `-EPERM` when SDRAM EDAC is active.
