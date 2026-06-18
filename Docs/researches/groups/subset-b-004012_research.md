# subset-b-004012 grouped research

Grouped source research for LED core, platform LED drivers, and RGB/multicolor LED drivers under `sources/distributed-fs/ceph-client/drivers/leds`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-pwm.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-pwm.c

Purpose: generic platform driver for device-tree/firmware described single-color PWM LEDs. It creates one LED class device per child node of a `pwm-leds` device and drives brightness by scaling a PWM duty cycle over the PWM period, optionally inverting it for `active-low`.

Important APIs, types, and functions: `struct led_pwm` holds firmware-derived static configuration; `struct led_pwm_data` stores the runtime `led_classdev`, `pwm_device`, cached `pwm_state`, optional enable GPIO, and polarity; `struct led_pwm_priv` is a flexible-array container for all LEDs. `led_pwm_set()` is the LED core callback and applies the PWM state. `led_pwm_add()` acquires the PWM via `devm_fwnode_pwm_get()`, handles default state, registers with `devm_led_classdev_register_ext()`, and optionally sets the starting PWM value. `led_pwm_create_fwnode()` parses child node properties, and `led_pwm_probe()` allocates the per-device array.

Control flow: probe counts children, allocates enough slots, parses each child, and registers each LED. Brightness writes flow from LED sysfs/triggers to `led_pwm_set()`, which computes `period * brightness / max_brightness`, applies active-low inversion, mirrors nonzero brightness to the enable GPIO, and calls `pwm_apply_might_sleep()`.

State and persistence: state is entirely in memory plus the PWM hardware. `LEDS_DEFSTATE_KEEP` reads the current PWM state and derives brightness from the existing duty cycle; otherwise the driver initializes a new PWM state. It deliberately keeps the PWM enabled during normal off states because disabled PWMs may not drive an inactive level; suspend is handled through `LED_CORE_SUSPENDRESUME`.

Dependencies and integration points: depends on LED class, PWM framework, firmware-node property APIs, optional GPIO descriptors, and the `pwm-leds` OF compatible. LED naming and default state are delegated to LED core init data.

Risks and test signals: validate child-node error handling, default-state keep with zero period fallback, active-low duty inversion, enable GPIO optionality, and suspend behavior where `LED_SUSPENDED` disables PWM output. Runtime tests should check sysfs brightness, trigger operation, DT bindings for `max-brightness`, `default-brightness`, `active-low`, and that off LEDs actually turn off on target hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-pwm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-qnap-mcu.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-qnap-mcu.c

Purpose: LED class integration for LEDs controlled by QNAP MCU devices. It exposes per-drive red error LEDs, an optional USB blue LED, and a dual red/green status LED pair by translating LED core brightness/blink callbacks into MCU command bytes.

Important APIs, types, and functions: `struct qnap_mcu_err_led`, `struct qnap_mcu_usb_led`, and `struct qnap_mcu_status` hold LED class devices and MCU state. `qnap_mcu_err_led_set()` and `_blink_set()` emit `@R` commands per drive. `qnap_mcu_usb_led_set()` and `_blink_set()` emit `@C` commands whose third byte is shared with buzzer control. `qnap_mcu_status_led_encode()` maps combined red/green modes to the MCU's single status-code byte. `qnap_mcu_leds_probe()` creates devices based on `struct qnap_mcu_variant`.

Control flow: platform probe gets the parent `struct qnap_mcu` and variant platform data, registers an error LED for each drive, conditionally registers the USB LED, then registers the two status LEDs. Brightness callbacks avoid disrupting existing blink modes when brightness remains nonzero. Blink callbacks coerce requested timing to the MCU-supported fast/slow values and update local mode before sending an acknowledged command.

State and persistence: each LED caches its MCU mode in RAM. The MCU holds the durable hardware state until new commands arrive. There is no remove-time restore. The status LEDs share a single MCU command path, so the red and green LED objects coordinate through the parent `qnap_mcu_status`.

Dependencies and integration points: depends on the QNAP MCU MFD interface and `qnap_mcu_exec_with_ack()`, LED class APIs, platform data from the parent variant, and uleds name-size constants.

Risks and test signals: the status LED pointer trick (`statusled_to_qnap_mcu_status()` via each member's `red` pointer) is subtle and should be tested with both red and green callbacks. Exercise blink/brightness transitions, especially nonzero brightness while blink is active, off-then-blink no-op behavior, and command-byte overlap with the input/buzzer driver for the USB LED.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-qnap-mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-rb532.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-rb532.c

Purpose: minimal Routerboard532 user LED driver. It registers one global LED class device named `uled` backed by the RC32434 board latch bit `LO_ULED`.

Important APIs, types, and functions: `rb532_led_set()` writes to latch U5 via `set_latch_u5()`, `rb532_led_get()` reads via `get_latch_u5()`, and `rb532_uled` describes the LED class device with a `nand-disk` default trigger. Platform `probe` and `remove` register and unregister the static class device.

Control flow: the platform driver binds to `rb532-led`; probe simply calls `led_classdev_register()`. Brightness set uses inverted latch semantics: nonzero brightness clears `LO_ULED`, while off sets `LO_ULED`. Brightness get returns `LED_FULL` when the latch bit is set, which mirrors the raw latch state rather than the set path's active-low write direction.

State and persistence: there is no allocated private state; the hardware latch is the source of truth. The class device is static module state, so only one instance is expected.

Dependencies and integration points: depends on MIPS Routerboard532 architecture headers, RC32434 GPIO/latch helpers, platform device registration elsewhere, and the LED trigger subsystem.

Risks and test signals: polarity deserves board-level validation because the set and get paths expose hardware-level inversion. Tests are mostly integration tests: load/unload on supported hardware, verify the NAND trigger toggles the visible LED, and confirm no duplicate platform instances are created.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-rb532.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-regulator.c

Purpose: LED class driver for LEDs powered directly by a regulator. It can treat the regulator as binary on/off or, when multiple voltage selectors are available, map brightness levels onto regulator voltages.

Important APIs, types, and functions: `struct regulator_led` stores `led_classdev`, mutex, enabled flag, and `struct regulator *vcc`. `led_regulator_get_max_brightness()` probes voltage-count capability. `led_regulator_get_voltage()` maps brightness to `regulator_list_voltage(brightness - 1)`. `regulator_led_brightness_set()` handles all brightness updates, and probe/register/remove wire the device into LED and regulator frameworks.

Control flow: probe gets exclusive `vled`, allocates state, derives `max_brightness`, accepts legacy platform-data name/default brightness, and registers with `led_classdev_register_ext()`. Brightness off disables the regulator. Nonzero brightness optionally programs a voltage first, then enables the supply.

State and persistence: in-memory `enabled` shadows regulator state and is initialized from `regulator_is_enabled()`. The driver does not persist brightness beyond LED core state. Remove unregisters the LED and disables the regulator.

Dependencies and integration points: integrates with regulator consumers, platform devices, LED class, fwnode naming, legacy `leds-regulator.h` platform data, and OF compatible `regulator-led`.

Risks and test signals: voltage selector math assumes brightness value N maps to selector N-1 and relies on regulator APIs returning valid voltages. Validate binary regulators, multi-voltage regulators, already-enabled supplies at probe, platform-data brightness bounds, suspend/resume flag behavior, and cleanup disabling the regulator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-sc27xx-bltc.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-sc27xx-bltc.c

Purpose: Spreadtrum SC27xx breathing light controller driver for up to three PMIC LED channels. It supports direct brightness and hardware breathing patterns through PMIC regmap registers.

Important APIs, types, and functions: `struct sc27xx_led_priv` holds regmap, base offset, mutex, and channel array. `sc27xx_led_init()` enables PMIC BLTC and RTC clocks and clears RGB power-down. `sc27xx_led_set()` selects enable/disable. `sc27xx_led_pattern_set()` accepts exactly four pattern tuples for rise, high, fall, and low times. `sc27xx_led_pattern_clear()` clears curve registers and disables run/type bits.

Control flow: probe validates child count and parent regmap, reads the controller `reg`, records active child channels by child `reg`, initializes the mutex, then registers active LEDs. Brightness writes update the duty register and per-line control bits. Pattern writes clamp/align each duration to 125 ms hardware steps, writes curve registers, writes duty from the high-stage brightness, and enables breathing mode.

State and persistence: active channel selection and fwnodes are stored in driver memory. Hardware registers hold run/type, duty, and curve state. Pattern clear updates `ldev->brightness` to off.

Dependencies and integration points: uses regmap from the parent PMIC, OF child nodes, LED pattern APIs, and `sprd,sc2731-bltc` compatible binding. The default LED trigger is `pattern`.

Risks and test signals: test invalid child counts, duplicate/out-of-range channel `reg`, exact four-tuple pattern validation, clamping at min/max duration, direct-to-pattern transitions, and mutex coverage when multiple LED channels are written concurrently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-sc27xx-bltc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-spi-byte.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-spi-byte.c

Purpose: simple SPI LED driver for controllers whose brightness is represented by a single MOSI byte. The included chip definition targets Ubiquiti airCube-compatible `ubnt,acb-spi-led` devices.

Important APIs, types, and functions: `struct spi_byte_chipdef` describes off and maximum byte values. `struct spi_byte_led` owns the LED class device, SPI device, mutex, and chip definition. `spi_byte_brightness_set_blocking()` writes `off_value + brightness` as one byte. `spi_byte_probe()` validates that exactly one LED child exists, sets default state, writes the initial value, and registers an extended LED class device.

Control flow: SPI probe allocates state, initializes the mutex, loads OF match data, calculates `max_brightness`, reads the single child node, applies `LEDS_DEFSTATE_ON` as max brightness, immediately writes hardware, and registers the LED.

State and persistence: no cached hardware value beyond LED core brightness. The device receives each brightness byte directly. Default state keep is not implemented; anything except explicit on starts off.

Dependencies and integration points: depends on SPI core, fwnode child properties, LED class, and OF match data. It declares only brightness control despite the hardware protocol documenting additional modes.

Risks and test signals: test child-count validation, initial brightness write before registration, SPI write failures, and max/off chip definition math. Hardware tests should confirm mode bits are not accidentally set by high brightness and that no MISO response is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-spi-byte.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-ss4200.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-ss4200.c

Purpose: Intel SS4200-E and related NAS/Home Server LED driver using ICH7 LPC GPIO I/O registers. It exposes drive and power LEDs plus a custom `blink` sysfs attribute.

Important APIs, types, and functions: `struct nasgpio_led` maps LED names to GPIO bits and class devices. `ich7_lpc_probe()` discovers PM/GPIO bases through PCI config space and requests the GPIO I/O region. `ich7_gpio_init()` configures GPIO use/direction non-destructively. `nasgpio_led_set_brightness()` and `nasgpio_led_set_blink()` control `GP_LVL` and `GPO_BLINK`. `register_nasgpio_led()` registers each LED with `nasgpio_led_groups`.

Control flow: module init checks a DMI whitelist unless `nodetect` is set, registers the PCI driver, then registers every LED against the discovered PCI device. Brightness writes clear blink on off and set binary output based on `LED_HALF`. Blink supports only 500/500 ms hardware blink. Load also changes the power indicator to solid amber.

State and persistence: global I/O base, PCI device pointer, resource pointer, and static LED array hold module state. Hardware registers are the persistent state. A spinlock protects port read-modify-write sequences.

Dependencies and integration points: DMI, PCI, x86 I/O port access, LED class, device attributes, and ICH7-specific register layout. It is not a conventional platform driver and assumes one supported NAS device.

Risks and test signals: risks include false-positive DMI/nodetect binding, global singleton state, direct I/O port programming, and partial LED registration cleanup. Tests should cover DMI gating, PCI resource failure paths, blink sysfs read/write, off clearing blink, module unload cleanup, and real GPIO polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-ss4200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-st1202.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-st1202.c

Purpose: I2C LED class driver for the STMicroelectronics LED1202 12-channel constant-current LED controller, including brightness and hardware pattern sequence support.

Important APIs, types, and functions: `struct st1202_chip` stores the I2C client, mutex, and fixed channel array. `struct st1202_led` maps an active DT channel to a LED class device. `st1202_read_reg()`/`st1202_write_reg()` wrap SMBus byte access. `st1202_pwm_pattern_write()` and `st1202_duration_pattern_write()` program pattern RAM. `st1202_led_pattern_set()` writes up to eight pattern entries and starts the sequence. `st1202_setup()` resets/enables the device and clears channel enables.

Control flow: probe checks SMBus byte support, allocates state, initializes the chip, parses child nodes by `reg`, then for each active channel enables the channel, clears patterns, and registers a LED. Brightness has two paths: `brightness_set` writes the current register, while `brightness_set_blocking` toggles the channel enable bit.

State and persistence: channel active/fwnode data is stored in RAM; PWM/current values, channel enables, and pattern RAM are in chip registers. Device setup resets chip state on probe and remove relies on devm cleanup without explicit shutdown.

Dependencies and integration points: I2C SMBus byte data, OF child nodes, LED class pattern API, cleanup guards, and compatible `st,led1202`.

Risks and test signals: probe lacks an explicit bounds check before indexing `chip->leds[reg]`; DT validation should cover `reg < 12`. Test pattern duration min/max, eight-pattern limit, channel high/low enable register paths, concurrent brightness/pattern access under the mutex, and setup timing after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-st1202.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-sun50i-a100.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-sun50i-a100.c

Purpose: Allwinner A100 LED controller driver for addressable RGB LED strings. It exposes each LED as a multicolor LED class device and transfers packed RGB data to hardware through PIO or DMA.

Important APIs, types, and functions: `struct sun50i_a100_ledc` stores MMIO base, clocks, reset, DMA resources, transfer buffer, spinlock-protected transfer state, format/timing, and LED array. `sun50i_a100_ledc_brightness_set()` computes color components and schedules transfers. `sun50i_a100_ledc_start_xfer()`, `_pio_xfer()`, `_dma_xfer()`, and IRQ handler implement the data path. Parse helpers read `allwinner,pixel-format` and timing properties.

Control flow: probe validates child `reg` and RGB color, allocates state, maps registers, gets clocks/reset, optionally configures DMA, requests IRQ, resumes hardware, then registers each multicolor LED. Brightness updates write one buffer word and either start a transfer or extend the pending transfer length. The IRQ completes transfers and starts any queued transfer.

State and persistence: the transfer buffer mirrors LED color state across writes. `xfer_active` and `next_length` persist scheduling state under spinlock. Suspend waits for active transfers to finish, then disables clocks and asserts reset; resume restores format/timing/interrupt setup.

Dependencies and integration points: platform resources, MMIO, clocks, reset controller, DMA engine, IRQs, LED multicolor class, OF/fwnode properties, and PM ops.

Risks and test signals: validate DMA fallback to PIO, interrupt-driven queueing, suspend waiting without deadlock, address gaps, pixel-format mapping, timing calculations with zero clock rate, and cleanup after partial multicolor registration failure. Hardware tests should inspect actual color order and reset timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-sun50i-a100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-sunfire.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-sunfire.c

Purpose: Sun Fire clockboard and FHC board LED driver for Ultra Enterprise systems. It registers three LEDs per board and manipulates UPA/FHC control register bits.

Important APIs, types, and functions: `struct sunfire_led` stores a class device and MMIO register pointer. `struct led_type` maps LED name, set handler, and optional trigger. `__clockboard_set()` and `__fhc_set()` implement per-bit polarity rules. `sunfire_led_generic_probe()` handles allocation and registration for both board types. Two platform drivers bind to `sunfire-clockboard-leds` and `sunfire-fhc-leds`.

Control flow: module init registers both platform drivers. Each probe requires exactly one resource, allocates a three-LED container, assigns the resource start as the register address for each LED, and registers the three class devices. Brightness callbacks read-modify-write the shared register, with left LEDs active-low and other positions active-high.

State and persistence: LED state is the hardware register. The driver does not lock register updates, so concurrent LED writes could race on shared read-modify-write operations.

Dependencies and integration points: SPARC UPA accessors, FHC/clockboard register bit definitions, platform resources provided by architecture code, and the LED trigger subsystem. Right LEDs use `heartbeat` default triggers.

Risks and test signals: test resource-count validation, polarity for left/middle/right bits, multi-driver registration/unregistration, and concurrent updates to LEDs on the same register. Architecture-level integration is required because the register pointer is not ioremap-managed in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-sunfire.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-syscon.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-syscon.c

Purpose: generic syscon-backed register-bit LED driver. It exposes a LED whose state is one bit in a parent syscon regmap.

Important APIs, types, and functions: `struct syscon_led` stores LED class device, parent regmap, register offset, mask, and cached boolean state. `syscon_led_set()` writes the bit with `regmap_update_bits()`. `syscon_led_probe()` reads `reg` or legacy `offset`, reads `mask`, applies default state, and registers the LED with fwnode init data.

Control flow: probe requires a parent device and parent syscon regmap, allocates state, parses properties, handles `default-state` as on/off/keep, then registers the LED. Brightness set maps off to zero and any nonzero brightness to the mask value.

State and persistence: hardware register bit is authoritative; `state` tracks the last known driver state but is not exposed through a get callback. `LEDS_DEFSTATE_KEEP` reads the current register bit at probe.

Dependencies and integration points: syscon MFD/regmap, OF, LED class, built-in platform driver, compatible `register-bit-led`, and `suppress_bind_attrs` to avoid manual bind/unbind.

Risks and test signals: test default-state handling, mask/offset parsing, parent regmap lookup errors, and shared register updates with other syscon consumers. Since there is no lock beyond regmap internals, concurrent updates rely on `regmap_update_bits()` atomicity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-syscon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-tca6507.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-tca6507.c

Purpose: I2C driver for TI TCA6507, a 7-output LED/GPO controller with limited hardware brightness banks and two blink engines. It exposes selected outputs as LED class devices and optionally as output-only GPIOs.

Important APIs, types, and functions: `struct tca6507_chip` contains the shadow register file, pending register bitmask, bank allocation state, I2C client, work item, spinlock, LED array, and optional GPIO chip. `choose_times()` maps requested millisecond delays to hardware time-code pairs. `led_prepare()`, `led_release()`, and `led_assign()` allocate brightness/blink banks. `tca6507_work()` writes dirty registers asynchronously. `tca6507_led_dt_init()` builds platform-data-like LED info from child nodes.

Control flow: probe validates I2C support and DT children, allocates chip state, registers LED devices for non-GPIO child entries, registers GPIOs for child entries compatible with `gpio`, initializes all registers to zero through scheduled work, and returns. Brightness and blink callbacks update per-LED desired state, re-run bank allocation under spinlock, and schedule I2C work if any shadow register changed.

State and persistence: the shadow `reg_file` is the driver's source of desired hardware state. Bank use counters track shared hardware brightness/timing resources and are recalculated when LEDs change. Hardware writes are asynchronous, so remove cancels work to flush/stop pending I2C operations.

Dependencies and integration points: I2C, LED class, optional gpiolib, firmware property parsing, workqueues, and compatible `ti,tca6507`.

Risks and test signals: the allocator is the main risk: test bank sharing, default vs explicit blink delays, fallback to software blink on unsupported times, brightness approximation, GPIO inverse semantics, work cancellation on remove, and concurrent LED/GPIO operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-tca6507.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-ti-lmu-common.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-ti-lmu-common.c

Purpose: shared helper library for TI LMU LED drivers. It exports brightness, ramp, and firmware-property helpers used by chip-specific LMU LED drivers.

Important APIs, types, and functions: `ti_lmu_common_set_brightness()` writes 8-bit or 11-bit brightness using `ti_lmu_bank` register metadata. `ti_lmu_common_set_ramp()` converts configured ramp-up/down microseconds into packed register nibbles. `ti_lmu_common_get_ramp_params()` reads `ramp-up-us` and `ramp-down-us`. `ti_lmu_common_get_brt_res()` reads `ti,brightness-resolution` from device or child fwnode and clamps it to supported max.

Control flow: callers populate a `struct ti_lmu_bank` with regmap and register addresses, then call exported helpers during probe or LED callbacks. Brightness updates write LSB bits first for 11-bit mode, then the MSB register. Ramp conversion chooses the nearest entry from a fixed 16-value table.

State and persistence: no private state; all state is held by caller-owned `ti_lmu_bank` and hardware registers. The helper mutates ramp and max-brightness fields based on firmware properties.

Dependencies and integration points: regmap through `linux/leds-ti-lmu-common.h`, fwnode/property APIs, and exported GPL symbols.

Risks and test signals: test 8-bit versus 11-bit register writes, ramp table boundaries and nearest-neighbor behavior, missing property warnings, invalid brightness resolution clamping, and callers passing complete register metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-ti-lmu-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-tlc591xx.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-tlc591xx.c

Purpose: I2C LED driver for TI TLC59116 and TLC59108 PWM LED controllers. It registers child-node LEDs and drives each output as off, on, or PWM-dimmed.

Important APIs, types, and functions: `struct tlc591xx_led` tracks active channel, LED class device, and parent. `struct tlc591xx_priv` stores the regmap and LEDOUT offset. Per-chip `struct tlc591xx` data selects max LED count and LEDOUT register base. `tlc591xx_set_mode()` initializes MODE registers, `tlc591xx_set_ledout()` changes 2-bit output mode, and `tlc591xx_set_pwm()` writes per-channel PWM.

Control flow: probe requires an OF node and match data, validates child count, initializes I2C regmap, sets dim mode, then iterates child nodes. Each child must provide unique `reg`; the driver registers an LED with max brightness 256 and blocking brightness callback. Brightness 0 selects output-low off, max brightness selects on/HI-Z mode, and intermediate brightness selects dim mode plus PWM value.

State and persistence: active channel flags prevent duplicate registration. Runtime state is stored in chip registers via regmap, with no explicit cached brightness.

Dependencies and integration points: I2C, regmap, OF child nodes, LED class, compatibles `ti,tlc59116` and `ti,tlc59108`.

Risks and test signals: max brightness is 256, not U8_MAX, so test boundary values 0, 255, and 256. Validate duplicate/out-of-range `reg`, MODE register setup, LEDOUT bit packing, and behavior for chips with 8 versus 16 outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-tlc591xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-tps6105x.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-tps6105x.c

Purpose: platform LED driver for TPS6105x devices operating in torch mode. It exposes the torch current control as a LED class device.

Important APIs, types, and functions: `struct tps6105x_priv` stores regmap, LED class device, and optional child fwnode. `tps6105x_brightness_set()` writes `TPS6105X_REG0_TORCHC_MASK` according to brightness. `tps6105x_led_probe()` validates torch mode, sets mode bits, and registers the LED as `tps6105x:*:torch`.

Control flow: probe receives parent MFD/platform data, exits if the chip is not configured for torch mode, gets an optional child fwnode from the parent, registers a cleanup action to put it, programs register 0 for torch mode, and registers the class device with max brightness 7.

State and persistence: hardware register 0 contains mode and torch current state. The fwnode reference is lifetime-managed through a devm action. No explicit remove action is required because LED registration is devm-managed.

Dependencies and integration points: TPS6105x MFD platform data and regmap, platform device, LED class extended registration, optional firmware child node.

Risks and test signals: test non-torch-mode probe rejection, fwnode absence, brightness values 0-7 mapping to shifted register bits, mode programming preserving unrelated bits, and cleanup of child fwnode references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-tps6105x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-turris-omnia.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-turris-omnia.c

Purpose: I2C LED driver for the CZ.NIC Turris Omnia MCU LED controller. It exposes up to twelve RGB multicolor LEDs, a private hardware trigger for MCU control, and controller-wide brightness/gamma sysfs attributes.

Important APIs, types, and functions: `struct omnia_led` stores multicolor LED state, cached RGB channels, on/off state, hardware-trigger state, and MCU LED number. `struct omnia_leds` stores client, mutex, feature flags, brightness sysfs knode, and LED array. `omnia_led_brightness_set_blocking()` sends color and state commands. `omnia_hwtrig_activate()`/`_deactivate()` switch MCU/software mode. `omnia_led_register()` validates DT and registers each multicolor LED. Controller attributes use `OMNIA_CMD_GET/SET_BRIGHTNESS` and gamma commands.

Control flow: probe counts child LEDs, queries the sibling MCU at address 0x2a for supported features, optionally requests a brightness-change IRQ, registers the private trigger, and registers each valid child LED. Brightness changes recalculate RGB with `led_mc_calc_color_components()`, avoid redundant color commands through cached channels, and then send state changes when needed.

State and persistence: cached per-channel values and `on/hwtrig` booleans prevent redundant MCU commands and preserve mode decisions. Remove restores all LEDs to default hardware-triggered white mode. Brightness sysfs notification caches a kernfs node after the first IRQ.

Dependencies and integration points: Turris Omnia MCU command interface, I2C, LED multicolor and trigger APIs, OF child nodes, sysfs attributes, threaded IRQ, and MCU feature discovery.

Risks and test signals: test feature detection fallback, missing IRQ with brightness interrupt support, gamma unsupported writes, hardware-trigger transitions while off, cached color consistency, invalid child nodes being skipped, and remove-time global restore. Commands share MCU state with other Omnia functions, so cross-driver integration matters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-turris-omnia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-upboard.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-upboard.c

Purpose: platform LED driver for UP Board FPGA-managed status LEDs. It exposes board-specific LED profiles through regmap fields in the parent FPGA MFD.

Important APIs, types, and functions: `struct upboard_led` stores one regmap field and LED class device. `struct upboard_led_profile` maps LED names to bit positions. `upboard_led_brightness_get()` reads the bit, and `upboard_led_brightness_set()` writes boolean brightness. `upboard_led_probe()` chooses the UP or UP2 profile from parent FPGA type and registers one LED per profile entry.

Control flow: probe gets the parent `struct upboard_fpga`, selects the static profile array, allocates each LED, creates a field for `UPBOARD_REG_FUNC_EN0` bit `bit`, assigns get/set callbacks and name, and registers each LED with devm.

State and persistence: state is the FPGA register bit. The driver has no aggregate private state and relies on devm allocations. Brightness max is `LED_ON`, so LEDs are binary.

Dependencies and integration points: UP Board FPGA MFD, regmap fields, platform devices, LED class, and two board type profiles.

Risks and test signals: test unknown FPGA type rejection, per-bit field allocation, read failure returning off, binary brightness writes, and correct LED naming/profile for UP versus UP2 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-upboard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-wm831x-status.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-wm831x-status.c

Purpose: LED class driver for WM831x status LEDs. It controls status LED mode, blink timing, duty cycle, and source selection through WM831x control registers.

Important APIs, types, and functions: `struct wm831x_status` caches class device, WM831x pointer, locks, register address/value, blink parameters, source, and brightness. `wm831x_status_set()` rebuilds and writes the control register. `wm831x_status_brightness_set()` updates brightness and clears blink on off. `wm831x_status_blink_set()` maps supported on/off timings to hardware duration and duty fields. The `src` sysfs attribute reads/writes one of `otp`, `power`, `charger`, or `soft`.

Control flow: probe gets a register resource, merges optional platform data, initializes locks, reads the current hardware register, derives startup brightness and source, sets LED class callbacks/groups, and registers the LED. Brightness/blink/src updates mutate cached fields under spinlock or mutex and call `wm831x_status_set()`.

State and persistence: `reg_val` mirrors the control register and preserves unspecified bits across updates. Hardware startup state can be preserved for source when platform data requests it. Remove unregisters the LED but does not reset hardware.

Dependencies and integration points: WM831x MFD core/status definitions, platform resources/data, LED class, sysfs attribute groups, and platform device ids.

Risks and test signals: supported blink timing is narrow and ratio-based; test invalid timings, 62/63 ms handling, source sysfs parsing, platform-data preserve/default behavior, concurrent brightness/src writes, and register read/write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-wm831x-status.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-wm8350.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-wm8350.c

Purpose: LED class driver for WM8350 current-sink LEDs. It maps LED brightness to a hardware current-limit table and manages the ISINK and DCDC regulators needed to drive the LED.

Important APIs, types, and functions: the `isink_cur[]` table lists supported current levels. `wm8350_led_enable()` enables ISINK then DCDC; `wm8350_led_disable()` disables DCDC then ISINK and attempts rollback on ISINK disable failure. `wm8350_led_set()` scales `LED_FULL` brightness to `max_uA_index`, sets current limit, and enables/disables supplies. Probe validates platform data, gets regulators, computes max current index, and registers the LED.

Control flow: probe requires `wm8350_led_platform_data`, obtains `led_isink` and `led_vcc`, initializes classdev name/default trigger/suspend flag, detects current enabled state, computes the nearest supported max current, and registers. Brightness off disables regulators; nonzero brightness updates current and enables power.

State and persistence: `enabled` tracks regulator state, and `value` stores current brightness under `value_lock`. Shutdown forces off and disables supplies. Remove unregisters and disables.

Dependencies and integration points: WM8350 PMIC platform data, regulator framework, LED class, platform device lifecycle.

Risks and test signals: validate max current boundary handling, regulator enable/disable rollback paths, current index scaling at low brightness, suspend/resume flag behavior, shutdown off behavior, and platform-data absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-wm8350.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-wrap.c -->
# sources/distributed-fs/ceph-client/drivers/leds/leds-wrap.c

Purpose: legacy PCEngines WRAP board LED driver using SCx200 GPIO helpers. It registers three binary LEDs: power, error, and extra.

Important APIs, types, and functions: `wrap_power_led_set()`, `wrap_error_led_set()`, and `wrap_extra_led_set()` drive fixed GPIO numbers 2, 3, and 18. Three static `led_classdev` instances define names and callbacks. `wrap_led_probe()` registers all three devices with devm. Module init detects SCx200 GPIO availability, registers a platform driver, and creates a simple platform device.

Control flow: module init exits if `scx200_gpio_present()` is false. Otherwise it registers the driver and a synthetic device. Each brightness callback uses active-low GPIO semantics: nonzero brightness calls `scx200_gpio_set_low()`, off calls `set_high()`.

State and persistence: no private per-device state beyond the global platform device pointer and static classdevs. Hardware GPIO levels hold LED state. The power LED defaults to the `default-on` trigger and all LEDs request suspend/resume handling.

Dependencies and integration points: SCx200 GPIO support, platform device/driver core, LED class, and module init/exit lifecycle.

Risks and test signals: test SCx200 detection, active-low polarity, all three devm registrations, platform device error cleanup, module unload order, and default trigger behavior on real WRAP hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds-wrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds.h -->
# sources/distributed-fs/ceph-client/drivers/leds/leds.h

Purpose: private LED core header used inside the LED subsystem. It exposes internal helpers and global LED lists to LED core implementation files, not to generic driver consumers.

Important APIs, types, and functions: `led_get_brightness()` inline returns `led_cdev->brightness`. Declarations include `led_init_core()`, `led_stop_software_blink()`, `led_set_brightness_nopm()`, `led_set_brightness_nosleep()`, and binary attribute handlers `led_trigger_read()`/`led_trigger_write()`. It also declares `leds_list_lock` and `leds_list`.

Control flow: there is no executable control flow beyond the inline getter. Including source files use these declarations to initialize LEDs, manage software blink, perform non-PM brightness updates, and expose trigger data through sysfs/bin attributes.

State and persistence: the header declares subsystem-global LED registry state: an RW semaphore and list head. Actual storage and lifetime are defined elsewhere.

Dependencies and integration points: includes `linux/rwsem.h` and public `linux/leds.h`. It is an internal integration point between LED core files and trigger code.

Risks and test signals: risks are ABI/API internal consistency rather than runtime behavior. Build tests should catch signature drift. LED core tests should verify list locking, brightness updates in sleep/nosleep contexts, and trigger read/write paths that rely on these declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/leds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/rgb/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/leds/rgb/Kconfig

Purpose: Kconfig menu for RGB and multicolor LED drivers under `drivers/leds/rgb`, gated by `LEDS_CLASS_MULTICOLOR`.

Important APIs, types, and functions: this is build configuration, not C code. It defines `LEDS_GROUP_MULTICOLOR`, `LEDS_KTD202X`, `LEDS_LP5812`, `LEDS_NCP5623`, `LEDS_PWM_MULTICOLOR`, `LEDS_QCOM_LPG`, and `LEDS_MT6370_RGB`. Each option declares dependencies such as `OF`, `I2C`, `PWM`, `SPMI`, or `MFD_MT6370`, plus selected helpers such as `REGMAP_I2C` and `LINEAR_RANGES`.

Control flow: menu visibility depends on `LEDS_CLASS_MULTICOLOR`. When an option is `y` or `m`, the matching Makefile object is compiled. Help text describes hardware support and module names.

State and persistence: Kconfig choices persist in kernel `.config` and control which drivers are available. There is no runtime state.

Dependencies and integration points: ties driver source files to kernel configuration symbols and dependency resolution. Some symbols referenced here, such as Qualcomm LPG, are outside this work item but share the same directory.

Risks and test signals: validate dependency completeness with randconfig/allmodconfig, especially that multicolor class dependencies are sufficient for every object. Ensure module names in help text match Makefile outputs and that `select` entries cover required helper libraries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/rgb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/rgb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/leds/rgb/Makefile

Purpose: build map from RGB LED Kconfig symbols to object files.

Important APIs, types, and functions: not executable code; it lists `obj-$(CONFIG_...) += ...` for group multicolor, KTD202x, LP5812, NCP5623, PWM multicolor, Qualcomm LPG, and MT6370 RGB drivers.

Control flow: Kbuild includes an object when the corresponding configuration symbol is built in or modular. Module names follow object names without `.o`.

State and persistence: build-system state only. It does not create runtime state.

Dependencies and integration points: integrates the RGB driver directory with Kbuild and the Kconfig symbols defined in the sibling `Kconfig`.

Risks and test signals: build tests should confirm each listed object exists in the tree and each object has a corresponding reachable Kconfig symbol. Allmodconfig and per-symbol module builds are the relevant validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/rgb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-group-multicolor.c -->
# sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-group-multicolor.c

Purpose: creates one multicolor LED class device from several already-registered monochrome LED devices. It keeps grouped color state consistent and disables direct writes to the underlying LEDs while the group exists.

Important APIs, types, and functions: `struct leds_multicolor` stores the multicolor class device and array of monochrome classdev pointers. `leds_gmc_set()` scales group brightness and per-subled intensity to each monochrome LED's max brightness. `leds_gmc_probe()` obtains referenced LEDs with `devm_of_led_get_optional()`, builds subled metadata, registers a multicolor device, initializes output, and disables individual LED sysfs write access. `restore_sysfs_write_access()` reverses that on devm cleanup.

Control flow: probe repeatedly fetches LED phandles until none remain, records common suspend/resume flags, allocates subleds, derives color from each source LED, registers the group, applies initial brightness, then disables each source LED's sysfs access under `led_access`.

State and persistence: the grouped class device stores subled intensities; underlying LEDs remain separate class devices but their sysfs write access is disabled for consistency. State persists only in LED core devices and hardware behind the monochrome LEDs.

Dependencies and integration points: OF LED lookup, LED class internals (`led_sysfs_disable/enable`), LED multicolor class, and compatible `leds-group-multicolor`.

Risks and test signals: test zero referenced LEDs, scaling with differing max brightness values, sysfs access restoration on probe failure/remove, suspend flag propagation, and interactions with triggers already attached to child monochrome LEDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-group-multicolor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-ktd202x.c -->
# sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-ktd202x.c

Purpose: I2C driver for Kinetic KTD2026/KTD2027 RGB/white LED controllers. It supports single-channel LEDs and grouped multicolor LEDs with brightness and hardware blink.

Important APIs, types, and functions: `struct ktd202x` stores mutex, regulators, regmap, enabled flag, chip channel count, and LED array. `struct ktd202x_led` is either a regular LED or multicolor LED. `ktd202x_chip_enable()/disable()` manage regulators and sleep/wake register. `ktd202x_brightness_set()` writes current registers and channel-control modes. `ktd202x_blink_set()` converts requested delays to flash-period and on-time register values. Setup helpers parse single or RGB child layouts.

Control flow: probe counts children, initializes regmap/mutex/regulators, enables regulators for reset and registration, resets the chip, registers each child LED, then disables regulators until needed. Brightness paths set the classdev brightness, lock the chip, compute subled brightness for multicolor, write current and channel mode, and power the chip down when no LEDs are in use. Blink defaults to 500/500 ms and uses PWM1 mode.

State and persistence: LED brightness in classdevs is used to determine whether the chip is in use. Regcache defaults describe reset state, but hardware power is explicitly disabled when idle. Shutdown resets registers to ensure LEDs are off.

Dependencies and integration points: I2C, regmap with flat cache, regulator bulk supplies `vin`/`vio`, fwnode child parsing, LED and multicolor APIs, compatibles `kinetic,ktd2026`/`ktd2027`.

Risks and test signals: test regulator enable/disable sequencing, chip-in-use logic around the current LED being updated, single versus RGB parsing, blink delay quantization, no-off/no-on blink edge cases, and shutdown reset. Validate child channel bounds and that multicolor channel control cannot mix blink and steady-on unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-ktd202x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-lp5812.c -->
# sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-lp5812.c

Purpose: I2C driver for TI LP5812, a matrix RGB LED driver with direct, time-coded, and mix drive modes. This implementation registers single-color and multicolor LED class devices and uses manual PWM/DC controls.

Important APIs, types, and functions: low-level `lp5812_write()`/`lp5812_read()` implement the chip's 10-bit register addressing by folding high address bits into the I2C address. `parse_drive_mode()` maps DT/sysfs-style mode strings to drive mode and scan-order fields. `lp5812_set_led_mode()`, `lp5812_manual_dc_pwm_control()`, `lp5812_set_brightness()`, and `lp5812_set_mc_brightness()` program channel mode and PWM. DT parsing is split across `lp5812_parse_led_channel()`, `lp5812_parse_led()`, and `lp5812_of_probe()`.

Control flow: probe parses child LED definitions and optional `ti,scan-mode`, initializes the chip, allocates LED objects, and registers each channel. Initialization enables the device, sets safety thresholds, programs drive mode/scan order, and commits configuration with `LP5812_CMD_UPDATE`. Registration writes max current to auto/manual DC registers, puts LEDs in manual mode, and enables each LED output.

State and persistence: `struct lp5812_chip` stores parsed channel config, mode, scan order, and mutex. Hardware registers hold enable, manual PWM/DC, and drive configuration. Remove disables LED enable registers and device enable.

Dependencies and integration points: raw I2C transfers, LED/multicolor class, OF properties, mutex locking, and local `leds-lp5812.h` definitions.

Risks and test signals: test 10-bit register-address encoding, scan-mode string coverage, config-update error bit handling, single versus child-channel multicolor parsing, max-current unit conversion, output-enable bit packing, and remove-time deinit. The code stores LED pointers in `dev->platform_data`, so check for unintended conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-lp5812.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-lp5812.h -->
# sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-lp5812.h

Purpose: private header for the LP5812 LED driver. It centralizes register addresses, bit constants, mode names, packed configuration unions, and driver state structures.

Important APIs, types, and functions: register defines cover device enable/configuration, update, LED enables, fault clear, manual/auto DC/PWM bases, and status registers. `union lp5812_scan_order` and `union lp5812_drive_mode` provide byte-level register packing. `struct lp5812_mode_mapping` describes text-to-mode mappings. `struct lp5812_led_config`, `struct lp5812_chip`, and `struct lp5812_led` define parsed firmware config, chip-wide state, and per-LED state.

Control flow: no executable logic is present. The C file consumes constants and structures to parse device tree, program mode registers, and register LED class devices.

State and persistence: state definitions include parsed channel count, label, scan mode string, mutex, I2C client, drive-mode register byte, and per-LED brightness/class devices.

Dependencies and integration points: includes LED, multicolor, I2C, mutex, sysfs, and type headers. The header is local to the RGB driver directory.

Risks and test signals: build tests catch structure/constant drift. Driver tests should ensure bitfield packing matches the datasheet for compiler assumptions, and that arrays sized by `LED_COLOR_ID_MAX` are large enough for all parsed color channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-lp5812.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-mt6370-rgb.c -->
# sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-mt6370-rgb.c

Purpose: MediaTek/Richtek MT6370/MT6371/MT6372 RGB indicator driver. It supports independent current-sink LEDs and virtual multicolor LEDs with brightness, PWM blink, and breath-pattern modes.

Important APIs, types, and functions: `struct mt6370_priv` stores mutex, parent regmap, regmap fields, chip-specific field/range/pdata tables, active LED bitmap, and LED array. `mt6370_check_vendor_info()` selects MT6372 versus common register maps. Brightness helpers set current, duty, frequency, and mode fields. `mt6370_gen_breath_pattern()` converts six LED pattern entries into three packed bytes. Separate callback families implement multicolor (`mt6370_mc_*`) and single ISINK (`mt6370_isnk_*`) behavior.

Control flow: probe counts child nodes, gets parent regmap, selects chip metadata from vendor ID, bulk-allocates regmap fields, then parses each child. RGB/MULTI colors become virtual multicolor devices with child channels; other nodes become single current sinks. Registration initializes max brightness from `led-max-microamp`, default state, CHRIND software control for ISINK4, and the proper LED class device type.

State and persistence: `leds_active` prevents duplicate channel use across single and multicolor devices. Hardware mode/current/enable state persists in PMIC registers. Default-state keep reads current level and enable bit before programming the LED.

Dependencies and integration points: platform child of MT6370 MFD, parent regmap, regmap fields, linear ranges, LED/multicolor/pattern APIs, fwnode properties, and compatible `mediatek,mt6370-indicator`.

Risks and test signals: test vendor-specific register maps and ranges, multicolor child validation, duplicate channel detection including virtual RGB bit use, frequency out-of-range returning `-EOPNOTSUPP`, breath pattern length handling, enable toggling to synchronize timing, and ISINK4 charger-indicator takeover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-mt6370-rgb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-ncp5623.c -->
# sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-ncp5623.c

Purpose: I2C multicolor LED driver for ON Semiconductor NCP5623 triple-output RGB controller. It supports global brightness and simple hardware dimming patterns.

Important APIs, types, and functions: `struct ncp5623` stores I2C client, multicolor class device, mutex, current brightness, and a jiffies delay guard while dimming is in progress. `ncp5623_write()` performs the chip's command-style SMBus write. `ncp5623_brightness_set()` writes per-channel PWM intensity, disables dimming time, and writes global current. `ncp5623_pattern_set()` programs an upward/downward step or direct brightness change and calculates when the hardware transition should finish.

Control flow: probe requires a named `multi-led` child node, allocates subled metadata from its children, initializes callbacks and default `pattern` trigger, registers the multicolor LED, and stores client data. Brightness and pattern writes are rejected with `-EBUSY` while a prior dimming transition is still in progress.

State and persistence: `current_brightness` mirrors the global brightness target; `delay` prevents overlapping hardware transitions. Remove clears delay, disables dimming time, unregisters, and destroys the mutex. Shutdown sends chip shutdown unless LED core retention is requested.

Dependencies and integration points: I2C SMBus, LED multicolor/pattern APIs, firmware child-node parsing, jiffies timing, and compatible `onnn,ncp5623`.

Risks and test signals: test busy-window timing, dimming time constraints and 8 ms granularity, brightness-difference edge case of one step, subled parsing failures with fwnode release, shutdown retention flag, and behavior when brightness is set during hardware fade.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-ncp5623.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-pwm-multicolor.c -->
# sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-pwm-multicolor.c

Purpose: generic platform driver for PWM-backed multicolor LEDs. It expects a `multi-led` child node containing PWM-backed monochrome color channels and exposes them as one multicolor LED class device.

Important APIs, types, and functions: `struct pwm_led` stores per-channel PWM device, cached state, and active-low flag. `struct pwm_mc_led` stores multicolor class device, mutex, and flexible channel array. `led_pwm_mc_set()` calculates subled brightness, scales each to PWM duty, applies active-low inversion, and calls `pwm_apply_might_sleep()`. `iterate_subleds()` acquires PWMs and color properties for child nodes. `led_pwm_mc_probe()` parses the group node and registers the multicolor LED.

Control flow: probe obtains the named `multi-led` node, counts channels, allocates state and subled array, reads group `max-brightness`, parses each child PWM/color, registers the multicolor LED, applies initial brightness, and stores driver data. Brightness writes lock the channel array and program all PWMs in order.

State and persistence: cached PWM states hold period, duty, enabled flag, and polarity for each channel. As with the single-color PWM driver, PWMs are kept enabled unless the LED core marks the device suspended.

Dependencies and integration points: PWM framework, LED multicolor class, fwnode parsing, platform driver, compatible `pwm-leds-multicolor`, and LED suspend/resume flag handling.

Risks and test signals: test missing `multi-led`, missing `max-brightness`, child PWM/color errors and fwnode release, active-low duty inversion, partial `pwm_apply` failure across channels, and suspend behavior. Hardware validation should verify color mixing and off-state electrical levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-pwm-multicolor.c -->
