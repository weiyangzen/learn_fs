<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/irq.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/irq.h

## Purpose
`irq.h` defines the WM831x interrupt-controller ABI used by the MFD core and child drivers. It assigns Linux-local interrupt numbers for temperature, GPIO, power path, watchdog, RTC, charger, touch, AUXADC, current-sink, high-current, and regulator undervoltage events, then maps the chip interrupt status and mask registers at `0x4010` through `0x401d`.

## Important APIs, types, and functions
There are no functions or structs. The public API is macro based: `WM831X_IRQ_*` indexes, `WM831X_NUM_IRQS`, root status bits such as `WM831X_PPM_INT`, per-source event bits such as `WM831X_CHG_BATT_HOT_EINT`, GPIO event bits `WM831X_GP1_EINT` through `WM831X_GP16_EINT`, IRQ output configuration bits `WM831X_IRQ_OD` and `WM831X_IM_IRQ`, and matching `WM831X_IM_*` masks.

## Control flow
The runtime IRQ controller code uses the root `System Interrupts` register to identify active interrupt classes, then reads the child status registers and dispatches child IRQ numbers. Mask updates write the parallel mask registers. This header supplies the bit layout needed for that decode/ack/mask flow.

## State and persistence behavior
State is in chip registers: latched event status, output-line mode, and interrupt mask bits. Driver state derived from these macros is volatile and must be reconstructed on probe or resume.

## Dependencies and integration points
The header is consumed by WM831x MFD IRQ setup and by child drivers requesting specific IRQ numbers. It aligns with PMU, RTC, charger, GPIO, touch, AUXADC, OTP, watchdog, current-sink, and regulator headers that define the controlled hardware blocks.

## Risks and test signals
Risks include off-by-one IRQ numbering, missing `WM831X_IRQ_CHG_END` gap handling, masking a root interrupt while leaving child status pending, and confusing status bits with mask bits. Test signals are probe-time IRQ-domain size checks against `WM831X_NUM_IRQS`, per-source interrupt injection, suspend/resume mask restoration, GPIO edge tests, and charger/regulator fault IRQ routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/otp.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/otp.h

## Purpose
`otp.h` describes the WM831x one-time-programmable memory register window. It covers unique ID words, factory OTP identity and trim fields, customer OTP identity/finality, and DBE check-data readback.

## Important APIs, types, and functions
The driver-facing entry points are `wm831x_otp_init(struct wm831x *wm831x)` and `wm831x_otp_exit(struct wm831x *wm831x)`. Register macros define repeated `WM831X_UNIQUE_ID_*` fields for `0x7800` through `0x7807`, factory fields such as `WM831X_OTP_FACT_ID_MASK`, `WM831X_OTP_FACT_FINAL`, DC trim masks, `WM831X_CHIP_ID_MASK`, oscillator/bandgap trims, child I2C address fields, charge trim fields, customer fields `WM831X_OTP_AUTO_PROG`, `WM831X_OTP_CUST_ID_MASK`, and `WM831X_OTP_CUST_FINAL`.

## Control flow
Initialization code can read OTP registers to discover chip identity, trim data, and customer-programmed behavior. Exit tears down any OTP-created state. The header itself performs no reads or writes; it supplies the bit definitions for register accessors in the core.

## State and persistence behavior
OTP contents are persistent in hardware and normally immutable after finalization bits are set. Runtime driver state should treat these registers as calibration and identity inputs, not as ordinary mutable configuration.

## Dependencies and integration points
The prototypes depend on `struct wm831x` from the WM831x core. OTP values influence regulator trims, oscillator/bandgap calibration, child addressing, and customer-specific startup behavior.

## Risks and test signals
Risks include treating duplicate `WM831X_UNIQUE_ID_*` macro names as register-specific constants, writing to final OTP areas accidentally, and mishandling customer/factory final bits. Test signals are read-only register dumps, chip-ID/unique-ID exposure tests, calibration application checks, and fault-injection around init failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/otp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/pdata.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/pdata.h

## Purpose
`pdata.h` defines board-supplied platform data for WM831x devices. It lets non-DT board files describe charger policy, backup battery charging, regulator init data, LEDs, touchscreen IRQs, watchdog action, GPIO defaults, and probe-time hooks.

## Important APIs, types, and functions
Key structs include `wm831x_backlight_pdata`, `wm831x_backup_pdata`, `wm831x_battery_pdata`, `wm831x_buckv_pdata`, `wm831x_status_pdata`, `wm831x_touch_pdata`, `wm831x_watchdog_pdata`, and the aggregate `wm831x_pdata`. Enums define status LED source selection and watchdog actions. Array sizing macros include `WM831X_MAX_STATUS`, `WM831X_MAX_DCDC`, `WM831X_MAX_EPE`, `WM831X_MAX_LDO`, `WM831X_MAX_ISINK`, and `WM831X_GPIO_NUM`.

## Control flow
The MFD core receives `wm831x_pdata`, optionally calls `pre_init`, configures IRQ/GPIO base behavior, creates child devices, supplies per-regulator `regulator_init_data`, and then calls `post_init`. Child drivers consume their sub-structs during probe.

## State and persistence behavior
Platform data is static board configuration. It is not persisted by the driver, but values can program persistent hardware state until reset, suspend, or power loss depending on the target register.

## Dependencies and integration points
The header references `struct wm831x`, `struct regulator_init_data`, Linux `bool`, regulator framework data, LED triggers, IRQ flags, GPIO numbering, charger and watchdog child drivers, and board setup code.

## Risks and test signals
Risks include invalid regulator array indexing, units confusion between mA/uA/mV/minutes, stale GPIO defaults, missing IRQ flags for touch events, and unsafe watchdog reset policy. Test signals include board probe with full/partial pdata, regulator constraint validation, charger limit programming, watchdog action tests, and suspend/shutdown behavior when `soft_shutdown` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/pdata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/pmu.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/pmu.h

## Purpose
`pmu.h` defines WM831x PMU, system-status, main battery charger, and backup charger register fields. It is the shared map for power-source status, USB current limit, charger setup, charger state, and backup-battery charger control.

## Important APIs, types, and functions
There are no functions. Important macros cover `Power State` bits including `WM831X_CHIP_ON`, `WM831X_CHIP_SLP`, `WM831X_REF_LP`, `WM831X_USB100MA_STARTUP_MASK`, and `WM831X_USB_ILIM_MASK`; `System Status` bits including thermal warning and power-source flags; charger controls `WM831X_CHG_ENA`, `WM831X_CHG_FRC`, `WM831X_CHG_ITERM_MASK`, `WM831X_CHG_TIME_MASK`, `WM831X_CHG_TRKL_ILIM_MASK`, `WM831X_CHG_VSEL_MASK`, and `WM831X_CHG_FAST_ILIM_MASK`; charger status states; and backup charger fields.

## Control flow
Power and charger drivers read system status to classify source and thermal state, write charger control registers from platform policy, and poll or interrupt on `Charger Status` to advance user-visible battery state. Backup charging uses its own control register.

## State and persistence behavior
All meaningful state is hardware register state: charger enable/force, current/voltage/time limits, elapsed charge time, charger FSM state, and backup charging mode. Driver caches must be treated as mirrors.

## Dependencies and integration points
The header integrates with the WM831x MFD register access layer, power-supply and charger child drivers, PMU IRQ bits from `irq.h`, and platform data in `pdata.h`.

## Risks and test signals
Risks include programming unsafe current or voltage selector values, confusing status bits with control bits, mishandling overtemperature charger states, and failing to handle USB current-limit transitions. Test signals include charger state decoding, limit-table boundary tests, power-source changes, thermal fault IRQs, and backup charger enable/disable tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/regulator.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/regulator.h

## Purpose
`regulator.h` is the WM831x regulator and current-sink register map. It defines enables, status/fault bits, DCDC/LDO operating modes, voltage selectors, startup/shutdown slots, sleep settings, hardware-control selectors, dynamic-voltage-scaling selectors, power-good sources, and current-sink selector data.

## Important APIs, types, and functions
The only symbol declaration is `extern const unsigned int wm831x_isinkv_values[WM831X_ISINK_MAX_ISEL + 1]`, with `WM831X_ISINK_MAX_ISEL` set to 55. Macro groups cover current sinks `CS1/CS2`, DCDC enable/status/UV/OV/HC registers, LDO enable/status/UV registers, DC1/DC2 BuckWise controls with DVS fields, DC3/DC4 controls, LDO1-LDO10 control/on/sleep fields, LDO11 on/sleep fields, and power-good source bits for DC and LDO rails.

## Control flow
Regulator drivers translate regulator framework operations into register updates: enable bits in aggregate registers, voltage selectors in ON/SLEEP/DVS registers, mode and hardware-control fields in per-rail control registers, and status/fault reads for `is_enabled`, error reporting, or IRQ handling.

## State and persistence behavior
Rail state lives in hardware registers and includes active/sleep voltage images, hardware-control source/mode, dynamic voltage state, current-sink drive/ramp/current, power-good state, and fault latches. Some values are board policy and should be restored after reset or resume.

## Dependencies and integration points
This header is consumed by WM831x regulator, LED/backlight current-sink, PMU, IRQ, and platform-data code. It is tied to Linux regulator constraints and to IRQ definitions for UV/high-current/current-sink events.

## Risks and test signals
Risks include rail-index/register mismatches, invalid voltage selector tables, ignoring LDO11's distinct 4-bit selector format, DVS source misconfiguration, and missed fault handling. Test signals include regulator list-voltage/set-voltage tests, enable/status readback, suspend mode restoration, DVS GPIO transitions, current-sink brightness tables, and UV/HC fault IRQ injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/status.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/status.h

## Purpose
`status.h` defines the compact register-field layout for WM831x status LED blocks. It gives LED drivers the masks and shifts needed to select source, blink mode, sequence length, duration, and duty cycle.

## Important APIs, types, and functions
There are no functions or structs. Public macros are `WM831X_LED_SRC_MASK/SHIFT/WIDTH`, `WM831X_LED_MODE_MASK/SHIFT/WIDTH`, `WM831X_LED_SEQ_LEN_MASK/SHIFT/WIDTH`, `WM831X_LED_DUR_MASK/SHIFT/WIDTH`, and `WM831X_LED_DUTY_CYC_MASK/SHIFT/WIDTH`.

## Control flow
The status LED child driver combines platform defaults from `wm831x_status_pdata` with LED-class operations, then updates the appropriate status LED register fields using these masks. Hardware can drive LEDs from OTP, power, charger, or manual sources.

## State and persistence behavior
LED mode state is stored in the PMIC LED control registers. Platform data may request preservation of existing hardware state, so probe must avoid overwriting fields when the default source is preserve.

## Dependencies and integration points
The header integrates with `pdata.h` status LED source definitions, Linux LED triggers, and WM831x MFD register access.

## Risks and test signals
Risks include overwriting preserved OTP settings, using raw enum values without accounting for register encoding, and applying blink timing masks to the wrong bits. Test signals include LED trigger registration, manual brightness updates, boot-preserve behavior, and charger/power-source LED source selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/watchdog.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/watchdog.h

## Purpose
`watchdog.h` defines the WM831x watchdog register fields. It supports enabling the watchdog, debug and sleep behavior, reset triggering, primary and secondary timeout actions, and timeout selection.

## Important APIs, types, and functions
There are no functions or structs. Macros describe register `0x4004`: `WM831X_WDOG_ENA`, `WM831X_WDOG_DEBUG`, `WM831X_WDOG_RST_SRC`, `WM831X_WDOG_SLPENA`, `WM831X_WDOG_RESET`, `WM831X_WDOG_SECACT_MASK`, `WM831X_WDOG_PRIMACT_MASK`, and `WM831X_WDOG_TO_MASK`, each with mask/shift/width companions.

## Control flow
The watchdog driver programs timeout and action fields from platform data, enables or disables the watchdog through `WM831X_WDOG_ENA`, and kicks or forces reset through the reset bit according to the chip protocol.

## State and persistence behavior
Watchdog configuration is hardware state. Once enabled, it can survive normal software control paths until explicitly disabled or until reset; sleep-enable and reset-source fields affect behavior across low-power and reboot paths.

## Dependencies and integration points
The header pairs with `wm831x_watchdog_pdata` and `enum wm831x_watchdog_action` in `pdata.h`, the watchdog subsystem, WM831x IRQ `WM831X_IRQ_WDOG_TO`, and core register access.

## Risks and test signals
Risks include choosing reset actions unexpectedly, failing to account for sleep behavior, writing timeout selectors outside hardware range, and mishandling debug mode. Test signals include watchdog start/stop/ping tests, timeout IRQ versus reset policy tests, suspend behavior, and reset-source readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/watchdog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/audio.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/audio.h

## Purpose
`audio.h` defines the WM8350 codec/audio register map and platform data. It covers clocking, FLL, DAC/ADC controls, input and output mixers, volume registers, anti-pop behavior, audio interface formatting, jack detect status, clock divider IDs, DAI IDs, audio IRQ numbers, and codec platform tuning.

## Important APIs, types, and functions
Public data types are `struct wm8350_audio_platform_data` and `struct wm8350_codec`. Macros define audio register addresses `0x28` through `0x74` plus jack status `0xe7`, field masks for FLL and clocks, DAC/ADC volume and mute bits, input/output mixer routing, AIF format and TDM controls, jack-detect IRQs `WM8350_IRQ_CODEC_*`, platform constants for VMID/discharge/tie-off behavior, and clock divider/source IDs.

## Control flow
The codec driver uses these fields while probing and during ALSA SoC DAI operations: configure VMID and anti-pop timing from platform data, set FLL/clock dividers, route mixers, update volume with VU bits, set AIF format, and service jack IRQs.

## State and persistence behavior
Codec routing, gains, mute state, clocks, FLL configuration, and jack status live in hardware registers. `struct wm8350_codec` stores the platform device and platform data pointer as runtime binding state.

## Dependencies and integration points
The header depends on `platform_device` and is embedded by `core.h`. It integrates with ASoC codec/DAI code, IRQ registration through WM8350 core, board platform data, and power-management register bits declared in `core.h`.

## Risks and test signals
Risks include clock-divider mistakes causing invalid sample rates, volume update bits not being set consistently across stereo channels, pop/click regressions from bad VMID timing, jack IRQ number drift, and routing loops. Test signals include ASoC probe, DAI format/rate tests, mixer control readback, suspend/resume audio path restoration, and jack-detect interrupt tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/comparator.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/comparator.h

## Purpose
`comparator.h` describes the WM8350 AUXADC and generic digital comparator block. It defines digitiser controls, AUX channel readback fields, USB/line/battery/chip-temperature readback fields, comparator threshold/source fields, comparator IRQ numbers, and the public AUXADC read helper.

## Important APIs, types, and functions
The public function is `wm8350_read_auxadc(struct wm8350 *wm8350, int channel, int scale, int vref)`. Register macros cover digitiser controls `WM8350_AUXADC_CTC`, `WM8350_AUXADC_POLL`, channel select bits, conversion rate/mask/calibration/wait bits, 12-bit readback masks, comparator enable bits `WM8350_DCMP1_ENA` through `WM8350_DCMP4_ENA`, comparator source/greater-than/threshold masks, channel IDs `WM8350_AUXADC_*`, and coefficient `WM8350_AUX_COEFF`.

## Control flow
The AUXADC implementation serializes conversions, selects a channel and scale/reference, starts or polls conversion, waits for data-ready IRQ or status, then reads the appropriate readback register and masks 12-bit data. Comparator users program source, threshold, and comparison direction, then consume comparator IRQs.

## State and persistence behavior
Conversion setup and comparator thresholds are hardware register state. `core.h` provides `auxadc_mutex` and `auxadc_done` for runtime coordination; conversion results are transient readback values.

## Dependencies and integration points
This header depends on `struct wm8350`, WM8350 core register access, IRQ definitions in `core.h`, and hardware monitor/power-supply users that read voltage or temperature channels.

## Risks and test signals
Risks include concurrent AUXADC conversions without the mutex, wrong scale/reference conversion math, stale data-ready completion, and threshold source mismatch. Test signals include channel-by-channel readback, timeout paths, IRQ completion, comparator threshold interrupts, and voltage conversion checks using `WM8350_AUX_COEFF`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/comparator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/core.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/core.h

## Purpose
`core.h` is the central WM8350 MFD contract. It defines core register addresses and bit fields, embeds child-device state, declares regmap/register helpers, exposes platform initialization data, and provides IRQ wrapper helpers for child drivers.

## Important APIs, types, and functions
Key types are `struct wm8350_hwmon`, `struct wm8350`, and `struct wm8350_platform_data`. Important APIs include `wm8350_device_init()`, `wm8350_clear_bits()`, `wm8350_set_bits()`, `wm8350_reg_read()`, `wm8350_reg_write()`, `wm8350_reg_lock()`, `wm8350_reg_unlock()`, `wm8350_block_read()`, `wm8350_block_write()`, `wm8350_irq_init()`, `wm8350_irq_exit()`, and inline IRQ helpers `wm8350_register_irq()`, `wm8350_free_irq()`, `wm8350_mask_irq()`, and `wm8350_unmask_irq()`. It also declares `wm8350_regmap`.

## Control flow
Bus glue creates a `struct wm8350`, initializes regmap, calls `wm8350_device_init()`, and child drivers use embedded sub-structs plus register/IRQ helpers. IRQ registration offsets child IRQ numbers by `irq_base` and requests threaded one-shot handlers.

## State and persistence behavior
`struct wm8350` stores runtime state: device pointer, regmap, register-lock state, AUXADC mutex/completion, IRQ lock/base/masks, chip IRQ, and child state for codec, GPIO, hwmon, PMIC, power, RTC, and watchdog. Hardware register state includes power management, hibernate, interface, interrupt, status, and override registers.

## Dependencies and integration points
The header includes completion, interrupt, mutex, regmap, and all WM8350 child headers. It integrates with MFD child creation, regulator, GPIO, ASoC, RTC, watchdog, power-supply, hwmon, and genirq.

## Risks and test signals
Risks include using IRQ helpers with `irq_base == 0`, losing mask state over suspend, incorrect register lock/unlock sequencing, child header circularity, and regmap cache mismatches. Test signals include full MFD probe/remove, regmap read/write/block tests, IRQ mask/unmask dispatch, AUXADC completion, and child-device registration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/gpio.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/gpio.h

## Purpose
`gpio.h` defines the WM8350 GPIO register map, alternate-function encodings for GPIO0 through GPIO12, electrical configuration constants, interrupt/status bits, the GPIO configuration helper, and GPIO child state.

## Important APIs, types, and functions
The public function is `wm8350_gpio_config(struct wm8350 *wm8350, int gpio, int dir, int func, int pol, int pull, int invert, int debounce)`. `struct wm8350_gpio` stores the platform device. Macros define debounce, pull-up/down, interrupt mode, direction, polarity/type, function-select, level registers, per-pin alternate functions, direction/polarity/pull/invert/debounce values, and `WM8350_IRQ_GPIO(x)` mapping GPIO pins to IRQ numbers starting at 50.

## Control flow
Platform init or a GPIO driver calls `wm8350_gpio_config()` to program pin direction, function select nibble, polarity/type, pull resistor, inversion, and debounce. Runtime GPIO reads use the level register, and IRQ handling maps pin events through the core IRQ domain.

## State and persistence behavior
Pin mux and electrical state are hardware register state. `struct wm8350_gpio` only tracks the child platform device; board policy must be re-applied after reset or resume if registers are not retained.

## Dependencies and integration points
The header depends on `platform_device` and `struct wm8350`. It integrates with core IRQ/status definitions, board `wm8350_platform_data.init`, gpiolib-facing implementation code, and alternate functions used by audio, power, RTC, charger, and reset signals.

## Risks and test signals
Risks include selecting an alternate function invalid for a pin, mixing active-low with invert semantics, enabling pulls on outputs, off-by-one GPIO IRQ mapping, and clobbering neighboring 4-bit function fields. Test signals include per-pin mux tests, direction/readback tests, interrupt edge tests, suspend/resume retention, and invalid argument validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/pmic.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/pmic.h

## Purpose
`pmic.h` defines the WM8350 regulator, current-sink, LED, power-check, fault, trim, and force-PWM register contract. It also declares regulator/LED registration helpers and extra control APIs that sit outside the generic regulator interface.

## Important APIs, types, and functions
Key types are `struct wm8350_led_platform_data`, `struct wm8350_led`, and `struct wm8350_pmic`. Public APIs include `wm8350_register_regulator()`, `wm8350_register_led()`, `wm8350_dcdc_set_slot()`, `wm8350_dcdc25_set_mode()`, `wm8350_ldo_set_slot()`, and `wm8350_isink_set_flash()`. Macros cover six DCDCs, four LDOs, two current sinks, current-sink flash timing, rail requested/status/fault bits, startup/shutdown slots, error actions, low-power/hibernate modes, regulator IRQ numbers, and `NUM_WM8350_REGULATORS`.

## Control flow
The PMIC child registers regulator platform devices from board constraints, maps LED current sinks to DCDC rails, and uses the extra helpers to configure enable/shutdown slots, DCDC2/5 boost or switch mode, feedback/ramp/current limits, LDO slots, and current-sink flash behavior.

## State and persistence behavior
Regulator enable, voltage selector, hibernate image, fault mask, trim, force-PWM, current-sink, and LED state are hardware state. `struct wm8350_pmic` persists runtime limits, ISINK-to-DCDC mapping, hibernate modes, child platform devices, and two LED objects.

## Dependencies and integration points
The header depends on platform devices, LED class, regulator machine data, workqueues, spinlocks, and regulator consumer supplies. It integrates with WM8350 core, regulator framework, LED class, IRQ fault reporting, and board constraints.

## Risks and test signals
Risks include mismatched regulator IDs, invalid startup/shutdown slot timing, DCDC2/5 mode confusion, LED current beyond `max_uA`, duplicated `LDO4_ERRACT_SHIFT` definition hiding edits, and fault masks that suppress critical shutdown. Test signals include regulator registration, voltage/mode set tests, LED brightness work, ISINK flash programming, UV/OC IRQ injection, and hibernate configuration checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/pmic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/rtc.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/rtc.h

## Purpose
`rtc.h` defines the WM8350 RTC and alarm register layout, time-control bits, tick-control bits, RTC IRQ numbers, and runtime RTC child state.

## Important APIs, types, and functions
The main data type is `struct wm8350_rtc`, storing the platform device, `rtc_device`, and suspend/resume booleans for alarm and update interrupts. Macros define time registers for seconds/minutes, hours/day, date/month, year, alarm equivalents, and control fields such as `WM8350_RTC_BCD`, `WM8350_RTC_12HR`, `WM8350_RTC_SET`, `WM8350_RTC_ALMSET`, periodic interval selection, digital square wave selection, tick status/source/trim, and IRQs `WM8350_IRQ_RTC_PER`, `WM8350_IRQ_RTC_SEC`, and `WM8350_IRQ_RTC_ALM`.

## Control flow
The RTC driver reads split time/date registers, converts binary or BCD fields, stops or sets the RTC with control bits when updating time, programs alarm fields with optional `DONT_CARE` sentinels, and handles periodic/second/alarm IRQs through the core IRQ helpers.

## State and persistence behavior
Time, alarm, format mode, periodic interrupt mode, square-wave mode, and trim are hardware-backed RTC state. `alarm_enabled` and `update_enabled` preserve interrupt enable intent across suspend/resume.

## Dependencies and integration points
The header depends on `platform_device` and implicitly on `rtc_device`. It integrates with WM8350 core IRQ registration, Linux RTC class operations, power management, and board clock/trim policy.

## Risks and test signals
Risks include BCD/binary month conversion errors, 12-hour AM/PM mishandling, invalid `-1` alarm wildcard propagation into bit fields, stopping the clock without restart, and lost wake alarms over suspend. Test signals include set/read time round trips, BCD mode tests, alarm wildcard tests, periodic IRQ tests, suspend wake tests, and trim register validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/rtc.h -->
