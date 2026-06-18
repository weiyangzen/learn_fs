# sources/distributed-fs/ceph-client/drivers/memory/omap-gpmc.c

## Purpose
`omap-gpmc.c` is the Texas Instruments General-Purpose Memory Controller driver. It manages chip-select address windows, GPMC timing programming, NAND/OneNAND integration, wait-pin GPIOs, a nested IRQ domain, device-tree child probing, and context save/restore for OMAP core power transitions.

## Important APIs, Types, And Functions
Global controller state includes `gpmc_base`, `gpmc_l3_clk`, `gpmc_cs[]`, `gpmc_mem_root`, `gpmc_cs_num`, `gpmc_nr_waitpins`, `gpmc_capability`, and `gpmc_irq_domain`. `struct gpmc_device` stores device, IRQ, irq/gpio chips, CPU PM notifier, saved context, wait pins, IRQ count, suspend flag, and optional data resource.

Exported APIs include `gpmc_cs_write_reg()`, `gpmc_calc_divider()`, `gpmc_cs_set_timings()`, `gpmc_cs_request()`, `gpmc_cs_free()`, `gpmc_configure()`, `gpmc_omap_get_nand_ops()`, `gpmc_omap_onenand_set_timings()`, `gpmc_calc_timings()`, `gpmc_cs_program_settings()`, and `gpmc_read_settings_dt()`. Major internal areas are chip-select memory allocation/remap, timing conversion and programming, IRQ domain setup, DT child probing, wait-pin GPIO registration, and OMAP3 context save/restore.

## Control Flow
Probe maps configuration registers, stores an optional data window resource, gets IRQ and `fck`, reads DT `gpmc,num-cs` and `gpmc,num-waitpins`, allocates wait-pin state, enables runtime PM, reads revision/capabilities, initializes the memory resource tree from existing bootloader chip-select mappings, registers wait-pin GPIOs, creates the IRQ domain and parent IRQ, probes DT children, and registers a CPU PM notifier.

Child probing parses `reg`, requests/remaps a chip-select, reads GPMC settings/timings from DT, optionally preserves bootloader timings if no `cs-rd-off` timing exists, handles NAND-specific bus width and write-protect, reserves wait pins, programs non-timing settings, programs timing registers, clears limited-address mode, enables the CS, and creates child platform devices.

## State And Persistence
Chip-select mappings are represented both in hardware CONFIG7 registers and in Linux resource objects under `gpmc_mem_root`. Wait pins are tracked as GPIO descriptors to allow sharing only with matching polarity. IRQ enable/status is managed through a nested irq domain. OMAP3 context save/restore records global and per-CS registers across CPU cluster PM and system sleep. Runtime PM gates the controller around suspend/resume.

## Dependencies And Integration Points
The driver integrates with OF, platform devices, MTD NAND platform data, GPMC public headers, GPIO provider APIs, irqdomain/generic IRQ APIs, CPU PM notifiers, runtime PM, clock framework, and child NAND/OneNAND/NOR drivers. It exports symbols consumed by memory and flash child drivers.

## Risks
The driver relies on several global single-controller variables, so multiple GPMC instances would be unsafe. Timing conversions mix ps and ns and retain legacy conversion paths. Child-probe failures can leave partially configured chip selects if cleanup misses a path. IRQ handling calls `generic_handle_irq()` even after warning about unmapped virqs, so virq-zero behavior should be considered. `gpmc_cs_set_reserved()` ignores its `reserved` argument and only sets the flag, so `gpmc_cs_free()` does not actually clear reservation through that helper. DT timing omissions intentionally preserve bootloader setup but can hide incomplete descriptions.

## Test Signals
Strong signals include DT probe with valid/invalid `num-cs` and waitpins, chip-select allocation/remap/resource collision tests, timing overflow errors, NAND register map retrieval, OneNAND sync timing programming, wait-pin GPIO reads and sharing validation, nested IRQ delivery for NAND and wait pins, context save/restore across suspend and CPU cluster PM, and child cleanup on probe failures.
