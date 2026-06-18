# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-common.c

## Purpose
Shared Synopsys DesignWare I2C core. It abstracts register access, parses firmware timing, initializes hardware, controls clocks/locks, handles common errors and PM, dispatches master/slave IRQs, and registers the Linux adapter for platform-specific front ends.

## Important APIs, Types, And Functions
This file implements exported APIs declared in `i2c-designware-core.h`: `i2c_dw_init()`, `i2c_dw_fw_parse_and_configure()`, `i2c_dw_scl_hcnt()`, `i2c_dw_scl_lcnt()`, `i2c_dw_prepare_clk()`, `i2c_dw_acquire_lock()`, `i2c_dw_release_lock()`, `i2c_dw_wait_bus_not_busy()`, `i2c_dw_handle_tx_abort()`, `i2c_dw_func()`, `i2c_dw_disable()`, `i2c_dw_probe()`, and `i2c_dw_dev_pm_ops`. Internal pieces include regmap detection, ACPI/OF configuration, FIFO-depth detection, and SDA hold setup.

## Control Flow
`i2c_dw_probe()` binds adapter fwnode, initializes regmap by detecting native/swapped/word register layout, sets SDA hold, detects FIFOs, runs master probe, initializes hardware, fills adapter algorithm and quirks, requests IRQ unless polling, masks interrupts, and registers a numbered adapter under a temporary runtime-PM usage hold. `i2c_dw_init()` acquires optional hardware lock, disables the controller, masks SMBus interrupts, writes timing registers, applies SDA hold, selects master/slave mode, and releases the lock. PM callbacks disable/reinitialize hardware and mark adapter suspend state.

## State And Persistence
All state lives in `struct dw_i2c_dev`, regmap-backed registers, runtime PM, and adapter registration. `sw_mask` mirrors interrupt masks for polling mode. `status` tracks active mode. No persistent storage is involved.

## Dependencies And Integration Points
Integrates with Linux regmap, ACPI timing methods (`SSCN`, `FMCN`, `FPCN`, `HSCN`), OF properties, DMI quirks, runtime PM, clocks, I2C bus recovery, DesignWare master/slave modules, and platform/PCI/AMD glue.

## Risks
Register layout autodetection is critical; wrong `COMP_TYPE` handling rejects hardware. Timing validation only allows 100 kHz, 400 kHz, 1 MHz, and 3.4 MHz. PM behavior differs for PUNIT-shared controllers. Disable must handle master-on-hold aborts without leaving SCL low. FIFO depth quirks and SDA hold workarounds are hardware-sensitive.

## Test Signals
Test native/swapped/word register maps, ACPI and OF timing sources, unsupported speed rejection, FIFO-depth detection and Wangxun override, interrupt versus polling registration, abort-source error mapping, bus-not-busy recovery, runtime/system PM, and master/slave IRQ dispatch.
