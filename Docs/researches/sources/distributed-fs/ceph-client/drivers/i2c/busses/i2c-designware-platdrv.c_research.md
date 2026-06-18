# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-platdrv.c

## Purpose
Platform/ACPI/OF front end for DesignWare I2C controllers. It gathers platform resources, firmware timing, semaphore support, clocks, reset, and PM policy, then delegates to the shared DesignWare core.

## Important APIs, Types, And Functions
Core routines are `dw_i2c_plat_probe()`, `dw_i2c_plat_remove()`, `dw_i2c_plat_request_regs()`, `dw_i2c_get_parent_regmap()`, `i2c_dw_probe_lock_support()`, and `dw_i2c_plat_pm_cleanup()`. Match tables include OF `mobileye,eyeq6lplus-i2c`, `mscc,ocelot-i2c`, `snps,designware-i2c`, many ACPI IDs, and platform ID `i2c_designware`.

## Control Flow
Probe derives flags from match data or `wx,i2c-snps-model`, treats missing IRQ as polling mode, allocates `dw_i2c_dev`, maps MMIO or gets parent regmap for Intel Xe/Wangxun, acquires optional reset, parses firmware configuration, probes BayTrail/AMD PSP semaphores, configures DesignWare mode, enables optional `pclk` and main clock, computes SDA hold from timing properties, initializes adapter class/number, sets PM flags and autosuspend, then calls `i2c_dw_probe()`.

## State And Persistence
All state is in `dw_i2c_dev` and runtime PM. `shared_with_punit` holds an extra runtime PM usage count and alters cleanup. DMI may select `I2C_CLASS_HWMON` for known hardware.

## Dependencies And Integration Points
Uses platform resources, MFD syscon/parent regmaps, clocks, resets, DMI, ACPI, OF, runtime PM, semaphore helper modules, and DesignWare common/master/slave code.

## Risks
Resource path differs by model: MMIO, parent regmap, polling, and semaphore variants must all initialize the common core correctly. Missing IRQ intentionally means polling only for `-ENXIO`, but other IRQ errors abort. Runtime PM must be disabled before cleanup and clocks must be balanced on probe failure.

## Test Signals
Test ACPI/OF/platform matching, IRQ and no-IRQ paths, parent regmap models, semaphore callbacks, clock prepare failure cleanup, DMI adapter class, autosuspend behavior, and remove with PUNIT-shared devices.
