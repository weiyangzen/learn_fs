# subset-b-004010 LED Driver Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-cpcap.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-cpcap.c

Purpose: CPCAP MFD child LED driver for Motorola CPCAP red, green, blue, auxiliary display, and camera privacy LEDs. It exposes one LED class device per platform child selected by OF compatible data.

Important APIs/types/functions: `struct cpcap_led_info` describes register, mask, brightness limit, and optional init bits; `struct cpcap_led` stores classdev, parent regmap, regulator, mutex, and power state. `cpcap_led_val()` packs 5-bit current and 4-bit duty. `cpcap_led_set_power()` wraps `regulator_enable/disable()`. `cpcap_led_set()` is the blocking brightness callback. `cpcap_led_probe()` resolves `device_get_match_data()`, parent `regmap`, `vdd`, `label`, optional init writes, and calls `devm_led_classdev_register()`.

Control flow: probe is table-driven by `cpcap_led_of_match`; brightness ON enables `vdd`, writes current/duty, and brightness OFF first writes `CPCAP_LED_NO_CURRENT`, then duty off, then disables `vdd`. Init masks are applied before registration for ADL and CP variants.

State and persistence: runtime state is volatile in CPCAP registers and `led->powered`; there is no persisted configuration. The mutex serializes power and register updates. Devm handles lifetime, but there is no explicit shutdown callback, so final LED state depends on LED core cleanup and last brightness state.

Dependencies/integration: depends on CPCAP MFD register definitions, parent regmap, regulator framework, OF match data, and LED class. Device tree must provide compatible-specific child nodes and a `label`.

Risks: label is mandatory; missing parent regmap or `vdd` aborts probe. OFF sequencing is hardware-specific and should not be reordered. Regulator state can become stale if a register write fails after enabling. There is no suspend/resume flag or retain-state policy.

Test signals: instantiate each compatible, verify regulator toggles only when needed, check OFF writes current cutoff before duty off, inject regmap/regulator failures, and confirm `max_brightness` is 31 or 1 as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-cpcap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-cr0014114.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-cr0014114.c

Purpose: SPI LED-chain driver for Crane CR0014114 boards. Each DT child becomes one LED class device whose brightness byte is sent as part of a chain-wide packet.

Important APIs/types/functions: `struct cr0014114` owns the SPI device, mutex, delayed recount work, shared transfer buffer, firmware pacing deadline, and flexible array of `cr0014114_led`. `cr0014114_calc_crc()` computes protocol CRC while avoiding command-byte collisions. `cr0014114_recount()` sends re-enumeration commands. `cr0014114_sync()` performs pacing, optional recount, packet assembly, CRC, and `spi_write()`. `cr0014114_set_sync()` is the blocking LED callback.

Control flow: probe counts child nodes, allocates private data and buffer, initializes `delay` so the first sync may proceed, performs two forced recount/sync passes, registers child LEDs with `devm_led_classdev_register_ext()`, schedules hourly recount work, and stores driver data. Brightness callbacks update one cached byte then sync the whole chain.

State and persistence: per-LED brightness is cached in RAM; hardware receives full snapshots. `do_recount` and `delay` are volatile pacing/recovery state. Delayed work periodically re-enumerates to work around firmware behavior. No persistent state survives driver removal.

Dependencies/integration: depends on SPI, child fwnodes, LED class extended registration, delayed work, jiffies timing, and Crane firmware protocol semantics.

Risks: all LED updates share one bus transaction and one mutex, so slow firmware pacing delays every brightness call. Bad child count or no DT children aborts probe. CRC special cases are protocol-critical. The delayed work must be canceled before private memory disappears.

Test signals: verify packet length `count + 2`, CRC collision handling, first and second recount sequences, hourly work cancellation on remove, per-child naming from fwnode, and synchronization under concurrent brightness writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-cr0014114.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-cros_ec.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-cros_ec.c

Purpose: ChromeOS EC LED driver that discovers EC-managed LEDs via `EC_CMD_LED_CONTROL` and exposes them as Linux multicolor LED class devices with an automatic EC hardware trigger.

Important APIs/types/functions: `struct cros_ec_led_priv` stores `led_classdev_mc`, EC device pointer, and EC LED id. Mapping tables translate EC LED ids to LED functions and EC colors to Linux color ids. `cros_ec_led_send_cmd()` wraps `cros_ec_cmd()`. `cros_ec_led_brightness_set_blocking()` computes multicolor components and sends EC brightness values. `cros_ec_led_probe_one()` queries one EC LED and registers it if supported.

Control flow: platform probe obtains the parent `cros_ec_device`, registers trigger `chromeos-auto`, iterates all `EC_LED_ID_COUNT` ids, queries each with `EC_LED_FLAGS_QUERY`, skips unsupported ids, validates uniform brightness ranges for multicolor API compatibility, allocates subleds, names devices as `chromeos:<color>:<function>`, and registers multicolor classdevs.

State and persistence: color intensities and brightness are maintained by the LED core and EC firmware. The driver keeps only per-device id and EC pointer. The hardware trigger activation sends `EC_LED_FLAGS_AUTO`, returning control to firmware policy.

Dependencies/integration: integrates with ChromeOS EC protocol, LED multicolor framework, LED trigger framework, platform MFD device `"cros-ec-led"`, and EC command definitions.

Risks: inconsistent EC brightness ranges cause `-EINVAL` because Linux multicolor expects one max brightness. `-EOPNOTSUPP` aborts all probing, while `-EINVAL` for a single id is treated as unknown and skipped. Mapping arrays rely on compile-time `static_assert()` against EC enum sizes.

Test signals: use EC emulation or hardware to exercise query, unsupported ids, auto trigger activation, single-color vs multicolor naming, and component-to-EC color mapping for all supported colors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-cros_ec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-da903x.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-da903x.c

Purpose: legacy platform-data LED/vibrator driver for Dialog/Marvell DA9030 and DA9034 PMIC MFD children.

Important APIs/types/functions: `struct da903x_led` stores LED class device, parent MFD device, PMIC id, and platform flags. `da903x_led_set()` maps LED ids to PMIC registers and brightness encodings. Probe consumes `struct led_info` platform data, validates `pdev->id`, registers the classdev on the parent, and stores driver data.

Control flow: brightness writes branch by DA9030/DA9034 id. DA9030 LED outputs encode enable and inverted 3-bit PWM; DA9030 vibrator toggles a misc-control enable bit. DA9034 LEDs scale `LED_FULL` to a 0x5f range and optionally apply ramp flag; DA9034 vibrator writes the raw even brightness value. Remove unregisters the classdev.

State and persistence: no software cache beyond id/flags. Hardware register state persists until overwritten or PMIC reset. No devm classdev registration is used, so unregister is explicit.

Dependencies/integration: depends on DA903x MFD register access via `da903x_write()`, platform ids from DA903x headers, and board platform data for names/triggers/flags.

Risks: probe silently returns success when platform data is missing, yielding no LED. Brightness scaling and bit inversions are chip-specific. Invalid platform ids fail. No locking is local, relying on parent MFD access serialization.

Test signals: platform-device id coverage for each DA9030/DA9034 output, register-value checks for OFF/ON/PWM extremes, missing platform data behavior, and unregister on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-da903x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-da9052.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-da9052.c

Purpose: Dialog DA9052 PMIC LED driver for two GPIO-backed LED outputs described by MFD platform data.

Important APIs/types/functions: `struct da9052_led` stores classdev, PMIC pointer, LED index, and id. `led_reg[]` maps logical LED indices to DA9052 LED control registers. `da9052_set_led_brightness()` writes brightness plus continuous-dim mode. `da9052_configure_leds()` configures GPIO14/15 nibbles as high-level open-drain LED outputs. Probe iterates `led_platform_data`.

Control flow: probe obtains parent `da9052`, validates `da9052_pdata->pled`, allocates an array sized to `num_leds`, registers each LED classdev on the parent, initializes brightness to OFF, then configures the shared GPIO register. Remove turns each LED off and unregisters it.

State and persistence: per-LED index and PMIC pointer are software state; brightness lives in hardware registers. GPIO output configuration remains until changed by another driver or PMIC reset.

Dependencies/integration: relies on DA9052 MFD core, DA9052 platform data, DA9052 register-update helpers, and LED class callbacks.

Risks: `led_index` comes from platform-data flags and is used as an array index into a two-entry `led_reg[]`; bad board data can address invalid memory. Registration uses manual cleanup. Errors during initial brightness writes are logged but probing continues for that LED.

Test signals: validate platform-data bounds, GPIO14/15 nibble configuration, brightness max `0x5f`, cleanup after mid-loop registration failure, and remove-time OFF writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-da9052.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-dac124s085.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-dac124s085.c

Purpose: simple SPI LED-class driver for the four-channel DAC124S085 DAC, treating each DAC output as a 12-bit brightness LED.

Important APIs/types/functions: `struct dac124s085_led` contains classdev, SPI device, channel id, generated name, and mutex. `dac124s085_set_brightness()` packs channel id, `REG_WRITE_UPDATE`, and 12-bit brightness into a little-endian 16-bit word and writes it over SPI. Probe allocates one `struct dac124s085` with four LEDs, sets `spi->bits_per_word = 16`, and registers four classdevs.

Control flow: probe initializes each channel name `dac124s085-N`, sets max brightness to `0xfff`, and registers classdevs, unwinding any earlier registrations on failure. Brightness callbacks serialize per channel and do a single `spi_write()`. Remove unregisters all four LEDs.

State and persistence: no cached brightness except LED core fields. DAC output state remains in hardware until rewritten, powered down externally, or device reset. Mutex scope is per LED, not global across all channels.

Dependencies/integration: SPI core, LED class, DAC124S085 command format. Device matching is by SPI modalias `"dac124s085"`.

Risks: per-channel mutexes do not serialize concurrent SPI writes across channels; SPI core serializes transfers, but shared-device timing assumptions should be verified. Endianness is explicitly little-endian in the command word. No devm classdev registration, so unregister paths matter.

Test signals: check four LEDs appear, write boundary brightness values 0/4095, verify command word channel bits, simulate register failure unwind, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-dac124s085.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-el15203000.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-el15203000.c

Purpose: SPI LED driver for Crane EL15203000 MCU boards controlling screen, pipe, and vending-area lights, including hardware pattern modes.

Important APIs/types/functions: `struct el15203000` owns SPI device, mutex, pacing deadline, and child LED array. `el15203000_cmd()` sends two one-byte SPI writes, LED id then command, with firmware-mandated delays. `el15203000_set_blocking()` maps binary brightness to ON/OFF commands. `el15203000_pattern_set_S()` accepts screen breathing pattern. `el15203000_pattern_set_P()`, `is_cascade()`, and `is_bounce()` validate pipe patterns and map them to MCU commands.

Control flow: probe counts DT children, allocates flexible array, initializes delay, stores drvdata, and registers each child from `reg`. Child id `'S'` gets breathing pattern callbacks; `'P'` gets cascade/bounce callbacks; others are simple on/off LEDs. Pattern clear sends OFF.

State and persistence: no brightness cache; hardware MCU owns active modes. `delay` is volatile pacing state and the mutex serializes all SPI command bytes. Device-managed registration handles classdev cleanup; remove destroys the mutex.

Dependencies/integration: SPI core, firmware-node child registration, LED pattern API, jiffies/usecs timing, and Crane board command vocabulary.

Risks: pattern support accepts only exact timing/brightness arrays, so generic LED pattern users may receive `-EINVAL`. Firmware requires 20 ms per byte; timing changes risk missed commands. `reg` values above `U8_MAX` are rejected but unknown characters still register without pattern support.

Test signals: verify exact accepted patterns for screen breathing and pipe cascade/inverse/bounce, invalid repeat handling, command byte sequencing with delays, child registration by `reg`, and SPI error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-el15203000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-expresswire.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-expresswire.c

Purpose: shared helper library for Kinetic ExpressWire LED-control protocol used by devices such as KTD2692 and KTD2801. It exports GPIO pulse primitives rather than registering LED class devices.

Important APIs/types/functions: public namespace exports are `expresswire_power_off()`, `expresswire_enable()`, and `expresswire_write_u8()`. Internal helpers `expresswire_start()`, `expresswire_end()`, and `expresswire_set_bit()` generate timing-specific GPIO pulses from `struct expresswire_common_props`.

Control flow: power-off drives the control GPIO low with a sleepable setter and waits `poweroff_us`. Enable disables local IRQs, emits the ExpressWire detect sequence using non-sleeping GPIO writes and `udelay()`, then restores IRQs. `write_u8()` similarly masks local IRQs, emits start timing, shifts bits MSB first using short/long low-high pulses, then emits end timing.

State and persistence: no internal state. The caller owns the GPIO descriptor and timing table. Hardware state persists in the target ExpressWire IC after commands.

Dependencies/integration: depends on GPIO descriptor API, delay APIs, local IRQ masking, and exported symbol namespace `"EXPRESSWIRE"`. Callers must ensure `ctrl_gpio` is usable with non-sleeping `gpiod_set_value()` during timing-critical sections.

Risks: IRQ-off sections protect pulse timing but can add latency if timings are long. Passing a sleep-capable GPIO to enable/write paths is unsafe. Timing data must match the target IC. There is no locking; callers must serialize accesses.

Test signals: scope GPIO waveforms for enable and byte writes, validate MSB-first bit order, ensure namespace exports resolve for dependent drivers, and test power-off with sleepable GPIOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-expresswire.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-gpio-register.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-gpio-register.c

Purpose: early-init helper for board files to register a `"leds-gpio"` platform device while keeping original platform data in init memory.

Important APIs/types/functions: `gpio_led_register_device()` copies `struct gpio_led_platform_data`, duplicates its `leds` array with `kmemdup()`, and calls `platform_device_register_resndata()` using the copied platform data.

Control flow: the helper rejects zero LEDs, duplicates the LED descriptors, registers a new platform device named `"leds-gpio"` with caller-provided id, and frees the duplicated LED array if device registration fails. On success, ownership is transferred to platform-device resources.

State and persistence: no module-level state. The created platform device persists until platform-device teardown. The copied platform data avoids references to discarded `__init` memory.

Dependencies/integration: integrates legacy board code with the generic GPIO LED driver in `leds-gpio.c`. Uses platform-device resource-data registration and GPIO LED platform-data definitions.

Risks: only the `leds` array is deep-copied; any strings or nested pointers inside LED descriptors must remain valid. Invalid `num_leds` returns `-EINVAL`. This is an `__init` helper, so it is for boot-time board setup rather than hotplug.

Test signals: call from board init with valid/empty data, confirm platform device binds to `leds-gpio`, verify copied array survives after init memory discard, and test registration failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-gpio-register.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-gpio.c

Purpose: generic GPIO-backed LED provider supporting firmware-node children and legacy platform data, including optional platform hardware blink callbacks.

Important APIs/types/functions: `struct gpio_led_data` stores classdev, GPIO descriptor, sleep capability, blink state, and optional blink function. `create_gpio_led()` configures LED metadata, default state, flags, GPIO direction, classdev registration, and per-LED pinctrl. `gpio_leds_create()` parses DT/ACPI child nodes. `gpio_led_get_gpiod()` handles platform-data descriptor, lookup, and legacy GPIO-number paths. `gpio_led_shutdown()` turns off LEDs unless retain-at-shutdown is set.

Control flow: probe chooses platform-data flow when `pdata->num_leds` exists; otherwise it parses child nodes. Brightness callbacks use atomic or sleepable GPIO setters based on `gpiod_cansleep()`. If hardware blink is active, the next brightness set first cancels blinking through the platform callback.

State and persistence: state is GPIO output level and `blinking` flag. Default state can be ON, OFF, or KEEP. LED core flags drive suspend/resume, panic indicator, and shutdown retention. Devm registration and GPIO acquisition manage lifetime.

Dependencies/integration: GPIO descriptor and legacy GPIO APIs, property/fwnode APIs, pinctrl default selection, LED class, OF compatible `"gpio-leds"`, optional board `gpio_blink_set`.

Risks: platform-data errors for one LED can abort the entire probe, while unavailable legacy GPIOs are skipped. Hardware blink semantics depend on board callback. Default state KEEP requires readable GPIO state. Shutdown unconditionally calls `gpio_led_set()` for non-retained LEDs.

Test signals: DT and platform-data probing, active-low handling, sleepable vs non-sleepable GPIO paths, default-state keep/on/off, blink cancellation, pinctrl warnings, panic/suspend/shutdown flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-hp6xx.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-hp6xx.c

Purpose: board-specific LED driver for HP Jornada 6xx handhelds, exposing fixed red and green LEDs through direct SuperH/HD64461 I/O register operations.

Important APIs/types/functions: `hp6xxled_green_set()` reads/writes `PKDR` and toggles `PKDR_LED_GREEN`; `hp6xxled_red_set()` reads/writes `HD64461_GPBDR` and toggles `HD64461_GPBDR_LED_RED`. Two static `led_classdev`s define names, default triggers, brightness callbacks, and suspend/resume behavior.

Control flow: platform probe registers red then green classdevs with devm. Brightness callbacks perform read-modify-write on board registers; a nonzero value clears the active-low LED bit, and zero sets it.

State and persistence: no allocated driver state. Hardware register bits persist until another board component changes them or the system resets. LED core suspend/resume flag requests core handling around power transitions.

Dependencies/integration: architecture headers `<asm/hd64461.h>` and `<mach/hp6xx.h>`, platform device `"hp6xx-led"`, LED triggers `"hp6xx-charge"` and `"disk-activity"`.

Risks: direct I/O has no local locking, so concurrent register users could race read-modify-write operations. Static classdev instances mean this is intended for one board instance. Active-low semantics are embedded in callbacks.

Test signals: verify red/green registration, active-low bit behavior on real or emulated HP6xx hardware, default trigger binding, and suspend/resume LED core behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-hp6xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-ip30.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-ip30.c

Purpose: SGI Octane IP30 LED driver exposing system and fault LEDs mapped as platform MMIO resources.

Important APIs/types/functions: `struct ip30_led` holds classdev and `__iomem` register pointer. `ip30led_set()` writes the brightness value directly to the mapped register. `ip30led_create()` allocates one LED, maps resource index 0 or 1, assigns fixed name, initializes brightness from `readl()`, and registers the classdev.

Control flow: probe creates the system LED then fault LED. Resource index 0 is named `white:power`; index 1 is `red:fault`. Brightness max is 1 and writes are direct `writel(value, reg)` operations.

State and persistence: per-LED state is the mapped register. Initial LED core brightness reflects hardware at probe. Register values persist in platform hardware until overwritten.

Dependencies/integration: platform resources, `devm_platform_ioremap_resource()`, MMIO accessors, platform device `"ip30-leds"`, LED class.

Risks: resource order is ABI-critical. Direct MMIO writes have no masking, so each resource must be a dedicated LED register. Static names are not firmware-configurable. There is no shutdown callback.

Test signals: validate both resources map, initial brightness mirrors `readl()`, writes 0/1 drive expected LEDs, invalid resource index path is unreachable except direct helper misuse, and devm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-ip30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-ipaq-micro.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-ipaq-micro.c

Purpose: notification LED subdevice driver for iPAQ h3xxx Atmel micro companion MFD.

Important APIs/types/functions: `micro_leds_brightness_set()` and `micro_leds_blink_set()` construct `struct ipaq_micro_msg` with `MSG_NOTIFY_LED` and four command bytes. A single static `led_classdev micro_led` provides blocking brightness, hardware blink, and suspend/resume flag.

Control flow: probe registers the static LED classdev. Brightness ON sends green LED on-time 0 and off-time 1 decisecond; OFF sends on-time 1 and off-time 0, reflecting firmware special meaning of zero as 256 deciseconds. Blink validates max 25.6 s delays, supplies 100/100 ms default when both are zero, rounds ms to deciseconds, and transmits synchronously.

State and persistence: no private driver allocation. Firmware stores notification timing after each sync message. LED core tracks requested values.

Dependencies/integration: iPAQ micro MFD parent data is reached via `led_cdev->dev->parent->parent`, and messages go through `ipaq_micro_tx_msg_sync()`.

Risks: the parent-pointer chain is fragile if device hierarchy changes. Only green LED is controlled; yellow behavior is documented but not exposed. Delay conversion can round small nonzero values to zero, which firmware treats specially.

Test signals: verify MFD parent lookup, ON/OFF command bytes, blink default and max validation, decisecond rounding, and synchronous error propagation from `ipaq_micro_tx_msg_sync()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-ipaq-micro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-is31fl319x.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-is31fl319x.c

Purpose: I2C/regmap LED driver for ISSI/Si-En IS31FL3190/3191/3193/3196/3199 light-effect controllers with 1, 3, 6, or 9 channels.

Important APIs/types/functions: `struct is31fl319x_chipdef` captures channel count, reset register, regmap config, current limits, and brightness callback. `is31fl3190_brightness_set()` and `is31fl3196_brightness_set()` write PWM registers, read cached PWM values to compute enabled channel bits, apply data-update registers, and enter/leave shutdown. `is31fl319x_parse_fw()` parses shutdown GPIO, child `reg`, labels/triggers, `led-max-microamp`, and optional audio gain.

Control flow: probe checks I2C functionality, initializes mutex, parses firmware, toggles optional shutdown GPIO, initializes regmap with unreadable-register cache, writes reset as a chip presence test, aggregates the minimum configured LED current for global current setting, then registers configured channels.

State and persistence: regmap is intentionally used as a write cache because hardware reads can hang. Configured child slots, max current, audio gain, and cached PWM values are software state; hardware shutdown and PWM registers hold runtime state.

Dependencies/integration: I2C, regmap flat cache, GPIO descriptor, firmware-node properties, OF compatible match data, LED class.

Risks: because hardware registers are not readable, cache correctness is essential for enable-bit computation. Per-LED current properties are collapsed to a global minimum, which may surprise board authors. Duplicate or out-of-range child `reg` values abort probe.

Test signals: check all compatible chipdefs, cache-based enable-bit updates, shutdown GPIO sequencing, current conversion for 3190 vs 3196 families, duplicate child rejection, and no hardware reads after initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-is31fl319x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-is31fl32xx.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-is31fl32xx.c

Purpose: I2C LED controller driver for ISSI/Si-En IS31FL32xx families, including 16/18/28/36-channel 8-bit devices and IS31FL3293 12-bit RGB device.

Important APIs/types/functions: `struct is31fl32xx_chipdef` defines channel count, optional registers, PWM layout, brightness steps, reset and shutdown callbacks. `is31fl32xx_brightness_set()` writes one or two PWM registers and pokes the update register. `is31fl3216_reset()` and `is31fl3293_reset()` handle chips without generic reset registers. `is31fl32xx_parse_dt()` registers LEDs from child nodes and detects channel conflicts.

Control flow: probe obtains chipdef from OF match, counts available child nodes, allocates flexible private data, parses children, registers classdevs with fwnode naming, then initializes/reset registers, enables channel-control bits, exits software shutdown, and applies optional global control.

State and persistence: private data stores immutable chipdef, client, and LED channel list. Hardware PWM and enable registers hold runtime state. Remove resets registers to a known state but does not maintain software brightness cache.

Dependencies/integration: I2C SMBus byte-data writes, OF child nodes, LED class extended registration, chip-specific current/reset macros from headers.

Risks: no mutex is used by design; correctness depends on independent writes and I2C bus serialization. `is31fl3293_reset()` uses max rather than min for `max_microamp`, which merits scrutiny against hardware limits. Some chipdefs rely on default-initialized fields, so missing `brightness_steps` would break brightness registration.

Test signals: exercise 256-step and 4096-step brightness writes, reversed PWM registers on IS31FL3216, reset/shutdown callbacks, `issi,22khz-pwm`, duplicate channel rejection, and remove-time reset error logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-is31fl32xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lm3530.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lm3530.c

Purpose: legacy I2C LED/backlight driver for LM3530 with manual, ALS, and PWM operating modes supplied through platform data.

Important APIs/types/functions: `struct lm3530_data` stores classdev, I2C client, platform data, current mode, regulator, brightness, and enable state. `lm3530_init_registers()` builds the full register initialization image, including ALS zone boundaries and ramp settings. `lm3530_brightness_set()` handles manual/PWM brightness. `mode_show/store` expose a sysfs mode switch.

Control flow: probe requires platform data and I2C functionality, gets `vin`, optionally initializes registers if `brt_val` is nonzero, and registers `lcd-backlight`. Manual brightness lazily initializes registers and disables regulator at zero. ALS brightness requests are ignored because hardware controls brightness. PWM mode calls the platform PWM intensity hook.

State and persistence: software caches mode, last brightness, and regulator enable state. Hardware configuration is rewritten on mode changes. Platform data values may be normalized in ALS configuration.

Dependencies/integration: platform data header `led-lm3530.h`, regulator framework, optional PWM callback, sysfs LED groups, I2C SMBus writes.

Risks: no locking around sysfs mode changes and brightness callbacks. Platform data is mandatory. ALS configuration mutates platform data fields. PWM mode depends entirely on board callback behavior.

Test signals: manual ON/OFF regulator sequencing, mode sysfs parsing for `man/als/pwm`, ALS zone calculations, PWM callback invocation, I2C failure handling during register initialization, and remove-time regulator disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lm3530.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lm3532.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lm3532.c

Purpose: DT/regmap backlight LED driver for TI LM3532 with up to three control banks, optional ALS control, enable GPIO, regulator, ramp settings, and LED-string assignment.

Important APIs/types/functions: `struct lm3532_data` owns GPIO, regulator, regmap, mutex, ALS data, ramp config, and flexible LED array. `struct lm3532_led` describes one control bank. `lm3532_brightness_set()` enables/disables a bank and writes zone target brightness. `lm3532_init_registers()` maps LED strings, writes mode/full-scale current/ramp registers. `lm3532_parse_node()` parses child fwnodes.

Control flow: probe counts child LEDs, initializes regmap and mutex, then parses top-level enable/regulator/ramp properties and each child `reg`, `ti,led-mode`, current, and `led-sources`. ALS children trigger top-level ALS parsing and hardware zone configuration. Each child is registered and then initialized.

State and persistence: enabled flag is per bank; mutex protects register transitions. Regmap cache holds defaults. Hardware retains output mapping, ramp, ALS, and brightness registers until reset.

Dependencies/integration: I2C regmap, GPIO descriptor, regulator, firmware-node child properties, LED class extended registration, ALS-related DT properties.

Risks: regulator is optional but `lm3532_led_enable()` unconditionally calls `regulator_enable()`, so missing regulator can lead to NULL dereference if a bank is enabled. Some invalid child configurations `continue` rather than fail, leaving index handling subtle. ALS parsing can allocate only one shared ALS data instance.

Test signals: child parsing for all control banks, regulator-present/absent behavior, ALS mode configuration, ramp index rounding, LED string output config masks, brightness OFF/ON transitions, and error paths during per-child registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lm3532.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lm3533.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lm3533.c

Purpose: LM3533 MFD child LED driver for low-voltage control banks, with brightness, hardware blink pattern generator, ALS controls, PWM/current setup, and sysfs attributes.

Important APIs/types/functions: `struct lm3533_led` contains parent MFD pointer, `lm3533_ctrlbank`, classdev, id, mutex, and pattern flag. `lm3533_led_set/get()` wrap ctrlbank brightness. `lm3533_led_blink_set()` maps delays to hardware pattern registers and enables pattern output. Attribute handlers expose id, rise/fall time, ALS channel/enabled, linear mapping, and PWM. Probe consumes `lm3533_led_platform_data`.

Control flow: platform probe validates parent and id, initializes ctrlbank id `pdev->id + 2`, registers LED on parent, then applies max current/PWM and enables ctrlbank. Blink requests program high/low times, clamp to supported ranges, update requested delays, then set pattern-enable bits. Shutdown disables ctrlbank and turns LED off.

State and persistence: pattern-enable state is cached in a bit flag under mutex. Brightness/PWM/current/ALS settings reside in LM3533 registers. Sysfs attributes directly read/write hardware.

Dependencies/integration: LM3533 MFD helpers `lm3533_read/write/update` and ctrlbank APIs, platform data, LED class, sysfs groups, optional parent ALS capability.

Risks: returns negative error values through `enum led_brightness` getter on read failure. Attribute visibility depends on parent `have_als`. Delay quantization is complex and hardware-limited. Manual classdev unregister is required.

Test signals: brightness and blink delay quantization, pattern enable idempotence, ALS attribute visibility, sysfs input validation, shutdown OFF behavior, and ctrlbank enable/disable errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lm3533.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lm355x.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lm355x.c

Purpose: platform-data I2C/regmap flash-lighting driver for TI LM3554 and LM3556, exposing flash, torch, and indicator LED class devices.

Important APIs/types/functions: chip-specific `lm355x_reg_data` tables encode register/mask/shift differences. `struct lm355x_chip_data` stores three classdevs, platform data, regmap, mutex, last fault flag, and register table. `lm355x_chip_init()` programs pin/pass modes. `lm355x_control()` reads fault flags, updates current registers, handles external pin modes, and writes operation mode. `pattern_store()` provides LM3556 indicator pattern sysfs.

Control flow: probe requires platform data and I2C, selects LM3554/LM3556 table from id, initializes regmap/mutex, configures pins, and registers flash, torch, then indicator. Brightness zero maps to shutdown. External torch/strobe/indicator pins cause brightness configuration without keeping I2C operation mode active.

State and persistence: last fault flag is cached for logging. Hardware registers hold current levels, pin config, operation mode, and LM3556 indicator pattern. Mutex serializes brightness calls.

Dependencies/integration: I2C regmap, platform data `leds-lm355x.h`, LED default triggers `"flash"`/`"torch"`, optional indicator sysfs group.

Risks: platform data is mandatory. There are hand-written unregister unwinds. `pattern_store()` lacks explicit mutex. External pin behavior changes the meaning of brightness requests.

Test signals: LM3554 and LM3556 register table coverage, fault flag logging, flash/torch/indicator max brightness, external pin modes, LM3556 pattern sysfs bounds, and remove shutdown write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lm355x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lm36274.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lm36274.c

Purpose: TI LM36274 backlight LED MFD child driver using the shared TI LMU brightness helper.

Important APIs/types/functions: `struct lm36274` stores platform device, classdev, `ti_lmu_bank`, parent regmap, child LED sources, and count. `lm36274_brightness_set()` calls `ti_lmu_common_set_brightness()`. `lm36274_parse_dt()` requires exactly one child node and reads `led-sources`. `lm36274_init()` enables selected strings and the global backlight enable bit.

Control flow: probe obtains parent `struct ti_lmu`, allocates state, parses the single child and fwnode naming data, initializes enable bits, fills `ti_lmu_bank` with 11-bit brightness registers, and registers one extended LED classdev.

State and persistence: enabled LED strings and brightness registers persist in parent LMU hardware. Software state is minimal and device-managed. The child fwnode is manually put after registration or init failure.

Dependencies/integration: TI LMU MFD, regmap, `leds-ti-lmu-common.h`, firmware-node LED naming, OF compatible `"ti,lm36274-backlight"`.

Risks: exactly one child is required; multiple logical banks are not supported. `led-sources` count is not explicitly bounded against `LM36274_MAX_STRINGS` before array read. No remove/shutdown disables backlight explicitly.

Test signals: single-child validation, `led-sources` parsing and enable mask, 11-bit brightness writes through common helper, fwnode reference release, and parent regmap error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lm36274.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lm3642.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lm3642.c

Purpose: platform-data I2C/regmap driver for TI LM3642 flash LED, exposing flash, torch, and indicator class devices plus sysfs control for external torch/strobe pins.

Important APIs/types/functions: `struct lm3642_chip_data` stores three classdevs, brightness caches, pin-enable settings, platform data, regmap, mutex, and last fault. `lm3642_chip_init()` writes initial TX pin enable. `lm3642_control()` reads fault flags, writes current bits, composes mode and external pin bits, and updates `REG_ENABLE`. Brightness callbacks use `guard(mutex)`. `torch_pin_store()` and `strobe_pin_store()` update pin bits.

Control flow: probe requires platform data and I2C, initializes regmap/mutex, copies pin settings, configures chip, registers flash with `strobe_pin` group, torch with `torch_pin` group, and indicator. Remove unregisters all and writes `REG_ENABLE = 0`.

State and persistence: software caches requested brightness and pin flags; hardware stores current, mode, and pin control. Fault register is read on every control call and logged.

Dependencies/integration: platform data `leds-lm3642.h`, I2C regmap, LED class default triggers, cleanup guard mutex helpers.

Risks: platform data is mandatory. Sysfs `torch_pin_store()` and `strobe_pin_store()` use `container_of(..., cdev_indicator)` even when attributes are attached to torch/flash classdevs, which is a suspicious container mismatch. External pin state can alter mode semantics.

Test signals: flash/torch/indicator brightness, pin sysfs writes and container correctness, fault logging, registration unwind paths, and remove-time disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lm3642.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lm3692x.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lm3692x.c

Purpose: TI LM36922/LM36923 I2C backlight driver supporting one LED class device, optional enable GPIO/regulator, boost configuration, fault checking, and selectable LED string sync.

Important APIs/types/functions: `struct lm3692x_led` stores mutex, client, classdev, regmap, enable GPIO, regulator, selected LED enable, model id, cached boost/brightness config, and enabled flag. `lm3692x_leds_enable()` powers supplies, clears faults, writes initialization sequence, and enables selected strings. `lm3692x_brightness_set()` disables on zero or writes 11-bit brightness split across MSB/LSB registers. `lm3692x_probe_dt()` parses OVP, child `reg`, and `led-max-microamp`.

Control flow: probe allocates state, initializes regmap, registers the LED from the first child, then enables hardware immediately. Brightness ON calls enable if needed, checks faults, writes brightness registers; OFF disables device bit, GPIO, and regulator.

State and persistence: enabled state is cached under mutex. Boost control and selected LED string are parsed once. Hardware initialization is repeated on re-enable after complete OFF.

Dependencies/integration: I2C regmap with maple cache, GPIO, optional regulator `vled`, fwnode child properties, OF and I2C ids distinguishing LM36922/LM36923.

Risks: `lm3692x_brightness_set()` ignores the return value of `lm3692x_leds_enable()` before continuing. Fault check reads twice but ignores second read errors. Probe only consumes the first child node. Max-brightness formula needs boundary validation for low currents.

Test signals: LM36922 vs LM36923 LED3 selection, OVP property values, regulator/GPIO sequencing, fault flag clear/read behavior, brightness split writes, and ignored enable-error path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lm3692x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lm3697.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lm3697.c

Purpose: TI LM3697 I2C backlight driver with up to two control banks, shared LED string output configuration, optional GPIO/regulator, and TI LMU common brightness/ramp helpers.

Important APIs/types/functions: `struct lm3697` owns regmap, mutex, GPIO/regulator, bank config, and flexible bank array. `struct lm3697_led` stores LED strings, classdev, `ti_lmu_bank`, control bank, enabled brightness, and count. `lm3697_brightness_set()` writes brightness via common helper and toggles bank enable bits. `lm3697_probe_dt()` parses children, brightness resolution, `led-sources`, ramp params, and output config bits. `lm3697_init()` resets/enables hardware and writes ramp settings.

Control flow: probe validates one or two child nodes, allocates state, initializes regmap, parses DT, then initializes hardware. Each child maps `reg` 0/1 to control bank A/B, registers a classdev, and accumulates output routing in `bank_cfg`.

State and persistence: per-bank `enabled` caches nonzero state. Hardware stores output config, ramp, brightness, and enable bits. Remove disables both banks, lowers GPIO, disables regulator if present, and destroys mutex.

Dependencies/integration: I2C regmap, LED class, fwnode properties, regulator/GPIO, `leds-ti-lmu-common.h`.

Risks: regulator is acquired but never enabled in probe/init, yet remove attempts to disable it if present. Output config bit construction depends on `led-sources` values. Duplicate control banks are not explicitly rejected.

Test signals: one/two-bank DTs, LED source routing, brightness resolution and ramp parsing, enable/disable register masks, regulator behavior, duplicate bank handling, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lm3697.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-locomo.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-locomo.c

Purpose: Locomo companion-chip LED driver for older Sharp/Zaurus-style platforms, exposing fixed amber charge and green mail LEDs.

Important APIs/types/functions: `locomoled_brightness_set()` writes `LOCOMO_LPT_TOFH` or `LOCOMO_LPT_TOFL` to one Locomo LED pulse/toggle register offset under local IRQ masking. Wrapper callbacks bind offsets `LOCOMO_LPT0` and `LOCOMO_LPT1`. A `locomo_driver` registers against `LOCOMO_DEVID_LED`.

Control flow: module init registers the Locomo driver. Probe registers two static LED classdevs with devm. Brightness nonzero writes the high command; zero writes the low command.

State and persistence: no private allocation; classdevs are static. Hardware Locomo registers hold output state. Local IRQ masking protects the small MMIO sequence from interruption on the local CPU.

Dependencies/integration: Locomo bus/device model, architecture Locomo accessors, LED triggers `"main-battery-charging"` and `"nand-disk"`.

Risks: static classdevs imply a single Locomo LED device. There is no module exit/unregister in this file, consistent with older bus code but relevant for unloadability. No locking beyond local IRQ masking.

Test signals: Locomo device binding, amber/green classdev registration, MMIO offsets and values for ON/OFF, default trigger attachment, and module init behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-locomo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp3944.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lp3944.c

Purpose: I2C driver for LP3944 funlight chip, exposing selected outputs as LED class devices with on/off and shared hardware blink support.

Important APIs/types/functions: `struct lp3944_data` holds mutex and eight LED slots. `lp3944_dim_set_period()` and `lp3944_dim_set_dutycycle()` program DIM prescaler/PWM. `lp3944_led_set()` read-modify-writes selector registers `LS0/LS1` with optional inversion. `lp3944_led_set_blink()` maps delay_on/off to DIM0 period/duty. `lp3944_configure()` consumes platform LED descriptors.

Control flow: probe requires platform data and SMBus byte-data support, allocates private data, initializes mutex, and registers configured LED or inverted LED outputs. Default status is written to hardware after registration. Remove unregisters all configured LEDs.

State and persistence: software stores id/type/client per LED. Hardware selector and DIM registers store output/blink state. DIM0 is shared by all blinking LEDs, so a new blink request changes the pattern for every LED using DIM0.

Dependencies/integration: platform data `leds-lp3944.h`, I2C SMBus byte data, LED blink API, mutex for selector RMW.

Risks: blink always uses DIM0, limiting independent blink patterns. `lp3944_led_set()` does not check read error before using `val`. Strings in platform data must remain valid. Manual unregister unwind is complex.

Test signals: normal and inverted LEDs, LS0/LS1 bit placement, blink period/duty conversion and max validation, shared DIM0 behavior, platform-data error paths, and removal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp3944.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp3952.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lp3952.c

Purpose: TI LP3952 I2C RGB LED-array driver using regmap, ACPI/device properties for LED labels, reset GPIO, and fixed pattern-generator initialization.

Important APIs/types/functions: `lp3952_register_write()` wraps regmap writes with logging. `lp3952_on_off()` updates LED enable bits. `lp3952_set_brightness()` uses four-level current control plus on/off. `lp3952_register_led_classdev()` registers named LEDs only for labels found in device properties. `lp3952_set_pattern_gen_cmd()` writes packed pattern-generator commands. `lp3952_configure()` disables LEDs and initializes pattern/active mode.

Control flow: probe allocates private state, asserts `nrst` GPIO high with a devm action to drive it low on cleanup, initializes regmap, configures the chip, then registers available LED classdevs from labels `blue2`, `green2`, `red2`, `blue1`, `green1`, `red1`.

State and persistence: per-channel classdev state is in `lp3952_led_array`; hardware stores active mode, enable bits, current levels, and pattern generator command.

Dependencies/integration: LP3952 platform header for register and enum definitions, I2C regmap, GPIO descriptor, device properties/ACPI labels, LED class.

Risks: no remove callback beyond devm cleanup; LED outputs are not explicitly disabled except reset GPIO action. Brightness only supports 0-4. Registration returns `-ENODEV` if no labels are found. Pattern generator setup is fixed and not exposed.

Test signals: reset GPIO lifecycle, property-label based registration, brightness value mapping and channel validation, all-labels-missing behavior, and regmap write failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp3952.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp50xx.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lp50xx.c

Purpose: TI LP5009/5012/5018/5024/5030/5036 I2C multicolor LED driver for RGB modules, supporting individual modules and banked groups.

Important APIs/types/functions: `struct lp50xx_chip_info` abstracts model register layout and module counts. `struct lp50xx_led` wraps `led_classdev_mc` plus bank/number metadata. `lp50xx_brightness_set()` writes per-module or bank brightness and per-color intensity registers. `lp50xx_set_banks()` enables bank control bits. `lp50xx_enable/disable()` handle optional enable GPIO, reset, and chip enable. `lp50xx_probe_dt()` parses multicolor child nodes.

Control flow: probe counts child nodes, allocates state, gets chip info from match data, initializes regmap, enables chip, then for each child parses `reg` count. Multiple `reg` values create a banked LED; one creates an individual module. Grandchildren define RGB color indices and module subregister positions. Each child registers a multicolor classdev.

State and persistence: private state stores chip info and child descriptors; hardware registers store bank config, brightness, and color mix. Mutex serializes brightness writes. Remove disables chip and optional regulator.

Dependencies/integration: I2C regmap, LED multicolor framework, GPIO/regulator, fwnode child/grandchild properties, OF/I2C model tables.

Risks: regulator is acquired after chip enable and never enabled, but remove may disable it. `led_number > num_leds` likely should be `>=` for zero-based modules. Bank setting is global and cumulative; duplicate banks are not rejected. Color grandchildren count is not required to be three.

Test signals: all model register layouts, banked and individual DTs, multicolor intensity writes, enable GPIO timing, reset and disable paths, invalid reg/color child cases, and regulator behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp50xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp5521.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lp5521.c

Purpose: LP5521 three-channel LED engine driver implemented as a chip-specific configuration for the shared LP55xx common framework.

Important APIs/types/functions: `lp5521_cfg` supplies register addresses, reset/enable values, max channels, brightness/current callbacks, firmware callback, run-engine callback, and sysfs group to `lp55xx_probe()`. `lp5521_post_init_device()` verifies reset state, writes direct-control mode, configures clock/charge pump, clears PWM, and enables run-program state. `lp5521_run_engine()` starts/stops LP55xx engines. `lp5521_selftest()` checks external clock status.

Control flow: I2C probe is delegated to `lp55xx_probe` using match/id `driver_data`. Common code handles LED parsing/registration. Post-init is called by common code after reset. Engine sysfs attributes expose engine mode/load, and firmware loading uses the common callback.

State and persistence: common LP55xx structures own channel state, firmware, lock, and platform data. This file defines chip-specific hardware register state and timing waits. Hardware program memory and PWM registers persist until reset or overwritten.

Dependencies/integration: `leds-lp55xx-common.h`, firmware loader, LP55xx platform data/OF, I2C, sysfs attributes, mutex guard in selftest.

Risks: reset verification depends on reading default R current register. External clock selftest only fails when ext clock was requested. Engine timing waits are required after mode/enable writes.

Test signals: common probe with three channels, post-init default register read, internal/external clock config, engine mode/load sysfs, firmware load/run/stop, and selftest output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp5521.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp5523.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lp5523.c

Purpose: LP5523/LP55231 nine-channel LED engine driver built on the LP55xx common framework, adding program-engine initialization, master fader controls, and LED selftest.

Important APIs/types/functions: `lp5523_cfg` defines register map hooks for common code, including engine busy, program memory, PWM/current bases, master fader, and LED control base. `lp5523_post_init_device()` enables chip, configures charge pump/clock, enables all LEDs, and calls `lp5523_init_program_engine()`. `lp5523_init_program_engine()` writes engine start addresses and MUX helper programs. `lp5523_selftest()` measures VDD and channel ADC values.

Control flow: common `lp55xx_probe` handles device/LED setup. Post-init writes configuration and validates engine status after running temporary programs. Engine sysfs attributes expose mode, load, LED mux, master faders, and selftest. `lp5523_run_engine()` stops engines and turns off channels or starts via common code.

State and persistence: common framework holds locks, channel/current state, firmware, and engine index. Hardware stores program pages, LED mux pages, master fader values, PWM/current, and ADC test state.

Dependencies/integration: LP55xx common framework, firmware loading, I2C, platform data/OF, sysfs, ADC LED-test hardware.

Risks: selftest loop uses `led->chan_nr` while iterating platform channels and increments `led`, so channel/config alignment is critical. Engine initialization returns `-1` instead of a conventional errno on status mismatch. Timing sleeps are hardware-sensitive.

Test signals: post-init engine status mask, engine LED mux sysfs, master fader attributes, external clock selftest, ADC short/open detection thresholds, firmware load/run/stop, and remove through common code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp5523.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp5562.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lp5562.c

Purpose: LP5562 four-channel RGBW LED engine driver using LP55xx common framework with chip-specific RGB/W engine muxing and predefined pattern support.

Important APIs/types/functions: `lp5562_cfg` provides LP55xx common register hooks and chip callbacks. `lp5562_post_init_device()` sets direct mode, clock config, clears PWM, and maps LEDs to register PWM. `lp5562_led_brightness()` and `lp5562_multicolor_brightness()` write channel PWM registers. `lp5562_run_predef_led_pattern()` loads predefined RGB programs and runs engines. Sysfs stores `led_pattern` and `engine_mux`.

Control flow: common `lp55xx_probe` performs device setup. Brightness uses direct PWM registers under the common lock. Pattern sysfs mode 0 stops engines; nonzero modes load common platform pattern arrays into three engine memories, map RGB to engines, and start engines. `engine_mux` maps RGB fixed engines or W to the currently selected engine.

State and persistence: common LP55xx chip state stores engine index, lock, LED/current data, and platform patterns. Hardware stores program memory, engine selection, PWM/current, and enable/opmode.

Dependencies/integration: LP55xx common framework, firmware/platform predefined patterns, I2C, LED multicolor support, sysfs device attributes.

Risks: predefined pattern pointer arithmetic assumes `mode <= num_patterns` and valid pattern data; program size must be below page size. `engine_mux` for W depends on current `chip->engine_idx`, which is set by other sysfs engine controls. Pattern loading is RGB-only, with W handled separately by mux.

Test signals: RGBW brightness writes, pattern off/on modes, program-size overflow rejection, engine mux strings `RGB` and `W`, engine timing waits, firmware loading, and common remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp5562.c -->
