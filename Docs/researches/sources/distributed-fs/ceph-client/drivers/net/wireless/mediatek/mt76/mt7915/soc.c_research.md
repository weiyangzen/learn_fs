# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/soc.c

## Purpose
This file provides the platform-driver bring-up path for integrated MT7981/MT7986 WMAC devices using the mt7915 core. It owns SoC resource mapping, reset and clock preparation, conninfra power sequencing, ADIE SPI access/calibration, WED/IRQ setup, and final registration through the common `mt7915_register_device()` path.

## Important APIs, Types, And Functions
The exported platform driver is `mt798x_wmac_driver`, matching `mediatek,mt7981-wmac` and `mediatek,mt7986-wmac`. `mt798x_wmac_probe()` maps MMIO, calls `mt7915_mmio_probe()`, initializes WED/IRQ, calls `mt798x_wmac_init()`, resets wfsys, and registers the common device. `mt798x_wmac_remove()` unregisters it.

The SoC enable/disable API is `mt7986_wmac_enable()` and `mt7986_wmac_disable()`. Supporting helpers include SPI accessors `mt76_wmac_spi_read/write/rmw`, semaphore helpers, conninfra checks/setup, SKU detection and update, GPIO pinctrl selection, ADIE efuse reads, thermal calibration, XTAL trim for 7975/7976 ADIEs, ADIE patch routines, AFE calibration, PLL/clock setup, WFSYS power and WM reset sequencing, and bus-timeout configuration.

## Control Flow
Probe starts with platform resource 0 as the device MMIO window, then delegates common MMIO allocation to mt7915. WED initialization may supply an IRQ; otherwise the platform IRQ is requested. The SoC init path enables named clocks (`mcu`, `ap2conn`), maps DCM/SKU resources, obtains the `consys` reset line, performs a wfsys reset, and registers the common wireless device.

The power-on sequence asserts/deasserts consys reset, selects pinctrl state based on ADIE type, releases conninfra sleep protection, validates conninfra version, programs reserved-memory EMI windows, detects main and optional second ADIE, applies ADIE configuration and calibration, initializes subsystem clocks, wakes WFSYS, powers WM, waits for ROM readiness, and writes SKU decode state. Disable reverses WFSYS power, sleep protection, EMI requests, wakeup, lockup, and reset.

## State And Persistence
Runtime state is stored in `struct mt7915_dev`: mapped `dcm` and `sku` bases, reset controller `rstc`, mt76 device state, WED attachment, and chip id/revision inherited from common code. Hardware state persists in conninfra, WFSYS, AFE, ADIE, SPI, EMI, and reset registers until powered down or reset. Calibration values are read from ADIE efuse and written into analog registers during each setup.

## Dependencies And Integration Points
The file depends on Linux platform, OF, reserved memory, pinctrl, reset, clock, and IRQ APIs. It integrates with mt7915 common MMIO, WED, IRQ handler, firmware registration, and register macros from `regs.h`. Device tree must provide compatible strings, memory resources, reserved memory, pinctrl states (`default` or `dbdc`), clocks, and `consys` reset.

## Risks
The sequencing is timeout-heavy and hardware-order-sensitive. A missing reserved-memory node, wrong pinctrl state, absent clocks, invalid SKU/ADIE combination, or SPI semaphore timeout prevents boot. Several helpers return success even after logging clock lookup failures, so later failures may be harder to attribute. ADIE trim paths use efuse validity flags and chip-specific magic values; regressions can degrade RF behavior without obvious driver errors. Disable paths use best-effort polling and do not propagate all timeout failures.

## Test Signals
Relevant tests are MT7981 and MT7986 probe/remove cycles, firmware boot after `mt7986_wmac_enable()`, suspend or module unload exercising disable, WED IRQ operation, device tree variants for single-band and DBDC ADIEs, ADIE SPI read/write timeout coverage, and RF sanity after thermal/XTAL calibration. Kernel logs should show no conninfra version, ROM index, sleep-protect, reset, or IRQ request failures.
