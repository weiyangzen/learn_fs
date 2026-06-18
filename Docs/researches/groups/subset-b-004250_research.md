# subset-b-004250 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/twl6030-irq.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/twl6030-irq.c

## Purpose
`twl6030-irq.c` implements the primary interrupt-handler demultiplexer for TI TWL6030/TWL6032 PMIC-family devices. The chip exposes three PIH interrupt status bytes; this driver maps the 24 PIH status bits into a smaller set of nested Linux IRQs for PMIC submodules such as power, RTC, hot-die, SMPS/LDO, battery, SIM/MMC detect, GPADC, gas gauge, USB, charger, and charger fault blocks.

## Important APIs, Types, And Functions
The central state is `struct twl6030_irq`, which stores the parent IRQ, nested IRQ domain, wake bookkeeping, PM notifier, selected model-specific mapping table, and cloned `irq_chip`. The exported setup and teardown functions are `twl6030_init_irq()` and `twl6030_exit_irq()`. The threaded parent IRQ handler is `twl6030_irq_thread()`. Nested IRQ domain operations are `twl6030_irq_map()` and `twl6030_irq_unmap()`. Subdrivers can call exported `twl6030_interrupt_mask()` and `twl6030_interrupt_unmask()` for PIH mask bits. Wake support is handled by `twl6030_irq_set_wake()` and `twl6030_irq_pm_notifier()`. Device matching chooses between `twl6030_interrupt_mapping[]` and `twl6032_interrupt_mapping[]`.

## Control Flow
Initialization matches the parent device against `"ti,twl6030"` or `"ti,twl6032"`, allocates the singleton state with `devm_kzalloc()`, masks all line/status interrupts, clears pending status, clones `dummy_irq_chip`, installs wake callbacks, creates a linear IRQ domain with 20 hardware IRQ numbers, and requests a threaded handler on the parent IRQ. The interrupt thread bulk reads `REG_INT_STS_A` through `REG_INT_STS_C`, patches the VBUS bit from charger status because the documented VBUS disconnect bit is unreliable, converts the 24-bit little-endian status to CPU order, and for each set bit finds the mapped nested module IRQ and calls `handle_nested_irq()`. It clears all three status registers by writing one byte to `REG_INT_STS_A`, matching the hardware behavior documented in the comment. Suspend prepare enables parent wake only when nested IRQs requested wake, disables the parent IRQ, and post-suspend reenables it.

## State, Persistence, And Dependencies
Runtime state is process-global through `static struct twl6030_irq *twl6030_irq`, so this file assumes one active TWL6030 PIH instance. Persistent hardware state is the three mask/status register sets and the parent IRQ wake-enable state. `wakeirqs` is an atomic count updated by nested IRQ wake calls and consumed by the PM notifier. Dependencies include the TWL I2C helpers from `linux/mfd/twl.h`, TWL core register constants from `twl-core.h`, Linux IRQ domains, nested threaded IRQ handling, OF matching, and PM notifier infrastructure.

## Integration Points
The TWL core calls `twl6030_init_irq()` while probing the parent PMIC and `twl6030_exit_irq()` on teardown. Child devices receive virtual IRQs from the domain and use normal Linux IRQ APIs; the map callback marks them nested and parents them to the PIH IRQ. TWL subdrivers also integrate through `twl6030_interrupt_mask()` and `twl6030_interrupt_unmask()` when they need direct mask control. Device-tree compatible data decides the status-bit-to-module mapping, which is different for TWL6030 and TWL6032 around system-low, watchdog, GPADC, and gas-gauge bits.

## Risks
The singleton state prevents multiple independent instances. `twl6030_exit_irq()` frees the IRQ with `NULL` dev_id even though request used `twl6030_irq`, which is fragile with shared teardown expectations. The teardown intentionally leaves the IRQ domain and nested descriptors allocated because child devices may retain resources; this can leak descriptors across remove/reprobe scenarios. Wake reference counting uses plain increment/decrement without underflow protection if wake disable calls are unbalanced. Mask/unmask callers must pass offsets matching the intended PIH mask register layout; the helpers do no validation. The handler maps 24 status bits into only 20 domain IRQ numbers, so reserved or unmapped bits are logged rather than serviced.

## Test Signals
Useful signals include boot-time probe on TWL6030 and TWL6032 boards, confirming all PIH masks are written and stale status is cleared. IRQ tests should trigger representative submodule bits, including RTC, power button, GPADC, USB ID/VBUS, charger, and charger fault, and confirm the expected nested virtual IRQ is invoked. Suspend/resume tests should enable wake on one nested IRQ and verify parent wake toggling, then repeat with no wake-enabled child IRQs. Fault injection on TWL I2C reads/writes should show warning/error paths without stuck IRQ storms. Remove/reprobe tests are valuable because teardown deliberately does not remove the domain.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/twl6030-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/twl6040.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/twl6040.c

## Purpose
`twl6040.c` is the MFD core for the TI TWL6040/TWL6041 audio companion chip. It owns the I2C regmap, power sequencing, PLL/sysclk state, interrupt-controller setup, regulator/clock resources, and MFD child registration for codec, vibra, GPO, and PDM clock functions.

## Important APIs, Types, And Functions
The file operates on `struct twl6040` from `linux/mfd/twl6040.h`. Exported register helpers are `twl6040_reg_read()`, `twl6040_reg_write()`, `twl6040_set_bits()`, and `twl6040_clear_bits()`. Exported power and clock APIs are `twl6040_power()`, `twl6040_set_pll()`, `twl6040_get_pll()`, `twl6040_get_sysclk()`, and `twl6040_get_vibralr_status()`. Internal helpers include `twl6040_power_up_manual()`, `twl6040_power_down_manual()`, `twl6040_power_up_automatic()`, `twl6040_readyint_handler()`, `twl6040_thint_handler()`, register access predicates, `twl6040_has_vibra()`, `twl6040_probe()`, and `twl6040_remove()`. Data tables include `twl6040_defaults[]`, `twl6040_patch[]`, `twl6040_irqs[]`, and child resource arrays.

## Control Flow
Probe requires an OF node and a valid I2C IRQ, initializes an 8-bit regmap with maple cache, gets optional `clk32k` and `mclk`, enables `vio` and `v2v1` regulators, applies the access-control patch, reads the ASIC revision, optionally requests the `ti,audpwron` GPIO for automatic power-up on post-ES1.0 silicon, creates a regmap IRQ chip, requests READY and thermal IRQs, builds MFD cells, marks the regmap cache-only/dirty because the chip is powered down, and adds children. `twl6040_power()` reference-counts power users under a mutex. On first power-up it enables `clk32k`, leaves cache-only mode, chooses automatic GPIO or manual register sequencing, waits for hardware access to settle, syncs regcache, and records the default LPPLL sysclk. On final power-down it toggles AUDPWRON or runs the manual shutdown sequence, sets regmap cache-only and dirty, clears sysclk, disables MCLK if HPPLL was active, and disables `clk32k`.

## State, Persistence, And Dependencies
State persists in `power_count`, `pll`, `sysclk_rate`, `mclk_rate`, the `ready` completion, regmap cache contents, IRQ data, and regulator/clock enable state. Hardware persistence is register state across power cycles only as restored by regcache sync and explicit power/PLL sequencing. The file depends on I2C, regmap/regcache, regmap IRQ, MFD core, regulator bulk APIs, gpiod, clocks, completion waits, and device-tree child detection for vibra. Register defaults seed codec, PLL, LDO, mic, headset, vibra, GPO, loopback, access-control, interrupt, and status registers.

## Integration Points
The codec child uses the plug IRQ and exported power/PLL helpers for ASoC operation. Vibra is created only when the OF child node `vibra` exists and receives the vibra IRQ. GPO and PDM clock children are always registered. The regmap IRQ chip maps thermal, plug/unplug, hook, hands-free, vibra, and ready interrupts out of `TWL6040_REG_INTID` with masks in `TWL6040_REG_INTMR`. Board integration must provide regulators and a correct IRQ; automatic power-up additionally depends on `ti,audpwron`.

## Risks
Several internal register reads return negative errno through `u8` temporaries in manual power-down and thermal handling, so failed reads can be collapsed into byte values. `regmap_register_patch()` return is ignored during probe. Automatic power-up relies on READYINT and falls back to checking INTID only after timeout, so interrupt misconfiguration can look like a power failure. `twl6040_set_pll()` enables `mclk` without checking the return from `clk_prepare_enable()`. The power reference count must be balanced by children; an extra power-off returns `-EPERM` and leaves state unchanged. Register 0 is unreadable, but most other addresses up to `TWL6040_REG_STATUS` are considered readable, so invalid-but-in-range accesses rely on hardware behavior.

## Test Signals
Probe tests should cover missing OF node, missing IRQ, regulator failures, optional clock deferral, revision read failure, AUDPWRON GPIO presence/absence, and child creation with and without a `vibra` node. Runtime tests should exercise balanced and nested `twl6040_power()` users, regcache sync after power-up, both automatic and manual sequences, thermal IRQ shutdown/restart, and READY timeout handling. PLL tests should cover LPPLL 17.64/19.2 MHz outputs, HPPLL inputs 12/19.2/26/38.4 MHz, unsupported rates, and switching back from HPPLL to LPPLL. Vibra status tests should verify combined left/right enable/select bits.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/twl6040.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ucb1x00-assabet.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/ucb1x00-assabet.c

## Purpose
`ucb1x00-assabet.c` is a small Assabet board-specific UCB1x00 child driver. It demonstrates board integration by exposing three ADC readings as device attributes and registering a polled `gpio-keys` platform device backed by the first six UCB1x00 GPIOs.

## Important APIs, Types, And Functions
The macro `UCB1X00_ATTR()` generates read-only sysfs show functions and `DEVICE_ATTR_RO()` instances for `vbatt`, `vcharger`, and `batt_temp`. The UCB child callbacks are `ucb1x00_assabet_add()` and `ucb1x00_assabet_remove()`, wired into `struct ucb1x00_driver ucb1x00_assabet_driver`. Module init/exit call `ucb1x00_register_driver()` and `ucb1x00_unregister_driver()`.

## Control Flow
When the UCB core registers this child, `ucb1x00_assabet_add()` clears static button and key metadata, maps six buttons to `BTN_0` through `BTN_5`, assigns GPIO numbers from `ucb->gpio.base`, sets a 50 ms poll interval, and registers a `gpio-keys` platform device beneath the UCB device. It then creates the three ADC sysfs files and stores the platform device pointer in `dev->priv`. Each sysfs read enables the ADC, performs one `ucb1x00_adc_read()` on the chosen channel with `UCB_NOSYNC`, disables the ADC, and prints the raw value. Remove unregisters the gpio-keys device if valid and removes the sysfs files.

## State, Persistence, And Dependencies
The only local state is the static `buttons[6]` array and the child-private platform device pointer. Persistent behavior is external: sysfs files remain while the child is attached, and the gpio-keys platform device remains registered until removal. Dependencies include the UCB core ADC/GPIO APIs, Linux platform device creation, gpio-keys platform data, input key codes, and the UCB core's ability to provide a valid gpiolib base.

## Integration Points
This driver is loaded through the UCB1x00 pseudo-driver registry rather than a normal bus match table. It assumes the parent UCB device has GPIOs registered with a stable base and an ADC path available. The gpio-keys child integrates with the input subsystem through the generic `gpio-keys` driver, while the ADC attributes integrate through the UCB class device.

## Risks
`platform_device_register_data()` errors are stored but do not make add fail, and sysfs creation return values are ignored; partial setup can therefore appear successful. GPIO numbers are computed from `ucb->gpio.base` without checking for `-1`, so boards without gpiolib support can register invalid keys. The static `buttons[]` array means multiple UCB instances would share mutable button metadata. Sysfs reads are raw ADC values with no scaling, calibration, or locking beyond the UCB ADC mutex. Removal checks only `IS_ERR(pdev)`, not `NULL`, but add normally stores the returned pointer.

## Test Signals
Validation should load the driver after UCB core probe, confirm six gpio-keys inputs appear with expected GPIOs and 50 ms polling, and read `vbatt`, `vcharger`, and `batt_temp` while observing ADC enable/read/disable behavior. Negative tests should cover missing gpiolib base, platform-device registration failure, sysfs creation failure, and unload ordering with the parent UCB device.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ucb1x00-assabet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ucb1x00-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/ucb1x00-core.c

## Purpose
`ucb1x00-core.c` is the core driver for Philips/NXP UCB1200, UCB1300, and TC35143 devices attached through the MCP bus. It centralizes register access locking, GPIO operations, ADC serialization, interrupt demultiplexing, pseudo-child driver registration, device class creation, and suspend/resume handling.

## Important APIs, Types, And Functions
Exported service APIs are `ucb1x00_io_set_dir()`, `ucb1x00_io_write()`, `ucb1x00_io_read()`, `ucb1x00_adc_enable()`, `ucb1x00_adc_read()`, `ucb1x00_adc_disable()`, `ucb1x00_register_driver()`, and `ucb1x00_unregister_driver()`. GPIO callbacks include `ucb1x00_gpio_set()`, `ucb1x00_gpio_get()`, direction callbacks, and `ucb1x00_to_irq()`. IRQ handling is split across `ucb1x00_irq()`, `ucb1x00_irq_mask()`, `ucb1x00_irq_unmask()`, `ucb1x00_irq_set_type()`, `ucb1x00_irq_set_wake()`, and `ucb1x00_detect_irq()`. Device lifecycle is handled by `ucb1x00_probe()`, `ucb1x00_remove()`, `ucb1x00_suspend()`, and `ucb1x00_resume()`. Global registries are `ucb1x00_drivers` and `ucb1x00_devices`, protected by `ucb1x00_mutex`.

## Control Flow
Probe optionally deasserts board reset, reads `UCB_ID`, accepts supported IDs, allocates and registers a class device, detects the physical IRQ by enabling the ADC interrupt and using `probe_irq_on/off()`, allocates 16 Linux IRQ descriptors, installs the UCB IRQ chip on each, and chains the detected parent IRQ to `ucb1x00_irq()`. If platform data supplies a GPIO base, it registers a 10-line gpiochip with direction, get/set, and GPIO-to-IRQ support. It then stores driver data, marks wake capability, adds the device to the global list, and calls every registered UCB child driver's `add()` callback. The chained IRQ handler enables MCP access, reads and clears `UCB_IE_STATUS`, dispatches each set bit to `generic_handle_irq(irq_base + i)`, and disables MCP access. Child driver registration is symmetric: adding a driver binds it to all existing devices, and unregistering removes all child instances.

## State, Persistence, And Dependencies
Per-device state includes cached GPIO direction/output bits, ADC control bits, IRQ mask/rising/falling/wake masks, allocated IRQ base, gpiochip state, list of child devices, and MCP pointer. ADC access is serialized by `adc_mutex`; GPIO shadow registers use `io_lock`; IRQ masks use `irq_lock`; global device/driver lists use `ucb1x00_mutex`. Hardware state persisted across runtime includes GPIO direction/output, interrupt edge enables, ADC control, and reset state delegated to platform callbacks. Dependencies include MCP bus APIs, Linux class/device infrastructure, gpiolib, legacy IRQ probing, chained IRQ handlers, platform data, and PM sleep ops.

## Integration Points
UCB child drivers such as the touchscreen and Assabet board driver integrate through `ucb1x00_register_driver()`. GPIOLIB consumers can use the registered gpiochip and convert GPIO lines to the 16 nested UCB IRQs. Platform data may provide reset callbacks, IRQ base, GPIO base, and wake capability. Suspend calls each child `suspend()` callback, programs only wake-enabled edge masks when needed, and enables parent IRQ wake. Resume restores reset if needed, rewrites cached GPIO data/direction, restores interrupt masks, disables parent wake, and resumes children.

## Risks
`ucb1x00_detect_irq()` busy-waits for ADC completion and depends on legacy IRQ probing, which is fragile on modern systems. Child `add()` failures during probe or driver registration are ignored in list iteration paths, so a partially unavailable child may not be obvious. GPIO support is skipped when `gpio_base` is absent, which affects child drivers that assume numeric GPIOs. IRQ descriptor allocation and chained handler setup are manual and require careful cleanup on each error path. The driver preserves state through shadow variables, so missed writes or reset events outside its control can desynchronize software and hardware. ADC users must call enable/disable in pairs or hold the mutex indefinitely.

## Test Signals
Core validation should probe all supported IDs, reject unsupported IDs, and exercise platform reset callbacks for probe, probe-fail, remove, suspend, and resume. GPIO tests should cover direction changes, output shadow retention, reads, and GPIO-to-IRQ conversion. IRQ tests should program rising/falling masks, trigger multiple simultaneous bits, confirm clear sequencing, and test wake-enabled suspend/resume. ADC tests should verify serialization across concurrent readers and conversion completion. Child registry tests should load/unload child drivers before and after core devices and verify add/remove ordering.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ucb1x00-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ucb1x00-ts.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/ucb1x00-ts.c

## Purpose
`ucb1x00-ts.c` implements the input touchscreen child driver for UCB1x00-based resistive touch panels. It uses UCB touchscreen control registers and ADC channels to report X, Y, pressure, and touch state through the Linux input subsystem.

## Important APIs, Types, And Functions
Driver state is `struct ucb1x00_ts`, which stores the input device, parent UCB pointer, IRQ wait queue, kernel sampling thread, plate resistance limits, IRQ-disable flag, and ADC sync mode. Sampling helpers are `ucb1x00_ts_read_pressure()`, `ucb1x00_ts_read_xpos()`, `ucb1x00_ts_read_ypos()`, `ucb1x00_ts_read_xres()`, `ucb1x00_ts_read_yres()`, `ucb1x00_ts_pen_down()`, and `ucb1x00_ts_mode_int()`. Event helpers are `ucb1x00_ts_evt_add()` and `ucb1x00_ts_event_release()`. Runtime callbacks are `ucb1x00_thread()`, `ucb1x00_ts_irq()`, `ucb1x00_ts_open()`, `ucb1x00_ts_close()`, `ucb1x00_ts_add()`, and `ucb1x00_ts_remove()`. The module parameter `adcsync` selects synchronized ADC conversions.

## Control Flow
When attached by the UCB core, `ucb1x00_ts_add()` allocates state and an input device, configures EV_ABS and BTN_TOUCH capabilities, measures X/Y plate resistance via ADC, sets ABS ranges, and registers the input device. Opening the input device requests the TSPX IRQ with rising edge on Collie or falling edge otherwise, measures resistance again, and starts kernel thread `ktsd`. The IRQ handler disables the touch IRQ and wakes the thread. The thread repeatedly enables ADC access, samples X, Y, and pressure, switches hardware back to interrupt mode, disables ADC, waits 10 ms, checks pen state, reenables the IRQ on release, emits release if a valid touch was active, or reports a sample and polls again after `HZ / 100`. It is freezer-aware and suppresses one sample after thaw. Close stops the thread, frees the IRQ, clears `UCB_TS_CR`, and disables the parent device.

## State, Persistence, And Dependencies
Runtime state is per child instance: thread pointer, IRQ wait queue, `irq_disabled`, plate resistance, and input device state. Hardware state is the touchscreen control register mode, ADC control held through the UCB core, and Collie-specific GPIO table-check control. The driver depends on the UCB core's ADC, IO, register, and nested IRQ APIs; Linux input subsystem; kthreads; freezer support; and machine-specific Collie helpers from `mach/collie.h` and `machine_is_collie()`.

## Integration Points
The driver registers through the UCB pseudo-driver list, so it is bound by `ucb1x00_register_driver()` rather than OF/ACPI matching. It consumes `ucb->irq_base + UCB_IRQ_TSPX`, UCB ADC inputs `TSPX/TSPY/AD2`, and UCB touchscreen register bits. User space sees a standard input device named `"Touchscreen panel"` with ABS_X, ABS_Y, ABS_PRESSURE, and BTN_TOUCH.

## Risks
The code uses legacy machine-specific Collie conditionals, limiting portability and testability. The thread intentionally leaves filtering to user space, so noisy panels can emit raw jitter. `BUG_ON(ts->rtask)` in open is harsh if input open/close state becomes inconsistent. IRQ disable/enable is coordinated manually with `irq_disabled`; missed transitions can leave the touch IRQ disabled or reenabled too early. Synchronized ADC mode can hang user-visible touch behavior if ADCSYNC pulses stop, as noted in the file comment. The pressure ABS range is initialized with max 0, which may constrain consumers depending on input stack interpretation.

## Test Signals
Tests should register and open the input device, confirm IRQ request flags on Collie and non-Collie systems, and verify the thread reports press samples followed by release events. ADC sync and non-sync modes should be exercised. Hardware tests should compare measured X/Y resistance and raw coordinate ranges against known panel positions. Suspend/freezer tests should confirm no stale sample is emitted immediately after thaw. Close/unload tests should verify thread stop, IRQ free, and touchscreen register clear.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ucb1x00-ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/upboard-fpga.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/upboard-fpga.c

## Purpose
`upboard-fpga.c` is the MFD core for the FPGA found on UP Board platforms. The FPGA exposes platform ID, firmware ID, pinmux/GPIO-enable, GPIO-direction, LED, and pin-control functions through a simple GPIO-bit-banged register protocol. The driver provides a regmap over that protocol and registers pinctrl and LED children.

## Important APIs, Types, And Functions
Low-level regmap bus callbacks are `upboard_fpga_read()` and `upboard_fpga_write()`, which clock address and data bits over `clear`, `strobe`, `datain`, and `dataout` GPIOs. Access tables and regmap configs are split between original UP and UP2-style FPGA layouts: `upboard_up_regmap_config` and `upboard_up2_regmap_config`. Platform data objects are `upboard_up_fpga_data` and `upboard_up2_fpga_data`. Setup helpers are `upboard_fpga_gpio_init()`, `upboard_fpga_get_firmware_version()`, and `upboard_fpga_version_show()`. `upboard_fpga_probe()` performs platform initialization and child registration.

## Control Flow
Probe allocates `struct upboard_fpga`, reads ACPI match data, initializes a custom regmap with the matched config, obtains all common GPIOs, enables the FPGA, reads platform/manufacturer ID and firmware ID, rejects unsupported manufacturers or major firmware revisions, and registers `upboard-pinctrl` and `upboard-leds` MFD children. Each regmap read clears the transaction, shifts out a 7-bit address plus read flag, then clocks in 16 data bits from `dataout`. Each write clears the transaction, shifts out address bits, then shifts out 16 data bits on `datain`. A read-only sysfs attribute reports parsed firmware major/minor/patch/build fields.

## State, Persistence, And Dependencies
Runtime state includes GPIO descriptors, matched FPGA type/config, regmap pointer, and cached firmware version. No regcache is used (`REGCACHE_NONE`), so every child access performs live GPIO transactions. Persistent hardware effects are writes to function-enable, GPIO-enable, and GPIO-direction registers. Dependencies include ACPI device IDs, gpiod consumer APIs, regmap custom callbacks, bitfield helpers, MFD core, sysfs attribute groups, and UP Board register definitions.

## Integration Points
ACPI IDs `"AANT0F01"` and `"AANT0F04"` select UP2 and original UP register access policies. Child drivers `upboard-pinctrl` and `upboard-leds` consume the shared regmap and FPGA metadata from `struct upboard_fpga`. Regmap access tables prevent children from reading or writing registers outside the model-specific readable/writable ranges. The sysfs attribute is attached through the platform driver's `dev_groups`.

## Risks
GPIO bit-banging uses `gpiod_set_value()` rather than cansleep variants, so GPIO providers must be safe in this context. There is no explicit transaction lock in the read/write callbacks; regmap serialization normally protects callers, but any bypass would corrupt bit streams. Probe always registers `upboard_up_mfd_cells` even for UP2 data, which is fine only if children adapt by FPGA type/regmap ranges. Unsupported firmware major versions reject the whole device; minor/patch compatibility is assumed. The manufacturer check masks only the low byte of platform ID. Timing is implicit in GPIO operations and may be sensitive to GPIO controller behavior.

## Test Signals
Bring-up tests should cover both ACPI IDs, verify GPIO acquisition and enable sequencing, read platform and firmware IDs, and confirm sysfs version formatting. Regmap tests should read all allowed ID/control ranges and reject out-of-range accesses for UP and UP2 configs. Child tests should exercise pinctrl and LED operations through the bit-banged regmap. Negative tests should simulate wrong manufacturer ID, unsupported major firmware, GPIO acquisition failures, and malformed dataout reads.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/upboard-fpga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/vexpress-sysreg.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/vexpress-sysreg.c

## Purpose
`vexpress-sysreg.c` exposes ARM Versatile Express system-register subfunctions as MFD children. The sysreg block is a mixed MMIO register area containing LEDs, MMC control pseudo-GPIOs, flash control pseudo-GPIOs, and system configuration registers.

## Important APIs, Types, And Functions
Static software nodes define labels and GPIO counts for `sys_led`, `sys_mci`, and `sys_flash`. `vexpress_sysreg_cells[]` creates three `basic-mmio-gpio` cells and one `vexpress-syscfg` cell with fixed offsets. The only active function is `vexpress_sysreg_probe()`, plus OF match table and platform driver registration.

## Control Flow
Probe obtains the first memory resource, maps the full sysreg range with `devm_ioremap()`, creates a duplicate generic GPIO chip for `SYS_MCI` compatibility with older device trees, sets its data register to `base + SYS_MCI`, forces `ngpio = 2`, and registers it with devm gpiolib. It then calls `devm_mfd_add_devices()` with the original parent memory resource and child cells. Each MFD cell receives relative memory resources for its portion of the sysreg block.

## State, Persistence, And Dependencies
The driver keeps no private runtime state after devm setup. Persistent state is in the sysreg hardware registers manipulated by child drivers. Dependencies include platform MMIO resources, OF matching on `"arm,vexpress-sysreg"`, generic MMIO GPIO helpers, software nodes/property entries, and MFD resource offset handling.

## Integration Points
The `basic-mmio-gpio` children expose LED, MCI, and flash bits using software-node properties for labels and line counts. The duplicate `SYS_MCI` gpiochip exists directly under the sysreg device for compatibility with older trees that referenced the sysreg node itself for MMC control lines. `vexpress-syscfg` receives the `SYS_MISC` through `SYS_CFGSTAT` register span.

## Risks
The full resource is mapped with `devm_ioremap()` rather than a reservation helper, so conflict detection depends on platform resource ownership. The compatibility MCI gpiochip duplicates the MFD child view of the same register, so concurrent users could race on `SYS_MCI`. Fixed offsets and sizes assume the expected Versatile Express sysreg layout. The driver does not validate resource size against the highest child range. There is no remove callback because devm handles cleanup.

## Test Signals
Probe should be tested with correct and missing memory resources, validating MFD child creation and duplicate MCI gpiochip registration. GPIO tests should toggle LED, MCI, and flash lines and verify MMIO writes hit `SYS_LED`, `SYS_MCI`, and `SYS_FLASH`. Compatibility tests should exercise old MMC bindings using the parent sysreg GPIO provider. Syscfg tests should confirm child access to the `SYS_MISC` register window.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/vexpress-sysreg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/viperboard.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/viperboard.c

## Purpose
`viperboard.c` is the USB MFD core for the Nano River Technologies Viperboard. It identifies the USB device, stores shared USB state, reads firmware version bytes, and registers hotplug child devices for GPIO, I2C, and ADC functions.

## Important APIs, Types, And Functions
The USB match table `vprbrd_table[]` matches vendor/product `0x2058:0x1005`. Child cells are `viperboard-gpio`, `viperboard-i2c`, and `viperboard-adc`. Lifecycle functions are `vprbrd_probe()` and `vprbrd_disconnect()`, registered through `module_usb_driver()`. Shared state is `struct vprbrd` from `linux/mfd/viperboard.h`, including USB device pointer, lock, and control buffer.

## Control Flow
Probe allocates state, initializes its mutex, stores the `usb_device` pointer from the interface, attaches state to the USB interface and embedded platform device, reads major and minor version bytes with USB control messages on endpoint zero, logs the version and bus/address, and calls `mfd_add_hotplug_devices()` for the child cells. On child-add failure it frees state and returns the error. Disconnect removes MFD children, clears USB interface data, frees state, and logs debug output.

## State, Persistence, And Dependencies
The core persists only the in-memory `struct vprbrd` while the USB interface is bound. Hardware state is not modified beyond control-message reads. Child drivers depend on the shared USB device pointer, buffer, and lock for their own transactions. Dependencies include USB core control transfers, MFD hotplug device support, child drivers for GPIO/I2C/ADC, and the Viperboard protocol constants.

## Integration Points
The MFD children are created as hotplug devices under the USB interface device so they follow USB connect/disconnect lifetime. The core does not implement GPIO/I2C/ADC protocols itself; it provides discovery and shared transport state for child drivers. Module aliasing comes from `MODULE_DEVICE_TABLE(usb, vprbrd_table)`.

## Risks
Version control-message failures are tolerated silently, leaving version fields partially zero while probe continues. The USB device pointer is not separately reference-counted with `usb_get_dev()`, so correctness relies on interface binding lifetime. Error cleanup frees state but does not clear interface data on the probe failure path. `dev_set_drvdata(&vb->pdev.dev, vb)` depends on the layout and initialization expectations of `struct vprbrd`. The core advertises no SPI child despite the board comment noting unsupported SPI.

## Test Signals
Tests should plug the matching USB device, confirm version log formatting, and verify hotplug creation of GPIO/I2C/ADC children. Disconnect should remove children before freeing shared state. Fault tests should inject failed major/minor version reads and failed MFD child registration. Concurrency tests should run child USB operations while disconnecting to verify child cleanup and shared-lock behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/viperboard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/vx855.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/vx855.c

## Purpose
`vx855.c` is a PCI MFD shim for VIA VX855 chipset integrated peripherals. Its practical role is to discover the chipset PMIO base, carve out GPIO input/output I/O-port resources, and register a `vx855_gpio` child while intentionally returning `-ENODEV` so other legacy drivers can still bind.

## Important APIs, Types, And Functions
The PCI config offset `VX855_CFG_PMIO_OFFSET` points to the PMIO base. `vx855_gpio_resources[]` holds two I/O resources for GPI and GPO registers. `vx855_cells[]` defines the `vx855_gpio` MFD child with `ignore_resource_conflicts = true`. Lifecycle functions are `vx855_probe()` and `vx855_remove()`, registered in `vx855_pci_driver`.

## Control Flow
Probe enables the PCI device, reads the 16-bit PMIO base from config offset `0x88`, rejects zero as unassigned, masks off the low seven bits because hardware returns bit 0 set, computes four-byte GPI and GPO I/O ranges at offsets `0x48` and `0x4c`, and calls `mfd_add_devices()` with the single GPIO cell. Regardless of `mfd_add_devices()` result, the function returns `-ENODEV` by design to allow other drivers such as legacy `i2c-viapro` to bind. On early error it disables the PCI device. Remove removes MFD children and disables the PCI device.

## State, Persistence, And Dependencies
The file stores computed resources in static arrays, so it assumes a single active VX855 instance. Persistent hardware state is not changed except PCI enable state and whatever the child GPIO driver later does with PMIO. Dependencies include PCI IDs for VIA VX855, PCI config access, I/O-port resources, MFD core, and platform child driver `vx855_gpio`.

## Integration Points
The child GPIO driver consumes the two I/O resources and must tolerate resource conflicts, as indicated by the cell flag. The parent PCI driver intentionally fails probe after creating children, which is an unusual integration pattern designed to coexist with older non-platform drivers. `MODULE_DEVICE_TABLE(pci, vx855_pci_tbl)` provides module autoloading.

## Risks
Returning `-ENODEV` after adding MFD devices means normal driver binding state does not represent the created children, and `vx855_remove()` may not be called for that probe path. This can leak children or leave PCI enable state active depending on PCI core behavior. Static resource storage is unsafe for multiple devices. `mfd_add_devices()` return is ignored because `-ENODEV` is always returned afterward. Resource conflicts are explicitly ignored, so overlapping I/O users can race. The code enables the PCI device but does not disable it after the intentional `-ENODEV` return.

## Test Signals
Validation should inspect PCI probe behavior on VX855 hardware, confirming that `vx855_gpio` appears even though the parent probe returns `-ENODEV`, and that legacy drivers can still bind. Tests should verify PMIO base masking and computed GPI/GPO ranges. Error tests should cover zero PMIO base and failed `pci_enable_device()`. Resource-conflict tests should ensure the GPIO child can operate alongside legacy users without corrupting non-GPIO PMIO registers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/vx855.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wcd934x.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/wcd934x.c

## Purpose
`wcd934x.c` is the SLIMbus MFD core for Qualcomm WCD9340/WCD934x audio codec devices. It manages supplies, reset, external clock, SLIMbus regmap creation, interrupt mapping, basic bring-up sequencing, and MFD child creation for codec, GPIO, and SoundWire functionality.

## Important APIs, Types, And Functions
Child cells are `wcd934x-codec`, `wcd934x-gpio`, and `wcd934x-soundwire`. IRQ metadata is built with `WCD934X_REGMAP_IRQ_REG()` and `wcd934x_irqs[]`, then exposed through `wcd934x_regmap_irq_chip`. Register access is controlled by `wcd934x_is_volatile_register()`, `wcd934x_ranges[]`, and `wcd934x_regmap_config`. Lifecycle functions are `wcd934x_slim_probe()`, `wcd934x_slim_status()`, `wcd934x_slim_status_up()`, `wcd934x_slim_remove()`, and `wcd934x_bring_up()`.

## Control Flow
SLIMbus probe allocates `struct wcd934x_ddata`, gets the first OF IRQ, obtains `extclk`, gets and enables five regulators, waits for buck/SIDO outputs, obtains optional reset GPIO low, waits, drives reset high, stores `ddata`, and returns. Actual register access waits for SLIMbus device status `SLIM_DEVICE_STATUS_UP`: `wcd934x_slim_status_up()` initializes a SLIMbus regmap with windowed range config, reads/logs chip ID bytes, performs a fixed RPM/reset/power sequence with a 1 ms VOUT settle delay, adds a regmap IRQ chip on the parent IRQ, and registers children. Status `DOWN` removes MFD children.

## State, Persistence, And Dependencies
State includes `ddata->regmap`, IRQ number/data, regulator handles, `extclk`, and device pointer. Hardware state includes enabled supplies, reset GPIO, RPM/reset/power registers written by bring-up, regmap IRQ masks/clears, and volatile status/MBHC/SoundWire bridge registers. Dependencies include SLIMbus device status callbacks, regmap SLIMbus support, regmap range windows through selector registers, regmap IRQ type configuration, regulators, optional reset GPIO, OF IRQ parsing, clocks, and WCD934x register definitions.

## Integration Points
The codec, GPIO, and SoundWire child devices are created only after the SLIMbus device reports `UP`, so children can assume regmap access works. The regmap IRQ chip maps SLIMbus, headphone PA over-current, MBHC insertion/button, and SoundWire interrupts across four status/mask/clear registers and supports both-edge type configuration through a shared config base. The range config maps logical 16-bit registers through WCD934x window selector registers.

## Risks
In the IRQ error path of probe, `dev_err_probe(ddata->dev, ...)` is called before `ddata->dev` is assigned, which is a likely NULL-device bug; it should use local `dev`. `regulator_bulk_get()` is not devm-managed and the successful probe path relies on remove for cleanup. If `wcd934x_slim_status_up()` fails after `regmap_init_slimbus()`, the regmap is not explicitly freed because it is not devm-initialized. `wcd934x_bring_up()` ignores return values from its fixed `regmap_write()` sequence after chip ID reads. Status `DOWN` removes children but does not delete the devm regmap IRQ chip. Probe obtains `extclk` but does not prepare/enable it in this file.

## Test Signals
Tests should cover probe with missing IRQ, clock deferral/failure, regulator get/enable failure, reset GPIO failure, and successful reset timing. SLIMbus status tests should transition UP and DOWN, verifying regmap creation, chip ID log, bring-up writes, IRQ chip registration, and child creation/removal. IRQ tests should trigger MBHC, SoundWire, and PA fault bits with rising/falling type configuration. Register tests should exercise windowed range access and volatile MBHC/SoundWire bridge/status registers. Failure-injection should target bring-up writes and child-add errors to detect leaked regmap/IRQ state.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wcd934x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm5102-tables.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/wm5102-tables.c

## Purpose
`wm5102-tables.c` supplies WM5102-specific static data for the Arizona MFD framework. It provides silicon revision patches, always-on and main interrupt chip descriptions, register defaults for regcache, readable/volatile register predicates, and exported SPI/I2C regmap configurations.

## Important APIs, Types, And Functions
The exported function is `wm5102_patch(struct arizona *arizona)`, which selects `wm5102_reva_patch[]` for revision 0 and `wm5102_revb_patch[]` otherwise, then writes it with `regmap_multi_reg_write_bypassed()`. Exported interrupt chips are `wm5102_aod` and `wm5102_irq`. Exported regmaps are `wm5102_spi_regmap` and `wm5102_i2c_regmap`. Large static tables include `wm5102_aod_irqs[]`, `wm5102_irqs[]`, and `wm5102_reg_default[]`. Access predicates are `wm5102_readable_register()` and `wm5102_volatile_register()`.

## Control Flow
Bus glue creates either the SPI or I2C regmap using 32-bit register addresses and 16-bit values in big-endian format; SPI adds 16 pad bits. The Arizona core calls `wm5102_patch()` after the regmap exists, applying a bypassed multi-register patch selected by `arizona->rev`. Runtime register operations then flow through the readable and volatile callbacks. The readable predicate allowlists reset/revision, control interfaces, write sequencer, wake/sequence controls, clocking, FLL1/FLL2, power supplies, mic/headphone detection, inputs/outputs, AIF1-AIF3, SLIMbus, mixers, DSP1, ASRC/ISRC, GPIO, IRQ, EQ/DRC/HPLPF, and ADSP memory windows. The volatile predicate narrows this to reset/revision, sequencer/status, sample-rate and haptics status, DAC compensation, FX status, IRQ/raw/AOD status, DSP status/buffers/scratch/config, headphone/mic detect live values, and ADSP memory windows.

## State, Persistence, And Dependencies
The file owns no mutable runtime state. Persistent effects are patch writes and regcache defaults. `wm5102_reg_default[]` seeds maple cache values for tone/PWM/wake sequencing, haptics, clocks, FLLs, mic charge pump/LDO/mic bias, accessory/headphone/mic detection, input and output paths, PDM speaker, AIFs, SLIMbus, extensive mixer routes, EQ/DRC/HPLPF/ASRC/ISRC blocks, GPIO1-GPIO5, interrupt masks, AOD masks, jack debounce, and DSP1 control. Dependencies include Arizona core structures, Arizona register definitions, Linux regmap, regmap IRQ, module exports, and `REGCACHE_MAPLE`.

## Integration Points
The Arizona MFD core consumes the regmap configs and patch function during WM5102 probe. Regmap IRQ infrastructure consumes `wm5102_irq` for the five main interrupt status registers and `wm5102_aod` for one always-on interrupt register with wake control. Codec, GPIO, haptics, jack-detect, clock, DSP, audio-routing, SLIMbus, and power-management components depend on this file for safe register visibility and cache coherency. ADSP memory ranges `0x100000-0x105fff`, `0x180000-0x1807ff`, `0x190000-0x1947ff`, and `0x1a8000-0x1a97ff` are explicitly readable and volatile.

## Risks
The revision selector treats every nonzero revision as Rev B-compatible; future incompatible revisions would need a new patch path. The readable allowlist is very large and hand-maintained, so omissions can block valid regmap access while excess entries can expose undefined registers. ADSP memory is volatile and uncached for correctness, which increases bus traffic. Main and AOD IRQ arrays are sparse over `ARIZONA_NUM_IRQ`; consumers must use matching enum indices. Patch writes are bypassed, so they deliberately avoid normal cache behavior and must remain consistent with defaults and later cache sync. Default-table drift can create subtle resume or first-use mismatches.

## Test Signals
Validation should probe WM5102 over SPI and I2C, confirm endian/pad configuration, and verify Rev A versus Rev B patch selection with injected write failures. Regmap tests should sample representative readable/unreadable registers and volatile/cacheable boundaries, including reset, FLLs, AIFs, SLIMbus status, IRQ masks/status, GPIOs, DSP1 scratch/status, and ADSP memory window edges. IRQ tests should trigger main and AOD interrupts, including wake behavior through `ARIZONA_WAKE_CONTROL`. Audio smoke tests should cover playback/capture routes through inputs, outputs, AIF1-AIF3, PDM speaker, mixers, ASRC/ISRC, haptics, jack/mic detection, and DSP firmware memory access. Suspend/resume should verify regcache restores defaults while volatile status is reread.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm5102-tables.c -->
