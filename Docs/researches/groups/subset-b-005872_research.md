# Research: subset-b-005872

This grouped report covers MFD interface headers under `sources/distributed-fs/ceph-client/include/linux/mfd`. Each source file section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/88pm860x.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/88pm860x.h

## Purpose
This header is the shared interface for Marvell 88PM8606/88PM8607 PMIC MFD support. It names chip and child-device IDs, maps PM8606 and PM8607 registers, defines interrupt numbers and status bits, describes the core `struct pm860x_chip`, and supplies platform-data contracts for child backlight, LED, RTC, touch, power, charger, and regulator drivers.

## Important APIs, Types, And Functions
- Chip and child IDs: `CHIP_PM8606`, `CHIP_PM8607`, `PM8606_ID_*`, and `PM8607_ID_*` enumerate MFD cells and regulator IDs.
- Register maps: `PM8606_*` covers boost, PWM, WLED, RGB, vibrator, charger sense, status, and protection registers; `PM8607_*` covers interrupt/status, LDO/buck, sleep, GPADC, battery monitor, RTC, charger, and miscellaneous registers.
- Bit helpers: `PM8606_WLED_CURRENT(x)`, `PM8606_LED_CURRENT(x)`, `PM8607_MEAS_EN1_*`, GPADC masks, interrupt clear/mask mode bits, and oscillator reference-client masks are consumed by child drivers.
- `struct pm860x_chip` stores core device, I2C clients for main and companion chips, regmaps, IRQ locks, oscillator vote state, chip version, wakeup state, and IRQ metadata.
- Exported helpers include `pm8606_osc_enable()`, `pm8606_osc_disable()`, register read/write/bulk helpers, bit update, and paged register helpers.

## Control Flow
The header itself is declarative. At runtime the MFD core probes the I2C chip, allocates and fills `struct pm860x_chip`, creates child devices using IDs and platform data, and child drivers then call the exported register and oscillator helpers. Backlight, RGB LED, vibrator, touch, power, RTC, charger, and regulator code use the register offsets and platform-data structures to program chip blocks without duplicating the core transport logic.

## State And Persistence
Runtime state is held in `struct pm860x_chip`, especially `osc_vote`, `osc_status`, `irq_lock`, `osc_lock`, `wakeup_flag`, chip ID/version fields, and paired regmaps. Persistent effects are hardware-register effects: regulator enable/voltage, sleep-mode programming, GPADC setup, RTC counters/alarm, charger configuration, interrupt masks, and oscillator/reference-group state survive only as chip state until reset or reprogramming.

## Dependencies And Integration Points
The header depends on Linux interrupt, mutex, I2C, regmap, and regulator platform-data types through users. It integrates with the MFD core driver and child drivers for regulators, backlight, LEDs, touch, RTC, charger, and power-supply. `struct charger_desc` is referenced as platform data, so charger users must provide the definition from the relevant power-supply side before dereferencing it.

## Risks And Edge Cases
- The register map spans two companion chips and paged accesses; using the wrong client or page helper can program the wrong hardware block.
- `osc_vote` is a shared bitmask for multiple consumers and must be protected by `osc_lock` to avoid shutting off a clock still needed by another client.
- Several regulator IDs and register IDs are dense ABI-like values used by child devices; changing enum order can break MFD cell matching.
- Bit macros that shift caller input assume sanitized values; callers should clamp brightness/current/prebias settings before composing register values.

## Test Signals
Useful signals include successful MFD probe with both main and companion clients, child-device enumeration, regulator enable/voltage changes, backlight and RGB current programming, RTC counter/alarm operation, GPADC/touch conversions, charger interrupts, oscillator vote transitions under multiple clients, suspend/resume wake behavior, and clean remove with no pending IRQ or child-driver register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/88pm860x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/88pm886.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/88pm886.h

## Purpose
This header defines the register, interrupt, GPADC, regulator, RTC, and core-device contract for the Marvell 88PM886 PMIC. It is used by the MFD core and children such as regulator, RTC, input/onkey, and GPADC consumers.

## Important APIs, Types, And Functions
- Identification and paging: `PM886_A1_CHIP_ID`, `PM886_REG_ID`, `PM886_PAGE_OFFSET_REGULATORS`, and `PM886_PAGE_OFFSET_GPADC`.
- Interrupt and shutdown registers: `PM886_REG_INT_STATUS1`, `PM886_REG_INT_ENA_1`, `PM886_INT_ENA1_ONKEY`, `PM886_REG_MISC_CONFIG1`, `PM886_SW_PDOWN`, and interrupt clear/mask mode bits in `PM886_REG_MISC_CONFIG2`.
- RTC registers: `PM886_REG_RTC_CNT1` through `PM886_REG_RTC_CNT4` and spare registers `PM886_REG_RTC_SPARE1` through `PM886_REG_RTC_SPARE6`.
- Regulator controls: buck/LDO enable and voltage registers plus `PM886_LDO_VSEL_MASK` and `PM886_BUCK_VSEL_MASK`.
- GPADC controls: channel enable bits, channel data registers, max register calculation, and bias conversion helper `PM886_GPADC_INDEX_TO_BIAS_uA(i)`.
- `struct pm886_chip` stores the I2C client, detected chip ID, and primary regmap.

## Control Flow
The MFD driver reads `PM886_REG_ID`, validates the A1-compatible chip ID, configures interrupt clear behavior, initializes regmap IRQ handling, and registers child cells. Child drivers use the named page offsets and register constants to address regulator and GPADC pages while sharing the core `regmap`.

## State And Persistence
In-memory state is minimal: `struct pm886_chip` binds the device identity to the regmap. Hardware state includes interrupt masks/status, onkey status, software-powerdown request, RTC counters/spares, regulator enables and voltage selectors, GPADC channel enables, and GPADC measurements.

## Dependencies And Integration Points
The header includes Linux I2C and regmap types. It integrates with `drivers/mfd/88pm886.c`, regmap IRQ infrastructure, regulator child code, RTC code, input/onkey resources, system-off handling through `PM886_SW_PDOWN`, and GPADC users.

## Risks And Edge Cases
- Regulator and GPADC page offsets must match the MFD regmap layout; wrong page selection can silently access unrelated registers.
- `PM886_GPADC_CONFIG(n)` returns `n`, so callers must pass a valid config-register index rather than an arbitrary channel ID.
- The interrupt configuration bits choose write-clear versus read-clear behavior; mismatched ack handling can lose or repeat interrupts.
- Software powerdown is a hardware-side persistent action and must only be requested through controlled system-off paths.

## Test Signals
Build the MFD, regulator, RTC, onkey, and GPADC users together; verify chip-ID rejection/acceptance, IRQ ack/unmask behavior, onkey interrupt delivery, regulator voltage and enable operations, RTC counter/spare access, GPADC channel reads and bias settings, and system-off write to `PM886_SW_PDOWN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/88pm886.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/aat2870.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/aat2870.h

## Purpose
This header is the public MFD contract for the AnalogicTech AAT2870 backlight and regulator chip. It defines register offsets, child IDs, backlight channel/current settings, the core cached-register device structure, subdevice descriptors, and platform-data structures.

## Important APIs, Types, And Functions
- Register offsets cover backlight channels and brightness, flash controls, ambient-light-sensor tables, subtype controls, LDO voltage registers, and `AAT2870_LDO_EN`.
- `enum aat2870_id` identifies the backlight child and four LDO regulator children.
- Backlight macros define channel bits `AAT2870_BL_CH1` through `AAT2870_BL_CH8`, `AAT2870_BL_CH_ALL`, and current steps from `AAT2870_CURRENT_0_45` to `AAT2870_CURRENT_27_9`.
- `struct aat2870_data` contains the parent device, I2C client, I/O mutex, register cache, enable GPIO, enable state, board init/uninit hooks, and function pointers for read/write/update.
- `struct aat2870_platform_data`, `struct aat2870_subdev_info`, and `struct aat2870_bl_platform_data` describe board-provided child devices and backlight defaults.

## Control Flow
The MFD core creates `struct aat2870_data`, assigns the register cache and I/O functions, optionally enables the external GPIO, runs board initialization, and registers requested MFD cells. Child drivers retrieve the parent data and call `read`, `write`, or `update` under the shared I/O lock. Suspend disables the chip and resume restores writable cached registers through the core implementation.

## State And Persistence
The software cache in `reg_cache` mirrors readable/writeable state and enables resume restoration. `is_enable` tracks whether the enable GPIO has powered the chip. Hardware state includes backlight channel enables, brightness/current values, ALS thresholds, sub controls, and LDO voltage/enables; it is volatile across power loss and restored from cache where possible.

## Dependencies And Integration Points
The header depends on debugfs and I2C declarations and is consumed by `drivers/mfd/aat2870-core.c`, `drivers/regulator/aat2870-regulator.c`, and backlight child code. Platform data connects board-specific GPIO and child-device configuration to MFD registration.

## Risks And Edge Cases
- The register cache marks readable/writeable capabilities; child drivers must not assume all offsets are readable.
- Resume restoration depends on cached values being updated on every successful write or update.
- `en_pin < 0` disables GPIO handling, so board data must be explicit when hardware requires an enable line.
- Current and brightness enums are raw selector values; invalid caller values can exceed hardware range without local type protection.

## Test Signals
Probe with board platform data, confirm requested subdevices appear, exercise backlight channel/current/brightness settings, enable and program all four LDOs, inspect debugfs register dump/write behavior, suspend/resume with cache restoration, and verify failure paths disable the chip and run uninit hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/aat2870.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/abx500.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/abx500.h

## Purpose
This header defines the generic ABX500 access abstraction for ST-Ericsson analog baseband chips. It provides a device-scoped register operation table plus exported wrappers used by ABX500 child drivers to read, write, page-read, page-write, mask-update registers, query chip ID, inspect startup events, and test startup IRQ enablement.

## Important APIs, Types, And Functions
- `struct abx500_init_settings` describes bank/register/value triples for setup-time initialization.
- Exported wrapper APIs include `abx500_set_register_interruptible()`, `abx500_get_register_interruptible()`, page read/write variants, `abx500_mask_and_set_register_interruptible()`, `abx500_get_chip_id()`, `abx500_event_registers_startup_state_get()`, and `abx500_startup_irq_enabled()`.
- `struct abx500_ops` is the backend vtable for chip-specific get/set/page/mask operations, startup state, startup IRQ checks, chip ID, and optional bank dump.
- `abx500_register_ops()` and `abx500_remove_ops()` attach or detach an ops table to a core device.

## Control Flow
Chip-specific MFD code registers an `abx500_ops` table for the core device. Child drivers call the generic wrappers with their device pointer; the wrapper resolves the parent/core operations and delegates to the chip-specific transport. This avoids binding child drivers directly to SPI, I2C, PRCMU, or variant-specific access methods.

## State And Persistence
The header defines no concrete storage beyond initialization records and ops pointers. State lives in the registered backend and target hardware. Register writes and mask updates change ABX500 chip state such as regulators, interrupts, clocks, GPADC, charger, audio, RTC, and miscellaneous blocks.

## Dependencies And Integration Points
It includes regulator machine data because ABX500 platform setup often configures regulators. The APIs are integrated with AB8500-family MFD code, ABX500 child drivers, startup-event handling, and debug register dumps.

## Risks And Edge Cases
- Wrappers are only valid after ops registration; child probe ordering must ensure the core has registered operations.
- The misspelled comment name for `abx500_mask_and_set_register_inerruptible()` does not match the function but may mislead text searches.
- Bank/register values are raw hardware ABI; callers need variant checks for registers that differ across AB8500, AB8505, AB9540, and AB8540.
- Interruptible operations can fail due to sleep interruption or bus errors, so child drivers must propagate errors.

## Test Signals
Check core registration before children probe, exercise single and page register reads/writes, verify mask-update read-modify-write semantics, test startup event and IRQ queries, run child-driver probes against all supported variants, and validate error handling when backend ops are absent or return bus failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/abx500.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/abx500/ab8500-codec.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/abx500/ab8500-codec.h

## Purpose
This header defines platform data for the audio portions of AB8500-family chips, especially analog microphone topology, mic-bias routing, and ear common-mode voltage selection.

## Important APIs, Types, And Functions
- `enum amic_type` distinguishes single-ended and differential analog microphone wiring.
- `enum amic_micbias` selects `VAMIC1`, `VAMIC2`, or unknown mic-bias routing.
- `enum ear_cm_voltage` encodes supported ear common-mode voltages from 0.95 V through 1.58 V plus unknown.
- `struct amic_settings` describes mic1/mic2 topology and mic-bias assignment for mic1a, mic1b, and mic2.
- `struct ab8500_codec_platform_data` aggregates analog microphone settings and ear common-mode voltage.

## Control Flow
The header contributes data consumed by the AB8500 codec/audio driver during probe or machine setup. Board or platform code fills `ab8500_codec_platform_data`; the codec driver translates those enum values into AB8500 audio register programming.

## State And Persistence
This file defines static configuration rather than runtime state. Once consumed, the settings become hardware audio-path state in AB8500 registers. Persistence is limited to platform data and live hardware register programming.

## Dependencies And Integration Points
It is referenced by `struct ab8500_platform_data` in `ab8500.h` and integrates with ASoC codec drivers for AB8500-family audio. It also indirectly depends on microphone bias supplies and jack/mic detection paths configured elsewhere.

## Risks And Edge Cases
- The `UNKNOWN` enum values must be handled defensively by codec users to avoid programming invalid voltage or bias selections.
- Board data must match actual analog wiring; wrong single-ended/differential or mic-bias assignments can break capture or damage signal quality.
- The header has no range checking; validation belongs in the consuming codec driver.

## Test Signals
Validate codec probe with populated platform data, confirm register programming for each microphone topology and bias route, measure capture on mic1 and mic2, verify ear output common-mode selection, and test behavior when unknown/default values are supplied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/abx500/ab8500-codec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/abx500/ab8500-sysctrl.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/abx500/ab8500-sysctrl.h

## Purpose
This header exposes AB8500 system-control register accessors and a register/bit map for power-on/reset status, software shutdown/reset, watchdog, battery thresholds, system clocks, RF clock requests, ultra-low-power clock control, dither clocks, SWAT, and related AB9540 extensions.

## Important APIs, Types, And Functions
- Conditional APIs: `ab8500_sysctrl_read()` and `ab8500_sysctrl_write()` are available with `CONFIG_AB8500_CORE`; otherwise inline stubs return success without touching hardware.
- Convenience helpers: `ab8500_sysctrl_set()` and `ab8500_sysctrl_clear()` compose masked writes for bit set/clear operations.
- Register constants span status (`AB8500_TURNONSTATUS`, `AB8500_RESETSTATUS`), watchdog, low-battery, clock timers, SMPS clock selection, ULP clock control, system clock request validity, RF clock buffers, dither control, SWAT, HIQ clock control, VSIM clock control, and AB9540 SYSCLK12 registers.
- Bit constants provide masks/shifts for every field, including shutdown/reset bits, watchdog enable/kick, low-battery thresholds, clock source selectors, request-valid bits, and dither delay fields.

## Control Flow
Sysctrl users read status registers to determine boot/reset reasons and use masked writes to update control fields. `ab8500_sysctrl_set()` writes `bits` with the same mask and value, while `ab8500_sysctrl_clear()` writes zero under the same mask. When `CONFIG_AB8500_CORE` is disabled, callers compile but sysctrl requests are no-ops.

## State And Persistence
State is entirely in AB8500 system-control hardware registers. Some fields represent latched status, while others control persistent live behavior such as shutdown/reset, watchdog, low-battery detection, clock-buffer requests, clock source selection, and dither enables. The inline stubs create no software state.

## Dependencies And Integration Points
The header depends on `linux/bitops.h` and AB8500 core support. It integrates with platform power management, watchdog, reset/shutdown paths, clock management, regulator/power logic, and drivers that need to coordinate system clock requests.

## Risks And Edge Cases
- The no-op stubs return success when the core is disabled, which can hide missing hardware support if callers do not guard by Kconfig or device presence.
- Register constants use combined bank/register-style `u16` addresses; users must pass them through sysctrl accessors rather than generic single-bank helpers unless they know the encoding.
- Shutdown, reset, and watchdog bits are high-impact controls and should only be written from controlled paths.
- Bitfield masks and shifts require callers to pre-shift values correctly before masked writes.

## Test Signals
Test boot reason and reset-status reads, sysctrl set/clear operations, software reset/shutdown paths, watchdog enable/kick/timer behavior, low-battery threshold programming, clock request/valid fields, AB9540-specific SYSCLK12 programming, and compile/runtime behavior with `CONFIG_AB8500_CORE` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/abx500/ab8500-sysctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/abx500/ab8500.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/abx500/ab8500.h

## Purpose
This is the central AB8500-family MFD core header. It defines AB8500/AB8505/AB9540/AB8540 variant IDs and cut revisions, bank numbers, logical IRQ numbers, maximum IRQ counts, turn-on status bits, the core `struct ab8500`, platform data, variant helper predicates, suspend hook, and debug/turn-on-status helper declarations.

## Important APIs, Types, And Functions
- Variant IDs: `enum ab8500_version` and cut constants such as `AB8500_CUT1P0`, `AB8500_CUT2P0`, and `AB8500_CUT3P3`.
- Bank constants map major hardware blocks: system control, regulators, USB, TVOUT, GPADC, charger, gas gauge, audio, interrupt, RTC, misc, debug, test, and OTP areas.
- IRQ constants define logical interrupt numbers across base AB8500 and variant-specific AB9540, AB8505, and AB8540 sources. `AB8500_MAX_NR_IRQS`, `AB8500_NUM_IRQ_REGS`, `AB9540_NUM_IRQ_REGS`, and `AB8540_NUM_IRQ_REGS` size IRQ-domain handling.
- `struct ab8500` contains parent device, access locks, atomic transfer marker, IRQ line/domain, version/chip ID, backend read/write/masked-write callbacks, SPI buffers, IRQ mask caches, IRQ register offsets, and latch hierarchy count.
- `struct ab8500_platform_data` carries board init and pointers to codec/sysctrl platform data.
- Inline helpers such as `is_ab8500()`, `is_ab8505()`, `is_ab9540()`, `is_ab8540()`, and cut-specific predicates centralize variant gating.

## Control Flow
The AB8500 core probes a transport-specific device, identifies the variant and cut, initializes `struct ab8500`, configures IRQ-domain/mask arrays according to the variant, registers children, and exposes read/write callbacks. Child drivers use variant predicates before touching registers or IRQs that are not present on all chips. Suspend flows call `ab8500_suspend()`, while board code may use `platform_data->init()` after detection.

## State And Persistence
Runtime state includes locks, IRQ-domain data, transfer-in-progress flag, mask and oldmask caches, chip identity, and backend callbacks. Hardware state is distributed across AB8500 banks and includes regulator, clock, charger, GPADC, audio, RTC, interrupt mask/latch/source, USB, and debug/test registers. Turn-on status may be overridden in software using `ab8500_override_turn_on_stat()`.

## Dependencies And Integration Points
The header depends on atomic, mutex, and irqdomain APIs. It integrates with `abx500.h` generic register access, AB8500 transport/core implementations, MFD child registration, genirq, codec and sysctrl platform data, regulator/charger/RTC/GPADC/audio/USB child drivers, and board initialization.

## Risks And Edge Cases
- IRQ numbers are variant-sensitive and include gaps or "not on variant" comments; child drivers must gate requests by detected chip and not just by numeric range.
- `AB8540_NR_IRQS` is 216 while the maximum logical IRQ constant is also 216, so off-by-one assumptions around count versus last ID deserve review in users.
- Cut helper predicates use raw chip ID ordering; adding revisions requires preserving the numeric comparison semantics.
- The read/write callback pointers are core transport ABI. Null or mismatched callbacks break all child register access.
- IRQ mask cache sizes must match the selected variant's register-offset table.

## Test Signals
Validate probe and child registration on each supported variant, confirm chip ID and cut predicates, request representative IRQs from base and variant-specific ranges, test mask/unmask/ack through irqdomain, exercise register read/write/masked-write callbacks, run suspend/resume, check board init and codec/sysctrl data propagation, and inspect behavior for absent variant-only IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/abx500/ab8500.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/ac100.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/ac100.h

## Purpose
This header defines the shared device structure and register map for the X-Powers/Allwinner AC100 codec plus RTC combo IC. It allows the MFD core, codec, clock, and RTC children to share one regmap and consistent register names.

## Important APIs, Types, And Functions
- `struct ac100_dev` binds the parent device to the regmap.
- Audio registers cover chip reset, PLL/sysclk/module clock/reset, I2S1-I2S3 controls, ADC/DAC digital controls, headphone mic detection, analog input/output controls, digital audio processing, sample-rate converters, and DAP enables.
- RTC and clock registers cover 32 kHz analog control, clock outputs, RTC reset/control, time fields, update triggers, alarm interrupt/status/time fields, and `AC100_RTC_GP(x)` general-purpose registers.

## Control Flow
The MFD core creates an AC100 regmap using the named readable/writeable/volatile ranges, stores it in `struct ac100_dev`, and registers children. Codec and RTC child drivers use the constants to access their register blocks through the shared regmap.

## State And Persistence
Software state is only the device/regmap pair. Hardware state includes audio clocking, I2S routes, ADC/DAC gain and processing coefficients, analog path controls, 32 kHz clock output configuration, RTC time and alarm values, alarm interrupt status, and RTC general-purpose registers. RTC time/alarm and GP registers may retain state according to the chip's backup-power behavior.

## Dependencies And Integration Points
The header includes regmap declarations and integrates with `drivers/mfd/ac100.c`, ASoC codec drivers, RTC drivers, and clock-output users. Register ranges in the MFD core directly depend on these constants.

## Risks And Edge Cases
- The register map combines unrelated audio and RTC domains; child drivers must stay within their block and respect volatile/writeable properties.
- `AC100_RTC_GP(x)` performs direct arithmetic without range checking; callers must keep `x` within 0-15.
- Time and alarm updates require using update-trigger registers correctly to avoid partially applied RTC values.
- Audio DAP coefficient registers are numerous and order-sensitive; bulk writes need careful bounds.

## Test Signals
Check MFD regmap initialization, codec probe and audio playback/capture controls, clock/reset programming, RTC read/set and alarm interrupts, volatile register reads for status/time, `AC100_RTC_GP(0..15)` access, suspend/resume retention, and regmap range validation for invalid offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/ac100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/adp5520.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/adp5520.h

## Purpose
This header defines registers, bit fields, child platform data, notifier APIs, and helper accessors for Analog Devices ADP5520/ADP5501 PMIC-style MFDs providing backlight, LED, GPIO, ambient-light, and keypad functions.

## Important APIs, Types, And Functions
- Device IDs: `ID_ADP5520` and `ID_ADP5501`.
- Register constants cover mode/status, interrupt enable, backlight control/timing/current levels, ambient light comparator thresholds, LED control/timing/current, GPIO direction/input/output/interrupt/debounce/pull-up, and keypad press/release/status registers.
- Bit and value helpers include status/interrupt bits, `FADE_VAL(in, out)`, `BL_CTRL_VAL(law, auto)`, `ALS_CMPR_CFG_VAL(filt, l3_en)`, current conversion helpers, LED blink timing constants, GPIO/key matrix masks, and `ADP5520_KEY(row, col)`.
- Platform data structures describe GPIO base/enables/pull-ups, keypad matrix and keymap, LEDs, backlight ambient-light thresholds, and aggregate MFD child configuration.
- Exported functions provide read/write, set/clear bits, and event notifier registration/unregistration.

## Control Flow
The MFD core probes the chip, configures register access and IRQ/event handling, and registers child drivers according to platform data. Child drivers call `adp5520_read()`, `adp5520_write()`, `adp5520_set_bits()`, and `adp5520_clr_bits()` for register operations. Keypad/GPIO/ALS events are distributed through notifier blocks registered for selected event masks.

## State And Persistence
The header defines platform configuration rather than concrete core state. Hardware state includes backlight mode/brightness/fade/ALS thresholds, LED current/blink mode, GPIO direction/output/pull-up/debounce/interrupt levels, keypad status, and interrupt enables. Event subscriptions are runtime notifier state owned by the MFD core.

## Dependencies And Integration Points
It integrates with backlight, LED, GPIO, input-keypad, and ambient-light users. It relies on Linux `struct device`, notifier blocks, LED metadata, and keymap conventions through consumers.

## Risks And Edge Cases
- `ADP5520_BL_LVL` and `ADP5520_BL_LAW` are defined with `x` but no macro parameter, which is suspicious and should not be used as-is.
- The comment spells "Blacklight" while describing backlight current, a documentation typo but a search hazard.
- GPIO pins overlap with LED/keypad functions; platform masks must avoid conflicting ownership.
- Conversion macros do integer scaling and do not clamp over-range current inputs.
- Notifier users must unregister on teardown to avoid callbacks into freed child state.

## Test Signals
Compile all child users, test backlight manual and ALS-auto modes, fade timing, LED current/blink settings, GPIO direction/input/output/interrupts, keypad matrix events and repeat, notifier registration/unregistration, ADP5501 versus ADP5520 capability differences, and invalid platform masks for shared pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/adp5520.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/adp5585.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/adp5585.h

## Purpose
This header defines the MFD register map and core state for Analog Devices ADP5585 and ADP5589 keypad/GPIO/PWM/reset-controller devices. It provides variant-specific register constants, event ranges, pin capabilities, and the shared `struct adp5585_dev` used by child drivers.

## Important APIs, Types, And Functions
- Register constants cover ID, interrupt status, event FIFO, GPI status/interrupt/event/debounce, pull configuration, GPO data/mode, GPIO direction, reset-event configuration, PWM timing/configuration, logic configuration, pin configuration, general configuration, and interrupt enable.
- Bit helpers use `BIT()` and `GENMASK()` for manufacturer/revision IDs, FIFO press/event fields, pull configuration, pin alternate functions, oscillator settings, interrupt configuration, reset settings, and unlock timers.
- Variant definitions include ADP5585 and ADP5589 manufacturer IDs, ADP5589 alternate register offsets, pin counts, event ranges, unlock wildcard, and reset output IDs.
- `enum adp5585_variant` names supported silicon revisions.
- `struct adp5585_regs` abstracts variant-dependent register offsets, and `struct adp5585_dev` stores regmap, variant metadata, event notifier, pin usage bitmap, IRQ, polling/unlock timings, reset/unlock key sequences, and reset configuration.

## Control Flow
The MFD core reads the ID register, selects a variant and `adp5585_regs` map, sets up regmap and IRQ/polling, initializes a blocking notifier for child event consumers, and tracks pin usage. Keypad, GPIO, PWM, and reset children use the shared register map and notifier to consume FIFO and GPI events while respecting pin-function ownership.

## State And Persistence
Software state in `struct adp5585_dev` includes active variant, pin-usage bitmap, notifier chain, event polling time, unlock/reset key sequences, reset configuration, and IRQ number. Hardware state includes event FIFO contents, interrupt status/enables, GPIO configuration, pull/debounce settings, PWM timing, logic blocks, reset/unlock key configuration, oscillator settings, and alternate pin function selection.

## Dependencies And Integration Points
The header depends on Linux bit helpers and notifier APIs and forward-declares regmap. It integrates with MFD core code plus GPIO, input-keypad, PWM, and reset/watchdog-style child drivers. Device-tree or platform data is expected to decide pin usage and optional unlock/reset behavior.

## Risks And Edge Cases
- ADP5585 and ADP5589 share concepts but not all register offsets; child code must use `dev->regs` instead of hard-coded ADP5585 offsets when variants differ.
- Event ranges differ by variant and row-extension mode; event decoding must use the selected range constants.
- `pin_usage` prevents conflicting functions, so leaks or missing reservations can create cross-child pin conflicts.
- Reset/unlock key arrays have fixed small sizes; parsing must validate counts before filling them.
- FIFO overflow (`ADP5585_OVRFLOW_INT`) indicates lost input events and should be surfaced.

## Test Signals
Validate ID/manufacturer detection for ADP5585 and ADP5589 variants, event FIFO decoding for key and GPI events, overflow handling, GPIO direction and pull settings, PWM enable/timing, reset1/reset2 and unlock key sequences, pin-function conflict rejection, interrupt and polling paths, and notifier cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/adp5585.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/altera-a10sr.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/altera-a10sr.h

## Purpose
This header describes the Altera/Intel Arria 10 MAX5 System Resource Chip MFD interface. It defines register addressing helpers, system-controller register constants, valid GPIO ranges for inputs and outputs, and the core `struct altr_a10sr`.

## Important APIs, Types, And Functions
- Address helpers: `WRITE_REG_MASK`, `READ_REG_MASK`, `ALTR_A10SR_REG_OFFSET(X)`, `ALTR_A10SR_REG_BIT(X)`, `ALTR_A10SR_REG_BIT_CHG(X, Y)`, and `ALTR_A10SR_REG_BIT_MASK(X)` model paired even write and odd read registers.
- Register constants cover version read/NOP, LED output, pushbutton/DIP input and IRQ flag clear, power-good registers, FMC/PCIe power enable, HPS reset/warm reset/key, USB/QSPI/file reset, SFP controls, I2C master select, and PMBus.
- Valid ranges distinguish LED/output bits and input pushbutton/DIP bits.
- `struct altr_a10sr` stores the parent device and assigned regmap.

## Control Flow
The MFD core creates a regmap for the MAX5 chip and exposes child devices. GPIO/LED/reset/power child code uses the helper macros to map logical GPIO numbers to paired register offsets and bit positions, handling the chip's even-address write and odd-address read convention.

## State And Persistence
Runtime software state is just the device/regmap pair. Hardware state includes LED outputs, pushbutton/DIP input status, power-good flags, power-enable controls, reset controls, SFP controls, I2C master selection, and PMBus control. Register effects persist in the system-resource chip until overwritten or reset.

## Dependencies And Integration Points
The header includes completion, list, MFD core, regmap, and slab headers for the core implementation context. It integrates with Arria10 board-management child drivers, GPIO/LED/reset consumers, and regmap-backed MFD cells.

## Risks And Edge Cases
- The even-write/odd-read register convention is easy to violate; helpers should be used consistently.
- `ALTR_A10SR_REG_BIT_CHG(X, Y)` shifts `X` by the bit position for `Y`; callers must pass a value already constrained to the intended bit width.
- Valid input/output ranges are not enforced by macros, so child drivers must reject unsupported GPIO numbers.
- Reset and power-enable registers can disrupt the board when written incorrectly.

## Test Signals
Verify regmap probe, version read, LED writes with matching odd-address readback, pushbutton/DIP input reads and IRQ flag clear, power-good reads, FMC/PCIe/SFP/reset control writes, logical GPIO-to-register mapping for boundary pins, and rejection of invalid GPIO ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/altera-a10sr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/altera-sysmgr.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/altera-sysmgr.h

## Purpose
This header exposes a small lookup API for Intel/Altera system manager regmaps referenced from device tree phandles. It lets drivers obtain a shared system-manager regmap without directly owning the MFD implementation.

## Important APIs, Types, And Functions
- `altr_sysmgr_regmap_lookup_by_phandle(struct device_node *np, const char *property)` returns a system-manager regmap for a named phandle property when `CONFIG_MFD_ALTERA_SYSMGR` is enabled.
- The disabled-Kconfig inline stub returns `ERR_PTR(-ENOTSUPP)`.
- The header includes error helpers and Stratix10 SMC firmware definitions needed by the implementation ecosystem.

## Control Flow
Consumers call the lookup helper during probe, passing their device node and the property that references the system manager. With the MFD enabled, the implementation resolves the phandle and returns the regmap. Without it, callers receive an encoded unsupported error and should defer or disable dependent features.

## State And Persistence
The header defines no state. Returned regmaps access shared system-manager hardware state. The fallback path creates no persistent state and signals unsupported configuration through an error pointer.

## Dependencies And Integration Points
It depends on device-tree nodes, regmap, Linux error-pointer conventions, and Intel Stratix10 firmware/SMC context. It integrates with SoC drivers needing system-manager registers for pin, clock, reset, FPGA, or firmware-mediated configuration.

## Risks And Edge Cases
- Consumers must check `IS_ERR()` before using the returned regmap, especially because the disabled stub returns `-ENOTSUPP`.
- Missing phandles and disabled Kconfig are different operational cases but both surface as lookup errors.
- Shared system-manager register writes may affect unrelated subsystems; consumers need mask-specific updates and documented ownership.

## Test Signals
Build with and without `CONFIG_MFD_ALTERA_SYSMGR`, test successful phandle lookup, missing-property error handling, disabled-Kconfig fallback, regmap read/update from a consumer, and conflict-free access when multiple consumers share the same system manager.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/altera-sysmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/arizona/core.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/arizona/core.h

## Purpose
This header defines the internal MFD core contract for Wolfson/Cirrus Arizona audio codec families such as WM5102, WM5110, WM8997, WM8280, WM8998, WM1814, WM1831, and CS47L24. It centralizes core supplies, clocks, IRQ IDs, device state, notifier support, IRQ helper APIs, 32 kHz clock reference APIs, and variant patch hooks.

## Important APIs, Types, And Functions
- Type and clock enums: `enum arizona_type`, `ARIZONA_MCLK1`, `ARIZONA_MCLK2`, and `ARIZONA_NUM_MCLK`.
- IRQ ABI: `ARIZONA_IRQ_*` logical interrupt IDs cover GPIOs, jack/mic/headphone detection, DSP RAM/IRQ signals, speaker faults, clock/FLL/ASRC/AIF errors, boot completion, DCS, short-circuit events, and `ARIZONA_NUM_IRQ`.
- `struct arizona` stores regmap, parent device, variant/revision, regulator supplies, DCVDD state, platform data, IRQ domains/chips, headphone-detect state, clock lock/refcount, MCLK handles, DAPM pointer, TDM settings, DAC compensation state, and notifier chain.
- Helper APIs include `arizona_call_notifiers()`, `arizona_clk32k_enable()`, `arizona_clk32k_disable()`, `arizona_request_irq()`, `arizona_free_irq()`, and `arizona_set_irq_wake()`.
- Patch hooks include `wm5102_patch()`, `wm5110_patch()`, `cs47l24_patch()`, `wm8997_patch()`, and `wm8998_patch()`.

## Control Flow
The core driver identifies the variant, powers supplies, initializes regmap IRQ chips and domains, applies variant patches, parses platform data, and registers audio/regulator/GPIO/IRQ children. Codec and accessory-detection drivers request logical IRQs through `arizona_request_irq()`, use `arizona_clk32k_enable()`/disable with reference counting, and publish cross-component events through the blocking notifier chain.

## State And Persistence
Software state in `struct arizona` tracks power-supply ownership, whether DCVDD is external, IRQ-domain handles, 32 kHz clock reference count, MCLK handles, DAPM context, TDM slots/widths, DAC compensation fields, and notifier subscribers. Hardware state includes codec registers, IRQ masks/status, clocks/FLLs, DSP state, jack detection, speaker protection, GPIOs, and audio route/power settings.

## Dependencies And Integration Points
The header depends on clk, interrupt, notifier, regmap, regulator, and Arizona platform-data APIs. It integrates with ASoC codec drivers, extcon/input jack detection, regulator child drivers, GPIO/pinctrl-style users, regmap IRQ, runtime PM, and variant-specific patch code.

## Risks And Edge Cases
- IRQ numeric IDs are an ABI between MFD core and child drivers; reordering breaks request mappings.
- `clk32k_ref` must be updated under `clk_lock` to avoid disabling a shared 32 kHz clock while a child still needs it.
- Variant patch stubs can compile to no-op depending on Kconfig, so users must not assume a patch ran for disabled variants.
- DAC compensation and DAPM pointers are shared with ASoC paths and require lifetime coordination.
- Power sequencing across `core_supplies`, `dcvdd`, reset GPIO, and register access is critical for reliable probe/resume.

## Test Signals
Validate probe for each supported variant, patch hook execution, regulator enable/disable and external DCVDD handling, logical IRQ request/free/wake behavior, 32 kHz clock reference counting under multiple users, notifier delivery, ASoC codec probe and DAPM integration, suspend/resume, and fault interrupt delivery for clock and speaker-protection events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/arizona/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/arizona/pdata.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/arizona/pdata.h

## Purpose
This header defines platform data for Wolfson/Cirrus Arizona audio codec devices. It covers reset and IRQ configuration, GPIO defaults, regulator child platform data, clocking hints, jack/headphone/mic-detection policy, digital microphone references, MICBIAS setup, input/output modes, speaker/haptic settings, and general-purpose switch control.

## Important APIs, Types, And Functions
- GPIO field masks define direction, pull-up/down, level, polarity, output config, debounce, and function fields for packed GPIO default values.
- Limits define array sizes: `ARIZONA_MAX_GPIO`, `ARIZONA_MAX_INPUT`, `ARIZONA_MAX_MICBIAS`, `ARIZONA_MAX_OUTPUT`, `ARIZONA_MAX_AIF`, and `ARIZONA_MAX_PDM_SPK`.
- `struct arizona_micbias` describes voltage, external capacitor, discharge, soft-start, and bypass behavior.
- `struct arizona_micd_config` and `struct arizona_micd_range` describe mic-detect polarity/source/bias and impedance-to-key mappings.
- `struct arizona_pdata` aggregates reset GPIO, MICVDD/LDO1 regulator data, 32 kHz clock source, IRQ flags/base GPIO, GPIO defaults, AIF clocking limits, jack detection policy, mic detection tuning, DMIC references, micbias settings, input/output modes and limits, speaker mute/format, haptic actuator type, optional legacy IRQ GPIO, and GPSW setting.

## Control Flow
Platform or device-tree parsing fills `struct arizona_pdata`, which is embedded in `struct arizona` during core probe. The core and codec drivers use it to configure reset, IRQ polarity, child regulators, GPIO register defaults, clock source selection, jack/mic detection algorithms, input/output analog modes, speaker outputs, and haptic behavior.

## State And Persistence
The structure is configuration state copied into the core device. Once applied, it influences hardware register state for GPIOs, MICBIAS, jack detection, DMIC references, input/output routing, output volume limits, PDM speaker behavior, haptics, and GPSW. Runtime detection state is owned by core/codec drivers rather than this header.

## Dependencies And Integration Points
The header includes device-tree bindings and regulator platform-data headers for Arizona LDO1 and microphone supply children. It integrates with the MFD core, ASoC codec drivers, extcon/input headset detection, regulator framework, GPIO descriptors, and optional legacy gpiolib paths.

## Risks And Edge Cases
- Array fields are fixed-size and variant-sensitive; board data must not configure non-existent inputs, outputs, GPIOs, micbiases, or AIFs.
- Mic-detect impedance ranges and polarity configs directly affect headset button reporting and can cause false events if misordered or mismatched.
- `gpio_defaults` are packed register values; callers must compose fields with the provided masks/shifts.
- Legacy `irq_gpio` exists only under `CONFIG_GPIOLIB_LEGACY`; portable users should prefer descriptors and `irq_flags`.
- Output volume limits and micbias voltage settings need validation to avoid unsafe board-level behavior.

## Test Signals
Test platform-data and device-tree parsing, reset GPIO sequencing, IRQ polarity, regulator child setup, GPIO default programming, 32 kHz source selection, jack insert/remove and mic/button detection across configured impedance ranges, DMIC reference and micbias settings, input/output mode programming, speaker/haptic settings, and bounds handling for variant-specific array entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/arizona/pdata.h -->
