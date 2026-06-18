# Research: subset-b-005877

Grouped research for MFD headers under `sources/distributed-fs/ceph-client/include/linux/mfd`. Each section preserves the source path for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lp8788.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/lp8788.h

**Purpose:** Declares the shared core contract for the TI LP8788 PMIC MFD. It names child devices for regulators, charger, RTC, backlight, vibrator, key LED, and ADC, and exposes shared register/IRQ helpers to LP8788 sub-drivers.

**Important APIs and types:** Key exports are `struct lp8788`, `struct lp8788_platform_data`, charger/LED/vibrator platform-data structs, interrupt IDs in `enum lp8788_int_id`, ADC channels in `enum lp8788_adc_id`, DVS selectors, alarm selection, backlight/current-sink modes, and functions `lp8788_irq_init()`, `lp8788_irq_exit()`, `lp8788_read_byte()`, `lp8788_read_multi_bytes()`, `lp8788_write_byte()`, and `lp8788_update_bits()`.

**Control flow:** The parent MFD driver owns I2C/regmap setup, calls optional platform `init_func`, initializes nested IRQs, then registers named child devices. Children use `struct lp8788` and helper functions rather than opening their own bus path.

**State and persistence:** Runtime state is held in `struct lp8788`: device, regmap, irq domain, IRQ number, and platform data. Persistent state lives only in hardware registers configured through regmap and platform data.

**Dependencies and integration:** Depends on Linux `regmap`, `irqdomain`, regulator init data, IIO maps, and child MFD devices named by the `LP8788_DEV_*` strings.

**Risks:** Platform-data pointers are not self-describing, so board files must keep array sizes aligned with `LP8788_NUM_*`. Interrupt IDs contain a gap before RTC alarm bits, making off-by-one IRQ mapping a test target. Charger callback execution context must be respected by platform code.

**Test signals:** Build coverage for all LP8788 sub-drivers, regmap read/write/update tests on known registers, IRQ domain mapping tests for all `LP8788_INT_MAX` IDs, and probe tests with absent optional platform-data blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lp8788.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lpc_ich.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/lpc_ich.h

**Purpose:** Provides the compact platform-description ABI for Intel ICH/PCH LPC bridge MFD support, especially watchdog, GPIO, GPE0, and Intel SPI child resources.

**Important APIs and types:** Defines GPIO resource indexes `ICH_RES_GPIO` and `ICH_RES_GPE0`, GPIO hardware-generation enum `lpc_gpio_versions`, forward-declared `struct lpc_ich_gpio_info`, and `struct lpc_ich_info` with name, TCO watchdog version, GPIO version/info, SPI type, and GPIO enable flag. Exports `lpc_ich_gpio_swnode`.

**Control flow:** PCI ID tables in the LPC ICH MFD driver select an `lpc_ich_info` entry, then child platform devices consume the encoded watchdog/GPIO/SPI capabilities and software node.

**State and persistence:** This header defines static hardware-description state only. Runtime persistence is in the parent device and child drivers; no mutable data is declared here.

**Dependencies and integration:** Depends on `linux/platform_data/x86/spi-intel.h` for `enum intel_spi_type` and on software nodes for GPIO child description.

**Risks:** The `use_gpio` byte and generation enum must match platform quirks. Wrong `spi_type` or GPIO version can expose invalid register layouts. Resource index macros are positional and must stay aligned with parent resource creation.

**Test signals:** Compile tests for LPC ICH and Intel SPI combinations, probe tests for representative chipset entries, and validation that GPIO software-node consumers bind only when `use_gpio` and `gpio_info` are valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/lpc_ich.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/macsmc.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/macsmc.h

**Purpose:** Defines the Apple Silicon SMC core API used by child drivers to access firmware keys, register event handlers, and issue atomic shutdown/reboot writes.

**Important APIs and types:** `smc_key`, `SMC_KEY()` and helper key-packing macros encode FourCC keys. `struct apple_smc_key_info` describes key type, size, and flags. `struct apple_smc` stores key bounds, notifier chain, RTKit handle, SRAM/shared memory, command completions, mutex/spinlock, and atomic-mode state. Public functions cover read, write, read/write transaction, key lookup, key info, atomic entry, and atomic writes. `APPLE_SMC_TYPE_OPS()` generates typed helpers for integer types; flag helpers wrap u8 operations.

**Control flow:** Child drivers resolve or know a key, optionally verify it with `apple_smc_key_exists()`, then call the typed or raw accessors. Normal calls serialize through the mutex and completion. Atomic mode switches to the spinlock/pending path and disables normal operations for shutdown-critical writes.

**State and persistence:** Kernel state tracks SMC boot stage, key table limits, message ID, command completion, and atomic-mode flags. Durable state is firmware-held SMC key data, not filesystem state.

**Dependencies and integration:** Integrates with Apple RTKit, SRAM shared memory, Linux completions, mutexes, spinlocks, and blocking notifier chains. Consumers include hwmon, reboot/poweroff, input, and platform feature drivers.

**Risks:** Key endianness is central; using raw integers outside `SMC_KEY()` can silently address the wrong key. Typed helpers treat short positive reads as `-EINVAL`, so backend return lengths must be exact. Atomic mode intentionally blocks all non-atomic API use.

**Test signals:** Unit tests for key packing, typed helper length handling, read/write error propagation, key-index boundary behavior, notifier delivery, and atomic-mode rejection before `apple_smc_enter_atomic()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/macsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/madera/core.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/madera/core.h

**Purpose:** Defines internal shared state and constants for Cirrus Logic Madera codec MFD devices such as CS47L35, CS47L85, CS47L90/91/92/93, WM1840, CS47L15, and CS42L92.

**Important APIs and types:** `enum madera_type`, MCLK indexes, GPIO and MICBIAS limits, notifier event bits, extensive GPIO-function constants, and `struct madera`. The structure contains 16-bit and 32-bit regmaps, device identity, core regulators, DCVDD/internal-LDO state, platform data, IRQ child state, clock bulk data, MICBIAS child counts, DAPM pointer/lock, headphone/output fault state, and notifier chain.

**Control flow:** The transport-specific parent probes the codec, identifies type/revision, creates regmaps, powers supplies/clocks, configures IRQ support, and exposes `struct madera` to child drivers. ASoC, GPIO, regulator, pinctrl, extcon, and IRQ children coordinate through shared regmap and notifier state.

**State and persistence:** Runtime state includes power rails, clock handles, IRQ mappings, DAPM association, output clamp/short flags, headphone enable bitmap, and notifiers. Persistent effects are hardware register changes and platform/firmware configuration.

**Dependencies and integration:** Depends on clk, GPIO descriptors, interrupts, Madera pdata, mutex, notifier, regmap, and regulator consumers; integrates heavily with ASoC DAPM through a forward-declared context.

**Risks:** This is an internal MFD contract; external use can couple to unstable details. GPIO-function constants are device-specific and must match the actual codec. Shared DAPM pointer access requires the provided lock discipline.

**Test signals:** Probe matrix across supported `madera_type` values, regulator/clock failure unwinds, IRQ child registration tests, GPIO function validation, and notifier tests for voice trigger, HPDET, and MICDET events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/madera/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/madera/pdata.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/madera/pdata.h

**Purpose:** Defines board/platform configuration data for Madera codec MFD devices, bridging regulator, pinctrl/GPIO, interrupt, general-purpose switch, and ASoC codec configuration.

**Important APIs and types:** `struct madera_pdata` includes reset GPIO, Arizona-compatible LDO1 and MICVDD regulator pdata, IRQ flags, legacy GPIO base, pinctrl maps and count, two GPSW mode values, and `struct madera_codec_pdata`.

**Control flow:** Parent probe imports firmware or board data into `madera_pdata`, then child regulator, GPIO/pinctrl, and codec drivers read their slices during registration.

**State and persistence:** This is configuration state copied into `struct madera`; it does not itself own runtime resources except referenced descriptors/maps.

**Dependencies and integration:** Includes Arizona regulator pdata headers, regulator machine constraints, Linux types, and `sound/madera-pdata.h`.

**Risks:** Mixed legacy and descriptor-based GPIO configuration can create board-specific corner cases. `gpio_configs` and `n_gpio_configs` must remain consistent. GPSW values are raw datasheet mode fields with no enum validation here.

**Test signals:** Probe tests with no reset GPIO, DT/ACPI-to-pdata conversion checks, pinctrl map count validation, regulator pdata handoff checks, and codec child tests using populated and empty `codec` data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/madera/pdata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/madera/registers.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/madera/registers.h

**Purpose:** Provides the generated register address and bitfield namespace for Madera codecs. It is the canonical compile-time map used by MFD, ASoC, regulator, GPIO, interrupt, clock/FLL, DSP, accessory-detect, and audio-route code.

**Important APIs and types:** The file is macro-only. Address macros cover reset/revision, clocks, FLLs, charge pumps, LDOs, MICBIAS, headphone/mic/accessory detection, inputs/outputs, AIF/SLIMbus/SPDIF, mixers, EQ/DRC/ASRC/ISRC/DFC, DSP IRQ/config/scratch regions, GPIOs, IRQ status/masks/raw status/debounce/control, write sequencer, OTP HPDET calibration, and 32-bit DSP windows. Bitfield macros provide value, mask, and shift triples for many registers.

**Control flow:** There is no executable control flow; users combine address macros with regmap reads/writes and bitfield masks. Control sequences are implemented in consumers such as codec, IRQ, clock, and regulator drivers.

**State and persistence:** The macros name hardware state. Persistence is entirely in codec registers and OTP/calibration fields. The same header supports volatile runtime registers and one-time calibration data.

**Dependencies and integration:** Standalone include guard with no includes. It integrates by being included into Madera core and child drivers that use regmap.

**Risks:** The map contains overlapping/common and chip-specific aliases, for example CS47L92 FLL and AIF/DSP regions that share addresses with generic names. Address ranges span normal 16-bit control registers, 32-bit OTP/calibration, and large DSP windows, so consumers must use the correct regmap width. Generated macro volume makes typo detection dependent on compile coverage.

**Test signals:** Compile all Madera consumers, regmap access tests for representative 16-bit and 32-bit registers, field-mask tests for clock/FLL/input/output/IRQ macros, chip-variant tests for CS47L35/CS47L85/CS47L92 aliases, and audio route tests exercising mixer address patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/madera/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max14577-private.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/max14577-private.h

**Purpose:** Defines the internal MFD register, IRQ, and regmap helper contract for Maxim MAX14577 and MAX77836 MUIC/charger/PMIC/fuel-gauge devices.

**Important APIs and types:** Declares I2C addresses for PMIC, MUIC, and fuel gauge; `enum maxim_device_type`; MUIC/charger/PMIC/fuel-gauge register enums; charger-type enums encoding MAX14577 and MAX77836 differences; interrupt masks; field masks for MUIC control/status, charger controls, LDOs, and PMIC top-system interrupts; charger voltage/current limits; `enum max14577_irq`; `struct max14577`; and inline regmap helpers for read, bulk read/write, write, and update.

**Control flow:** The parent MFD creates one or more I2C clients/regmaps based on device type. MUIC, charger, regulator, and fuel-gauge child drivers select register enums and masks for their sub-block and use the inline regmap wrappers.

**State and persistence:** Runtime state is the parent `struct max14577`, including MUIC/charger and PMIC regmaps, IRQ chip data, device type, and IRQ number. Hardware state persists in PMIC/MUIC/fuel-gauge registers.

**Dependencies and integration:** Depends on I2C and regmap. Integrates with MUIC/extcon, charger/power-supply, regulator, and IRQ children.

**Risks:** MAX14577 and MAX77836 share fields but differ in charger type meanings and current limits; wrong `dev_type` changes behavior. A source typo appears in the CDET mask area: `MAX77836_CDETCTRL1_CDLY_SHIFT` is defined, while `MAX77836_CDETCTRL1_CDDLY_MASK` references `MAX77836_CDETCTRL1_CDDLY_SHIFT`, which would fail if compiled through that macro. Inline `max14577_read_reg()` writes `*dest` even when `regmap_read()` fails, using the last local `val`.

**Test signals:** Compile tests that exercise every mask macro, device-type-specific charger limit tests, regmap error-path tests for read helper behavior, IRQ mapping tests for MUIC/charger/top-system sources, and probe tests for MAX14577-only vs MAX77836 multi-client paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max14577-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max14577.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/max14577.h

**Purpose:** Public platform-data and regulator-ID header for MAX14577/MAX77836 consumers.

**Important APIs and types:** Exposes regulator IDs for MAX14577 safeout/charger and MAX77836 safeout/charger/LDO1/LDO2. Defines `struct max14577_regulator_platform_data`, `struct max14577_charger_platform_data`, parent `struct max14577_platform_data`, `struct maxim_charger_current`, the `maxim_charger_currents[]` limit table, and `maxim_charger_calc_reg_current()`.

**Control flow:** Board or firmware glue populates IRQ base, pogo current-control GPIOs/callbacks, and regulator init data. Charger code uses `maxim_charger_currents[]` plus `maxim_charger_calc_reg_current()` to translate requested current ranges into CHGCTRL4 register values.

**State and persistence:** Platform initialization data is static configuration; actual state persists in charger and regulator registers after child drivers apply it. Pogo GPIO callbacks control board-level current paths outside the PMIC register map.

**Dependencies and integration:** Includes regulator consumer API and is consumed by MAX14577/MAX77836 MFD, charger, regulator, and board glue code.

**Risks:** Current conversion must stay aligned with the CHGCTRL4 low/high current fields and chip-specific current limits. Platform GPIO callbacks may be NULL and must not be called blindly. Regulator ID order is lookup-sensitive.

**Test signals:** Charger current conversion boundary tests for both chip variants, probe tests with missing and populated GPIO callbacks, regulator ID coverage for MAX14577 and MAX77836, and charger platform-data validation for voltage/current fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max14577.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max5970.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/max5970.h

**Purpose:** Defines common register addresses and conversion helpers for MAX5970/MAX5978 hot-swap/power-controller regulator, monitoring, fault, and LED support.

**Important APIs and types:** Macros describe switch/LED counts, per-channel current/voltage ADC registers, monitor range extraction, threshold registers, DAC fast register, status/fault bits, channel enable bits, ADC mask, and register limit. `MAX5970_VAL2REG_H/L()` split threshold values.

**Control flow:** Consumers compute channel-specific register addresses with `(ch)` macros, read ADC/status/fault registers through regmap, and program thresholds/DAC/enable fields.

**State and persistence:** No structs are declared; hardware registers hold channel enable, thresholds, monitor ranges, and faults.

**Dependencies and integration:** Depends on regmap declarations and integrates with regulator, hwmon/IIO-style monitoring, LED, and fault/alert handling.

**Risks:** Channel macros assume callers bound `ch` to the correct device switch count; MAX5978 has fewer switches. Threshold conversion uses 10-bit split values, so callers must clamp before using `_H/_L`. Fault bits are per-channel positional.

**Test signals:** Channel-bound tests for MAX5970 vs MAX5978, ADC conversion tests, threshold split/round-trip tests, and simulated fault/status decoding tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max5970.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max7360.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/max7360.h

**Purpose:** Provides shared register, dimension, bitfield, and IRQ definitions for the MAX7360 keypad/GPIO/GPO/PWM/rotary MFD.

**Important APIs and types:** Declares keypad matrix limits, GPIO/GPO/PWM counts, register addresses for keypad and GPIO/PWM blocks, FIFO encodings, config/debounce/interrupt masks, autosleep values, rotary debounce fields, and internal IRQ numbers for GPIO, keypad, and rotary.

**Control flow:** Child keypad, GPIO, PWM, and rotary code use this register map to configure debounce/sleep/interrupt behavior, parse FIFO entries into row/column/release events, and route internal IRQs.

**State and persistence:** State is in hardware registers and FIFO contents. The header has no runtime structures.

**Dependencies and integration:** Uses `linux/bits.h` for `BIT()` and `GENMASK()`. Integrates with input matrix keypad, GPIO, PWM, and IRQ subsystems.

**Risks:** `MAX7360_PORTS` uses `GENMASK(8, 5)`, which exceeds an 8-bit register if callers assume byte-only masks without care. FIFO empty/overflow values overlap row/column encoding and must be checked before decoding. GPIO reset bit resets a whole register group.

**Test signals:** FIFO decode tests for empty, overflow, press, and release entries; debounce range validation; IRQ mapping tests; and GPIO reset/configuration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max7360.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77541.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/max77541.h

**Purpose:** Defines register and shared core state for MAX77540/MAX77541 dual-buck PMIC MFD support.

**Important APIs and types:** Address and bit macros cover interrupt source/mask, top-system thermal/UVLO/status bits, buck interrupt/mask bits, enable control, two buck VOUT and CFG registers, ADC interrupt/data registers, and mask values. `enum max7754x_ids` identifies MAX77540 vs MAX77541. `struct max77541` stores I2C, regmap, ID, and separate regmap IRQ chip data for top-level, buck, top-system, and ADC IRQ domains.

**Control flow:** Parent probe creates the regmap, identifies chip ID, initializes IRQ chips for the grouped domains, and children use the shared register macros for regulator and ADC functions.

**State and persistence:** Runtime state is held in `struct max77541`; persistent hardware state includes buck enables, voltages, ADC data/status, and interrupt masks.

**Dependencies and integration:** Depends on bits/types and forward-declared regmap/I2C/IRQ chip data. Integrates with regulator, IIO/ADC, and interrupt subsystems.

**Risks:** Several interrupt mask macros are defined as `0x00`, likely intended as default mask values rather than register addresses; consumers must not confuse them with the actual `*_INT_M` register macros. IRQ data is split by domain, so cleanup paths must free all initialized domains.

**Test signals:** Probe/remove tests with partial IRQ init failures, regulator VOUT mask tests, ADC channel data tests, and interrupt domain tests for top/buck/top-system/ADC events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77541.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77620.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/max77620.h

**Purpose:** Defines the MAX77620/MAX20024/MAX77663 PMIC register map and shared core state for regulators, GPIOs, FPS sequencing, on/off control, watchdog, low-battery, RTC/top interrupts, and backup battery charging.

**Important APIs and types:** Macros define global, interrupt, SD/LDO, GPIO, FPS, CID, 32K, on/off, watchdog, and backup-battery registers and fields. Enums cover top IRQs, GPIO numbers, FPS sources, and chip IDs. `struct max77620_chip` stores device/regmap, chip IRQ, chip ID, sleep/global low-power flags, FPS period arrays, and top/GPIO IRQ chip data.

**Control flow:** Parent probe selects chip ID, creates regmap IRQ chips, registers regulator/GPIO/RTC/onoff children, and children program register fields using chip-specific constraints such as FPS period min/max.

**State and persistence:** Runtime state includes chip identity, IRQ data, sleep/LPM flags, and suspend/shutdown FPS period arrays. Hardware registers persist regulator voltages, FPS sequencing, GPIO configuration, watchdog, and on/off behavior.

**Dependencies and integration:** Depends on Linux types and common bit macros. Integrates with regulator, GPIO, RTC, power/reset, watchdog, and IRQ subsystems.

**Risks:** MAX77620 and MAX20024 share many fields but differ in FPS timing and some register bits; chip ID must gate these paths. GPIO config macros combine direction, output, interrupt, and debounce in one byte, so update masks must be precise. Watchdog/onoff bits can reset or power off hardware.

**Test signals:** Chip-variant tests for FPS period limits, GPIO direction/IRQ/debounce tests, regulator mask tests, watchdog/onoff register tests, and suspend/shutdown FPS sequencing tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77620.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77650.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/max77650.h

**Purpose:** Common register and chip-ID definitions for MAX77650/MAX77651 charger/PMIC/regulator/LED/GPIO support.

**Important APIs and types:** Defines global and charger interrupt/status/mask registers, global/GPIO/charger/SBB/LDO/LED configuration registers, CID mask/extraction macro, and known CID values for MAX77650A/C and MAX77651A/B.

**Control flow:** Parent and child drivers read `MAX77650_REG_CID`, extract ID with `MAX77650_CID_BITS()`, then use the register map for charger, regulator, LED, and GPIO configuration.

**State and persistence:** No structs are declared. Hardware registers hold interrupt/status/configuration state.

**Dependencies and integration:** Uses `linux/bits.h`. Integrates with charger/power-supply, regulator, LED, GPIO, and IRQ drivers.

**Risks:** CID extraction keeps only four low bits; revision handling outside those known values must be robust. Register names are shared across close variants, so unsupported variant IDs should fail safely.

**Test signals:** CID decode tests, probe tests for all known IDs and unknown IDs, charger interrupt mask/status tests, and LED/SBB/LDO register access smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77650.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77686-private.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/max77686-private.h

**Purpose:** Internal register, IRQ, and device-state definitions for MAX77686 and MAX77802 PMIC/RTC MFD support.

**Important APIs and types:** Provides PMIC and RTC register enums for MAX77686 and MAX77802, IRQ source/group enums, PMIC and RTC IRQ IDs, interrupt masks, `struct max77686_dev`, and `enum max77686_types`.

**Control flow:** Parent probe selects MAX77686 or MAX77802, configures a regmap and IRQ handling, then child regulator and RTC drivers use the correct register enum namespace. IRQ masks are cached in `irq_masks_cur` and `irq_masks_cache` under `irqlock`.

**State and persistence:** Runtime state includes I2C, regmap, IRQ number, IRQ lock, current/cache masks, and type. Hardware state includes regulator settings, PMIC status, RTC time/alarm/update registers, and interrupt masks.

**Dependencies and integration:** Depends on I2C, regmap, module, mutex, regulator and RTC child drivers, and MFD IRQ infrastructure.

**Risks:** MAX77686 RTC registers start at 0 while MAX77802 RTC registers are offset into the PMIC map; selecting the wrong type corrupts accesses. Some IRQ enum values restart at zero for RTC group, so group context is required. Cached masks must stay synchronized with hardware.

**Test signals:** Variant-specific register access tests, IRQ mask sync tests, RTC alarm/time register tests for both address layouts, and probe failure unwind tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77686-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77686.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/max77686.h

**Purpose:** Public regulator ID and operating-mode definitions for MAX77686/MAX77802 regulator consumers.

**Important APIs and types:** `enum max77686_regulators` enumerates 26 LDOs and 9 bucks. `enum max77802_regulators` enumerates 10 bucks and supported LDOs with gaps matching hardware availability. `enum max77686_opmode` defines normal, low-power, and standby regulator modes.

**Control flow:** Regulator child drivers and board constraints use these IDs to bind regulator descriptors and constraints to the right PMIC output.

**State and persistence:** The header has no mutable state; regulator operating mode and voltage state persist in PMIC registers programmed by children.

**Dependencies and integration:** Includes regulator consumer API and integrates with regulator framework, MFD core, and board/DT regulator descriptions.

**Risks:** ID ordering is lookup-sensitive. MAX77802 omits some LDO numbers, so array indexing must use enum IDs, not physical LDO number arithmetic. Opmode values are generic names whose bit encoding must be handled in the regulator driver.

**Test signals:** Regulator descriptor count checks against `*_REG_MAX`, ID-to-register mapping tests, and mode transition tests for normal/LP/standby.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77686.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77693-common.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/max77693-common.h

**Purpose:** Shared device-state definition for the related MAX77693, MAX77705, and MAX77843 MFD families.

**Important APIs and types:** `enum max77693_types` identifies supported family members. `struct max77693_dev` stores parent device, multiple I2C clients, type, regmaps for PMIC/MUIC/haptic/charger/LEDs, IRQ chip data for LED/top-system/charger/MUIC, and the host IRQ.

**Control flow:** Family-specific parent code initializes only the I2C clients/regmaps/IRQ domains present for the detected chip, then children share this structure.

**State and persistence:** Runtime state is the multi-regmap, multi-IRQ-chip parent structure. Hardware state persists in the individual PMIC, MUIC, haptic, charger, and LED register blocks.

**Dependencies and integration:** Relies on forward-declared device/I2C/regmap/IRQ types through including C files. Integrates with charger, MUIC/extcon, haptic, flash LED, RGB LED, and top-system IRQ children.

**Risks:** Not every pointer is valid for every chip type; child drivers must gate on `type` or presence. Multiple slave addresses make probe and cleanup ordering important.

**Test signals:** Probe/remove matrix across all `TYPE_MAX77693*` values, child registration tests for absent optional regmaps, and IRQ-domain tests per available sub-block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77693-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77693-private.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/max77693-private.h

**Purpose:** Internal register, bitfield, charger-state, LED, MUIC, haptic, and IRQ definitions for MAX77693.

**Important APIs and types:** Register enums cover PMIC/charger/flash LED, MUIC, and haptic slaves. Macros define torch/flash currents and timeouts, charger defaults and fields, MUIC status/control masks, safeout bits, source IRQ bits, LED/top/charger/MUIC IRQ masks, and haptic config bits. Enums describe charger charging/battery states plus top-level and MUIC IRQ IDs.

**Control flow:** The parent IRQ handler reads source bits and dispatches to LED, top-system, charger, and MUIC regmap IRQ chips. Child charger, flash LED, MUIC, haptic, and regulator code uses register macros to configure each block.

**State and persistence:** No runtime struct is defined here; hardware register state controls charger policy, LED current/timeout, MUIC routing, haptic mode, and interrupt masks.

**Dependencies and integration:** Includes I2C and relies on common MFD state. Integrates with power-supply, extcon/MUIC, LED flash, haptic input, regulator, and IRQ subsystems.

**Risks:** Raw charger defaults encode policy in micro-units and minutes; drivers must convert carefully. `CHG_CNFG_01_PQEN_MAKS` appears misspelled, so users looking for `_MASK` may miss it. MUIC and charger IRQ names are similar but separate domains.

**Test signals:** Compile use of all mask macros, charger status decode tests, flash current/timeout conversion tests, MUIC switch routing tests, haptic mode tests, and source IRQ demultiplex tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77693-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77693.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/max77693.h

**Purpose:** Public platform-data and regulator/LED configuration header for MAX77693 child drivers.

**Important APIs and types:** Defines regulator IDs for safeout1, safeout2, and charger; `struct max77693_reg_data`; `struct max77693_muic_platform_data`; LED trigger, trigger type, and boost mode enums; and `struct max77693_platform_data` with MUIC and LED data pointers.

**Control flow:** Board data can provide MUIC initialization writes, cable-detect delay, default USB/UART paths, and LED platform data. Children consume this during probe.

**State and persistence:** Platform data is static initialization. Applied settings persist in MUIC switch, regulator, charger, and LED hardware registers.

**Dependencies and integration:** Consumed by MAX77693 MFD, MUIC, regulator, charger, and flash LED drivers. The `max77693_led_platform_data` type is forward-declared elsewhere.

**Risks:** Raw path values can misroute USB/UART pins. LED trigger/boost policy must match hardware current limits from the private header. Init data count must match the provided array.

**Test signals:** Platform-data validation tests, regulator ID mapping checks, MUIC path tests, and LED trigger/boost configuration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77693.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77705-private.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/max77705-private.h

**Purpose:** Internal register and field definitions for the MAX77705 PMIC family, covering top-system, charger, fuel gauge, RGB LED, haptics, revision, and interrupt source bits.

**Important APIs and types:** Defines source IRQ bits, PMIC revision masks, main control and haptic config bits, system IRQ masks, RGB LED blink timing constants, hardware revision enum, PMIC/charger/fuel-gauge/RGB LED register enums, and charger battery/charge state enums.

**Control flow:** Parent and child drivers use source bits to demultiplex PMIC/top/charger/fuel-gauge/USBC interrupts, then access relative charger/LED register blocks and absolute PMIC/fuel-gauge addresses.

**State and persistence:** Hardware registers retain PMIC control, charger policy/status, fuel-gauge measurements, LED brightness/blink, and haptic mode. This header has no runtime struct.

**Dependencies and integration:** Uses bit macros expected from including contexts and integrates with the shared MAX77693-family state, charger/power-supply, fuel-gauge, RGB LED, haptic, and USBC-related drivers.

**Risks:** Charger register enum starts with a base plus relative offsets, so consumers must add the base consistently. RGB blink timing constants encode nonlinear steps and need conversion tests. Fuel-gauge register names are generic, increasing collision risk if included broadly.

**Test signals:** Register-address tests for base-relative blocks, revision decode tests, charger/fuel-gauge state decode tests, RGB blink conversion tests, and interrupt-source demux tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77705-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77714.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/max77714.h

**Purpose:** Defines register, watchdog, 32 kHz oscillator, top interrupt, and IRQ ID constants for MAX77714 MFD support.

**Important APIs and types:** Macros include top interrupt and mask registers, top interrupt source bits, 32K status/config bits, global config registers, watchdog enable/sleep/clear/timer values, watchdog reset wake bit, and top IRQ enum values for onoff, RTC, GPIO, LDO, SD, and global resources.

**Control flow:** Parent IRQ code reads top interrupt status and dispatches child IRQs. Watchdog/onoff/clock children use the register bits to configure oscillator and watchdog behavior.

**State and persistence:** State is hardware-held in top interrupt masks/status, 32K oscillator status/config, global config, and watchdog/onoff registers.

**Dependencies and integration:** Uses `linux/bits.h`. Integrates with watchdog, RTC, GPIO, regulator, clock, power/reset, and IRQ subsystems.

**Risks:** The comment notes `MAX77714_INT_TOPM` is documented read-only but is actually read/write, so driver behavior intentionally differs from datasheet text. Watchdog bits can reset the system and need guarded writes.

**Test signals:** Top IRQ mask/read tests, watchdog timeout encode tests, 32K status/config tests, and suspend/resume wake behavior tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77714.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77759.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/max77759.h

**Purpose:** Defines core register map and MaxQ command API for MAX77759 PMIC/charger/MaxQ/fuel-gauge/TCPCI MFD support.

**Important APIs and types:** Macros cover PMIC ID/revision/interrupt source/top-system/software reset/control registers, MaxQ UIC interrupt/status/AP data windows, charger interrupt/status/config registers, MaxQ opcode length and opcode values, charger input/battery/charge detail enums, charger mode enum, `struct max77759`, counted flexible-array command/response structs, and `max77759_maxq_command()`.

**Control flow:** Core code owns top, MaxQ, and charger regmaps. Callers serialize MaxQ commands with `maxq_lock`, write command bytes through AP data-out registers, wait on `cmd_done`, and copy optional response bytes from AP data-in registers. Charger and top-system children read status/detail fields and program charger mode/config.

**State and persistence:** Runtime state includes three regmaps, MaxQ mutex, and command completion. Hardware retains PMIC/top, MaxQ firmware, charger, fuel-gauge, and TCPCI state.

**Dependencies and integration:** Depends on completion, mutex, and regmap. Integrates with charger/power-supply, USB-C/TCPCI, GPIO-over-MaxQ, fuel-gauge, and top-system IRQ handling.

**Risks:** MaxQ accepts only one active command, so all callers must use the core API and respect `MAX77759_MAXQ_OPCODE_MAXLENGTH`. `MAX77759_MAXQ_REG_UIC_STATUS7` and `MAX77759_MAXQ_REG_UIC_STATUS8` are both defined as `0x6f`, which may be intentional aliasing or a register-map bug. Flexible-array command/response structs require correct allocation sizes.

**Test signals:** MaxQ command length/allocation tests, concurrent command serialization tests, response timeout/error tests, charger detail decode tests, duplicate UIC status register review, and top/charger IRQ demux tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77759.h -->
