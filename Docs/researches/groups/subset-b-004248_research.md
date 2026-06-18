# subset-b-004248 research

This grouped report covers Linux MFD drivers under `sources/distributed-fs/ceph-client/drivers/mfd`. Each section preserves the original source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/si476x-prop.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/si476x-prop.c

## Purpose
`si476x-prop.c` exposes Silicon Labs Si476x radio chip properties through a custom regmap. It validates property IDs by chip revision and adapts regmap reads and writes to the device command protocol.

## Important APIs, Types, and Functions
`struct si476x_property_range` models inclusive property ranges. `si476x_core_element_is_in_array()` and `si476x_core_element_is_in_range()` implement table lookups. Revision predicates `si476x_core_is_valid_property_a10()`, `si476x_core_is_valid_property_a20()`, and `si476x_core_is_valid_property_a30()` layer newer property sets on older revisions. `si476x_core_is_readonly_property()` blocks writes to revision-specific read-only properties. Regmap callbacks are `si476x_core_regmap_readable_register()`, `si476x_core_regmap_writable_register()`, `si476x_core_regmap_read()`, and `si476x_core_regmap_write()`. The exported entry point is `devm_regmap_init_si476x()`.

## Control Flow
Consumers call `devm_regmap_init_si476x()`, which installs a 16-bit register and 16-bit value regmap with `REGCACHE_MAPLE`. Each regmap access consults the current `struct si476x_core` stored on the I2C client. Reads call `si476x_core_cmd_get_property()` and return the command result as the register value. Writes call `si476x_core_cmd_set_property()`.

## State and Persistence
The file has no persistent state of its own. Runtime behavior depends on `core->revision`, the I2C client data, the regmap cache, and device-resident property values.

## Dependencies and Integration Points
It depends on `linux/mfd/si476x-core.h`, I2C client data, the regmap core, and Si476x command helpers supplied by the core driver. The exported initializer is used by Si476x subdrivers that want property access via regmap.

## Risks and Edge Cases
`BUG_ON()` fires if the revision is invalid or not initialized, so callers must set revision before regmap use. Property tables are hard-coded and incomplete tables can reject valid hardware properties or expose unsupported ones. Read-only filtering is revision-sensitive.

## Test Signals
Useful checks include successful regmap creation after revision detection, readable and writable table behavior for A10/A20/A30-only properties, read-only write rejection, get/set command error propagation, and regcache behavior across repeated property access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/si476x-prop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/simple-mfd-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/simple-mfd-i2c.c

## Purpose
`simple-mfd-i2c.c` is a generic I2C parent driver for simple register-mapped MFD devices. It creates a shared regmap, then either populates child DT nodes or registers static MFD cells for known compatible strings.

## Important APIs, Types, and Functions
The probe entry is `simple_mfd_i2c_probe()`. Default register format is `regmap_config_8r_8v`. Static cell arrays describe `sy7636a`, `max5970`/`max5978`, `max77705-battery`, and `spacemit,p1` children. `simple_mfd_i2c_of_match` maps compatible strings to optional `struct simple_mfd_data`.

## Control Flow
Probe fetches match data with `device_get_match_data()`, chooses a device-specific or default regmap config, and calls `devm_regmap_init_i2c()`. If no static MFD cells are configured, `devm_of_platform_populate()` creates child devices from firmware child nodes. Otherwise `devm_mfd_add_devices()` creates the declared cell list.

## State and Persistence
State is devm-managed: the parent regmap and child devices live for the I2C device lifetime. The driver itself keeps no global or persistent state.

## Dependencies and Integration Points
It integrates with OF matching, `devm_regmap_init_i2c()`, MFD cell registration, and child drivers that obtain the parent regmap through `dev_get_regmap(dev->parent, NULL)` or equivalent parent-device lookup.

## Risks and Edge Cases
Any compatible without match data gets an 8-bit register and 8-bit value map, which must match hardware. Static-cell devices ignore DT child-node enumeration. Cell names must match child platform drivers exactly.

## Test Signals
Probe success, shared parent regmap visibility from children, correct child list for each compatible, fallback DT population for simple CPLD/FPGA compatibles, and failure propagation from regmap or MFD registration are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/simple-mfd-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/simple-mfd-i2c.h -->
# sources/distributed-fs/ceph-client/drivers/mfd/simple-mfd-i2c.h

## Purpose
`simple-mfd-i2c.h` defines the match-data contract used by the simple I2C MFD parent driver.

## Important APIs, Types, and Functions
`struct simple_mfd_data` contains an optional `const struct regmap_config *regmap_config`, an optional `const struct mfd_cell *mfd_cell`, and `size_t mfd_cell_size`.

## Control Flow
There is no runtime control flow in this header. `simple-mfd-i2c.c` reads this structure during probe to select regmap formatting and decide whether to register static child cells.

## State and Persistence
The structure is immutable match data for OF device IDs. It contains pointers to static config tables and no mutable state.

## Dependencies and Integration Points
The header depends on `linux/mfd/core.h` and `linux/regmap.h`. It is private to this driver directory and couples OF match entries to MFD child registration.

## Risks and Edge Cases
The structure does not encode validation, so mismatched `mfd_cell_size`, stale cell names, or an incorrect regmap config fail only at runtime.

## Test Signals
Compile coverage, correct designated initializers, and successful probe of each compatible using static `simple_mfd_data` exercise this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/simple-mfd-i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/sky81452.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/sky81452.c

## Purpose
`sky81452.c` is the MFD parent for the Skyworks SKY81452 backlight/regulator chip. It creates an 8-bit I2C regmap and registers backlight and regulator child devices.

## Important APIs, Types, and Functions
`sky81452_config` defines the regmap. `sky81452_probe()` allocates fallback platform data when none is supplied, initializes the regmap, stores it as client data, fills two `mfd_cell` entries, and calls `devm_mfd_add_devices()`.

## Control Flow
Probe initializes the regmap, builds cells for `sky81452-backlight` and `sky81452-regulator`, passes regulator init data through the regulator cell, and registers both children. OF and legacy I2C IDs bind the driver.

## State and Persistence
The parent stores only the regmap in I2C client data. Regulator init data is copied by pointer into the cell's platform data. Hardware register state is not cached beyond regmap defaults.

## Dependencies and Integration Points
It depends on I2C, regmap, MFD core, and `linux/mfd/sky81452.h`. Child drivers consume the shared regmap and optional regulator platform data.

## Risks and Edge Cases
When no platform data exists, the allocated structure is zeroed, so `pdata->regulator_init_data` is NULL and `pdata_size` still uses the pointed-to type size. Child drivers must tolerate missing regulator init data. Child cell names and OF compatibles are the integration contract.

## Test Signals
Probe on `skyworks,sky81452`, regmap access by both children, regulator child behavior with and without platform data, and error logging from failed child registration are useful validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/sky81452.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/sm501.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/sm501.c

## Purpose
`sm501.c` is the core MFD driver for the Silicon Motion SM501/SM502 multimedia companion chip. It supports both platform and PCI instantiation, manages shared system registers, clocks, power gates, optional GPIO, and registers child devices such as framebuffer, USB host, UARTs, GPIO-backed I2C, and serial ports.

## Important APIs, Types, and Functions
`struct sm501_devdata` is the parent runtime state: locks, child list, resources, platform data, registers, power refcounts, suspend flags, revision, and IRQ. Exported helpers include `sm501_misc_control()`, `sm501_modify_reg()`, `sm501_unit_power()`, and `sm501_set_clock()`. Clock helpers include `sm501_calc_clock()`, `sm501_calc_pll()`, and `sm501_select_clock()`. Child construction uses `sm501_create_subdev()`, `sm501_register_device()`, `sm501_register_usbhost()`, `sm501_register_uart()`, and `sm501_register_display()`. GPIO support, when enabled, is implemented through `sm501_gpio_*()` callbacks and two 32-pin gpiochips.

## Control Flow
Platform and PCI probes allocate `sm501_devdata`, claim and map resources, then call `sm501_init_dev()`. Common init validates the device ID, disables IRQs, computes local memory from DRAM control, creates a debug sysfs register file, applies optional platform init register values, registers requested optional children, validates clock-source errata, and always registers the framebuffer child. PCI probe also enables the PCI device and installs default platform data. Remove paths unregister children, remove debug files, remove GPIO chips, unmap registers, and release resources.

## State and Persistence
The driver persists runtime state in `sm501_devdata`, including child platform-device list, `unit_power[]` refcounts, clock/power locks, mapped register bases, and saved `pm_misc` across suspend. Hardware state lives in SM501 system, GPIO, power mode, clock, and gate registers. Suspend can power off the chip via platform callbacks and resume reapplies saved miscellaneous control and optional init data if register state changed.

## Dependencies and Integration Points
It depends on platform resources, PCI, SM501 register definitions, serial 8250 platform data, optional gpiolib, optional I2C-GPIO, and child drivers named `sm501-fb`, `sm501-usb`, `serial8250`, and `i2c-gpio`. It exports shared register and clock helpers to SM501 children.

## Risks and Edge Cases
Clock switching toggles between power modes and must preserve gate state; bad M/M1 PLL sources can hit documented errata and fail initialization. `unit_power[]` is refcounted but invalid unit IDs and unbalanced shutdowns are only logged. PCI probe calls `sm501_init_dev(sm)` but does not check its return before returning success. GPIO lookup tables are registered for generated I2C-GPIO devices and must align with gpiochip labels. Child resource carving from local memory is order-sensitive.

## Test Signals
Signals include successful platform and PCI probe, child device creation for all requested platform-data bits, framebuffer always appearing, clock set/readback behavior, power gate refcounting under multiple children, suspend/resume with and without platform power-off, GPIO get/set/direction paths, and failure cleanup for resource claim or child registration errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/sm501.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/smpro-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/smpro-core.c

## Purpose
`smpro-core.c` is the Ampere Altra SMPro I2C MFD parent. It creates a custom regmap for SMPro command formatting, validates the manufacturer ID, and registers hardware monitor, error monitor, and miscellaneous child devices.

## Important APIs, Types, and Functions
`smpro_core_write()` wraps `i2c_master_send()`. `smpro_core_read()` sends a register plus requested length and then reads the value in a two-message I2C transfer. `smpro_regmap_bus` declares big-endian value formatting. `smpro_core_readable_noinc_reg()` marks error-data registers as no-increment readable. `smpro_core_probe()` initializes the regmap, reads `MANUFACTURER_ID_REG`, checks `AMPERE_MANUFACTURER_ID`, and registers `smpro_devs`.

## Control Flow
Probe requires OF match data containing a regmap config. It creates the regmap with the device as bus context, reads the ID, rejects non-Ampere devices with `-ENODEV`, and uses `devm_mfd_add_devices()` for three fixed child cells.

## State and Persistence
No global state exists. Runtime state is the devm regmap and child devices. Error monitor data is read directly from hardware through no-increment registers.

## Dependencies and Integration Points
The file depends on I2C, regmap custom bus hooks, OF matching for `ampere,smpro`, and child drivers `smpro-hwmon`, `smpro-errmon`, and `smpro-misc`.

## Risks and Edge Cases
Partial I2C transfers return `-EIO`. Read transactions depend on the device protocol accepting a two-byte command `{reg, val_size}`. Manufacturer-ID mismatch prevents all children. No remove path is needed because devm handles children.

## Test Signals
Validate big-endian 16-bit reads, no-increment error data reads, manufacturer-ID rejection, child-device creation, and I2C short-transfer handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/smpro-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/sprd-sc27xx-spi.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/sprd-sc27xx-spi.c

## Purpose
`sprd-sc27xx-spi.c` is the SPI MFD parent for Spreadtrum SC2730/SC2731 PMICs. It exposes PMIC registers through regmap, creates a regmap IRQ chip, populates child devices, supports wakeup, and exports charger-type detection.

## Important APIs, Types, and Functions
`struct sprd_pmic` stores regmap, IRQ chip data, PMIC data, and parent IRQ. `struct sprd_pmic_data` supplies interrupt base/count and charger-detection register. `sprd_pmic_detect_charger_type()` polls charger detection and returns a USB charger type. SPI regmap bus callbacks are `sprd_pmic_spi_write()` and `sprd_pmic_spi_read()`. `sprd_pmic_probe()` sets up the regmap IRQ chip and child devices. PM callbacks are `sprd_pmic_suspend()` and `sprd_pmic_resume()`.

## Control Flow
Probe loads match data for SC2730 or SC2731, allocates state, initializes a 32-bit native-endian SPI regmap, builds one `regmap_irq` mask per PMIC interrupt, registers the IRQ chip on the SPI IRQ line, populates OF child nodes, and initializes wakeup support. Suspend enables IRQ wake when allowed; resume disables it.

## State and Persistence
Runtime state is devm-managed. Hardware interrupt enable/status registers and charger-detection bits are volatile. Wake capability is stored in the device PM state.

## Dependencies and Integration Points
It depends on SPI, regmap, regmap-irq, OF platform population, `linux/mfd/sc27xx-pmic.h`, and USB charger type definitions. Child PMIC function drivers bind under the parent DT node.

## Risks and Edge Cases
The SPI read path supports only one 32-bit register and one 32-bit value at a time. Charger detection can time out after polling. IRQ chip `ack_base = 0` relies on this PMIC's interrupt semantics and regmap-irq behavior. Match data is mandatory even though SPI IDs exist.

## Test Signals
Exercise both PMIC variants, regmap 32-bit read/write, PMIC IRQ delivery, wakeup suspend/resume, OF child population, and charger detection returning SDP/CDP/DCP/UNKNOWN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/sprd-sc27xx-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ssbi.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/ssbi.c

## Purpose
`ssbi.c` implements the Qualcomm Single-wire Serial Bus Interface parent driver. It provides serialized byte read/write helpers over SSBI, SSBI2, or PMIC-arbiter controller variants and populates child devices.

## Important APIs, Types, and Functions
`struct ssbi` stores mapped registers, a spinlock, controller type, and selected read/write operations. Public exports are `ssbi_read()` and `ssbi_write()`. Controller helpers include `ssbi_wait_mask()`, `ssbi_read_bytes()`, `ssbi_write_bytes()`, `ssbi_pa_transfer()`, `ssbi_pa_read_bytes()`, and `ssbi_pa_write_bytes()`.

## Control Flow
Probe maps the controller registers, reads `qcom,controller-type`, selects either the SSBI/SSBI2 or PMIC-arbiter accessors, initializes the lock, and populates child OF devices. Public read/write APIs take the spinlock, call the selected accessor, and release the lock.

## State and Persistence
State is per-controller runtime state plus volatile MMIO registers. SSBI2 writes high address bits through `SSBI2_MODE2`. No suspend cache or persistent storage is present.

## Dependencies and Integration Points
It depends on platform MMIO resources, OF, `linux/ssbi.h`, and downstream SSBI child drivers that call the exported read/write helpers with the parent `struct device`.

## Risks and Edge Cases
Transactions busy-wait up to `SSBI_TIMEOUT_US`; slow or stuck hardware returns `-ETIMEDOUT`. PMIC-arbiter transfers can return `-EPERM` on transaction denied. The controller type property is required and invalid values fail probe. SSBI2 address-high programming is shared state protected by the lock.

## Test Signals
Validate all three controller types, concurrent child read/write serialization, timeout paths, PMIC-arbiter denied transactions, multi-byte operations, and child OF population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ssbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/stm32-lptimer.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/stm32-lptimer.c

## Purpose
`stm32-lptimer.c` is the MFD parent for STM32 low-power timers. It maps timer registers through a clocked regmap, detects hardware capabilities, and populates child devices.

## Important APIs, Types, and Functions
`stm32_lptimer_regmap_cfg` configures 32-bit MMIO register access. `stm32_lptimer_detect_encoder()` probes legacy encoder support by writing and reading the encoder bit. `stm32_lptimer_detect_hwcfgr()` reads version and HW configuration registers for encoder and capture/compare channel count. `stm32_lptimer_probe()` performs resource, regmap, clock, capability, and child setup.

## Control Flow
Probe allocates `struct stm32_lptimer`, maps the MMIO resource, initializes a regmap gated by the `"mux"` clock, gets the timer clock, detects capability from `HWCFGR` or the legacy write/readback fallback, stores driver data, and calls `devm_of_platform_populate()`.

## State and Persistence
State is the parent `stm32_lptimer` structure: regmap, clock, version, encoder support, and channel count. Hardware registers are volatile and no explicit suspend cache is provided here.

## Dependencies and Integration Points
It depends on STM32 LPTIM register definitions, platform resources, regmap MMIO with clock support, and child drivers under the low-power timer DT node.

## Risks and Edge Cases
Legacy detection writes `STM32_LPTIM_ENC`, so the timer should be inactive or safe to probe. Missing or unreadable HWCFGR falls back only when the first HWCFGR value is zero. Clock name `"mux"` must match device tree/clock provider expectations.

## Test Signals
Probe on legacy and HWCFGR-capable timers, correct encoder detection, channel-count detection, child population, and failures from MMIO, regmap, or clock acquisition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/stm32-lptimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/stm32-timers.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/stm32-timers.c

## Purpose
`stm32-timers.c` is the MFD parent and shared helper provider for STM32 general-purpose timers. It exposes a clocked MMIO regmap, IRQ metadata, optional DMA channels, counter-width detection, and an exported DMA burst-read API for child drivers.

## Important APIs, Types, and Functions
The exported helper is `stm32_timers_dma_burst_read()`. DMA internals include `stm32_timers_dma_done()`, `stm32_timers_dma_probe()`, and `stm32_timers_dma_remove()`. Hardware probing uses `stm32_timers_get_arr_size()` and `stm32_timers_probe_hwcfgr()`. IRQ discovery uses `stm32_timers_irq_probe()`. Parent lifecycle is `stm32_timers_probe()` and `stm32_timers_remove()`.

## Control Flow
Probe maps registers, stores the physical base for DMA, creates a regmap using the `"int"` clock, gets the timer clock, detects counter width from HWCFGR/IPIDR or ARR write/readback fallback, discovers either a global IRQ or all four named IRQs, requests optional DMA channels, stores driver data, and populates child OF devices. Remove depopulates children before releasing DMA channels.

## State and Persistence
`struct stm32_timers` holds regmap, clock, maximum ARR, optional IP ID, IRQ array/count, and DMA state. DMA state includes channel array, active channel, completion, mutex, and physical base. Hardware timer and DMA registers are volatile. No persistent storage exists.

## Dependencies and Integration Points
It depends on STM32 timer headers, platform resources, regmap MMIO with clock support, DMAengine, OF child population, resets indirectly through included headers, and child PWM/counter/IIO drivers using parent data and exported DMA burst reads.

## Risks and Edge Cases
DMA burst read validates ranges but still depends on caller-provided DMA-safe buffers. It serializes one DMA burst at a time with a mutex and terminates DMA on all exits. IRQ configuration must be either one global IRQ or exactly all four named IRQs. HWCFGR IPIDR mismatch rejects unsupported hardware.

## Test Signals
Exercise global and split IRQ DT layouts, optional DMA absent and present, timeout and interruptible DMA completion paths, ARR-width fallback, STM32MP25 IPIDR validation, child depopulation before DMA release, and exported burst reads from child drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/stm32-timers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/stmfx.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/stmfx.c

## Purpose
`stmfx.c` is the I2C MFD core for STMicroelectronics STMFX-0300 multifunction expander. It manages the chip regmap, optional VDD supply, function enable/disable arbitration, nested interrupts, reset, suspend/resume restore, and child devices for pinctrl, IDD measurement, and touchscreen.

## Important APIs, Types, and Functions
Regmap callbacks are `stmfx_reg_volatile()` and `stmfx_reg_writeable()`. Exported function controls are `stmfx_function_enable()` and `stmfx_function_disable()`. IRQ functions include `stmfx_irq_handler()`, `stmfx_irq_map()`, `stmfx_irq_init()`, and `stmfx_irq_exit()`. Chip lifecycle functions are `stmfx_chip_init()`, `stmfx_chip_reset()`, `stmfx_chip_exit()`, `stmfx_probe()`, `stmfx_remove()`, `stmfx_suspend()`, and `stmfx_resume()`.

## Control Flow
Probe creates an 8-bit regmap, initializes the mutex, enables optional VDD, verifies chip ID against the I2C address, reads firmware version, resets the chip, configures the IRQ output pin from DT and parent IRQ trigger, requests a threaded IRQ, creates an IRQ domain, and registers three MFD cells with IRQ resources. The threaded handler reads pending sources, ACKs non-GPIO sources, and dispatches nested IRQs.

## State and Persistence
`struct stmfx` stores the regmap, IRQ domain, cached IRQ source mask, locks, optional regulator, and suspend backups for SYS_CTRL and IRQ_OUT_PIN. Suspend backs up selected registers, disables the IRQ, and may disable VDD. Resume re-enables VDD, resets the chip, restores backed-up registers and `irq_src`, then re-enables the IRQ.

## Dependencies and Integration Points
It depends on I2C, regmap with maple cache, regulator framework, irqdomain, nested threaded IRQ handling, and child drivers compatible with `st,stmfx-0300-pinctrl`, `st,stmfx-0300-idd`, and `st,stmfx-0300-ts`.

## Risks and Edge Cases
Function conflicts are enforced in software because IDD/TS firmware behavior can disable ALTGPIO. GPIO pending has no direct ACK and is represented by a logical OR of GPIO pending banks. Resume resets the chip, so all necessary state must be backed up or reconfigured by children. Probe defers only when chip init returns `-ETIMEDOUT`.

## Test Signals
Validate chip ID/address matching, firmware logging, function conflict rejection, nested IRQ delivery for GPIO/IDD/TS sources, open-drain and polarity configuration, suspend/resume with regulator off, and child drivers reusing exported function controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/stmfx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/stmpe-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/stmpe-i2c.c

## Purpose
`stmpe-i2c.c` is the I2C transport wrapper for the STMPE MFD core. It supplies byte/block SMBus accessors, maps OF/I2C IDs to STMPE part numbers, and delegates common setup and teardown to `stmpe_probe()` and `stmpe_remove()`.

## Important APIs, Types, and Functions
Transport callbacks are `i2c_reg_read()`, `i2c_reg_write()`, `i2c_block_read()`, and `i2c_block_write()`. `stmpe_i2c_probe()` prepares `stmpe_client_info` and selects the part number from OF match data or I2C ID. `stmpe_i2c_remove()` calls core removal. OF and I2C tables cover STMPE610, 801, 811, 1600, 1601, 1801, 2401, and 2403.

## Control Flow
The I2C driver probes, fills the static `i2c_ci` with current client, IRQ, and device pointers, resolves the part number, and calls the common STMPE core. Remove fetches core state from device data and tears it down through `stmpe_remove()`.

## State and Persistence
This wrapper has static callback data updated at probe time and no separate persisted state. Device state is allocated by `stmpe.c`.

## Dependencies and Integration Points
It depends on SMBus byte and I2C block operations and the internal `stmpe.h` core interface. The PM ops are exported by the common STMPE core.

## Risks and Edge Cases
The static `i2c_ci` is shared by all devices, so concurrent multi-device probe would rewrite the transport context before the common core copies/uses it. OF-less matching falls back to I2C ID and logs that compatible strings are preferred.

## Test Signals
Probe all supported compatibles, exercise byte and block register access, verify fallback ID matching, check PM callback wiring, and remove/reprobe without stale core state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/stmpe-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/stmpe-spi.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/stmpe-spi.c

## Purpose
`stmpe-spi.c` is the SPI transport wrapper for the STMPE MFD core. It implements the STMPE SPI command format, enforces the device speed limit, performs SPI-specific initialization, and delegates common logic to `stmpe_probe()`.

## Important APIs, Types, and Functions
`spi_reg_read()` uses `spi_w8r16()` with `READ_CMD`. `spi_reg_write()` sends a two-byte command with value in the high byte. Block access loops through byte accesses in `spi_block_read()` and `spi_block_write()`. `spi_init()` sets 8 bits per word, writes STMPE811 SPI mode when applicable, and calls `spi_setup()`. Probe/remove functions are `stmpe_spi_probe()` and `stmpe_spi_remove()`.

## Control Flow
Probe rejects SPI speeds above 1 MHz, fills static `spi_ci`, and calls `stmpe_probe()` with the SPI ID's part number. The common core later invokes `spi_init()` before chip initialization. Remove delegates to `stmpe_remove()`.

## State and Persistence
The wrapper has no independent device state beyond the static `stmpe_client_info`. SPI device configuration is modified at runtime by `spi_init()`.

## Dependencies and Integration Points
It depends on SPI core helpers and the common STMPE core. OF compatibles cover the SPI-capable STMPE variants, while device IDs provide the part numbers.

## Risks and Edge Cases
The static transport info has the same multi-instance caveat as the I2C wrapper. `spi_block_write()` writes bytes in reverse value order while incrementing register addresses, matching this bus protocol but worth regression testing. `spi_setup()` failures are only debug-logged in `spi_init()`.

## Test Signals
Validate 1 MHz speed rejection, STMPE811 SPI_CFG programming, byte read/write command encoding, block read/write ordering, common core probe for all SPI IDs, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/stmpe-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/stmpe.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/stmpe.c

## Purpose
`stmpe.c` is the common core for STMicroelectronics STMPE multifunction expanders. It abstracts I2C/SPI register access, models multiple chip variants, controls functional blocks, manages nested interrupts, parses DT children, and registers GPIO, keypad, touchscreen, ADC, and PWM child devices as supported.

## Important APIs, Types, and Functions
Exported register and block APIs include `stmpe_enable()`, `stmpe_disable()`, `stmpe_reg_read()`, `stmpe_reg_write()`, `stmpe_set_bits()`, `stmpe_block_read()`, `stmpe_block_write()`, `stmpe_set_altfunc()`, `stmpe811_adc_common_init()`, `stmpe_probe()`, and `stmpe_remove()`. Variant descriptors are `struct stmpe_variant_info` and `struct stmpe_variant_block` instances for STMPE610/801/811/1600/1601/1801/2401/2403. IRQ handling uses `stmpe_irq()`, `stmpe_irq_mask()`, `stmpe_irq_unmask()`, `stmpe_irq_sync_unlock()`, and an irqdomain.

## Control Flow
Transport wrappers call `stmpe_probe()` with callbacks and a part number. Probe parses DT for requested child blocks and ADC settings, handles optional VCC/VIO regulators, resolves parent IRQ or IRQ GPIO, selects no-IRQ variant data when supported, initializes the chip, creates an IRQ domain and threaded parent IRQ when present, then registers requested child cells. Chip init reads and validates the chip ID, disables all modules, resets the chip, configures interrupt control from trigger type, optionally enables autosleep, and writes the interrupt-control register. Nested IRQ handling reads ISR banks, masks by cached IER state, dispatches mapped child IRQs, and clears serviced bits.

## State and Persistence
`struct stmpe` stores transport callbacks, variant info, register index table, locks, child block requests, regulator handles, IRQ domain, IER/old IER caches, ADC configuration, and optional IRQ line. Hardware state is reset during probe; block enable bits, interrupt masks, alternate functions, autosleep, and ADC setup live in volatile chip registers. Suspend/resume only toggles IRQ wake for wake-capable devices.

## Dependencies and Integration Points
The file depends on transport wrappers, regulators, gpio descriptors for optional IRQ GPIO, irqdomain/nested IRQ handling, and MFD children named `stmpe-gpio`, `stmpe-keypad`, `stmpe-ts`, `stmpe-adc`, and `stmpe-pwm`. Child drivers use exported register/block APIs and `stmpe_set_altfunc()`.

## Risks and Edge Cases
Variant tables encode register ordering and interrupt counts; mistakes map child drivers to wrong registers. Only STMPE801 supports no-IRQ mode here. Some variants do not support edge-trigger configuration. `stmpe_devices_init()` mutates static resource arrays to fill IRQ numbers, which can be risky with multiple instances. Regulator enable failures are warnings, not fatal, after optional supplies are found.

## Test Signals
Test each variant ID and requested child combination, no-IRQ STMPE801, parent IRQ trigger polarity, IRQ mask/unmask synchronization, reset completion timeout, autosleep timeout rounding, ADC common init, alternate-function programming, and remove path regulator disable plus child removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/stmpe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/stmpe.h -->
# sources/distributed-fs/ceph-client/drivers/mfd/stmpe.h

## Purpose
`stmpe.h` is the private interface and register map header for the STMPE core and its I2C/SPI transport wrappers. It defines variant metadata, transport callbacks, exported core entry points, interrupt bits, and register constants for supported STMPE chips.

## Important APIs, Types, and Functions
`struct stmpe_variant_block` binds an MFD cell, base IRQ, and block ID. `struct stmpe_variant_info` describes chip ID/mask, GPIO count, alternate-function width, register index table, block table, IRQ count, and callbacks. `struct stmpe_client_info` is the transport abstraction consumed by `stmpe_probe()`. Declarations include `stmpe_probe()`, `stmpe_remove()`, and `stmpe_dev_pm_ops`.

## Control Flow
The header has no executable control flow. The core uses these definitions to select register addresses, enable blocks, configure autosleep, and register child cells for each variant.

## State and Persistence
It defines constants and type layouts only. Runtime state is held in `struct stmpe` from the public MFD header and in variant instances declared in `stmpe.c`.

## Dependencies and Integration Points
It depends on Linux device, MFD core, public `linux/mfd/stmpe.h`, printk, and basic types. The private transport wrappers include this header to call the common core.

## Risks and Edge Cases
Register constants include variant-specific byte ordering and LSB/MSB conventions, so child drivers are sensitive to correct register-index tables in `stmpe.c`. The duplicated comment block in the simple transport abstraction is harmless but signals legacy maintenance.

## Test Signals
Build coverage across I2C and SPI wrappers, all variant table initializers, and child drivers using public STMPE definitions exercises this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/stmpe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/stpmic1.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/stpmic1.c

## Purpose
`stpmic1.c` is the I2C MFD parent for STPMIC1 PMICs. It defines regmap access rules, exposes PMIC interrupts through regmap-irq, registers child devices from DT, and installs a power-off handler.

## Important APIs, Types, and Functions
Regmap access tables define readable, writable, and volatile ranges. `stpmic1_irqs` maps PMIC interrupt bits. `stpmic1_regmap_irq_chip` defines pending, mask, unmask, and ACK bases. `stpmic1_power_off()` requests software switch-off with retries. `stpmic1_probe()` initializes the regmap, reads version, registers the IRQ chip and power-off handler, and populates children. PM callbacks are `stpmic1_suspend()` and `stpmic1_resume()`.

## Control Flow
Probe allocates `struct stpmic1`, creates an 8-bit cached regmap, gets the main IRQ from DT, reads `VERSION_SR`, creates the regmap IRQ domain on the main IRQ, registers the system power-off callback, and populates OF child devices. Suspend disables the main IRQ. Resume syncs the regcache and re-enables the IRQ.

## State and Persistence
State includes the parent regmap, IRQ number, IRQ chip data, and device pointer. Regmap maple cache preserves writable register values for resume synchronization. Interrupt pending/source and status registers are volatile.

## Dependencies and Integration Points
It depends on I2C, OF IRQ parsing, regmap/regmap-irq, reboot sys-off handlers, and STPMIC1 child devices under the PMIC DT node.

## Risks and Edge Cases
The power-off path retries because I2C access can transiently time out, but even repeated failure returns `NOTIFY_DONE`. Resume depends on `regcache_sync()` restoring cached writable state. Main IRQ acquisition is mandatory.

## Test Signals
Verify version read, all regmap IRQ lines and masks, child OF population, system power-off register update with retry behavior, suspend/resume regcache sync, and access-table enforcement for invalid registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/stpmic1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/stw481x.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/stw481x.c

## Purpose
`stw481x.c` is the I2C MFD core for STw4810/STw4811 PMICs. It reads power-control configuration, logs startup voltage/status information, creates a shared regmap, and registers the VMMC regulator child.

## Important APIs, Types, and Functions
`stw481x_get_pctl_reg()` accesses one-time-programmable power-control registers through split address bits in `STW_PCTL_REG_HI/LO` and verifies the selected address. `stw481x_startup()` reads configuration and voltage selector registers. `stw481x_probe()` allocates state, initializes the regmap, runs startup, and registers `stw481x-vmmc-regulator`.

## Control Flow
Probe creates an 8-bit regmap, validates readable startup state through several regmap reads, fills the child cell's platform data with the parent `struct stw481x`, and registers the regulator child through `devm_mfd_add_devices()`.

## State and Persistence
Parent state is the I2C client and regmap in `struct stw481x`. The driver reads OTP-backed power-control values but does not modify or persist them.

## Dependencies and Integration Points
It depends on I2C, regmap, `linux/mfd/stw481x.h`, and the child regulator driver. It is OF matched by `st,stw4810` and `st,stw4811`.

## Risks and Edge Cases
Power-control register access relies on write-then-read address latch behavior and returns `-EIO` if verification fails. The driver logs many status fields but does not correct unexpected configuration. Only non-USB register space is accessible through this path.

## Test Signals
Probe on both compatibles, successful power-control register verification, correct logged voltage selectors, regulator child registration, and failure behavior for I2C/regmap errors are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/stw481x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/sun4i-gpadc.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/sun4i-gpadc.c

## Purpose
`sun4i-gpadc.c` is the MFD parent for Allwinner sunxi GPADC/touchscreen blocks. It creates an MMIO regmap, exposes FIFO/temp interrupts through regmap-irq, and registers GPADC IIO and hwmon children for supported SoC variants.

## Important APIs, Types, and Functions
`sun4i_gpadc_regmap_irq` maps FIFO data and temperature data interrupts. `sun4i_gpadc_regmap_irq_chip` defines status, ACK, and unmask registers. Variant-specific MFD cell arrays name the IIO child for sun4i, sun5i, or sun6i. `sun4i_gpadc_probe()` selects the cell array, maps registers, initializes regmap and IRQ chip, and registers children.

## Control Flow
Probe matches the DT compatible to an architecture ID, selects child cells, allocates `struct sun4i_gpadc_dev`, maps the MMIO resource, initializes a 32-bit regmap, disables all interrupts, obtains the platform IRQ, adds the regmap IRQ chip, and registers child MFD devices.

## State and Persistence
State is per-device: mapped base, regmap, regmap IRQ data, and device pointer. Interrupt and ADC registers are volatile. No suspend or persistent state is handled in this parent.

## Dependencies and Integration Points
It depends on platform MMIO resources, regmap-irq, Allwinner GPADC register definitions, and child IIO/hwmon drivers named by the selected cells.

## Risks and Edge Cases
Interrupts are disabled before regmap-irq setup, so child drivers must enable what they need. Variant selection is DT-compatible driven; unsupported data values fail probe. The parent assumes one IRQ resource exists.

## Test Signals
Validate all three compatibles, FIFO and temperature interrupt delivery, disabled-interrupt startup state, IIO child naming, hwmon child creation, and cleanup on regmap-irq or MFD-add failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/sun4i-gpadc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/sun6i-prcm.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/sun6i-prcm.c

## Purpose
`sun6i-prcm.c` is the Allwinner PRCM MFD parent. It splits one PRCM memory resource into clock, reset, and codec-analog child devices based on SoC compatible.

## Important APIs, Types, and Functions
`struct prcm_data` stores the selected child list. Static `mfd_cell` arrays describe sun6i-a31 and sun8i-a23 PRCM subdevices and their relative memory resources. `sun6i_prcm_probe()` selects match data, gets the parent memory resource, and calls `mfd_add_devices()`.

## Control Flow
The built-in platform driver matches the PRCM node, picks the SoC-specific `prcm_data`, verifies a memory resource exists, and registers all child cells with the parent resource as the base for relative offsets.

## State and Persistence
The file has no allocated runtime state. Hardware state is managed by child clock/reset/codec drivers.

## Dependencies and Integration Points
It depends on MFD core, OF matching, and child drivers for Allwinner AR100/APB0 clocks, gate clocks, reset control, IR clock, and codec analog blocks.

## Risks and Edge Cases
Relative child resources assume the parent resource covers all offsets. Missing parent memory resource returns `-ENOENT`. The driver uses `builtin_platform_driver()`, making it part of early platform setup rather than a loadable module path.

## Test Signals
Boot on sun6i-a31 and sun8i-a23 DTs, child resource offsets, clock/reset provider registration, codec analog child on sun8i-a23, and failure logging for missing memory resources are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/sun6i-prcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/syscon.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/syscon.c

## Purpose
`syscon.c` provides shared regmap access to system-controller MMIO regions described by device tree. It lazily registers syscon regmaps, supports lookup by compatible or phandle, and allows external drivers to register a regmap for a node.

## Important APIs, Types, and Functions
`struct syscon` tracks a device node, regmap, optional reset, and list entry. Internal registration is `of_syscon_register()` and lookup is `device_node_get_regmap()`. Exported APIs include `of_syscon_register_regmap()`, `device_node_to_regmap()`, `syscon_node_to_regmap()`, `syscon_regmap_lookup_by_compatible()`, `syscon_regmap_lookup_by_phandle()`, `syscon_regmap_lookup_by_phandle_args()`, and `syscon_regmap_lookup_by_phandle_optional()`.

## Control Flow
Lookup functions find or parse a device node, then call `syscon_node_to_regmap()` or `device_node_to_regmap()`. `device_node_get_regmap()` searches the global list under `syscon_list_lock`; if absent and creation is allowed, `of_syscon_register()` maps the resource, configures endianness, IO width, optional hwspinlock, regmap name/stride/value width/max register, creates the regmap, optionally attaches clock/reset resources, deasserts reset, and appends it to the list.

## State and Persistence
Global state is `syscon_list` protected by `syscon_list_lock`. Created regmaps and MMIO mappings persist for system lifetime; there is no unregister path for lazily created syscons. Externally registered regmaps are also stored in the list.

## Dependencies and Integration Points
It depends on OF address/phandle parsing, MMIO regmap, clocks, reset controls, optional hardware spinlocks, and many platform drivers that use syscon phandles for shared control registers.

## Risks and Edge Cases
`syscon_node_to_regmap()` only creates a regmap automatically for nodes compatible with `"syscon"` and checks resources, while `device_node_to_regmap()` can create for any node without clock/reset management. Resource size must be at least `reg-io-width`. Optional hwspinlock errors other than missing lock can defer or fail registration. Lazy-created entries are singleton per `device_node *`.

## Test Signals
Validate lookup by compatible, direct node, phandle, phandle args, and optional phandle. Exercise endianness and `reg-io-width`, hwspinlock configuration, clock attach/reset deassert paths, duplicate external registration returning `-EEXIST`, and deferred creation for non-syscon nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/syscon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tc3589x.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/tc3589x.c

## Purpose
`tc3589x.c` is the core MFD driver for Toshiba TC3589x I2C GPIO/keypad expanders. It provides shared SMBus register helpers, initializes the chip, creates an IRQ domain, dispatches nested interrupts, and registers GPIO and keypad child devices selected by platform data or DT children.

## Important APIs, Types, and Functions
Exported helpers are `tc3589x_reg_read()`, `tc3589x_reg_write()`, `tc3589x_block_read()`, `tc3589x_block_write()`, and `tc3589x_set_bits()`. IRQ functions include `tc3589x_irq()`, `tc3589x_irq_map()`, and `tc3589x_irq_init()`. Chip and child setup are `tc3589x_chip_init()`, `tc3589x_device_init()`, `tc3589x_of_probe()`, and `tc3589x_probe()`. PM callbacks set clock mode to sleep/operation when the device is not wake-enabled.

## Control Flow
Probe obtains platform data or builds it from DT child compatibles, checks SMBus functionality, allocates state, chooses GPIO count by chip version, initializes hardware by verifying manufacturer code and resetting unused modules, creates an IRQ domain, requests the falling-edge threaded parent IRQ, and registers selected child cells. The IRQ thread repeatedly reads IRQ status, dispatches nested IRQs for each set bit, performs another read to flush/observe clears, and loops while pending status remains.

## State and Persistence
`struct tc3589x` stores I2C client, device, platform data, lock, domain, and GPIO count. Hardware reset and clock mode are volatile. No register cache is used.

## Dependencies and Integration Points
It depends on I2C SMBus byte/block support, irqdomain, nested threaded IRQs, MFD child drivers `tc3589x-gpio` and `tc3589x-keypad`, and public `linux/mfd/tc3589x.h`.

## Risks and Edge Cases
`request_threaded_irq()` is not devm-managed and remove only calls `mfd_remove_devices()`, so IRQ lifetime relies on driver-core cleanup or legacy assumptions. The IRQ domain is not explicitly removed in remove. Dummy readback is required for interrupt clear effects. Unsupported SMBus adapters fail probe.

## Test Signals
Test all compatibles and legacy IDs, GPIO count selection, manufacturer-code rejection, nested IRQ delivery and repeated-status loop, child selection from DT, sleep/operation PM writes, and remove/reprobe behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tc3589x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ti-lmu.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/ti-lmu.c

## Purpose
`ti-lmu.c` is the I2C MFD core for TI Lighting Management Unit devices. It powers up the chip, creates a shared regmap, initializes a fault notifier, and registers regulator, backlight, LED, and fault-monitor child devices according to chip family.

## Important APIs, Types, and Functions
`struct ti_lmu_data` stores chip-specific child cells and maximum register. `ti_lmu_enable_hw()` drives the optional enable GPIO and applies the LM3631 LCD_EN sequence. `ti_lmu_disable_hw()` is the devm cleanup action. `ti_lmu_probe()` selects match data, initializes the regmap, enables hardware, initializes the blocking notifier, and registers children.

## Control Flow
Probe gets OF match data, allocates `struct ti_lmu`, builds an 8-bit regmap config named after the I2C ID, requests optional enable GPIO high, waits for hardware, performs any chip-specific power-up sequence, registers a cleanup action to turn the GPIO off, initializes the fault notifier head, stores client data, and registers chip-specific MFD cells.

## State and Persistence
State is the parent `struct ti_lmu`: device, regmap, optional enable GPIO, and notifier chain. Child drivers own functional register programming. The cleanup action disables the hardware enable GPIO on detach or failed later probe.

## Dependencies and Integration Points
It depends on I2C, GPIO descriptors, regmap, TI LMU headers/register definitions, and children such as `ti-lmu-backlight`, `lm363x-regulator`, `lm3633-leds`, `lm36274-leds`, and `ti-lmu-fault-monitor`.

## Risks and Edge Cases
Probe requires OF match data even though I2C IDs are present. `id->driver_data` is used for the LM3631 special sequence and assumes a matching I2C ID is available. Enable GPIO is requested initially high before `ti_lmu_enable_hw()` sets it again. Child set varies significantly by compatible.

## Test Signals
Validate each compatible's child list and max register, optional enable GPIO sequencing and cleanup, LM3631 LCD_EN update, notifier availability to fault-monitor children, and regmap access bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ti-lmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ti_am335x_tscadc.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/ti_am335x_tscadc.c

## Purpose
`ti_am335x_tscadc.c` is the MFD parent for TI AM335x touchscreen/ADC and AM437x magnetic-stripe/ADC subsystems. It configures shared sequencer registers, runtime PM, clock divider, child cells, and exports serialized step-enable helpers for ADC and touchscreen children.

## Important APIs, Types, and Functions
Exported sequencer helpers are `am335x_tsc_se_set_cache()`, `am335x_tsc_se_set_once()`, `am335x_tsc_se_adc_done()`, and `am335x_tsc_se_clr()`. Internal synchronization uses `am335x_tscadc_need_adc()` and `reg_se_wait`. `tscadc_idle_config()` programs idle step config. `ti_tscadc_probe()` parses DT, validates channel/step counts, initializes regmap and clocks, enables the subsystem, and registers child cells. PM callbacks are `tscadc_suspend()` and `tscadc_resume()`.

## Control Flow
Probe parses touchscreen wires/readouts or magnetic-stripe defaults, counts ADC channels, validates that total input channels do not exceed 8 and touchscreen steps do not exceed 16, maps registers, creates a 32-bit regmap, enables runtime PM, computes and writes the ADC clock divider, configures control bits, programs idle config, enables the subsystem, creates secondary and ADC child cells as requested, and registers them. Sequencer helpers serialize `REG_SE` access so one-shot ADC operations can wait for an active sequencer to reach an acceptable state before taking over.

## State and Persistence
`struct ti_tscadc_dev` stores regmap, MMIO base/physical base, IRQ, control register cache, clock divider, `REG_SE` cache, spinlock, waitqueue, and flags for ADC use/waiting. Suspend clears step enables, may keep subsystem enabled for wake-capable children, and runtime-suspends the parent. Resume restores clock divider, control, idle config, and subsystem enable.

## Dependencies and Integration Points
It depends on DT child nodes `tsc` and `adc`, regmap MMIO, clocks, runtime PM, MFD children for ADC/TSC/MAG, and public `linux/mfd/ti_am335x_tscadc.h`.

## Risks and Edge Cases
There is compatibility for misspelled `ti,coordiante-readouts`. `pm_runtime_get_sync()` return is not checked. The sequencer wait uses uninterruptible sleep and assumes a wake-up from step-cache updates. Channel and step validation is strict and DT-driven. Clock divider calculation assumes parent clock is at least target rate.

## Test Signals
Validate DT parsing for touchscreen and ADC-only modes, invalid channel rejection, sequencer arbitration under concurrent ADC/TSC users, suspend wake-child behavior, resume register restoration, runtime PM balance, and child platform data correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ti_am335x_tscadc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/timberdale.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/timberdale.c

## Purpose
`timberdale.c` is the PCI MFD driver for the Timberdale FPGA card. It validates FPGA firmware, enables MSI-X, resets on-card peripherals, configures board data from the hardware image, and registers many child devices spread over PCI BARs.

## Important APIs, Types, and Functions
`struct timberdale_device` stores control register mapping and firmware version/config. Large static resource, board-info, and platform-data tables describe I2C, SPI, Ethernet, GPIO, DMA, UART, media, radio, video, and SDHCI children. `fw_ver_show()` exposes firmware version. `timb_probe()` performs PCI setup and child registration. `timb_remove()` removes children and releases PCI resources.

## Control Flow
Probe allocates private state, enables the PCI device, maps the control block in BAR0, reads firmware major/minor/config, rejects unsupported versions, allocates 16 MSI-X entries, creates the firmware sysfs attribute, resets PLB peripherals, rewrites I2C board-info IRQs to MSI-X vectors, chooses 8-bit or 16-bit SPI board data from config, selects the BAR0 child-cell set by hardware version, registers BAR0 children, registers BAR1 SDHCI, optionally registers BAR2 SDHCI for hardware versions 0 and 3, frees the temporary MSI-X array, and logs the detected card. Remove reverses child and resource setup.

## State and Persistence
State is the mapped control area, firmware version/config values, and devres-independent child devices. Hardware reset is issued at probe. MSI-X vectors remain enabled until remove or error unwind.

## Dependencies and Integration Points
It depends on PCI, MSI-X, MFD core, software nodes/properties for the TSC2007 I2C child, and many child subsystem drivers including `timb-dma`, `timb-uart`, `xiic-i2c`, `ocores-i2c`, `timb-gpio`, `timb-video`, `timb-radio`, `xilinx_spi`, `ks8842`, `uartlite`, `timb-mlogicore`, and `sdhci`.

## Risks and Edge Cases
The error path returns `-ENODEV` for all probe failures, losing specific error causes. Static board-info IRQs and SPI platform data are mutated at runtime, which can be problematic across multiple cards. MSI-X entry zero is supplied as the MFD IRQ base while child resources use relative IRQ numbers. Firmware versions outside major 3 or below minor 8 are rejected.

## Test Signals
Test supported and unsupported firmware revisions, all four hardware configurations, 8-bit and 16-bit SPI setup, MSI-X vector assignment to children, BAR1/BAR2 SDHCI registration, sysfs `fw_ver`, PLB reset write, and error unwind after each setup stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/timberdale.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/timberdale.h -->
# sources/distributed-fs/ceph-client/drivers/mfd/timberdale.h

## Purpose
`timberdale.h` defines firmware compatibility constants, register offsets, BAR-relative child resource offsets, PCI IDs, IRQ indices, GPIO pins, and DMA channel numbers for the Timberdale FPGA MFD driver.

## Important APIs, Types, and Functions
Key constants include `DRV_VERSION`, `TIMB_SUPPORTED_MAJOR`, `TIMB_REQUIRED_MINOR`, control registers `TIMB_REV_MAJOR`, `TIMB_REV_MINOR`, `TIMB_HW_CONFIG`, `TIMB_SW_RST`, hardware config masks, BAR offset/end pairs, `PCI_VENDOR_ID_TIMB`, `PCI_DEVICE_ID_TIMB`, `IRQ_TIMBERDALE_*`, `TIMBERDALE_NR_IRQS`, GPIO pins, and DMA channel identifiers.

## Control Flow
There is no executable control flow. `timberdale.c` consumes these constants to validate firmware, map control registers, select child cell configuration, and assign resources.

## State and Persistence
The header defines static constants only. Firmware revision and hardware config values are read at runtime by the driver.

## Dependencies and Integration Points
It is private to the Timberdale MFD driver and aligns resource numbers with child platform drivers for DMA, media, networking, GPIO, SPI, I2C, UART, and SDHCI blocks.

## Risks and Edge Cases
Incorrect offsets or IRQ indices would misroute child MMIO or MSI-X interrupts. The firmware support window is encoded here, so driver updates are required for newer major versions.

## Test Signals
Compile coverage and runtime resource verification for every hardware config exercise this header. Firmware compatibility tests should confirm the major/minor constants match intended support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/timberdale.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps6105x.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/tps6105x.c

## Purpose
`tps6105x.c` is the I2C MFD core for TI TPS61050/TPS61052 boost converters. It creates a regmap, reports startup mode, always registers a GPIO child, and registers one operational child for LED torch, flash, regulator, or shutdown mode.

## Important APIs, Types, and Functions
`tps6105x_regmap_config` defines an 8-bit regmap bounded by `TPS6105X_REG_3`. `tps6105x_startup()` reads mode bits from register 0 and logs the current hardware mode. `tps6105x_add_device()` attaches the parent state as child platform data and calls `mfd_add_devices()`. `tps6105x_parse_dt()` derives mode from available child node names. Probe/remove are `tps6105x_probe()` and `tps6105x_remove()`.

## Control Flow
Probe obtains platform data or parses DT, allocates parent state, initializes regmap, stores client data, reads startup mode, registers the GPIO child, then registers one child based on requested mode: LEDs, flash, regulator, or none. Remove removes children and writes shutdown mode to register 0.

## State and Persistence
State is `struct tps6105x` with I2C client, regmap, and platform data. Child cells receive a pointer to this state. Remove deliberately persists shutdown mode to hardware.

## Dependencies and Integration Points
It depends on I2C, regmap, MFD core, public `linux/mfd/tps6105x.h`, and child drivers `tps6105x-gpio`, `tps6105x-leds`, `tps6105x-flash`, and `tps6105x-regulator`.

## Risks and Edge Cases
DT parsing supports at most one available operational child and uses child node names `regulator` and `led`; flash mode is not selected by the shown DT parser. If second child registration fails after GPIO registration, `mfd_remove_devices()` removes all children. Invalid mode is warned but not fatal unless a previous error exists.

## Test Signals
Validate DT and platform-data modes, GPIO child always present, each operational child selection, startup-mode logging, shutdown write on remove, and error cleanup when operational child registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/tps6105x.c -->
