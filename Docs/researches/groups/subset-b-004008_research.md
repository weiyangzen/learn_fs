# subset-b-004008 research

This grouped report covers Linux LED framework Kconfig/Makefile wiring plus blink and flash LED drivers under `sources/distributed-fs/ceph-client/drivers/leds`. Each section preserves the original source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/leds/Kconfig

## Purpose
This Kconfig file is the main LED subsystem configuration menu. It defines the framework-level symbols for LED core support, LED class devices, flash LEDs, multicolor LEDs, brightness hardware-change reporting, KUnit coverage, and a long list of concrete platform/I2C/SPI/MFD LED drivers. It also includes the subordinate blink, flash, RGB, trigger, and Simatic LED Kconfig files.

## Important APIs, Types, and Functions
The file is declarative Kconfig rather than C code. Its important "APIs" are symbols consumed by Makefiles and C preprocessor conditionals: `NEW_LEDS`, `LEDS_CLASS`, `LEDS_CLASS_FLASH`, `LEDS_CLASS_MULTICOLOR`, `LEDS_TRIGGERS`, `LEDS_EXPRESSWIRE`, and many `LEDS_*` driver symbols. It uses Kconfig primitives such as `menuconfig`, `config`, `depends on`, `select`, `default`, `source`, and `comment`.

## Control Flow
Configuration flow starts with helper symbols that can exist outside `NEW_LEDS`, then opens the `NEW_LEDS` menu. Enabling `NEW_LEDS` exposes framework classes and the driver menu. Driver symbols gate platform objects in `drivers/leds/Makefile`; subordinate files are sourced near the end so specialized blink, flash/torch, RGB, trigger, and Simatic drivers are only visible inside LED support.

## State and Persistence
Selected symbols persist in the kernel `.config` and determine whether LED framework code and drivers are built in, modular, or omitted. Runtime LED state is not handled here, but misconfiguration changes which runtime sysfs classes and device drivers can exist.

## Dependencies and Integration Points
The file integrates with architecture, bus, and subsystem symbols such as `GPIOLIB`, `I2C`, `SPI`, `OF`, `MFD_*`, `V4L2_FLASH_LED_CLASS`, `LEDS_CLASS_MULTICOLOR`, and `COMPILE_TEST`. `LEDS_EXPRESSWIRE` is intentionally outside `NEW_LEDS` because other subsystems can select it. The `source` lines are key integration points with `drivers/leds/blink/Kconfig` and `drivers/leds/flash/Kconfig`.

## Risks and Edge Cases
Incorrect `depends on` clauses can expose drivers without required bus/regmap/GPIO support or hide valid compile-test coverage. `select` use must remain conservative because it bypasses dependency checking for selected symbols. Moving subordinate `source` lines outside `if NEW_LEDS` would change menu visibility and build behavior. Framework symbols are shared by many drivers, so changing their type or defaults has broad build fallout.

## Test Signals
Useful signals are `olddefconfig`, `allyesconfig`, `allmodconfig`, and targeted `COMPILE_TEST` builds. Kconfig warnings about unmet direct dependencies, recursive dependencies, or unknown symbols are high-value signals. Runtime confirmation comes from the expected `/sys/class/leds`, flash class attributes, multicolor class attributes, and trigger availability matching the selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/Makefile -->
# sources/distributed-fs/ceph-client/drivers/leds/Makefile

## Purpose
This Makefile maps LED Kconfig symbols to build objects. It builds framework objects, individual LED platform/bus drivers, helper protocol code, and descends into flash, RGB, trigger, blink, and Simatic subdirectories.

## Important APIs, Types, and Functions
The important build interfaces are `obj-$(CONFIG_...) += ...` assignments. Framework objects include `led-core.o`, `led-class.o`, `led-class-flash.o`, `led-class-multicolor.o`, `led-triggers.o`, and `led-test.o`. Driver objects are kept mostly sorted. The directory recursions are `flash/`, `rgb/`, `trigger/`, `blink/`, and `simatic/`.

## Control Flow
Kbuild evaluates the selected `CONFIG_*` symbols and includes the associated objects in `vmlinux` or modules. `flash/` is only entered when `CONFIG_LEDS_CLASS_FLASH` is enabled, `rgb/` only with `CONFIG_LEDS_CLASS_MULTICOLOR`, and `trigger/` only with `CONFIG_LEDS_TRIGGERS`. `blink/` and `simatic/` are always descended into via `obj-y`, but their contents are still controlled by subdirectory Kconfig symbols.

## State and Persistence
The Makefile has no runtime state. Its persistent effect is build artifact composition: selected objects become built-in or module outputs according to their Kconfig tristate value.

## Dependencies and Integration Points
It is tightly coupled to `drivers/leds/Kconfig` symbol names and to object filenames in the same tree. `LEDS_EXPRESSWIRE` builds `leds-expresswire.o`, which is used by ExpressWire flash drivers such as KTD2692. The flash directory depends on the flash LED class object being built.

## Risks and Edge Cases
A missing object assignment makes an enabled Kconfig option silently produce no driver. A stale assignment to a removed file breaks builds. The comment says platform drivers should remain sorted; merge conflicts in this list are common. Recursive subdirectory entries must match framework availability or they can expose code before required class helpers exist.

## Test Signals
Build signals include successful `make drivers/leds/`, module generation for selected `LEDS_*` symbols, and no orphan Kconfig symbols without objects. `modinfo` names should match Kconfig help text for modular drivers. `allmodconfig` catches most stale object references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/blink/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/leds/blink/Kconfig

## Purpose
This file defines hardware blink-capable LED controller drivers. In this subset it exposes Broadcom BCM63138-family LED controller support and Intel Lightning Mountain SSO LED/GPIO support.

## Important APIs, Types, and Functions
The Kconfig symbols are `LEDS_BCM63138` and `LEDS_LGM`. `LEDS_BCM63138` is a tristate LED class driver for MMIO Broadcom SoC LED hardware. `LEDS_LGM` is a tristate driver requiring GPIO, LED class, syscon MFD, and OF support for the LGM Serial Shift Output controller.

## Control Flow
When included by the top-level LED Kconfig, these symbols become visible under LED support. Selecting them controls `drivers/leds/blink/Makefile`, which builds `leds-bcm63138.o` and `leds-lgm-sso.o`.

## State and Persistence
Selections persist in `.config` and determine whether the blink drivers are built in, modular, or omitted. Runtime LED state is owned by the corresponding C drivers.

## Dependencies and Integration Points
`LEDS_BCM63138` depends on `LEDS_CLASS`, `HAS_IOMEM`, `OF`, and Broadcom architecture or `COMPILE_TEST` symbols. `LEDS_LGM` depends on `X86 || COMPILE_TEST`, `GPIOLIB`, `LEDS_CLASS`, `MFD_SYSCON`, and `OF`. These dependencies reflect the drivers' MMIO/syscon, GPIO, and LED class integration.

## Risks and Edge Cases
The Broadcom default of `ARCH_BCMBCA` changes built-in default behavior for that platform. LGM depends on syscon regmap access rather than directly mapped resources, so enabling it without the right firmware node layout will still fail at probe. Kconfig dependency mistakes here can affect compile-test coverage for SoC-specific code.

## Test Signals
Run Kconfig builds with Broadcom, x86 LGM, and `COMPILE_TEST` configurations. Confirm selected symbols produce the expected modules and that disabled `NEW_LEDS` hides these entries. Runtime probe should bind OF compatibles `brcm,bcm63138-leds` and `intel,lgm-ssoled`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/blink/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/blink/Makefile -->
# sources/distributed-fs/ceph-client/drivers/leds/blink/Makefile

## Purpose
This small Makefile maps blink LED Kconfig symbols to driver objects.

## Important APIs, Types, and Functions
The object mappings are `obj-$(CONFIG_LEDS_BCM63138) += leds-bcm63138.o` and `obj-$(CONFIG_LEDS_LGM) += leds-lgm-sso.o`.

## Control Flow
When the top-level LED Makefile descends into `blink/`, Kbuild evaluates these assignments and includes the relevant objects according to each tristate symbol.

## State and Persistence
There is no runtime state. The persistent effect is whether the two driver objects are compiled into the kernel tree or emitted as modules.

## Dependencies and Integration Points
The file depends on symbol definitions in `drivers/leds/blink/Kconfig` and source files in the same directory. It is reached unconditionally from the parent Makefile, but object inclusion remains conditional.

## Risks and Edge Cases
Any rename mismatch between Kconfig, Makefile, and source filenames breaks the selected driver build. Because the parent descends unconditionally, stale entries are caught in broad builds even if only as disabled references in review.

## Test Signals
Enable `CONFIG_LEDS_BCM63138=m` and `CONFIG_LEDS_LGM=m` and confirm `leds-bcm63138.ko` and `leds-lgm-sso.ko` are produced. `allmodconfig` should catch missing include dependencies in both objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/blink/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/blink/leds-bcm63138.c -->
# sources/distributed-fs/ceph-client/drivers/leds/blink/leds-bcm63138.c

## Purpose
This platform driver controls the Broadcom BCM63138-family SoC LED hardware block, also used by related BCM49xx/68xx/63xx parts. It registers each firmware-described LED as a Linux LED class device with brightness and fixed-rate hardware blinking support.

## Important APIs, Types, and Functions
`struct bcm63138_leds` stores the device, MMIO base, and spinlock; `struct bcm63138_led` stores per-LED classdev state, pin number, and polarity. Register helpers are `bcm63138_leds_read()`, `bcm63138_leds_write()`, and `bcm63138_leds_update_bits()`. LED operations are `bcm63138_leds_brightness_set()` and `bcm63138_leds_blink_set()`. Probe and registration flow is in `bcm63138_leds_probe()` and `bcm63138_leds_create_led()`.

## Control Flow
Probe allocates private state, maps the MMIO resource, initializes global controller registers, optionally programs `brcm,serial-shift-bits`, disables hardware LED ownership, clears serial/parallel polarity, and iterates available child nodes. Each child must provide `reg`, may provide `active-low`, and is registered with `devm_led_classdev_register_ext()`. Brightness writes update `BCM63138_SW_DATA`; nonzero brightness programs one of four brightness registers, while zero also clears flash rate. Blink requests accept only equal on/off delays and map supported periods near 65, 140, 320, 640, and 1280 ms to hardware codes.

## State and Persistence
State is volatile and per platform device. The driver does not persist user settings across reboot or module unload. Hardware registers hold current brightness/blink state while the device is bound. Spinlock protection is used for read-modify-write sequences called from LED class callbacks.

## Dependencies and Integration Points
The driver depends on OF child nodes, `devm_platform_ioremap_resource()`, MMIO accessors, pinctrl defaults per LED, and LED class registration. It binds `brcm,bcm63138-leds` through a platform driver named `leds-bcm63xxx`.

## Risks and Edge Cases
`GENMASK(shift_bits - 1, 0)` assumes a nonzero valid `brcm,serial-shift-bits` value. Unsupported blink periods return `-EINVAL`; unequal delays are not approximated. LED child creation logs errors but does not fail the whole probe, so a partial LED set is possible. Pinctrl failure other than `-ENODEV` is only a warning after LED registration. Polarity and hardware-ownership register writes affect shared controller outputs globally.

## Test Signals
Use device-tree nodes with valid and invalid `reg` values, active-high and active-low LEDs, and optional pinctrl states. Validate sysfs brightness writes, fixed blink delays, rejection of unequal/unsupported blink delays, no races under concurrent trigger updates, and correct module binding on Broadcom OF compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/blink/leds-bcm63138.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/blink/leds-lgm-sso.c -->
# sources/distributed-fs/ceph-client/drivers/leds/blink/leds-lgm-sso.c

## Purpose
This platform driver supports the Intel Lightning Mountain Serial Shift Output controller as both a GPIO provider and an LED provider. It can drive up to 32 serial outputs, expose some pins as GPIOs, register LED class devices, and configure hardware blink or hardware-triggered outputs.

## Important APIs, Types, and Functions
Core structures are `struct sso_led_priv`, `struct sso_gpio`, `struct sso_led`, and `struct sso_led_desc`. LED callbacks include `sso_led_brightness_set()`, `sso_led_brightness_get()`, and `sso_led_blink_set()`. GPIO callbacks include `sso_gpio_request()`, `sso_gpio_free()`, `sso_gpio_dir_out()`, `sso_gpio_get()`, and `sso_gpio_set()`. Hardware setup is handled by `sso_gpio_hw_init()`, `sso_gpio_freq_set()`, `sso_register_shift_clk()`, `sso_init_freq()`, and `sso_led_hw_cfg()`. Probe/remove are `intel_sso_led_probe()` and `intel_sso_led_remove()`.

## Control Flow
Probe obtains `sso` and `fpid` clocks, enables them with a devm cleanup action, obtains a syscon regmap, initializes GPIO hardware and a gpiochip, initializes frequency tables, parses a named `ssoled` child node, and registers LED children. LED children require a GPIO descriptor and `reg`; optional properties set default trigger, suspend/shutdown retention, panic indicator, hardware blink, hardware trigger, blink rate, and default state. Brightness writes update the duty-cycle register and either drive the GPIO output or let hardware trigger state control the pin. Blink requests quantize delay to the closest supported controller frequency and enable the pin in `SSO_CON2`.

## State and Persistence
Runtime state is in `sso_led_priv` and linked `sso_led` objects. LED descriptor fields cache brightness, blink rate, selected frequency index, retention flags, and whether hardware blinking is currently active. GPIO allocation is tracked in `alloc_bitmap`. Nothing is persistent beyond the device binding, but `retain-state-*` flags influence LED core suspend/shutdown behavior.

## Dependencies and Integration Points
The driver uses clocks, syscon/regmap, GPIO consumer and provider APIs, firmware node LED properties, LED class registration, and platform OF matching for `intel,lgm-ssoled`. It registers a gpiochip named `lgm-sso` and LED class devices under device name `lgm-sso`.

## Risks and Edge Cases
The SSO controller has grouped blink encoding: group 0 pins do not get per-pin blink rate programming in `sso_led_freq_set()`. The code calls `regmap_exit()` on a syscon regmap in error/remove paths, which is unusual for regmaps not allocated by the driver and should be reviewed carefully against syscon lifetime rules. `gptc_clkrate` is set after `sso_init_freq()`, so GPTC-derived entries initially use zero unless later corrected by hardware defaults. LED parse errors unwind already registered LEDs, but list iteration during shutdown must remain safe. GPIO and LED users can contend for the same pins, so `alloc_bitmap` and firmware reservations matter.

## Test Signals
Validate gpiochip registration, GPIO output set/get, LED brightness, hardware blink rates, hardware-triggered LEDs, and retention flags. Test firmware with `ngpios`, `intel,sso-update-rate-hz`, `ssoled` children, invalid `reg`, and overlapping GPIO/LED pins. Suspend/resume and remove should leave clocks disabled and no registered LEDs or GPIOs dangling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/blink/leds-lgm-sso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/leds/flash/Kconfig

## Purpose
This Kconfig file defines flash and torch LED driver options that are only visible when `LEDS_CLASS_FLASH` is enabled. It covers GPIO/protocol flash parts, I2C flash controllers, PMIC/MFD flash blocks, and optional V4L2 flash LED class integration.

## Important APIs, Types, and Functions
The main symbols in this subset are `LEDS_AAT1290`, `LEDS_AS3645A`, `LEDS_KTD2692`, `LEDS_LM3601X`, `LEDS_MAX77693`, `LEDS_MT6360`, `LEDS_MT6370_FLASH`, `LEDS_QCOM_FLASH`, `LEDS_RT4505`, `LEDS_RT8515`, and `LEDS_SGM3140`. The file also defines nearby flash drivers such as `LEDS_SY7802` and `LEDS_TPS6131X`. Several entries use `depends on V4L2_FLASH_LED_CLASS || !V4L2_FLASH_LED_CLASS` so the LED driver can build whether V4L2 flash support is enabled or not.

## Control Flow
The whole file is wrapped in `if LEDS_CLASS_FLASH`. Each selected symbol maps to an object in `drivers/leds/flash/Makefile`. `select REGMAP_I2C` and `select LEDS_EXPRESSWIRE` pull helper code needed by particular drivers.

## State and Persistence
Selections persist in kernel configuration and determine build inclusion. Runtime flash timeout, torch current, strobe state, and V4L2 subdevice state are handled by the C drivers, not this file.

## Dependencies and Integration Points
Dependencies connect drivers to I2C, GPIO, OF, pinctrl, MFD parents, multicolor LED class, and V4L2 flash class. PMIC drivers depend on their MFD parent symbols (`MFD_MAX77693`, `MFD_MT6360`, `MFD_MT6370`, `MFD_SPMI_PMIC`). KTD2692 selects the LED ExpressWire helper.

## Risks and Edge Cases
Flash LED drivers often expose camera-facing V4L2 subdevices when available. Incorrect V4L2 dependency expressions can break either media-disabled or media-enabled builds. PMIC dependencies must match actual parent regmap providers. Since the file is inside `LEDS_CLASS_FLASH`, adding a driver that only uses plain LED class here would unnecessarily hide it.

## Test Signals
Run `allmodconfig`, `allyesconfig`, media-disabled, and PMIC-specific builds. Confirm each selected symbol produces its module and that V4L2-enabled builds register flash subdevice hooks without requiring V4L2 in media-disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/Makefile -->
# sources/distributed-fs/ceph-client/drivers/leds/flash/Makefile

## Purpose
This Makefile maps flash and torch LED Kconfig symbols to their driver objects.

## Important APIs, Types, and Functions
The file contains Kbuild object assignments for MT6360, MT6370, AAT1290, AS3645A, KTD2692, LM3601X, MAX77693, Qualcomm flash, RT4505, RT8515, SGM3140, SY7802, and TPS6131X drivers.

## Control Flow
The parent LED Makefile enters `flash/` only when `CONFIG_LEDS_CLASS_FLASH` is enabled. Within this directory, each `obj-$(CONFIG_LEDS_*)` line includes the matching driver object as built-in or module according to its Kconfig tristate.

## State and Persistence
No runtime state exists in this file. The persistent effect is build composition and module naming.

## Dependencies and Integration Points
The file depends on `drivers/leds/flash/Kconfig` symbols and matching C source filenames. Driver objects rely on LED flash class helpers from the parent directory.

## Risks and Edge Cases
Missing or stale entries make enabled Kconfig symbols fail to build or produce no object. Ordering is not strictly sorted in all groups, so adding new objects should minimize merge churn while preserving readable grouping.

## Test Signals
Enable each flash Kconfig symbol as `m` and confirm the expected `.ko` file is produced. Broad `allmodconfig` catches stale filenames and missing helper dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-aat1290.c -->
# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-aat1290.c

## Purpose
This platform driver supports the Skyworks AAT1290 flash LED current regulator. It drives the part through FLEN and EN/SET GPIOs using the AS2Cwire pulse protocol, registers a flash LED class device, and optionally exposes a V4L2 flash subdevice.

## Important APIs, Types, and Functions
`struct aat1290_led` stores GPIOs, mutex, flash class device, V4L2 handle, movie-mode current scale, and mode cache. `struct aat1290_led_config_data` stores device-tree current/timeout limits. Protocol programming is `aat1290_as2cwire_write()`. LED operations are `aat1290_led_brightness_set()`, `aat1290_led_flash_strobe_set()`, and `aat1290_led_flash_timeout_set()`. Configuration helpers include `aat1290_led_parse_dt()`, `init_mm_current_scale()`, `aat1290_led_validate_mm_current()`, and `aat1290_init_flash_timeout()`.

## Control Flow
Probe allocates state, reads GPIOs and the first LED child node, initializes current scales from `flash-max-microamp`, validates `led-max-microamp`, registers `led_classdev_flash`, and creates a V4L2 flash device. Torch/movie brightness writes enter movie mode if needed, program current ratio, write current level, and enable movie mode. Flash strobe writes the cached timeout into the safety timer immediately before enabling FLEN. Strobe-off clears both GPIO lines and resets the software brightness/movie-mode cache.

## State and Persistence
State is volatile. `movie_mode` prevents redundant ratio programming while torch mode is active. The LED flash core caches timeout because directly writing the timer register can spuriously turn torch mode on. The nonlinear movie current scale is retained only when V4L2 flash class is enabled because V4L2 conversion callbacks need it.

## Dependencies and Integration Points
The driver depends on GPIO descriptors `flen` and `enset`, OF child properties `led-max-microamp`, `flash-max-microamp`, and `flash-max-timeout-us`, optional pinctrl states for external strobe source switching, LED flash class registration, and V4L2 flash integration. It binds `skyworks,aat1290`.

## Risks and Edge Cases
The macro `AAT1290_MM_TO_FL_RATIO` is integer arithmetic (`1000 / 1920`) and evaluates to zero, which can collapse default movie current calculations; this is a high-value review target. `aat1290_led_parse_dt()` assigns a `__free(device_node)` child to `*sub_node`, which needs care because the returned node must stay valid for later registration. Flash timer writes are deliberately delayed to strobe time due to side effects. External strobe switching depends on pinctrl state names `isp` and `host`.

## Test Signals
Test GPIO pulse timing with a scope or logic analyzer, torch brightness levels, flash strobe timeout programming, V4L2 intensity conversion, and external strobe pinctrl switching. Device-tree tests should cover missing child nodes and missing current/timeout properties. Verify no use-after-put for the LED child fwnode during probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-aat1290.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-as3645a.c -->
# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-as3645a.c

## Purpose
This I2C driver supports AS3645A, LM3555, and compatible flash controllers. It registers a flash/assist LED and an indicator LED, programs current, timeout, control, and boost registers, and exposes V4L2 flash and indicator subdevices.

## Important APIs, Types, and Functions
`struct as3645a` stores the I2C client, mutex, flash and indicator class devices, V4L2 handles, firmware nodes, configuration, cached mode, current, timeout, and strobe source. Low-level I/O is `as3645a_read()` and `as3645a_write()`. Hardware setup and detection are `as3645a_detect()` and `as3645a_setup()`. LED operations include `as3645a_set_indicator_brightness()`, `as3645a_set_assist_brightness()`, `as3645a_set_flash_brightness()`, `as3645a_set_flash_timeout()`, `as3645a_set_strobe()`, and `as3645a_get_fault()`.

## Control Flow
Probe requires firmware nodes, parses child nodes by `reg` values 0 for flash and 1 for indicator, detects the chip from design/version registers, unlocks and disables boost current, initializes the device, registers LED class devices, then registers V4L2 flash and indicator devices. Brightness paths convert user-visible brightness or microamp values to register codes, update current/timer registers, and call `as3645a_set_control()` to select indicator, assist, flash, or external torch mode.

## State and Persistence
Runtime state is protected by `flash->mutex`. Cached fields mirror hardware settings for timeout, flash current, assist current, indicator current, mode, and strobe source. Firmware node references are manually retained and released in remove/error paths. There is no persistence across device removal.

## Dependencies and Integration Points
The driver depends on I2C SMBus byte access, LED flash class, plain LED class for the indicator, firmware child properties (`flash-timeout-us`, `flash-max-microamp`, `led-max-microamp`, `voltage-reference`, `ams,input-max-microamp`), and V4L2 flash helpers. It binds `ams,as3645a` and I2C ID `as3645a`.

## Risks and Edge Cases
`AS_PEAK_mA_TO_REG()` subtracts 1250 from a clamped value, so missing or very small `ams,input-max-microamp` can underflow in unsigned arithmetic before register programming. The setup path returns `rval & ~AS_FAULT_INFO_LED_AMOUNT ? -EIO : 0`; fault interpretation should be checked when adding fault bits. Probe must release both retained child nodes on every error. The driver requires both flash and indicator child nodes; systems without indicator support are rejected.

## Test Signals
Test chip detection against real AS3645A/LM3555-compatible hardware, current and timeout sysfs attributes, indicator brightness, assist/torch mode, flash strobe, and fault mapping for timeout, thermal, short, over-voltage, and LED amount faults. V4L2 tests should confirm both flash and indicator subdevices appear and release cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-as3645a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-ktd2692.c -->
# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-ktd2692.c

## Purpose
This platform driver supports the Kinetic KTD2692 flash LED controller through the LED ExpressWire single-wire protocol. It provides torch/movie brightness and flash strobe control through the LED flash class.

## Important APIs, Types, and Functions
`struct ktd2692_context` stores ExpressWire properties, flash class device, mutex, optional regulator, optional auxiliary GPIO, mode, and torch brightness. `ktd2692_timing` defines protocol pulse timing. LED operations are `ktd2692_led_brightness_set()`, `ktd2692_led_flash_strobe_set()`, and `ktd2692_led_flash_timeout_set()`. Setup/configuration helpers include `ktd2692_parse_dt()`, `ktd2692_init_flash_timeout()`, `ktd2692_init_movie_current_max()`, and `ktd2692_setup()`.

## Control Flow
Probe allocates context, sets ExpressWire timing, parses GPIO/regulator and the first child LED node, initializes flash timeout and max movie brightness, registers the flash LED class device, and writes initial hardware settings. Torch brightness writes movie current and mode registers over ExpressWire, using the auxiliary GPIO low for off. Flash strobe writes timeout, drives the auxiliary GPIO high for flash, programs flash mode, and clears brightness/mode state after the flash event.

## State and Persistence
The driver caches only volatile mode, brightness, and LED flash class settings. Regulator enable is managed by a devm cleanup action if the optional `vin` supply exists. Hardware is explicitly powered off during setup and disabled on brightness/strobe off.

## Dependencies and Integration Points
Dependencies include the ExpressWire helper namespace, `ctrl` GPIO, optional `aux` GPIO, optional `vin` regulator, OF child properties `led-max-microamp`, `flash-max-microamp`, and `flash-max-timeout-us`, and the LED flash class. It binds `kinetic,ktd2692` and imports the `EXPRESSWIRE` namespace.

## Risks and Edge Cases
`aux_gpio` is optional but several paths call `gpiod_direction_output()` on it unconditionally; if optional GPIO absence returns NULL, behavior depends on gpiod helper tolerance and should be verified. Flash timeout setter is a no-op because the class core caches the value, but invalid hardware programming can still happen if timeout step calculation is wrong. ExpressWire pulse timing is tight and hardware-sensitive. Regulator enable failure logs an error but continues without returning if the regulator object exists and enable fails.

## Test Signals
Use a logic analyzer to validate ExpressWire writes, test torch off/on levels, flash timeout levels, regulator cleanup, optional aux GPIO absence, and suspend/resume LED core behavior. Build tests should confirm the ExpressWire namespace import and selected helper object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-ktd2692.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-lm3601x.c -->
# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-lm3601x.c

## Purpose
This I2C/regmap driver supports Texas Instruments LM36010 and LM36011 flash lighting controllers. It exposes either torch or infrared mode plus flash strobe controls through the LED flash class.

## Important APIs, Types, and Functions
`struct lm3601x_led` stores the flash class device, I2C client, regmap, mutex, cached timeout/faults, firmware current limits, and selected LED mode. Regmap configuration is `lm3601x_regmap`, with `LM3601X_FLAGS_REG` marked volatile. LED flash operations are `lm3601x_brightness_set()`, `lm3601x_strobe_set()`, `lm3601x_flash_brightness_set()`, `lm3601x_flash_timeout_set()`, `lm3601x_strobe_get()`, and `lm3601x_flash_fault_get()`.

## Control Flow
Probe parses the first child node for `reg`, torch max current, flash max current, and max timeout, creates an I2C regmap, tries a software reset, initializes the mutex, and registers a flash LED class device. Torch brightness reads/clears faults, writes the torch register, and sets enable bits for torch or IR mode. Flash brightness writes the flash current register. Strobe computes the timeout register encoding using lower or upper timeout step ranges, sets strobe mode in the enable register, then reads faults.

## State and Persistence
State is volatile and protected by `led->lock`. `flash_timeout` is cached by the timeout setter and applied during strobe. `last_flag` caches translated LED fault bits from the hardware flags register. Regmap caching uses `REGCACHE_MAPLE` for nonvolatile registers.

## Dependencies and Integration Points
The driver depends on I2C, regmap, LED flash class, and firmware node properties. It binds OF compatibles `ti,lm36010` and `ti,lm36011`, plus matching I2C IDs. The LED label defaults to `torch` or `infrared` according to child `reg`.

## Risks and Edge Cases
`lm3601x_parse_node()` stores the child fwnode in an output parameter and then always drops it before returning; this can leave registration with a stale fwnode pointer and should be reviewed. The strobe code compares `led->flash_timeout` in microseconds to a raw register value read from `LM3601X_CFG_REG`, so it may rewrite more often than intended. Timeout mask updates pass an unshifted value to `LM3601X_TIMEOUT_MASK`; this relies on the mask starting at bit 1 and may need field preparation. Fault reads ignore errors in `fault_get()`.

## Test Signals
Test both LM36010 and LM36011 compatibles, torch and IR child `reg` modes, timeout values below and above 400 ms, flash brightness programming, strobe get/set, standby on remove, and fault mapping for timeout, UVLO, thermal, current limit, short, IVFM, and OVP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-lm3601x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-max77693.c -->
# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-max77693.c

## Purpose
This platform driver controls the flash LED block inside the Maxim MAX77693 MFD. It supports one or two FLED outputs, optional joint current-output mode, torch and flash modes, external strobe, fault reporting, and V4L2 flash subdevices.

## Important APIs, Types, and Functions
`struct max77693_led_device` stores parent regmap, mutex, sub-LEDs, current limits, mode flags, allowed modes, current-output mask, and joint-output state. `struct max77693_sub_led` stores per-FLED flash class device, V4L2 handle, brightness/timeout/fault caches, and ID. Key helpers include `max77693_set_mode_reg()`, `max77693_add_mode()`, `max77693_clear_mode()`, `max77693_distribute_currents()`, `max77693_set_torch_current()`, `max77693_set_flash_current()`, `max77693_set_timeout()`, and `max77693_get_flash_faults()`.

## Control Flow
Probe obtains the parent MFD regmap, parses child nodes and `led-sources`, validates/clamps current, timeout, boost, and voltage settings, initializes hardware registers, initializes one or two flash class devices, and registers corresponding V4L2 devices. Torch brightness sets ITORCH and enables torch mode. Flash brightness sets IFLASH registers. Strobe updates timeout if needed, records the strobing LED, enables flash mode, reads faults, and clears flash mode flags after the one-shot programming path.

## State and Persistence
State is volatile and mutex-protected. `mode_flags` tracks active torch/external modes while flash modes are cleared after triggering to avoid repeated strobes. `torch_iout_reg` caches combined torch current register fields. Per-sub-LED timeout and fault fields cache class settings and last fault state. Firmware node references are manually put after registration or errors.

## Dependencies and Integration Points
The driver depends on the MAX77693 MFD parent, MAX77693 register definitions, regmap, OF child nodes with `led-sources`, LED flash class, and optional V4L2 flash class. It binds `maxim,max77693-led` as a platform child of the MFD.

## Risks and Edge Cases
Joint-output mode changes current distribution and allowed modes, so one LED node with two `led-sources` behaves differently from two independent nodes. External flash mode deliberately enables both FLASHEN and TORCHEN hardware pins, which can interfere with software modes if not cleared. Fault mapping treats open faults as over-voltage. Error cleanup must unregister FLED1 if FLED2 registration fails. Boost mode is forced on for joint outputs when firmware requested no boost.

## Test Signals
Test single FLED1, single FLED2, two independent LEDs, and joint-output DT layouts. Validate torch current distribution, flash current splitting, timeout programming, external strobe, boost mode/voltage registers, fault reporting, and remove cleanup. V4L2 tests should confirm unique device names and external strobe support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-max77693.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-mt6360.c -->
# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-mt6360.c

## Purpose
This platform driver exposes the MediaTek MT6360 PMIC LED block. It supports individual current-sink LEDs, a virtual multicolor RGB LED, and two flash LEDs with torch, strobe, timeout, fault, and optional V4L2 flash support.

## Important APIs, Types, and Functions
`struct mt6360_priv` stores the parent regmap, lock, active LED bitmaps, torch/strobe usage masks, and a flexible array of `struct mt6360_led`. `struct mt6360_led` is a union over plain LED, multicolor LED, and flash LED class devices. Brightness and flash operations include `mt6360_isnk_brightness_set()`, `mt6360_mc_brightness_set()`, `mt6360_torch_brightness_set()`, `mt6360_strobe_set()`, `mt6360_strobe_get()`, `mt6360_timeout_set()`, and `mt6360_fault_get()`.

## Control Flow
Probe counts child nodes, allocates private storage, gets the parent regmap, then iterates children. Child `color` selects virtual multicolor versus normal `reg`-indexed LED. Current-sink children initialize max brightness and default state, then register plain or multicolor class devices. Flash children initialize torch and strobe limits, preprogram minimum strobe current to avoid current spikes, initialize default torch state, register LED flash devices, and optionally create V4L2 flash subdevices.

## State and Persistence
Runtime state is held in bitmaps: `leds_active` prevents duplicate child use, `fled_torch_used` and `fled_strobe_used` enforce mutual exclusion between torch and strobe paths. Default state may keep hardware brightness at probe, but no state persists beyond the PMIC binding. V4L2 handles are explicitly released on remove or probe failure.

## Dependencies and Integration Points
The driver depends on a parent regmap from the MT6360 MFD, LED class, multicolor LED class, LED flash class, firmware LED properties, and optional V4L2 flash class. Flash fault reporting reads charger and FLED status registers via regmap/raw read.

## Risks and Edge Cases
The hardware has one flash control logic block, so torch and strobe are mutually exclusive and return `-EBUSY` if used concurrently. Multicolor child parsing marks component channels active; malformed child lists can partially mutate `leds_active` before returning errors. The code uses raw 16-bit reads from `MT6360_REG_FLEDSTAT1`, so endianness/regmap bus behavior matters. Probe failure after devm LED registration relies on devm cleanup plus explicit V4L2 release.

## Test Signals
Test current-sink LEDs with `default-state` off/on/keep, RGB multicolor registration with two or three channels, flash torch/strobe mutual exclusion, timeout programming, fault bits for input voltage, timeout, short, and undervoltage, V4L2 external strobe, and duplicate `reg`/channel rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-mt6360.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-mt6370-flash.c -->
# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-mt6370-flash.c

## Purpose
This platform driver supports the MT6370 PMIC flashlight block. It exposes one or two flash LED class devices, including a joint-output mode when a firmware LED uses both flash channels.

## Important APIs, Types, and Functions
`struct mt6370_priv` stores regmap, mutex, torch/strobe usage masks, active channel bitmap, count, and per-LED array. `struct mt6370_led` stores the flash class device, V4L2 handle, parent private pointer, and LED number. LED operations are `mt6370_torch_brightness_set()`, `mt6370_flash_brightness_set()`, `_mt6370_flash_brightness_set()`, `mt6370_strobe_set()`, `mt6370_strobe_get()`, `mt6370_timeout_set()`, and `mt6370_fault_get()`.

## Control Flow
Probe counts child nodes, gets the parent regmap, and parses each child. `led-sources` selects channel 0, channel 1, or joint mode with both channels. Current and timeout properties are clamped to hardware ranges, minimum strobe current is preprogrammed, class callbacks are installed, and each flash LED is registered with optional V4L2 flash support. Torch and strobe setters split current across both channels for joint mode and program enable bits in `MT6370_REG_FLEDEN`.

## State and Persistence
State is volatile and mutex-protected. `leds_active` prevents duplicate channel allocation. `fled_torch_used` and `fled_strobe_used` track active modes and enforce mutual exclusion. Devm actions release V4L2 flash handles. No hardware state is persisted across removal.

## Dependencies and Integration Points
The driver depends on the MT6370 parent regmap, LED flash class, firmware `led-sources`, `led-max-microamp`, `flash-max-microamp`, and `flash-max-timeout-us` properties, and optional V4L2 flash class. It binds `mediatek,mt6370-flashlight`.

## Risks and Edge Cases
Joint mode uses synthetic `led_no == 2`, so all bit operations involving `BIT(led_no)` must remain separate from hardware channel masks. Torch and strobe share control logic and intentionally reject concurrent use. The timeout setter lacks explicit locking while most related paths use the mutex. Fault reads use raw 16-bit status and must match regmap endianness. There is no remove callback because devm manages class devices and V4L2 release is registered as a devm action.

## Test Signals
Test one-channel and two-channel `led-sources`, duplicate channel rejection, current splitting in joint mode, torch/strobe mutual exclusion, ramp delays on strobe transitions, timeout register values, fault mapping, and V4L2 external strobe. Remove/unbind should release V4L2 subdevices through the devm action.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-mt6370-flash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-qcom-flash.c -->
# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-qcom-flash.c

## Purpose
This platform driver supports Qualcomm SPMI PMIC multi-channel flash LED modules. It handles three- and four-channel hardware variants, multi-channel LEDs, torch and flash current programming, thermal derating, fault reporting, and optional V4L2 flash integration.

## Important APIs, Types, and Functions
`struct qcom_flash_data` stores shared module state, regmap fields, lock, hardware type, total current budget, channel count, revision, and V4L2 handles. `struct qcom_flash_led` stores per-LED flash class device, channel IDs, max currents/timeouts, cached flash settings, current allocation, and enable state. Key helpers are `set_flash_module_en()`, `update_allowed_flash_current()`, `set_flash_current()`, `set_flash_timeout()`, and `set_flash_strobe()`. LED callbacks include `qcom_flash_led_brightness_set()`, `qcom_flash_brightness_set()`, `qcom_flash_timeout_set()`, `qcom_flash_strobe_set()`, `qcom_flash_strobe_get()`, and `qcom_flash_fault_get()`.

## Control Flow
Probe gets the parent regmap and register base, verifies module type/subtype, selects the proper reg-field table, adjusts fields by base address, allocates regmap fields, counts child LEDs, and registers each child. Each child parses 1-based `led-sources`, torch current, optional flash current/timeout, and registers a flash class device. Torch brightness disables current strobe state, derates requested current based on current thermal status and shared current budget, programs current and timeout, enables the module, and enables software strobe. Flash strobe follows a similar sequence with flash current and safety timer.

## State and Persistence
Shared state tracks `chan_en_bits`, total allocated current in mA, per-LED current allocation, and per-LED enabled state. These are runtime-only and protected by `flash_data->lock` for shared budget/module updates. LED class settings cache requested flash current and timeout before strobe.

## Dependencies and Integration Points
The driver depends on a parent SPMI PMIC regmap, firmware `reg` base and child `led-sources`, LED flash class, regmap fields, and optional V4L2 flash. It binds `qcom,spmi-flash-led`.

## Risks and Edge Cases
The V4L2 release loops index `v4l2_flash[leds_count]` before decrementing, which appears off by one after `leds_count` has been incremented; cleanup should be reviewed. Thermal derating temporarily lowers threshold registers and must always restore defaults on errors. Channel IDs in firmware are 1-based, while internal regfield IDs are 0-based. Shared total current limiting can reduce a strobe to zero current when thermal/current budget is exhausted. `FIELD_PREP()` is used with single-bit macros rather than masks in strobe config, which should be verified.

## Test Signals
Test PM8150/Pmi8998 three-channel and four-channel subtype detection, multi-channel current splitting, torch clamp programming, thermal derating status paths, simultaneous LEDs sharing the total current budget, V4L2 external strobe, fault reporting for short/thermal/over-current/input-voltage/timeout, and probe/remove cleanup under partial registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-qcom-flash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-rt4505.c -->
# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-rt4505.c

## Purpose
This I2C/regmap driver supports the Richtek RT4505 flash LED controller. It exposes torch brightness, flash brightness, strobe, timeout, fault reporting, external strobe, and V4L2 flash support.

## Important APIs, Types, and Functions
`struct rt4505_priv` stores device, regmap, mutex, flash class device, and V4L2 handle. LED operations are `rt4505_torch_brightness_set()`, `rt4505_torch_brightness_get()`, `rt4505_flash_brightness_set()`, `rt4505_flash_strobe_set()`, `rt4505_flash_strobe_get()`, `rt4505_flash_timeout_set()`, and `rt4505_fault_get()`. Regmap access is limited by `rt4505_is_accessible_reg()` and `rt4505_regmap_config`.

## Control Flow
Probe allocates private state, initializes regmap, resets the chip, obtains the first child node, initializes torch/flash/timeout limits from firmware with hardware clamps, registers the flash LED class device, initializes V4L2 configuration, and creates a V4L2 flash subdevice. Torch brightness writes torch current into `RT4505_REG_ILED` and updates enable bits. Flash brightness writes flash current bits. Strobe writes enable mode bits, while external strobe uses a different enable pattern.

## State and Persistence
State is volatile. Register state is reset on probe and shutdown. The mutex serializes register updates. V4L2 state is released on remove. LED flash class settings hold max/current timeout values.

## Dependencies and Integration Points
Dependencies include I2C, regmap, firmware LED child properties, LED flash class, and optional V4L2 flash. The driver binds `richtek,rt4505` and uses OF matching through the I2C driver.

## Risks and Edge Cases
The child fwnode acquired with `device_get_next_child_node()` is not explicitly released after probe, which should be checked for reference leaks. Clamp logic does not align DT current values down to step size before deriving max brightness/settings, so class values can imply nonexact hardware steps. `rt4505_fault_get()` maps over-temperature to `LED_FAULT_OVER_TEMPERATURE`, while V4L2 config advertises `LED_FAULT_LED_OVER_TEMPERATURE`; consistency should be verified. Shutdown reset ignores errors.

## Test Signals
Test probe reset, torch brightness set/get, flash brightness and timeout registers, software and external strobe, fault bit mapping for OVP/short/OTP/timeout, V4L2 intensity bounds, and shutdown leaving hardware off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-rt4505.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-rt8515.c -->
# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-rt8515.c

## Purpose
This platform driver supports the Richtek RT8515 GPIO-driven flash/torch LED controller found on some phones. It approximates brightness through GPIO pulse counts, enforces flash timeout with a kernel timer, and can expose a V4L2 flash device.

## Important APIs, Types, and Functions
`struct rt8515` stores the flash class device, V4L2 handle, mutex, optional regulator pointer, flash/torch GPIOs, powerdown timer, timeout, and computed intensity limits. GPIO helpers are `rt8515_gpio_led_off()` and `rt8515_gpio_brightness_commit()`. LED operations are `rt8515_led_brightness_set()`, `rt8515_led_flash_strobe_set()`, `rt8515_led_flash_strobe_get()`, and `rt8515_led_flash_timeout_set()`. Configuration uses `rt8515_determine_max_intensity()`.

## Control Flow
Probe gets `enf` and `ent` GPIOs, reads the child LED node, computes flash and torch intensity caps from DT resistor values and max microamp properties, initializes a timer and LED flash timeout settings, registers the flash LED class device, and optionally initializes V4L2 flash. Torch brightness pulses the torch GPIO for intermediate levels or drives it high for max. Flash strobe pulses the flash GPIO for configured max flash intensity and arms a timer to turn the LED off.

## State and Persistence
The timer represents active flash state; `strobe_get()` reports whether it is pending. Brightness and timeout settings are volatile. The driver destroys the timer and mutex on remove. The regulator member exists but is not acquired or used in this source.

## Dependencies and Integration Points
The driver depends on two GPIO descriptors, firmware resistor properties `richtek,rfs-ohms` and `richtek,rts-ohms`, child current/timeout properties, LED flash class, and optional V4L2 flash. It binds `richtek,rt8515`.

## Risks and Edge Cases
There is no datasheet-backed register interface, so brightness pulse behavior is inferred and hardware-sensitive. `rt8515_determine_max_intensity()` can compute intensity values beyond the hardware maximum or below useful range if DT values are inconsistent; it does not clamp to `hw_max`. Strobe-on does not explicitly clear torch first beyond using the flash GPIO pulses. The optional V4L2 init failure logs but continues, leaving `rt->v4l2_flash` as an error pointer; remove must tolerate this through the conditional helper path.

## Test Signals
Use GPIO tracing or a scope to validate pulse counts and off sequencing. Test resistor/current DT combinations, torch levels, flash timeout auto-off, manual strobe off, V4L2 registration failure handling, and removal while timer is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-rt8515.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-sgm3140.c -->
# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-sgm3140.c

## Purpose
This platform driver supports SGMicro SGM3140-compatible charge-pump flash LED circuits, including compatibles for OCP8110 and RT5033 LED. It uses GPIOs and a regulator to switch torch or flash mode and a timer to enforce flash timeout.

## Important APIs, Types, and Functions
`struct sgm3140` stores flash class device, V4L2 handle, timer, flash and enable GPIOs, VIN regulator, enabled state, timeout, and max timeout. LED operations are `sgm3140_brightness_set()`, `sgm3140_strobe_set()`, `sgm3140_strobe_get()`, and `sgm3140_timeout_set()`. Timer callback `sgm3140_powerdown_timer()` turns GPIOs off, disables the regulator, and clears `enabled`.

## Control Flow
Probe obtains `flash` and `enable` GPIOs, gets the `vin` regulator, reads the first child LED node and optional `flash-max-timeout-us`, initializes current timeout and LED flash settings, registers the LED flash class device, and creates a V4L2 flash subdevice. Torch brightness enables the regulator, drives flash GPIO low and enable GPIO high. Flash strobe enables the regulator, drives both flash and enable GPIOs high, and arms the timer. Turning either mode off deletes the timer, clears GPIOs, disables the regulator, and updates `enabled`.

## State and Persistence
The only software state is volatile: `enabled`, current timeout, max timeout, timer state, and V4L2 handle. There is no mutex around `enabled`, timer callback, brightness, and strobe paths, so concurrent LED class operations rely on higher-level serialization and should be considered carefully.

## Dependencies and Integration Points
The driver depends on GPIO consumer APIs, regulator framework, LED flash class, firmware child nodes, and optional V4L2 flash. It binds `ocs,ocp8110`, `richtek,rt5033-led`, and `sgmicro,sgm3140`.

## Risks and Edge Cases
Regulator enable/disable calls can become unbalanced if concurrent brightness and strobe operations race. `sgm3140_init_flash_timeout()` sets the class default value to 250 ms even if `max_timeout` is lower; the separate `priv->timeout` cache is clamped, but the class setting may advertise an out-of-range default. The child fwnode is not put on the successful probe path. Timer callback uses non-cansleep GPIO setters and regulator disable in timer context, which is risky if the regulator operation can sleep.

## Test Signals
Test torch on/off, flash strobe auto-timeout, manual strobe off, regulator balance under repeated operations, V4L2 subdevice creation, missing timeout property defaulting, and remove with active timer. Lockdep or sleep-in-atomic diagnostics are important for the timer callback path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/flash/leds-sgm3140.c -->
