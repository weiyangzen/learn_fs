# subset-b-004011 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp5569.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lp5569.c

Purpose: TI LP5569 nine-channel programmable LED engine driver built on the shared LP55xx common layer. It supplies LP5569-specific register layout, startup programming, master fader attributes, mux handling, and open/short self-test behavior.

Important APIs/types/functions: `lp5569_cfg` is the `struct lp55xx_device_config` consumed by `lp55xx_probe`; `lp5569_post_init_device()` programs MISC, clock, charge pump, enable, and initial engine state; `lp5569_init_program_engine()` loads fixed per-engine mux setup programs; `lp5569_run_engine()` delegates start/stop to common helpers; `lp5569_selftest()`, `lp5569_led_open_test()`, and `lp5569_led_short_test()` expose diagnostics through sysfs. Attribute macros from `leds-lp55xx-common.h` create engine load/mode/leds and master-fader files.

Control flow: module registration binds an I2C driver to `lp55xx_probe`; the common probe allocates chip/LED state, calls LP5569 post-init, registers LEDs, then installs this driver's device attributes. Post-init writes default power/charge-pump settings, selects internal clock output when requested, waits for startup busy to clear, writes engine program start addresses, loads mux helper bytecode for engines 1-3, starts it briefly, checks engine interrupt status, then stops all engines. Brightness/current writes are handled by common LP55xx callbacks.

State and persistence: runtime state lives in `struct lp55xx_chip`, per-engine mode/mux fields, per-LED brightness/current fields, and hardware registers. Firmware patterns are loaded from sysfs or firmware request into volatile program memory. Self-test temporarily changes charge pump, PWM, current, and test bits, then restores LED current and brightness from cached LED state.

Dependencies and integration: depends on I2C SMBus, firmware loader, DT/platform data from `linux/platform_data/leds-lp55xx.h`, LED class and multicolor support, bitfield helpers, and LP55xx common exports. Device match is `ti,lp5569`; user integration is via standard LED class nodes plus engine and selftest sysfs files.

Risks: self-test and mux setup rely on exact register semantics and timing; errors during cleanup writes are ignored. The short-test enable call passes the open-test bit as mask while writing short-test value, which is a suspicious bit-mask interaction worth regression testing against hardware. Engine status validation assumes all three engine interrupt bits assert after the bootstrap program. Firmware/program memory parsing inherits common LP55xx ASCII-hex limitations.

Test signals: probe on real LP5569 with DT children, verify LED brightness/current sysfs, engine load/mode/leds programming, master fader mappings, firmware pattern execution, and `selftest` output with known good/open/shorted LED loads. I2C fault injection should cover post-init failures and cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp5569.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp55xx-common.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lp55xx-common.c

Purpose: shared implementation for TI LP55xx programmable LED controllers. It provides register helpers, engine state transitions, firmware/program memory loading, LED and multicolor class registration, sysfs engine controls, DT parsing, clock/GPIO enable handling, and common probe/remove.

Important APIs/types/functions: exports `lp55xx_probe()`, `lp55xx_remove()`, `lp55xx_write/read/update_bits()`, `lp55xx_load_engine()`, `lp55xx_run_engine_common()`, `lp55xx_update_program_memory()`, `lp55xx_firmware_loaded_cb()`, brightness/current helpers, engine sysfs helpers, and master-fader helpers. Internally, `lp55xx_init_device()`, `lp55xx_register_leds()`, `lp55xx_register_sysfs()`, and `lp55xx_of_populate_pdata()` are the main orchestration points.

Control flow: chip-specific I2C drivers pass a `struct lp55xx_device_config` through match data. Probe obtains platform data or parses DT, validates program size, allocates LED slots, initializes enable GPIO/reset/detection/post-init, registers active LED channels, applies initial currents, and creates common and chip-specific sysfs groups. Engine sysfs selects an engine, optionally requests firmware asynchronously, loads ASCII-hex bytecode into program memory, then switches LOAD engines to RUN through OP_MODE/EXEC registers.

State and persistence: state is volatile and held in `struct lp55xx_chip` (`engine_idx`, `engines[]`, firmware pointer, mutex, LED count) and `struct lp55xx_led` (`chan_nr`, current, max current, brightness, multicolor metadata). Hardware registers persist only until chip reset/power loss. Firmware bytes are released after load, not retained.

Dependencies and integration: depends on I2C SMBus, LED class, LED multicolor class, firmware loader, GPIO descriptors, optional 32 kHz clock, OF parsing, and `dt-bindings/leds/leds-lp55xx.h`. Chip drivers integrate by filling `lp55xx_device_config` register addresses, callbacks, max channels, and optional attribute groups.

Risks: sysfs paths expose mutable engine/program state, so locking correctness is critical; most operations use `chip->lock`, but asynchronous firmware load depends on `engine_idx` remaining meaningful. Program parsing accepts ASCII hex and requires even byte count; malformed input returns `-EINVAL`. Shared PWM/fader register assumptions must match each chip config. `lp55xx_unregister_sysfs()` removes the common engine group unconditionally even when it may not have been created, relying on sysfs tolerance.

Test signals: unit or hardware tests should cover DT parsing for single and RGB LEDs, current bounds, firmware load size/format failures, engine mode transitions, mux parsing, master fader read/write, enable GPIO timing, external-clock selection, and remove-time shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp55xx-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp55xx-common.h -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lp55xx-common.h

Purpose: public in-driver contract between LP55xx chip-specific drivers and the shared LP55xx implementation.

Important APIs/types/functions: defines `LP55xx_BYTES_PER_PAGE`, engine index/mode enums, sysfs attribute-generation macros, `struct lp55xx_reg`, `struct lp55xx_device_config`, `struct lp55xx_engine`, `struct lp55xx_chip`, and `struct lp55xx_led`. It declares all common register, engine, brightness, current, probe/remove, and sysfs helper exports.

Control flow: chip drivers include this header, instantiate a `lp55xx_device_config`, use macros such as `LP55XX_DEV_ATTR_ENGINE_MODE()` to generate sysfs callbacks, and pass common `lp55xx_probe`/`lp55xx_remove` as their I2C driver hooks.

State and persistence: the header defines the in-memory state model but stores no data itself. Persistent behavior is determined by chip-specific register callbacks and hardware state.

Dependencies and integration: depends on `linux/led-class-multicolor.h` and platform data types from the C file's include graph. It is tightly coupled to LED class devices, firmware-backed engine programming, I2C client ownership, and chip-specific register maps.

Risks: the config structure is a soft ABI inside the driver family; missing function pointers or wrong register shifts/masks produce runtime hardware corruption rather than compile-time errors. Attribute macros assume common helper names and engine numbering from 1 to 3.

Test signals: build all LP55xx chip drivers, validate each config initializes every required register/callback, and exercise generated sysfs attributes for all engines and master faders on chips that expose them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp55xx-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp8501.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lp8501.c

Purpose: TI LP8501 nine-channel LED controller glue driver using the LP55xx common framework.

Important APIs/types/functions: `lp8501_cfg` supplies register addresses, max channels, engine busy bit, callbacks, and one program page per engine. `lp8501_post_init_device()` enables the chip, waits for startup, configures clock/charge pump, and applies output power selection. `lp8501_run_engine()` starts common engine execution or stops all engines and clears PWM channels.

Control flow: the I2C driver matches `ti,lp8501` and delegates probe/remove to LP55xx common code. During common initialization, post-init programs LP8501-specific config registers. Runtime LED brightness, current, firmware load, and engine sysfs are handled by shared LP55xx helpers.

State and persistence: state lives in LP55xx common chip/LED objects and LP8501 registers. Program memory is volatile and limited to one page per engine. Platform/DT `pwr-sel`, charge pump, and clock mode determine startup register state.

Dependencies and integration: depends on I2C, LED class, firmware support, OF match data, `leds-lp55xx-common`, and `linux/platform_data/leds-lp55xx.h`.

Risks: wrong `pwr_sel`, charge-pump, or clock-mode data can produce unusable outputs. Engine register shifts default to zero in config, so this relies on LP8501 layout matching common bit macros. Stop uses `lp55xx_stop_all_engine()` rather than selected-engine stop, affecting all engines.

Test signals: probe with DT/platform data, verify current/PWM channels 0-8, firmware load/run/stop, output power selection bits, internal/external clock modes, and behavior when engine busy polling times out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp8501.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp8788.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lp8788.c

Purpose: keyboard backlight LED driver for the TI LP8788 MFD current-sink block.

Important APIs/types/functions: `struct lp8788_led` stores parent MFD pointer, mutex, LED class device, selected ISINK, and on/off state. `lp8788_led_init_device()` configures ISINK scale and current code; `lp8788_brightness_set()` writes PWM and toggles sink enable; `lp8788_led_probe()` registers one LED class device.

Control flow: the platform child gets the parent `struct lp8788`, selects platform data or defaults, initializes ISINK registers, then registers `keyboard-backlight` or the platform-provided name. Brightness writes update PWM for ISINK 1-3 and only change enable state when zero/nonzero state changes.

State and persistence: `led->on` caches enable state to avoid redundant writes. Brightness/current values are stored in parent hardware registers and are not persisted by this driver across MFD reset.

Dependencies and integration: depends on LP8788 MFD helpers, `lp8788-isink` register tables, platform data, LED class, and mutex serialization.

Risks: only ISINK 1-3 are accepted in brightness path; bad platform data returns `-EINVAL`. The default config mutates a static object when platform data is present, which is safe only because devices are expected to be singular or identical. No OF parsing is present in this file.

Test signals: platform probe under LP8788 MFD, PWM writes at min/max brightness, enable transition at zero/nonzero, platform current/scale overrides, and invalid ISINK configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp8788.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp8860.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lp8860.c

Purpose: TI LP8860 display-cluster/backlight LED driver using regmap, optional regulator, optional enable GPIO, fault clearing, and optional EEPROM programming.

Important APIs/types/functions: `struct lp8860_led` holds mutex, I2C client, LED class device, and regmap. `lp8860_fault_check()` reads LED and general fault registers and clears them. `lp8860_brightness_set()` scales LED class brightness into 16-bit display brightness registers. `lp8860_program_eeprom()` unlocks, writes a static EEPROM table, locks, and triggers programming when module parameter `program_eeprom` is set.

Control flow: probe requires one child LED node, enables optional `vled`, drives optional enable GPIO, creates an 8-bit regmap with an access table, optionally programs EEPROM, then registers one extended LED class device with default label `:display_cluster`. Brightness writes clear faults first, then write MSB/LSB.

State and persistence: normal brightness is volatile register state. EEPROM programming is persistent on the chip and intentionally guarded by a module parameter because endurance is limited. Faults are read and cleared opportunistically on brightness/programming operations.

Dependencies and integration: depends on I2C, regmap, regulator framework, GPIO descriptors, OF LED init data, module parameters, and LED class.

Risks: EEPROM table is hard-coded; enabling `program_eeprom` on production systems can consume EEPROM cycles or install wrong panel settings. Brightness scale uses `brt_val * 255`, producing 0..65025 instead of full 0xffff. Fault check clears faults without surfacing which fault occurred.

Test signals: probe with/without GPIO and regulator, brightness writes at 0/255, fault-clear behavior, regmap access limits, EEPROM path only in controlled hardware tests, and missing child-node failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp8860.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp8864.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lp8864.c

Purpose: TI LP8864/LP8866 display LED driver with 16-bit little-endian regmap brightness control and detailed fault reporting.

Important APIs/types/functions: `struct lp8864_led` stores I2C client, LED class device, regmap, and a mask of already reported sticky LED faults. `lp8864_fault_check()` reports and clears supply, boost, and LED status faults. `lp8864_brightness_set()` maps LED class brightness to 16-bit hardware brightness. `lp8864_brightness_get()` maps hardware value back to LED class scale.

Control flow: probe requires a child LED node, enables optional `vled`, asserts optional enable GPIO high, initializes 16-bit regmap, selects register-controlled brightness in `USER_CONFIG1`, clears/reports existing faults, then registers one extended LED class device. Every brightness set checks faults before writing `BRT_CONTROL`.

State and persistence: brightness and fault-clear state are hardware registers. `led_status_mask` suppresses repeated warnings for sticky LED status bits until power-down. GPIO cleanup disables the chip through a managed action.

Dependencies and integration: depends on I2C, regmap with 16-bit little-endian values, regulator and GPIO frameworks, OF child node naming, and LED class.

Risks: `brightness_get()` returns an enum but returns negative errors cast as brightness on read failure. Fault-clearing writes rely on paired status/clear bit layout. Only one LED class device is registered even though hardware has multiple channels.

Test signals: fault injection for supply/boost/LED status, brightness set/get scale round trips, enable GPIO cleanup on probe failure/remove, regulator optional handling, and child-node validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lp8864.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lt3593.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-lt3593.c

Purpose: GPIO pulse driver for Linear Technology LT3593 LED controllers.

Important APIs/types/functions: `struct lt3593_led_data` stores one LED class device and one control GPIO. `lt3593_led_set()` implements the controller's pulse protocol. `lt3593_led_probe()` validates exactly one LED child, obtains `lltc,ctrl` GPIO, handles `default-state`, and registers the LED.

Control flow: nonzero brightness is converted into a number of falling-edge pulses that reduce current from maximum; zero drives the GPIO low. Full brightness resets the internal level by a low-delay-high sequence. Probe sets initial LED class brightness based on firmware node state but does not explicitly pulse hardware to that state before registration.

State and persistence: current level is stored inside the LT3593 after pulse programming; the driver does not cache it except LED class brightness. Power loss or GPIO reset changes hardware state.

Dependencies and integration: depends on platform devices, firmware-node properties, GPIO descriptors that can sleep, LED class extended registration, and OF compatible `lltc,lt3593`.

Risks: pulse timing is implemented with microsecond delays and can be affected by sleepable GPIO latency. Brightness changes are relative to the chip reset protocol, so missed pulses desynchronize actual current from requested brightness.

Test signals: oscilloscope/GPIO trace for pulse counts and timing, brightness 0/1/255 behavior, default-state handling, missing/multiple child-node failures, and slow GPIO controller behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-lt3593.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-max5970.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-max5970.c

Purpose: LED driver for MAX5970/MAX5978 hot-swap controller indicator outputs.

Important APIs/types/functions: `struct max5970_led` stores parent regmap, LED class device, index, and device pointer. `max5970_led_set_brightness()` updates the LED flash register bit for one LED. `max5970_led_probe()` walks the parent `leds` firmware node and registers one binary LED per valid child `reg`.

Control flow: probe gets the parent MFD regmap and named child node, parses child `reg` and optional `label`, assigns max brightness 1 and default trigger `none`, then registers each LED. Brightness clears a bit for on and sets it for off, matching active-low hardware semantics.

State and persistence: no software cache; state is the parent regmap register. Device-managed LED registration owns cleanup.

Dependencies and integration: depends on MAX5970 MFD definitions, regmap, firmware-node child properties, and LED class.

Risks: probe returns the last registration status, initialized to `-ENODEV`, so a `leds` node with no valid children fails. Active-low semantics are easy to invert in tests or board descriptions. Invalid children are logged and skipped rather than aborting immediately.

Test signals: parent MFD probe with valid/invalid `reg`, on/off bit polarity in `MAX5970_REG_LED_FLASH`, label fallback, and absent regmap or `leds` node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-max5970.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-max77650.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-max77650.c

Purpose: LED driver for MAX77650/MAX77651 charger and power-supply PMIC LEDs.

Important APIs/types/functions: `struct max77650_led` stores LED class device, parent regmap, and two per-LED registers. `max77650_led_brightness_set()` updates brightness and enable bits in register A. `max77650_led_probe()` parses up to three child LEDs, registers them, initializes LED A/B defaults, and enables the top-level LED master bit.

Control flow: probe obtains parent regmap, validates child count and `reg`, maps each `reg` to A/B register offsets, registers with extended LED init data, writes per-channel defaults, then writes `MAX77650_REG_CNFG_LED_TOP`. Brightness zero disables the LED; nonzero writes enable bits plus 5-bit brightness.

State and persistence: state is in PMIC registers; no software brightness cache beyond LED core. Probe resets LED channel registers to defaults.

Dependencies and integration: depends on MAX77650 MFD regmap, platform-device child, firmware-node LED properties, and LED class.

Risks: duplicate child `reg` values reuse the same array slot without explicit duplicate detection. Register B is initialized but not otherwise used by brightness set. Only 5-bit brightness is exposed.

Test signals: child count validation, invalid/duplicate reg behavior, brightness 0/max register writes, top-level enable bit, and probe failure when parent regmap is missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-max77650.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-max77705.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-max77705.c

Purpose: MAX77705 PMIC RGB LED driver supporting single-color and multicolor LED class devices.

Important APIs/types/functions: `struct max77705_led` stores single and multicolor class devices, regmap, and subled metadata. `max77705_rgb_blink()` maps requested delays to hardware blink register fields. `max77705_led_brightness_set()` writes per-channel brightness and enable bits. `max77705_add_led()` parses one LED node, handling RGB child channels or single-channel LEDs.

Control flow: probe creates a regmap over the RGB LED register window on the parent I2C client, then iterates child nodes. RGB nodes allocate subled info from children and register a multicolor class device; non-RGB nodes allocate one subled and register a normal LED. Each LED is turned off after registration. Blink programming writes one global blink register shared by all channels.

State and persistence: brightness and enable are hardware register state; subled brightness is cached in `mc_subled` structures for LED-core calculations. No remove-time explicit shutdown beyond managed resources.

Dependencies and integration: depends on MAX77705 private register definitions, I2C regmap, LED multicolor class, OF/fwnode properties `color` and `reg`, and platform-device MFD binding.

Risks: `max77705_parse_subled()` rejects `reg == 0`, so channel 0 cannot be used despite `MAX77705_LED_NUM_LEDS` being 4. The enable update call appears to pass value and mask arguments in reversed order for `regmap_update_bits()`, a high-risk functional bug. Blink timing math has threshold edge cases and is global, not per LED.

Test signals: single-channel and RGB DT parsing, all channel numbers including 0, brightness register writes and LEDEN bit masks, blink delay boundary values, multicolor intensity calculations, and initial off state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-max77705.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-max8997.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-max8997.c

Purpose: LED class driver for MAX8997 flash/movie LEDs under the MAX8997 MFD.

Important APIs/types/functions: `struct max8997_led` stores parent device, LED class device, enable flag, platform ID, mode, and mutex. `max8997_led_set_mode()` programs flash/movie/pin-control mode and max brightness. `max8997_led_enable()` toggles boost. `max8997_led_set_current()` writes mode-specific current registers. `mode` sysfs attribute exposes mode selection.

Control flow: probe uses `pdev->id` as LED number, names the LED, installs brightness and mode sysfs handlers, applies platform-data mode/brightness if present, initializes mutex, and registers the LED. Brightness writes set current and boost enable for nonzero values, or current zero and boost off for zero.

State and persistence: software caches `enabled` and `led_mode`; hardware current, mode, and boost bits live in MAX8997 registers. Platform data can define initial state.

Dependencies and integration: depends on MAX8997 MFD/private register helpers, platform data, LED class, and sysfs attribute groups.

Risks: brightness callback is non-blocking but performs I2C register updates and has no mutex around brightness path, while mode sysfs uses a mutex. `name` is a stack buffer assigned to `cdev.name` before registration; LED core must copy or use it immediately, otherwise this would be unsafe. Unsupported mode leaves max brightness zero.

Test signals: mode sysfs strings, current register programming per mode and LED ID, boost enable transitions, platform-data initial mode/brightness clamping, and concurrent mode/brightness operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-max8997.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-mc13783.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-mc13783.c

Purpose: LED driver for Freescale/NXP MC13783, MC13892, and MC34708 PMIC LED controller blocks.

Important APIs/types/functions: device-type descriptors define LED ID ranges, register counts, and LEDCTRL base offsets. `mc13xxx_max_brightness()` derives per-output brightness width. `mc13xxx_led_set()` maps each logical LED ID to register and bit shift. `mc13xxx_led_probe_dt()` parses `led-control` and child LED nodes. `mc13xxx_led_probe()` initializes control registers and registers LED class devices.

Control flow: platform driver probe gets parent `mc13xxx`, selects device type from platform ID, parses DT or platform data, writes initial LED control registers, validates IDs and duplicates, then registers each LED with suspend/resume flag. Brightness writes perform register read-modify-write with masks based on maximum brightness width.

State and persistence: LED state resides in PMIC registers; driver stores LED IDs and parent pointers. Initial control register values come from board data/DT and are written on probe.

Dependencies and integration: depends on `linux/mfd/mc13xxx.h`, MC13xxx register helpers, platform IDs, optional OF parsing from parent `leds` node, and LED class.

Risks: probe cleanup uses manual unregister because registrations are not devm-managed. Duplicate or invalid IDs abort registration after warning/error. `BUG()` is used for impossible LED IDs in brightness path, so bad internal state is fatal.

Test signals: DT `led-control` array size per chip, ID mapping for all supported PMIC variants, brightness masks for 4/5/6-bit outputs, duplicate ID handling, and remove-time unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-mc13783.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-menf21bmc.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-menf21bmc.c

Purpose: LED driver for the MEN 14F021P00 board management controller, exposing four binary LEDs.

Important APIs/types/functions: static `struct menf21bmc_led leds[]` defines status, hotswap, user1, and user2 LEDs. `menf21bmc_led_set()` performs a locked read-modify-write of BMC command `0xA0`. `menf21bmc_led_probe()` registers all four LED class devices.

Control flow: platform child uses parent I2C client, assigns names and brightness callback to static LED descriptors, then registers each with devm. Brightness writes read the current LED bitfield, set or clear one bit, and write it back.

State and persistence: driver has no per-device dynamic state besides the I2C client pointer in static descriptors. Hardware BMC state persists outside the driver until changed.

Dependencies and integration: depends on platform device under an I2C-backed BMC, SMBus byte read/write, LED class, and a global mutex for register serialization.

Risks: static LED descriptors and global lock make multiple device instances unsafe. Brightness set ignores I2C write errors and cannot report failure because it uses non-blocking callback signature.

Test signals: registration of all four LEDs, bit preservation across read-modify-write, I2C read error behavior, and multiple-instance avoidance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-menf21bmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-mlxcpld.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-mlxcpld.c

Purpose: legacy Mellanox CPLD LED driver using LPC I/O port access and DMI-selected board profiles.

Important APIs/types/functions: profile arrays describe CPLD offsets, masks, base colors, defaults, and LED names. `mlxcpld_led_platform_check_sys_type()` selects default or MSN2100 profile by DMI product name. `mlxcpld_led_store_hw()` performs spinlocked nibble updates through `inb/outb`. Brightness and blink callbacks map LED class state to CPLD color codes.

Control flow: module init checks chassis vendor, creates a platform device, probes the driver once, allocates global private state, selects profile, registers each LED, and applies default-on LEDs. Blink accepts only off/on pairs for 3 Hz or 6 Hz, or defaults to 3 Hz when both delays are zero.

State and persistence: driver state is global `mlxcpld_led` plus LED profile data. Hardware state is CPLD register nibbles; no readback cache is maintained beyond register read-modify-write.

Dependencies and integration: depends on DMI, direct I/O port access, platform-device self-registration, LED class, and spinlock serialization.

Risks: global singleton design and manual platform-device lifecycle are fragile. Hard-coded LPC base and DMI profiles limit portability. `mlxcpld_led_exit()` assumes init/probe created global state. Blink only supports exact delay constants.

Test signals: DMI match and profile selection, I/O nibble polarity for high/low masks, default LED state writes, blink delay validation, and module load/unload on unsupported systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-mlxcpld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-mlxreg.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-mlxreg.c

Purpose: generic Mellanox LED driver driven by `mlxreg_core_platform_data` and a parent regmap.

Important APIs/types/functions: `struct mlxreg_led_data` binds one `mlxreg_core_data` entry to a LED class device and base color. `mlxreg_led_store_hw()` and `mlxreg_led_get_hw()` update/read masked nibbles through regmap. `mlxreg_led_config()` iterates platform entries, applies capability checks, derives color from labels, and registers LEDs.

Control flow: platform probe obtains platform data, initializes a mutex, then configures each LED. If a capability register is present and the bit is absent, that LED is skipped. Brightness writes store base color or off; blink writes base color plus 3 Hz/6 Hz offsets; get maps current code back to LED_FULL/OFF.

State and persistence: LED state is in the parent regmap; no persistent software cache beyond per-LED pointers and generated names. Capability bit mutation clears the capability byte from `data->bit` before using the remaining offset bits.

Dependencies and integration: depends on Mellanox platform data, regmap, LED class, platform bus, and label conventions containing `red`, `orange`, or `amber` to infer color.

Risks: color selection from label strings is heuristic. `mlxreg_led_get_hw()` masks with `~data->mask`, which assumes platform masks are inverse preservation masks rather than direct field masks. Shared blink limitations accept only exact 3 Hz/6 Hz or solid requests.

Test signals: platform data with capability-present/skipped LEDs, mask/bit combinations for low/high nibbles, brightness get/set round trips, blink validation, and generated LED names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-mlxreg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-mt6323.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-mt6323.c

Purpose: MediaTek MT6323/MT6331/MT6332 PMIC LED and WLED driver using parent `mt6397` regmap.

Important APIs/types/functions: hardware descriptors `mt6323_regs`, `mt6323_hwspec`, and `mt6323_data` describe register layouts and limits. `mt6323_led_set_brightness()`, `mt6323_led_set_blink()`, and `mt6323_get_led_hw_brightness()` manage ISINK LEDs. `mt6323_wled_set_brightness()` and WLED helpers manage paired WLED channels. Probe parses child `reg` and `mediatek,is-wled`.

Control flow: probe enables the common 32 kHz clock, allocates controller state, validates each child `reg`, selects normal LED or WLED callbacks, applies default-state, and registers extended LED class devices. Normal LED on enables clock source, channel clock, channel enable, brightness, full duty, and default period. Off disables channel and clock. Blink programs duty and period if within hardware limits.

State and persistence: `current_brightness` caches requested brightness, while hardware registers hold real enable, clock, duty, and brightness state. Remove turns LEDs off and disables the common clock, but iterates only contiguous `leds->led[i]` entries from zero.

Dependencies and integration: depends on MT6397/MT6323 MFD regmap, OF compatible match data, LED class, and PMIC clock/register layout.

Risks: `mt6323_led_hw_brightness()` subtracts one from brightness, so callers must avoid zero there. Remove loop can miss non-contiguous registered LED IDs. WLED brightness does not program an analog brightness register; it only toggles channel pair and cache. Blink duty math and max period vary by hardware spec.

Test signals: DT coverage for MT6323, MT6331, and MT6332; normal LED on/off/get/blink; WLED pair enable/disable; default-state `on`, `off`, and `keep`; non-contiguous `reg` remove behavior; and regmap error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-mt6323.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-net48xx.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-net48xx.c

Purpose: Soekris net48xx error LED driver using the SCx200 GPIO infrastructure.

Important APIs/types/functions: static `net48xx_error_led` exposes `net48xx::error`; `net48xx_error_led_set()` writes GPIO 20 through `scx200_gpio_ops`; module init self-registers a platform driver and platform device.

Control flow: init first checks `scx200_gpio_ops.dev`, registers the platform driver, creates a simple platform device, and probe registers one LED class device. Brightness writes directly set GPIO 20 high or low.

State and persistence: no dynamic state except the created platform device pointer. Hardware GPIO level is the only LED state.

Dependencies and integration: depends on x86 SCx200/NSC GPIO support, platform-device self-registration, LED class, and suspend/resume LED core flag.

Risks: direct dependency on global `scx200_gpio_ops` makes probe order important. No GPIO reservation is performed in this file. Unsupported systems return `-ENODEV` at module init.

Test signals: load with and without SCx200 GPIO present, LED class registration, GPIO 20 polarity, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-net48xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-netxbig.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-netxbig.c

Purpose: LaCie 2Big/5Big Network series LED driver using a GPIO extension latch with LED mode, brightness, timer, and SATA-activity modes.

Important APIs/types/functions: `struct netxbig_gpio_ext` models address/data/enable GPIO latch lines. `netxbig_led_data` stores LED class state, mode values, timer table, SATA flag, and lock. `gpio_ext_set_value()` writes latch address/data under a global spinlock. `netxbig_led_set()`, `netxbig_led_blink_set()`, and `sata` sysfs handlers control modes.

Control flow: probe parses a `gpio-ext` phandle, obtains unmanaged GPIO descriptors from that device with managed cleanup, parses optional `timers`, parses per-LED mode/brightness addresses and mode-value pairs, allocates runtime LED data, and registers each LED. Brightness chooses OFF, SATA, ON, or existing timer mode and writes mode and brightness latch registers.

State and persistence: per-LED software state tracks current mode and SATA flag because the GPIO extension bus cannot read back registers. Initial hardware state is intentionally not reprogrammed, so sysfs brightness/SATA may not match bootloader state until first write.

Dependencies and integration: depends on OF phandles, platform device lookup, GPIO descriptors from a sibling device, LED class, spinlocks, and board-specific mode tables.

Risks: shared brightness register for SATA LEDs means one LED brightness write affects others. GPIO descriptors are intentionally not devm-owned by their original device, so cleanup correctness is important. Mode tables can omit modes; missing SATA or blink modes return `-EINVAL`.

Test signals: DT parser validation for `gpio-ext`, `timers`, and `mode-val`; latch GPIO sequencing; SATA sysfs mode transitions; unsupported blink period rejection; shared brightness behavior; and cleanup of externally acquired GPIOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-netxbig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-nic78bx.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-nic78bx.c

Purpose: National Instruments PXI user LED driver for ACPI device `NIC78B3`.

Important APIs/types/functions: static `nic78bx_leds[]` defines green/yellow LEDs for user1/user2 with bit and mask fields. `nic78bx_brightness_set()` and `nic78bx_brightness_get()` access I/O ports under a spinlock. `lock_led_reg_action()` relocks the LED register on managed cleanup.

Control flow: probe validates I/O resource size, requests the region, records base port, installs cleanup action, registers four LEDs, then unlocks the LED register. Setting a color clears the whole user LED color mask then sets the chosen bit, making green/yellow mutually exclusive per user LED.

State and persistence: no cache; state is read from I/O port. Register lock state is restored on device cleanup.

Dependencies and integration: depends on ACPI matching, I/O port resources, `inb/outb`, LED class, spinlocks, and devm cleanup.

Risks: cleanup action is registered before the unlock write, so failures after action registration relock as intended. Hardware access assumes the platform resource points to a two-byte lock/data region. Only one color per user LED can be active due to mask clearing.

Test signals: ACPI enumeration, I/O resource validation, register unlock/lock sequence, four LED get/set callbacks, and mutual exclusion of green/yellow bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-nic78bx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-ns2.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-ns2.c

Purpose: LaCie Network Space v2 dual-GPIO LED mode driver with optional SATA activity mode.

Important APIs/types/functions: `struct ns2_led_modval` maps mode to command/slow GPIO levels. `struct ns2_led` stores LED class device, GPIOs, mode map, SATA flag, sleep capability, and rwlock. `ns2_led_get_mode()`, `ns2_led_set_mode()`, brightness callbacks, and `sata` sysfs handlers implement mode control.

Control flow: probe allocates one `ns2_led` per child. Registration obtains `cmd` and `slow` GPIOs, parses `modes-map` triples, picks blocking or atomic brightness callback based on `gpiod_cansleep`, reads current GPIO state to infer initial mode, then registers the LED with a `sata` attribute. Brightness selects OFF, ON, or SATA based on value and SATA flag.

State and persistence: `sata` and LED class brightness cache the inferred/requested state; actual mode is encoded in two GPIO levels. Initial state is read from hardware, unlike netxbig.

Dependencies and integration: depends on firmware-node GPIO descriptors, LED class, OF platform binding `lacie,ns2-leds`, and the local `leds.h` header for LED defaults.

Risks: `ns2_led_set_mode()` returns void and silently ignores missing modes. The sleepable GPIO path is called while holding an irqsave rwlock, which is risky if GPIO operations actually sleep. Mode map binary layout relies on packed triples and `fwnode_property_read_u32_array()` into that structure.

Test signals: all mode-map combinations, initial hardware mode detection, SATA sysfs toggling while on/off, sleepable and non-sleepable GPIO controllers, and malformed `modes-map` rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-ns2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-ot200.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-ot200.c

Purpose: Bachmann OT200 board LED driver for three back-panel and seven front-panel LEDs.

Important APIs/types/functions: static `leds[]` lists names, I/O ports, and bit masks. `ot200_led_brightness_set()` updates shadow bytes and writes ports under a spinlock. Probe registers all LEDs and initializes front/back panel output bytes.

Control flow: platform probe registers ten LED class devices, then writes initial state with all front LEDs off and the init LED on. Brightness writes select the shadow byte by port, set/clear the LED mask, and write the whole byte to the hardware port.

State and persistence: `leds_front` and `leds_back` are required shadow registers because the hardware state cannot be read with `inb()`. Hardware state is initialized on every probe.

Dependencies and integration: depends on platform device, direct I/O port access, LED class, and a global spinlock.

Risks: uses static global descriptors and shadow state, so multiple instances are not supported. `BUG()` is used for impossible port values. No I/O region request is made here.

Test signals: probe initial port values, each LED bit on/off, shadow preservation across multiple LEDs on the same port, and platform unload/reload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-ot200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-pca9532.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-pca9532.c

Purpose: PCA9530/31/32/33 I2C LED dimmer driver with optional GPIO and Thecus N2100 beeper support.

Important APIs/types/functions: `struct pca9532_data` stores client, LED array, mutex, optional input device/work, optional gpio chip, chip info, PWM/PSC state, and hardware-blink availability. `pca9532_set_brightness()`, `pca9532_set_blink()`, `pca9532_setled()`, `pca9532_configure()`, and `pca9532_of_populate_pdata()` are core paths.

Control flow: probe gets platform data or parses OF, checks SMBus byte support, allocates state, then configures initial PWM/PSC registers and each channel as none, GPIO, LED, or beeper. LED brightness routes off/full directly or non-full brightness through shared PWM0. Hardware blink uses PWM1 only when not reserved by beeper. Optional GPIO exposes LED pins through gpiochip operations.

State and persistence: driver caches PWM/PSC values and each LED state; hardware selector registers hold output routing. Beeper PWM updates are deferred via workqueue from input events. GPIO and LED roles are fixed by platform/DT data.

Dependencies and integration: depends on I2C SMBus, LED class, optional GPIO library, input subsystem for beeper, platform data header `leds-pca9532.h`, OF parsing, mutex/workqueue.

Risks: shared PWM channels mean multiple dimmed LEDs get averaged brightness and one blink configuration. I2C read/write return values are often ignored in low-level setters. GPIO mode can conflict with LED mode if platform data is wrong. Hardware blink is disabled when PWM1 is reserved for beeper.

Test signals: all supported chip sizes, OF/platform data parsing, LED off/full/dim routing, shared PWM averaging, blink conflict/period bounds, beeper input events, GPIO request/set/get, and cleanup after partial registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-pca9532.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-pca955x.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-pca955x.c

Purpose: PCA9550/51/52/53 and IBM PCA9552 I2C LED driver with LED, blink, and optional GPIO roles.

Important APIs/types/functions: chip definitions provide bit count, address mask, and blink divider. `struct pca955x` tracks mutex, chip definition, active blink bitmap, active pins, and blink period. `pca955x_led_set()`, `pca955x_led_get()`, `pca955x_led_blink()`, GPIO callbacks, `pca955x_get_pdata()`, and `pca955x_probe()` implement behavior.

Control flow: probe validates chip match and I2C address, parses child nodes, reads current LED selector registers, applies default-state changes, registers LED class devices, preserves existing BLINK0 LEDs when requested, initializes blink prescaler/PWM1, and optionally registers a GPIO chip. Brightness uses selector states: on, off, shared PWM1 for variable brightness, and BLINK0 for blink.

State and persistence: `active_blink`, `active_pins`, and `blink_period` cache software ownership and shared blink state. Hardware LED selector, PSC, PWM, and input registers hold device state; probe may preserve existing blink selector state.

Dependencies and integration: depends on I2C SMBus byte and block reads, LED class, fwnode/OF child properties, optional GPIO chip support, and DT binding constants.

Risks: hardware supports only one BLINK0 period for all blinking LEDs, so incompatible blink requests return `-EBUSY`. Variable brightness through PWM1 is shared by all non-full/non-off LEDs. Active pin tracking prevents GPIO from taking LED-owned pins, but type configuration must be correct. Address validation can reject nonstandard wiring.

Test signals: address-mask validation for each chip, default-state off/on/keep, preserving bootloader blink, shared blink conflict handling, PWM brightness sharing, GPIO ownership, and suspend/resume via LED core flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-pca955x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-pca963x.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-pca963x.c

Purpose: PCA9632/33/34/35 I2C PWM LED driver with optional shared hardware blink and power management.

Important APIs/types/functions: `struct pca963x_chipdef` describes GRPPWM/GRPFREQ/LEDOUT layout and LED count. `pca963x_brightness()` writes individual PWM and LEDOUT state. `pca963x_blink_set()` maps delays to group duty/frequency. `pca963x_power_state()` sleeps/wakes the oscillator based on active LEDs. Probe and `pca963x_register_leds()` configure MODE2 and register children.

Control flow: probe picks chip definition from I2C ID, validates child count, allocates flexible state, turns off LEDOUT registers, powers down MODE1, then registers children. Registration configures output driver polarity from properties, optionally enables blink callback, and registers each child with fallback labels. Brightness changes update PWM/LEDOUT and then MODE1 sleep state.

State and persistence: `leds_on` bitmap tracks whether the chip should be awake; each LED caches blink flag and group duty/frequency values. Hardware registers hold PWM, group blink, LEDOUT, and sleep state.

Dependencies and integration: depends on I2C SMBus, LED class, fwnode/OF properties `nxp,hw-blink`, `nxp,totem-pole`, `nxp,inverted-out`, `nxp,period-scale`, and simple PM ops.

Risks: hardware blink is global, so the last blink settings affect all blinking LEDs. `pca963x_brightness()` reads registers into `u8` without checking negative SMBus errors. `pca963x_power_state()` uses LED core brightness cache, which must remain synchronized with requested writes.

Test signals: child count/reg validation, output mode polarity properties, brightness off/full/PWM, shared blink delay mapping and bounds, suspend/resume sleep bit, and all supported chip register layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-pca963x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-pca995x.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-pca995x.c

Purpose: PCA9952/PCA9955B/PCA9956B I2C LED driver for 16- or 24-output PWM controllers.

Important APIs/types/functions: `struct pca995x_chipdef` defines LED count, PWM base, and IREFALL register. `struct pca995x_chip` holds regmap and LED array. `pca995x_brightness_set()` selects LEDOUT off/on/PWM modes and writes per-output PWM values. Probe parses child `reg` nodes and registers LEDs.

Control flow: probe requires firmware node data, initializes regmap, collects child fwnodes by output index with duplicate validation, registers corresponding LED class devices, writes MODE1 normal mode, and sets global output current to half scale. Brightness full/off changes LEDOUT bits; intermediate brightness writes PWM then switches LEDOUT to PWM mode.

State and persistence: no software brightness cache beyond LED core. Hardware PWM, LEDOUT, MODE1, and IREFALL registers hold state. Fwnode handles are retained during registration and manually put on error.

Dependencies and integration: depends on I2C regmap, LED class extended registration, OF/fwnode child `reg`, and chip match data.

Risks: validation checks `reg >= PCA995X_MAX_OUTPUTS` rather than `chipdef->num_leds`, so a PCA9952/PCA9955B child above 15 can be accepted and later address unsupported outputs. Fwnode references are not explicitly put on successful registration. No blink support despite hardware families often having more features.

Test signals: valid/invalid child `reg` per chip type, full/off/PWM brightness writes, MODE1/IREFALL initialization, duplicate child detection, and regmap error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-pca995x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-pm8058.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-pm8058.c

Purpose: Qualcomm PM8058 LED driver for common, keypad, and flash LED register fields.

Important APIs/types/functions: `struct pm8058_led` stores parent regmap, register offset, LED type, and class device. `pm8058_led_set()` and `pm8058_led_get()` map brightness into 5-bit or 4-bit fields depending on LED type. Probe parses match data and `reg`, applies default state, and registers the LED.

Control flow: platform probe gets parent regmap, reads register offset, configures callbacks and max brightness, applies `default-state` (`on`, `keep`, or off), sets suspend/resume flag for keypad/flash, then registers with LED init data.

State and persistence: state is hardware register bits; `keep` reads current hardware brightness into LED core. No explicit remove-time state change.

Dependencies and integration: depends on parent regmap, OF compatibles `qcom,pm8058-led`, `qcom,pm8058-keypad-led`, `qcom,pm8058-flash-led`, LED class, and PM suspend/resume flags.

Risks: brightness callback is non-blocking but performs regmap I/O and cannot report errors. Invalid `ledtype` silently uses zero mask/value. Register field masks assume board `reg` points to the correct PMIC field.

Test signals: all three compatible types, max brightness 31 vs 15, default-state on/off/keep, get/set field round trip, missing regmap/register errors, and suspend/resume LED state behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-pm8058.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-powernv.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-powernv.c

Purpose: IBM PowerNV OPAL LED driver exposing firmware-controlled identify, fault, and attention LEDs.

Important APIs/types/functions: `powernv_led_common` stores max LED type, global mutex, and unload-disable flag. `powernv_led_data` stores LED class device, location code, LED type, and common pointer. `powernv_led_set()` performs asynchronous OPAL set calls; `powernv_led_get()` queries OPAL state; `powernv_led_classdev()` walks OPAL LED device-tree nodes and `led-types` strings.

Control flow: probe locates `/ibm,opal/leds`, initializes common state, then registers one LED class device per location-code child and supported `led-types` string. Brightness set locks globally, obtains an OPAL async token, submits a set-indicator call, waits for completion, checks async return code, and releases the token. Remove marks operations disabled and destroys the mutex, intentionally preserving firmware LED state.

State and persistence: LED state is firmware/service-processor controlled and intentionally persists across driver unload/reboot. The driver caches only static type/location metadata and a disabled flag to avoid writes during teardown.

Dependencies and integration: depends on PowerNV OPAL firmware APIs, Open Firmware device tree, LED class, platform device matching `ibm,opal-v3-led`, and asynchronous OPAL token management.

Risks: OPAL calls can sleep and fail asynchronously, so blocking brightness callbacks and mutex serialization are necessary. Unsupported LED type strings abort registration for that path. Location code is taken from node name. Destroying the mutex while devm LED devices still exist is safe only because remove disables operations and device teardown ordering prevents later callbacks.

Test signals: OPAL DT nodes with multiple `led-types`, set/get success and OPAL_PARTIAL handling, async token interruption, unsupported type warnings, remove-time no-reset behavior, and service-processor state changes visible through brightness_get.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-powernv.c -->
