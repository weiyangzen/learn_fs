# sources/distributed-fs/ceph-client subset-b-005122 research

Grouped research for subset `subset-b-005122`. Each section preserves the source path and is wrapped for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wmt.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wmt.c

Purpose: shared WonderMedia/WMT pin controller and GPIO implementation used by SoC-specific vt8500-family pinctrl drivers. It registers a pinctrl device, exposes each pin as a single-pin group, implements three mux functions (`gpio_in`, `gpio_out`, `alt`), parses legacy DT properties, applies pull bias, and registers a GPIO chip backed by memory-mapped register banks.

Important APIs, types, and functions: `wmt_pinctrl_probe()` is the exported entry point used by chip-specific drivers after filling `struct wmt_pinctrl_data`. `wmt_setbits()` and `wmt_clearbits()` perform relaxed read/modify/write MMIO updates. `wmt_set_pinmux()` maps mux selectors to enable/direction register changes. `wmt_pctl_dt_node_to_map()` converts `wm,pins`, `wm,function`, and `wm,pull` properties into pinctrl maps. `wmt_pinconf_set()` supports bias disable, pull-down, and pull-up through per-bank pull enable/config registers. The GPIO path uses `wmt_gpio_get_direction()`, `wmt_gpio_get_value()`, `wmt_gpio_set_value()`, and `wmt_gpio_direction_output()`.

Control flow: probe maps the first platform MMIO resource, installs the SoC-provided pin table in the global `wmt_desc`, copies the static GPIO template, sets `ngpio = nbanks * 32`, registers pinctrl with `devm_pinctrl_register()`, registers the GPIO chip, then adds a pin range spanning all bank pins. Pinctrl calls resolve functions/groups directly from `data->groups` and `data->pins`. DT map parsing validates property presence and lengths, allocates one or two maps per pin, emits mux maps and config maps, and frees allocated config arrays on failure. GPIO direction changes delegate through pinctrl GPIO helpers after setting output value where needed.

State and persistence: all durable hardware state is in MMIO registers. Driver state is held in `wmt_pinctrl_data`, including SoC register offsets and pin/group arrays supplied by caller files. `wmt_desc` is a file-static descriptor whose `pins`/`npins` are overwritten at probe time, so concurrent multi-instance use would share descriptor metadata. Pull config maps allocate transient per-map config words freed by `dt_free_map`.

Dependencies and integration points: depends on the Linux pinctrl, pinmux, pinconf, GPIO, OF, and platform-device frameworks. SoC-specific vt8500 drivers provide banks, pins, and groups and call `wmt_pinctrl_probe()`. Device tree bindings are legacy WMT-specific properties rather than generic `pinconf` property parsing.

Risks and edge cases: register offsets may be `NO_REG`; muxing to `alt` on dedicated GPIO banks and bias operations on banks without pull registers fail with `-EINVAL`. MMIO updates are unlocked read/modify/write operations, so concurrent GPIO/pinctrl users could race if the same register bits are touched simultaneously. DT parser error text says `wmt,pins` while the property name is `wm,pins`. The driver accepts any pin less than `nbanks * 32`, then separately requires it to be present in the provided pin descriptors. `wmt_pinconf_get()` always returns `-ENOTSUPP`, so state is write-only from generic pinconf.

Test signals: useful coverage includes boot/probe with valid and invalid DT maps, mux transitions for GPIO in/out/alt, GPIO get/set/direction through gpiolib, bias enable/disable on banks with and without pull registers, and fault-injection for map allocation failures. Hardware tests should verify actual register bits and pin electrical behavior because there is little internal readback beyond direction/value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wmt.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wmt.h

Purpose: private interface for WMT/vt8500-family pinctrl implementations. It defines register-bank descriptors, pin/group encoding helpers, the shared per-controller state container, and the `wmt_pinctrl_probe()` entry point.

Important APIs, types, and functions: `NO_REG` marks unsupported bank registers. `WMT_PINCTRL_BANK()` initializes `struct wmt_pinctrl_bank_registers`. `WMT_PIN()`, `WMT_BANK_FROM_PIN()`, and `WMT_BIT_FROM_PIN()` encode bank and bit into a linear pin number. `WMT_GROUP()` initializes a named pin group. `struct wmt_pinctrl_data` carries device pointers, MMIO base, bank descriptors, pin descriptors, group names, counts, and embedded GPIO/pinctrl range storage.

Control flow: SoC-specific source files include this header, statically define banks/pins/groups with these macros, initialize `wmt_pinctrl_data`, then call `wmt_pinctrl_probe()` from their platform probe. The shared C file consumes the register offsets and counts directly.

State and persistence: the header declares no storage by itself. Its structures describe runtime state owned by each platform instance and hardware register layout. The MMIO base is documented as needing initialization before probe, but the shared probe also maps it itself, so the comment is partially stale.

Dependencies and integration points: includes `linux/gpio/driver.h` and relies on pinctrl descriptors from the including C files. It is internal to `drivers/pinctrl/vt8500`.

Risks and edge cases: `NO_REG` uses `0xFFFF`, so real register offsets must not collide with that sentinel. Pin encoding assumes 32 pins per bank. `WMT_GROUP()` can describe multi-pin groups, but the shared implementation effectively treats groups as single pin descriptors, so users must align group arrays with shared driver expectations.

Test signals: compile coverage of all including SoC drivers, static inspection of bank offsets/counts, and hardware probe confirming `ngpio == nbanks * 32` matches the actual controller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/vt8500/pinctrl-wmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/Kconfig

Purpose: top-level Kconfig aggregator for platform-specific drivers under `drivers/platform`. It does not define options itself; it sources architecture/vendor submenus.

Important APIs, types, and functions: sources `mips`, `loongarch`, `goldfish`, `chrome`, `cznic`, `mellanox`, `olpc`, `surface`, `x86`, `arm64`, `raspberrypi`, and `wmi` Kconfig files.

Control flow: during Kconfig parsing, this file makes each subordinate platform menu visible according to its own dependencies. Option symbols from those files are later consumed by `drivers/platform/Makefile`.

State and persistence: no runtime state. Build configuration persists in generated kernel `.config`.

Dependencies and integration points: integrated by the kernel's drivers Kconfig hierarchy. Ordering can affect menu display but not object linking directly.

Risks and edge cases: missing a `source` line hides an entire platform family. Adding a submenu here without a matching Makefile dispatch can make options selectable but unbuilt.

Test signals: `make menuconfig`/`olddefconfig` parse success and all sourced paths existing in tree. Build tests should toggle representative symbols and verify Makefile traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/Makefile

Purpose: top-level build dispatch for `drivers/platform`, mapping configuration symbols to architecture/vendor subdirectories.

Important APIs, types, and functions: `obj-$(CONFIG_...) += dir/` entries select `x86`, `loongarch`, `mellanox`, `mips`, `olpc`, `goldfish`, `chrome`, `cznic`, `surface`, `arm64`, `raspberrypi`, and `wmi` subdirectories.

Control flow: kbuild descends into a subdirectory when the associated symbol is enabled. Some entries are architecture gates (`CONFIG_X86`, `CONFIG_MIPS`), while others are menuconfig/vendor symbols (`CONFIG_CHROME_PLATFORMS`, `CONFIG_ARM64_PLATFORM_DEVICES`).

State and persistence: no runtime state. It affects built-in and module object graph only.

Dependencies and integration points: must stay aligned with `drivers/platform/Kconfig` and subdirectory Makefiles. Subdirectory Makefiles perform per-driver object selection.

Risks and edge cases: using a broad architecture symbol can build a directory whenever the architecture is selected, relying on the child Makefile to avoid unwanted objects. A Kconfig symbol without a Makefile entry results in dead configuration.

Test signals: kbuild traversal with multiple architecture/config combinations, especially `COMPILE_TEST`, and `make W=1` for stale object names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/arm64/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/arm64/Kconfig

Purpose: Kconfig menu for ARM64 platform-specific, mostly EC-like, laptop/tablet drivers.

Important APIs, types, and functions: `ARM64_PLATFORM_DEVICES` is the parent menuconfig gated by `ARM64 || COMPILE_TEST`. Child tristates are `EC_ACER_ASPIRE1`, `EC_HUAWEI_GAOKUN`, `EC_LENOVO_YOGA_C630`, and `EC_LENOVO_THINKPAD_T14S`.

Control flow: enabling the parent reveals child drivers. Each child declares subsystem dependencies matching its source file: Acer needs I2C, DRM, POWER_SUPPLY, and INPUT; Huawei needs I2C, INPUT, HWMON, and selects AUXILIARY_BUS; Yoga C630 needs I2C and selects AUXILIARY_BUS; T14s needs I2C and INPUT plus LED and sparse-keymap support.

State and persistence: no runtime state. Selected tristate values drive module/built-in build results through the arm64 Makefile.

Dependencies and integration points: tied to Qualcomm/ARM64 laptop DT-described EC devices. Auxiliary-bus selects support downstream PSY/UCSI subdrivers for Huawei and Yoga C630.

Risks and edge cases: `COMPILE_TEST` broadens build coverage beyond real hardware. Missing dependencies can cause link failures; excessive dependencies can prevent useful compile coverage. The user-visible help emphasizes nonstandard battery/EC exposure compared with ACPI.

Test signals: all child symbols should compile as `m` under `COMPILE_TEST` with dependencies enabled. Runtime smoke tests are hardware-specific and should verify probe, IRQs, and subsystem registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/arm64/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/arm64/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/arm64/Makefile

Purpose: kbuild mapping from ARM64 EC Kconfig symbols to object files.

Important APIs, types, and functions: maps `CONFIG_EC_ACER_ASPIRE1` to `acer-aspire1-ec.o`, `CONFIG_EC_HUAWEI_GAOKUN` to `huawei-gaokun-ec.o`, `CONFIG_EC_LENOVO_YOGA_C630` to `lenovo-yoga-c630.o`, and `CONFIG_EC_LENOVO_THINKPAD_T14S` to `lenovo-thinkpad-t14s.o`.

Control flow: when symbols are `y`, objects are linked built-in; when `m`, modules are generated. No composite objects are defined here.

State and persistence: build-only; no runtime state.

Dependencies and integration points: must align exactly with `drivers/platform/arm64/Kconfig` symbol names and source filenames.

Risks and edge cases: filename-symbol drift prevents selected drivers from building. The comment scopes this directory to EC-like devices, which is a maintenance boundary rather than an enforced rule.

Test signals: `make M=drivers/platform/arm64` or whole-kernel compile with each symbol as module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/arm64/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/arm64/acer-aspire1-ec.c -->
# sources/distributed-fs/ceph-client/drivers/platform/arm64/acer-aspire1-ec.c

Purpose: I2C embedded-controller driver for Snapdragon-based Acer Aspire 1. It reconstructs platform services not exposed through standard firmware interfaces: battery and AC power supplies, lid switch input, Fn-lock sysfs control, and USB-C DisplayPort HPD via a DRM bridge.

Important APIs, types, and functions: `struct aspire_ec` holds the I2C client, two power supplies, input device, DRM bridge, and HPD work. `aspire_ec_ram_read()`/`aspire_ec_ram_write()` access EC RAM commands. `aspire_ec_irq_handler()` dispatches EC event IDs. `aspire_ec_bat_psy_get_property()` and `aspire_ec_adp_psy_get_property()` expose `power_supply` properties. `aspire_ec_bridge_hpd_enable()` schedules initial HPD readback, and `fn_lock_show()`/`fn_lock_store()` expose keyboard mode state.

Control flow: probe allocates the DRM bridge-embedded private struct, registers battery and mains power supplies, registers an input device for `SW_LID`, programs keyboard Fn/media notification bits in EC RAM, optionally registers a child-node-backed USB connector bridge, then requests a threaded IRQ. IRQ handling waits briefly after resume-prone interrupts, reads `ASPIRE_EC_EVENT`, and handles watchdog clear, lid events, fuel-gauge changes, HPD connect/disconnect, and ignored keyboard/backlight events. Resume reads the lid status RAM byte and reports switch state.

State and persistence: persistent state lives in EC RAM, including watchdog, keyboard mode, HPD status, lid status, and adapter status registers. Kernel state tracks whether the DRM bridge is configured. Fn-lock writes persist at least until EC state changes or reset. Power-supply properties are read live from static/dynamic EC fuel-gauge blocks and converted from milli-units to micro-units.

Dependencies and integration points: uses I2C SMBus, input, power_supply, DRM bridge/HPD, OF child node `connector`, threaded IRQ, and simple PM ops. Device IDs are `aspire1-ec` and OF compatible `acer,aspire1-ec`.

Risks and edge cases: low-level RAM read/write helpers ignore SMBus return values and always report success, so read failures can propagate as stale stack data. Capacity computation divides by `capacity_full` without explicit zero guard. HPD work is scheduled but no explicit cancellation is visible on remove, relying on devm lifetime and short work. Lid resume reports `!!(tmp & ASPIRE_EC_LID_OPEN)` directly as `SW_LID`, while IRQ close/open reports `1` for closed and `0` for open; this polarity merits hardware validation. Event handling contains several no-op known events.

Test signals: hardware tests should verify battery status/capacity/current, AC online changes, Fn-lock sysfs read/write, lid switch polarity across IRQ and resume, DP HPD notifications with a Type-C display, and watchdog event clearing. Fault tests should simulate SMBus errors if possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/arm64/acer-aspire1-ec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/arm64/huawei-gaokun-ec.c -->
# sources/distributed-fs/ceph-client/drivers/platform/arm64/huawei-gaokun-ec.c

Purpose: I2C EC core driver for Huawei Matebook E Go (`gaokun`) devices. It provides a serialized EC transaction API, exposes helper APIs for power-supply and UCSI auxiliary subdrivers, creates lid input and hwmon temperature interfaces, handles Fn-lock sysfs, and sends modern-standby enter/exit commands.

Important APIs, types, and functions: `struct gaokun_ec` stores the client, EC transaction mutex, notifier chain, hwmon device, lid input, and suspend state. Exported helpers include `gaokun_ec_read()`, `gaokun_ec_write()`, `gaokun_ec_read_byte()`, notifier register/unregister, PSY register reads and smart-charge get/set/enable APIs, and UCSI read/write/register/pin-assignment-ack APIs. `gaokun_ec_request()` is the central two-message I2C transfer. `gaokun_aux_init()` creates auxiliary devices named by platform data.

Control flow: requests use a three-byte header `{master_cmd, slave_cmd, data_len}` followed by payload; responses begin with status and length before data. `gaokun_ec_request()` holds `ec->lock`, writes and reads via `i2c_transfer()`, returns EC status, then sleeps like the ACPI reference method. Probe allocates state, initializes the notifier chain, registers a `SW_LID` input device, creates PSY and UCSI auxiliary devices, requests the threaded IRQ, and registers a multi-channel hwmon temp device. IRQ reads the event query command, reports lid state directly for `EC_EVENT_LID`, and forwards all other nonzero events to the blocking notifier chain. Suspend/resume sends standby commands, with resume retrying three times.

State and persistence: transaction serialization is per-device. Fn-lock, smart-charge settings, UCSI registers, temperature readings, lid state, and standby state live in EC firmware. Kernel `suspended` prevents duplicate standby entry/exit. Auxiliary devices receive the EC pointer through `platform_data` and inherit the parent OF node.

Dependencies and integration points: uses I2C, input, hwmon, auxiliary bus, blocking notifiers, OF matching `huawei,gaokun3-ec`, and public platform data declarations in `linux/platform_data/huawei-gaokun-ec.h`. Exported GPL symbols are consumed by separate gaokun PSY/UCSI drivers.

Risks and edge cases: `gaokun_ec_request()` treats any short `i2c_transfer()` as an error value but may return a positive count rather than a normalized negative errno. Response length byte is documented unreliable and mostly ignored, so callers rely on fixed buffer sizes. `gaokun_ec_read_byte()` extracts a byte even if the read failed, although it returns the error. Smart-charge threshold validation only checks start/end range. IRQ lid path ignores the return value of the register read. Resume clears `suspended` even if all retries fail.

Test signals: unit-like tests can cover smart-charge validation. Hardware tests should verify auxiliary PSY/UCSI devices bind, Fn-lock toggles, all advertised hwmon channels read plausible temperatures, lid events report correct polarity, standby commands are sent around suspend, and notifier consumers receive EC events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/arm64/huawei-gaokun-ec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/arm64/lenovo-thinkpad-t14s.c -->
# sources/distributed-fs/ceph-client/drivers/platform/arm64/lenovo-thinkpad-t14s.c

Purpose: I2C EC driver for Qualcomm-based Lenovo ThinkPad T14s systems. It exposes EC-controlled LEDs, keyboard backlight, audio mute LEDs, and extra-key input events, and performs modern-standby register handshakes.

Important APIs, types, and functions: `struct t14s_ec` contains regmap, device pointer, several LED classdevs, keyboard backlight, audio LEDs, and input device. `t14s_ec_read()`/`t14s_ec_write()` implement custom regmap bus operations over I2C. `t14s_ec_read_evt()` reads EC event bytes. `t14s_led_*()` functions implement platform LED brightness/blink support. `t14s_kbd_bl_*()` handles keyboard backlight get/set and hardware-change notifications. `t14s_input_probe()` sets up `sparse_keymap`.

Control flow: probe initializes a custom 8-bit regmap backed by two-part I2C transfers, registers four platform LEDs, keyboard backlight, mic/speaker mute LEDs with audio triggers, extra-button input, then requests a threaded IRQ and disables wakeup by default. IRQ reads one event, updates keyboard-backlight state on Fn+Space, maps known Fn/touchpad events through sparse-keymap, and logs other AC/lid/thermal/performance events. Suspend writes the modern-standby entry bit three times and suspends the keyboard backlight LED classdev; resume writes the exit bit three times and resumes the LED.

State and persistence: LED state is stored in EC registers. `t14s_ec_led_classdev.cache` preserves blink/on choice for each platform LED. Regmap has no cache configuration, so reads and writes go to hardware. Keyboard backlight exposes hardware-changed notifications. Wakeup is explicitly disabled to avoid lid-close wake behavior until event masking exists.

Dependencies and integration points: uses I2C, regmap custom bus, LED class, audio LED triggers, input sparse-keymap, threaded IRQs, OF compatible `lenovo,thinkpad-t14s-ec`, and system sleep PM. Kconfig selects sparse-keymap and LED support.

Risks and edge cases: regmap read/write operations use fixed sleeps and raw I2C segment locking; timing assumptions are hardware-specific. Event reads process only one event per IRQ. Some known events only log and do not notify subsystems such as power_supply or thermal. Blink supports only the hardware 1 Hz rate. Wakeup disabled by default may surprise users expecting lid/power wake.

Test signals: verify each LED class device, blink rejection/acceptance, keyboard backlight brightness and hardware-change notification on Fn+Space, sparse-keymap event codes, suspend/resume register writes, and no wakeup from closed lid unless policy changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/arm64/lenovo-thinkpad-t14s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/arm64/lenovo-yoga-c630.c -->
# sources/distributed-fs/ceph-client/drivers/platform/arm64/lenovo-yoga-c630.c

Purpose: core I2C EC driver for Lenovo Yoga C630. It exports serialized register and UCSI helpers, forwards EC events through a notifier chain, and creates auxiliary PSY and UCSI devices.

Important APIs, types, and functions: `struct yoga_c630_ec` stores the I2C client, mutex, and notifier chain. Exported functions include `yoga_c630_ec_read8()`, `yoga_c630_ec_read16()`, `yoga_c630_ec_ucsi_get_version()`, `yoga_c630_ec_ucsi_write()`, `yoga_c630_ec_ucsi_read()`, and notifier register/unregister helpers. `yoga_c630_ec_request()` writes a request block and reads a response block under caller-held lock. `yoga_c630_ec_thread_intr()` retrieves the next event and calls the notifier chain.

Control flow: register reads build command buffers and call the shared request helper while holding `ec->lock`; `read16()` reads adjacent bytes little-endian style and rejects address `0xff`. UCSI data uses dedicated SMBus block read/write commands. Probe allocates state, initializes mutex/notifier, requests threaded IRQ, and creates auxiliary devices for PSY and UCSI via `devm_auxiliary_device_create()`.

State and persistence: all EC-visible state is firmware-owned. Kernel state is limited to serialization and notifier registration. Auxiliary consumers receive the EC pointer.

Dependencies and integration points: uses I2C SMBus block transfers, auxiliary bus, blocking notifiers, and platform data in `linux/platform_data/lenovo-yoga-c630.h`. OF compatible is `lenovo,yoga-c630-ec`.

Risks and edge cases: `yoga_c630_ec_request()` returns raw SMBus block-read byte count rather than checking it equals the requested response length. UCSI write/read similarly normalize only negative errors, not short transfers. Notifier events are untyped bytes and consumers must interpret them consistently. There are no PM hooks in this core file.

Test signals: verify PSY and UCSI auxiliary drivers bind, EC read8/read16 return known registers, UCSI version/read/write work, IRQ notifiers fire, and short-transfer behavior is acceptable on target adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/arm64/lenovo-yoga-c630.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/Kconfig

Purpose: Kconfig menu for ChromeOS/Chromebook platform support and Chrome EC child/transport drivers.

Important APIs, types, and functions: parent `CHROME_PLATFORMS` gates the submenu for X86, ARM, ARM64, or compile-test builds. Major symbols include `CHROMEOS_ACPI`, `CHROMEOS_LAPTOP`, `CHROMEOS_PSTORE`, `CHROMEOS_TBMC`, `CHROMEOS_OF_HW_PROBER`, `CROS_EC`, bus transports (`I2C`, `RPMSG`, `ISHTP`, `SPI`, `UART`, `LPC`), EC child interfaces (`CHARDEV`, `LIGHTBAR`, `VBC`, `DEBUGFS`, `SENSORHUB`, `SYSFS`, `TYPEC`, `USBPD_NOTIFY`, etc.), privacy screen, Type-C switch, Wilco EC, and KUnit protocol tests.

Control flow: `CROS_EC` selects `CROS_EC_PROTO`; transport symbols depend on the core plus their bus subsystems. MFD child drivers generally depend on `MFD_CROS_EC_DEV` and often default to that symbol. Privacy screen selects DRM privacy-screen support. The KUnit test symbol selects protocol helpers.

State and persistence: build-configuration only; selected symbols determine object graph and module availability.

Dependencies and integration points: tied to `drivers/platform/chrome/Makefile`, MFD Chrome EC devices, ACPI/OF firmware descriptions, USB Type-C, IIO sensorhub, debugfs, sysfs, and Wilco EC subdirectory.

Risks and edge cases: the LPC help text says the module is `cros_ec_lpcs`, matching the composite object, but user expectations may look for `cros_ec_lpc`. Defaults tied to `MFD_CROS_EC_DEV` pull in user interfaces automatically when the MFD core is enabled. Dependency mistakes can cause either missing child drivers or excessive build surface on non-ChromeOS machines.

Test signals: all enabled Chrome symbols should compile in representative x86/ARM/ARM64 and `COMPILE_TEST` configs. KUnit protocol tests exercise `CROS_EC_PROTO`, while transport and ACPI/OF drivers require integration hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/Makefile

Purpose: kbuild mapping for ChromeOS platform support drivers.

Important APIs, types, and functions: maps Kconfig symbols to single objects and composite modules. Composite objects include `cros_ec_lpcs-objs := cros_ec_lpc.o cros_ec_lpc_mec.o`, `cros-ec-typec-objs`, `cros-ec-proto-objs`, `cros-ec-sensorhub-objs`, and `cros_kunit_proto_test-objs`. It sets include flags for trace-generated objects.

Control flow: kbuild includes objects according to `obj-$(CONFIG_...)`. Optional Type-C altmode object inclusion is guarded by `ifneq ($(CONFIG_CROS_EC_TYPEC_ALTMODES),)`.

State and persistence: build-only; no runtime state.

Dependencies and integration points: must match Chrome Kconfig symbols and source filenames. The LPC object layout is important because MEC helper functions are linked into the same module. Trace objects need `-I$(src)` so generated trace headers resolve.

Risks and edge cases: composite module names differ from some source filenames (`cros_ec_lpcs`, `cros-ec-proto`, `cros-ec-typec`). Missing objects in composites can create unresolved symbols. Test object naming must align with KUnit module expectations.

Test signals: module builds for each Chrome symbol, especially composites and optional Type-C altmode inclusion. `modinfo` can confirm module descriptions and dependency graph.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_acpi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_acpi.c

Purpose: ACPI platform driver that exposes ChromeOS firmware ACPI package data as read-only sysfs attributes.

Important APIs, types, and functions: `chromeos_acpi_evaluate_method()` evaluates named ACPI methods. `chromeos_acpi_handle_package()` formats integer, string, and buffer package elements. `parse_attr_name()` maps sysfs names like `BINF.2` into ACPI method name plus package index. Macro-generated attributes expose first-level methods and up to eight `GPIO.N` attribute groups. `chromeos_acpi_device_probe()` records how many GPIO package groups firmware provides.

Control flow: sysfs reads parse the attribute name, call ACPI evaluation on the device handle, select the requested package/subpackage element, and format it to userspace. Probe only computes GPIO group visibility. `dev_groups` attaches all static groups to the platform device, with `is_visible` hiding GPIO groups above firmware count.

State and persistence: file-static `chromeos_acpi_gpio_groups` controls group visibility. Firmware data is read fresh on each sysfs access. No writable attributes or persistent kernel state.

Dependencies and integration points: ACPI platform IDs `GGL0001` and `GOOG0016`; sysfs device attributes; platform-driver core. The driver expects ChromeOS ACPI methods such as `BINF`, `CHSW`, `FMAP`, `FRID`, `FWID`, `GPIO`, `HWID`, `MECK`, `VBNV`, and `VDAT`.

Risks and edge cases: `chromeos_acpi_gpio_groups` is global, so multiple device instances would share visibility state. Buffers larger than PAGE_SIZE are truncated with a once-only info log. Unsupported ACPI object types fail with `-EINVAL`. Attribute-name parsing depends on exactly four-character method names plus dotted indexes.

Test signals: on ACPI Chromebook hardware, verify each expected sysfs file reads valid data, GPIO groups match firmware package count, oversized buffers truncate safely, and missing methods return errors without probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_laptop.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_laptop.c

Purpose: legacy Chromebook helper that instantiates or augments I2C/SMBus peripherals, mainly touchpads, touchscreens, and light sensors, on systems whose firmware does not fully describe them.

Important APIs, types, and functions: `struct i2c_peripheral` describes board info, alternate probe address, DMI IRQ source, adapter type, PCI device filter, software properties, and created client. `struct acpi_peripheral` describes ACPI HID devices needing software-node properties. `chromeos_laptop_check_adapter()` instantiates missing I2C devices on matching adapters. `chromeos_laptop_adjust_client()` attaches software nodes to existing ACPI-backed I2C clients. `chromeos_laptop_prepare_*()` deep-copy static DMI tables into mutable runtime state. `chromeos_laptop_i2c_notifier_call()` reacts to I2C bus add/remove events.

Control flow: module init finds a DMI match, prepares runtime peripheral arrays, registers an I2C bus notifier, then scans existing I2C adapters/clients. For non-ACPI entries it matches adapter names and optional PCI IDs, scans the primary address, optionally probes an alternate bootloader address through a dummy client, and creates the real client. For ACPI entries it checks HID presence, duplicates properties, attaches software nodes to matching clients, and re-triggers device attach if needed. Exit unregisters the notifier, unregisters created clients, removes software nodes, frees property copies and arrays.

State and persistence: `cros_laptop` is a global pointer to runtime-copied descriptors. Each descriptor caches the created or adjusted `i2c_client`. Software nodes and DMI-derived IRQ resources persist until module exit. Hardware state is not modified except through child driver probing.

Dependencies and integration points: depends on DMI, I2C bus notifiers, ACPI device matching, software nodes/property entries, PCI parent matching, DMI onboard-device IRQ data, and drivers for `cyapa`, `elan_i2c`, `atmel_mxt`, `isl29018`, `tsl2583`, and `tsl2563`.

Risks and edge cases: adapter matching uses string prefixes and can be fragile. The function name `chromes_laptop_instantiate_i2c_device` is misspelled but internal. DMI tables are broad for generic Google Atmel devices and rely on ACPI presence validation. IRQ lookup from DMI can fail and abort preparation for affected devices. The notifier must carefully detach clients on removal to avoid stale pointers.

Test signals: validate DMI matching on each listed Chromebook family, ensure the correct adapter/Pci ID receives each client, verify alternate bootloader address detection, confirm ACPI clients get software properties and reprobe, and unload/reload without leaking clients or software nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_laptop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_of_hw_prober.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_of_hw_prober.c

Purpose: OF/DT hardware prober for ChromeOS devices with drop-in I2C component variants, such as alternate touchscreens or trackpads.

Important APIs, types, and functions: `struct hw_prober_entry` maps a machine compatible to a prober function and data. `struct chromeos_i2c_probe_data` wraps I2C OF prober config and simple options. `chromeos_i2c_component_prober()` calls `i2c_of_probe_component()`. Static data describes dumb and simple probing for touchscreen/trackpad types, with board-specific power/reset delays for Hana and Squirtle.

Control flow: module init first checks whether any `hw_prober_platforms` entry matches `of_machine_is_compatible()`. If none match, it returns `-ENODEV`. Otherwise it registers a platform driver and a simple platform device. Probe iterates all matching entries and invokes their probers; only `-EPROBE_DEFER` stops iteration and defers probe, while other failures are ignored so later probers can run.

State and persistence: file-static `chromeos_of_hw_prober_pdev` holds the synthetic platform device until module exit. The prober mutates the live device tree through the I2C OF prober machinery, enabled by `OF_DYNAMIC`.

Dependencies and integration points: depends on OF, I2C, and the `I2C_OF_PROBER` namespace. It integrates with machine compatibles `google,hana`, `google,spherion`, `google,squirtle`, `google,steelix`, and `google,voltorb`.

Risks and edge cases: non-defer prober failures are intentionally ignored, which can hide misconfiguration. Static compatible tables must be maintained as boards/components change. Power/reset delay assumptions are encoded per board and may be sensitive to regulator or device-driver behavior.

Test signals: boot DT-based target devices and verify the chosen touchscreen/trackpad nodes become available, confirm regulator/reset sequencing on simple probes, ensure `-EPROBE_DEFER` eventually succeeds, and check module unload removes the synthetic device/driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_of_hw_prober.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_privacy_screen.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_privacy_screen.c

Purpose: ACPI DRM privacy-screen provider for ChromeOS devices exposing electronic privacy screens via GOOG0010 and a firmware `_DSM` interface.

Important APIs, types, and functions: `chromeos_privacy_screen_get_hw_state()` calls `_DSM` function 1 to read status. `chromeos_privacy_screen_set_sw_state()` calls `_DSM` functions 2 or 3 to enable or disable. `chromeos_privacy_screen_ops` registers those callbacks with `drm_privacy_screen_register()`.

Control flow: probe registers a DRM privacy screen tied to the platform device and stores the returned object as driver data. DRM consumers call the ops to read or set state; set validates requested state and updates both `hw_state` and `sw_state` after firmware accepts. Remove unregisters the privacy screen.

State and persistence: authoritative state is in firmware/privacy-screen hardware. The DRM privacy-screen object caches software and hardware state after reads/writes. No module-level state.

Dependencies and integration points: depends on ACPI and DRM privacy-screen framework. i915 and other DRM drivers may defer until this provider registers. ACPI match ID is `GOOG0010`; DSM GUID and function numbers are contract with ChromeOS firmware.

Risks and edge cases: get failure logs but leaves cached state unchanged. set treats any non-NULL `_DSM` result as success without validating object type or return value. Unsupported status values other than integer 1 are treated as disabled. Build help recommends built-in use to avoid DRM probe deferral latency.

Test signals: verify provider registration before display driver privacy-screen lookup, successful get/set over ACPI DSM, bad DSM object handling, and DRM userspace privacy-screen state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_privacy_screen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_pstore.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_pstore.c

Purpose: instantiates a `ramoops` platform device for ChromeOS persistent crash logging, using either ACPI-provided memory or a traditional x86 Chromebook VGA memory range.

Important APIs, types, and functions: `chromeos_ramoops_data` defines default pstore sizes and address `0xf00000`/`0x100000`. `ecc_size` module parameter optionally enables ECC. `chromeos_probe_acpi()` reads a memory resource from ACPI `GOOG9999`. `chromeos_pstore_init()` chooses ACPI or DMI path and registers `chromeos_ramoops`.

Control flow: init applies ECC size if positive, probes ACPI first, then falls back to DMI checks for known Chromebook/coreboot signatures. If either path matches, it registers the static `ramoops` platform device. Exit unregisters it. ACPI probing uses `platform_driver_probe()` only at init time.

State and persistence: persistent data resides in the reserved RAM range consumed by ramoops across reboots. Kernel state is static platform data and device registration. ACPI can override default address/size.

Dependencies and integration points: depends on DMI, ACPI when enabled, pstore/ramoops platform data, and the ramoops driver. DMI table matches Google coreboot Chromebooks plus early Samsung/Acer/Cr-48 devices.

Risks and edge cases: the hardcoded VGA range is x86-Chromebook-specific and unsafe on unmatched systems, so DMI gating is important. ACPI resource absence returns `-ENOMEM`, which prevents ACPI path. ECC parameter is read-only after load. The static ramoops device means only one instance.

Test signals: verify ramoops device registration on ACPI GOOG9999 and DMI-only systems, crash log persistence across reboot, ECC sizing behavior, and non-ChromeOS systems returning `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_pstore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_tbmc.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_tbmc.c

Purpose: ACPI tablet-mode switch driver for ChromeOS convertibles exposing GOOG0006 and method `TBMC`.

Important APIs, types, and functions: `chromeos_tbmc_query_switch()` evaluates ACPI integer method `TBMC` and reports `SW_TABLET_MODE`. `chromeos_tbmc_notify()` handles ACPI notify event `0x80`. `chromeos_tbmc_open()` reports current state when the input device is opened. `chromeos_tbmc_resume()` refreshes state after resume.

Control flow: probe allocates an input device named `Tablet Mode Switch`, sets ACPI HID as phys path, registers `SW_TABLET_MODE`, enables device wakeup, and installs an ACPI notify handler. Notifications trigger wakeup accounting and state refresh. Remove unregisters the notify handler and disables wakeup.

State and persistence: tablet mode state is read from firmware on demand. The input subsystem stores last reported switch state. No writable state.

Dependencies and integration points: ACPI platform device `GOOG0006`, input subsystem, PM wakeup framework. Firmware event is described as EC host mode-change propagated through ACPI.

Risks and edge cases: only notify `0x80` is recognized; other events log errors. ACPI method failure returns `-ENODEV` but notifications remain installed. The raw integer from firmware is reported as switch state without normalization.

Test signals: verify initial/open/resume state reports, ACPI notify changes, wakeup behavior, and removal cleans up notify handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_tbmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec.c

Purpose: core ChromeOS EC device layer shared by bus transports. It allocates common `cros_ec_device` state, registers EC/PD child platform devices, handles MKBP event interrupts and notifiers, and centralizes suspend/resume host-sleep events.

Important APIs, types, and functions: exported functions are `cros_ec_device_alloc()`, `cros_ec_register()`, `cros_ec_unregister()`, `cros_ec_irq_thread()`, `cros_ec_suspend_prepare()`, `cros_ec_suspend_late()`, `cros_ec_suspend()`, `cros_ec_resume_early()`, `cros_ec_resume_complete()`, and `cros_ec_resume()`. Internal helpers include `cros_ec_handle_event()`, `cros_ec_sleep_event()`, `cros_ec_ready_event()`, and IRQ top half `cros_ec_irq_handler()`.

Control flow: bus drivers allocate an EC device, fill bus callbacks and metadata, then call `cros_ec_register()`. Registration attempts RWSIG continue, queries protocol/features, requests IRQ if present, creates a `cros-ec-dev` child for the EC and optionally PD passthrough, populates OF child devices, clears sleep event, registers an interface-ready notifier, marks the device registered, and drains pending MKBP events. IRQ top half timestamps the event and wakes the thread; the thread loops `cros_ec_get_next_event()` until no more events, triggering wakeups and notifier calls. Suspend/resume helpers send host sleep events, disable/enable IRQs, preserve wake IRQ state, and report events queued during suspend.

State and persistence: `cros_ec_device` owns command buffers, max request/response sizes, protocol feature flags from `cros_ec_query_all()`, event/panic notifier chains, lockdep class, registered/suspended/wake flags, last event time, last resume result, and suspend timeout. Firmware state changes through host sleep commands and feature queries.

Dependencies and integration points: depends on Chrome EC protocol helpers, platform devices, PM wakeup/suspend, OF population, IRQ threading, and child drivers under MFD/platform Chrome EC. Bus transports provide `cmd_xfer`, `pkt_xfer`, optional `cmd_readmem`, IRQ, and physical name.

Risks and edge cases: child platform devices are manually unregistered on failures; ordering matters. Sleep-event commands are allowed to fail on firmware without support. Event fanout relies on `ec_dev->event_data` being populated by protocol helpers before notifier call. The registered flag is protected by the EC mutex but not every reader may hold it. IRQ disable assumes valid IRQ when suspend helpers are used.

Test signals: protocol query success, child device creation, PD passthrough when `max_passthru` is set, MKBP interrupt fanout, interface-ready re-query, suspend/resume host-sleep events, wake IRQ behavior, and removal unregistering children/notifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec.h -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec.h

Purpose: private header declaring the core Chrome EC APIs used by bus transports and related platform code.

Important APIs, types, and functions: forward declares `struct cros_ec_device` and `struct device`, and declares allocation, registration/unregistration, suspend/resume stage helpers, and `cros_ec_irq_thread()`.

Control flow: transport drivers include this header, allocate an EC device, assign transport callbacks, register with the core, and wire PM ops to the suspend/resume helpers. Event-only transports can call `cros_ec_irq_thread()` when their bus-specific event notification arrives.

State and persistence: no storage; it defines cross-file contracts for state owned by `struct cros_ec_device`.

Dependencies and integration points: includes `linux/interrupt.h` for `irqreturn_t`. It is internal to `drivers/platform/chrome`, not the public protocol header.

Risks and edge cases: the header exposes only high-level lifecycle functions; transports must still know public `cros_ec_device` fields from platform-data headers. Missing declarations here would cause bus drivers to duplicate externs.

Test signals: compile coverage for all Chrome EC transports and PM configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_chardev.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_chardev.c

Purpose: misc character device for userspace access to ChromeOS EC commands, legacy version text, direct EC memory reads, and queued MKBP events.

Important APIs, types, and functions: `struct chardev_priv` stores per-open EC pointer, notifier, waitqueue, event mask, event list, queued length, and command offset. `ec_get_version()` implements legacy read output. `cros_ec_chardev_mkbp_event()` enqueues selected events from the EC notifier chain. File operations implement open, poll, read, release, and ioctls `CROS_EC_DEV_IOCXCMD`, `CROS_EC_DEV_IOCRDMEM`, and `CROS_EC_DEV_IOCEVENTMASK`.

Control flow: probe registers a miscdevice named from platform data (`cros_ec` or `cros_pd`). Open allocates per-file state and registers a notifier on `ec_dev->event_notifier`. If the user sets an event mask, read blocks or returns queued event records containing one event-type byte plus payload. Without an event mask, read returns EC version strings once. Ioctl command copies a bounded `struct cros_ec_command` from userspace, applies command offset, calls `cros_ec_cmd_xfer()`, and copies response back. Release unregisters notifier and frees queued events.

State and persistence: event queue is per file descriptor and bounded by `CROS_MAX_EVENT_LEN` (`PAGE_SIZE`). `event_mask` selects event types. No persistent hardware state except commands userspace sends.

Dependencies and integration points: depends on `cros-ec-dev` platform devices, miscdevice, notifier chain, poll/waitqueue, userspace ABI headers in `linux/platform_data/cros_ec_chardev.h`, and EC protocol helpers.

Risks and edge cases: event bit calculation uses `1 << event_type`; large event types can overflow `unsigned long` semantics. `copy_to_user(buffer, &event->event_type, count)` relies on event_type and flexible data being contiguous. Event drops are silent when queue limit is exceeded. Ioctl command sizes are bounded by `EC_MAX_MSG_BYTES` but still trust userspace-provided header consistency.

Test signals: userspace `ioctl` command round trips, readmem on LPC-supported devices, event mask filtering and poll behavior, nonblocking reads, queue overflow/drop behavior, compat ioctl, and separate EC/PD command offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_chardev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_debugfs.c

Purpose: debugfs support for ChromeOS EC internals, including console log streaming, panicinfo blob, USB-PD status, EC uptime, last resume result, and suspend timeout tuning.

Important APIs, types, and functions: `struct cros_ec_debugfs` stores EC pointer, debugfs dir, circular log buffer, preallocated console read command, delayed work, panicinfo blob, and panic notifier. `cros_ec_console_log_work()` snapshots and drains EC console logs. `cros_ec_create_console_log()` gates creation on console-read v1 support. `cros_ec_get_panicinfo()` fetches panic data. `cros_ec_pdinfo_read()` queries PD port status. `cros_ec_uptime_is_supported()` and `cros_ec_uptime_read()` expose uptime conditionally.

Control flow: probe creates a debugfs directory named for the EC, fetches panicinfo once, creates console log polling if supported, creates `pdinfo`, optional `uptime`, `last_resume_result`, and writable `suspend_timeout_ms`, then registers a panic notifier. Console work sends `EC_CMD_CONSOLE_SNAPSHOT`, repeatedly issues `EC_CMD_CONSOLE_READ` recent reads, appends data to a fixed circular buffer, wakes readers, and reschedules itself. Panic notifier forces an immediate log poll and flushes it. Suspend cancels log polling; resume schedules it again. Remove removes debugfs and cancels work.

State and persistence: log buffer is in memory and lossy when full. Panicinfo is a snapshot at probe. `suspend_timeout_ms` writes modify the core EC device value used by host sleep v1 commands. `last_resume_result` is updated by core resume handling.

Dependencies and integration points: depends on debugfs, delayed work, EC protocol commands, panic notifier from core EC, PD command definitions, and platform `cros-ec-dev` data.

Risks and edge cases: debugfs is diagnostic and not stable ABI. The circular log can drop data if EC output exceeds polling capacity. Remove unregisters debugfs but does not visibly unregister the panic notifier, so lifetime depends on platform-device teardown ordering and devm state; this is worth review. `pdinfo` stops at first failed port query, which is normal for absent ports but hides later sparse ports.

Test signals: debugfs file creation based on feature support, blocking/nonblocking console reads and poll, log flush on EC panic notifier, uptime feature detection, writable suspend timeout changing suspend command parameters, and suspend/resume cancel/reschedule behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_i2c.c

Purpose: I2C transport driver for ChromeOS EC, supporting legacy protocol v2 and packet protocol v3.

Important APIs, types, and functions: `struct ec_host_request_i2c` and `struct ec_host_response_i2c` define the v3 I2C framing. `cros_ec_pkt_xfer_i2c()` sends v3 packets using core `cros_ec_prepare_tx()`. `cros_ec_cmd_xfer_i2c()` sends legacy v2 packets with command/version/length/checksum framing. Probe allocates a core EC device and assigns both transfer callbacks.

Control flow: v3 transfer sizes EC input/output buffers, writes protocol byte `0xda`, temporarily advances `ec_dev->dout` so `cros_ec_prepare_tx()` writes after the protocol byte, performs a combined I2C write/read, validates result, header length, response size, and checksum, then copies payload to `msg->data`. It returns `-EPROTONOSUPPORT` if a v2 EC responds to protocol byte as invalid with zero packet length. v2 transfer allocates temporary buffers, computes additive checksum, performs combined transfer, checks result and response checksum, and returns payload length. Probe sets `priv`, IRQ, callbacks, and phys name, then calls `cros_ec_register()`.

State and persistence: per-device state is the core EC object and I2C client pointer. v3 uses shared core buffers; v2 allocates per command. No transport-specific persistent hardware state.

Dependencies and integration points: I2C core, OF compatible `google,cros-ec-i2c`, ACPI ID `GOOG0008`, core Chrome EC lifecycle, and PM sleep helpers. IRQ comes from the I2C client.

Risks and edge cases: v3 response reads a fixed `insize + header` length; devices returning shorter transfers depend on adapter behavior. v2 path uses dynamic allocation for each command. I2C checksum logic assumes full buffers initialized by EC. Reboot command sleeps after transfer in both paths. PM ops use late suspend/resume wrappers around core full suspend/resume.

Test signals: protocol negotiation from v3 to v2 fallback, command transfer with payload boundaries, checksum failure handling, EC reboot delay, IRQ event delivery, OF/ACPI probe, and suspend/resume host-sleep behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_ishtp.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_ishtp.c

Purpose: ISH-TP transport driver for ChromeOS EC firmware running on Intel Integrated Sensor Hub.

Important APIs, types, and functions: ISH message `struct header` distinguishes `CROS_EC_COMMAND` responses from `CROS_MKBP_EVENT` notifications. `struct response_info` coordinates command response wait state. `struct ishtp_cl_data` stores ISH client, response state, reset/event work, and core EC device. `ish_send()` sends a tokenized command and waits for response. `process_recv()` parses incoming packets. `cros_ec_pkt_xfer_ish()` adapts core EC v3 packets to ISH framing. Probe/reset/remove manage ISH client lifecycle.

Control flow: probe takes a write lock on global `init_lock`, allocates and connects an ISH client, registers the receive callback, initializes work and waitqueue, releases the lock, then creates/registers a core EC device using packet transfer only. Command transfer takes a read lock unless reset/init is active, prepares EC request after ISH header, sends through `ish_send()`, validates response and checksum, and returns data length. Receive callback drains RX buffers: command responses validate token/status, copy into waiting buffer, set `received`, and wake the sender; MKBP events timestamp and schedule work to call `cros_ec_irq_thread()`. Reset work takes write lock, destroys/re-establishes the ISH connection, and refreshes EC private pointers.

State and persistence: `init_lock` globally serializes init/reset against send/receive. `next_token` in `ish_send()` is static across devices. Response state is single outstanding command per client. Work items bridge asynchronous ISH notifications to the core EC event path.

Dependencies and integration points: Intel ISH client interface, Chrome EC core/protocol helpers, waitqueues, workqueues, PM ops, and ISH GUID matching. No separate IRQ is assigned; MKBP channel drives event handling.

Risks and edge cases: `wait_event_interruptible_timeout()` return value is ignored except via `received`, so interrupted waits become timeout-like if no response arrived. Static token is global, which is acceptable for serialized commands but not per-client isolated. Global `init_lock` serializes all instances. Receive path has several error labels that set shared response error even for malformed async packets. PM calls core suspend/resume on the EC device.

Test signals: ISH connection establishment, host command round trips, token mismatch drop, timeout handling, MKBP event delivery, reset recovery, suspend/resume, and module remove cancelling work before unregistering EC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_ishtp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_lightbar.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_lightbar.c

Purpose: sysfs interface exposing Chromebook Pixel-style EC lightbar control to userspace.

Important APIs, types, and functions: global knobs include `lb_interval_jiffies`, `userspace_control`, `has_manual_suspend`, and `lb_version`. `alloc_lightbar_cmd_msg()` creates EC lightbar command buffers. `get_lightbar_version()` detects support and flags. Sysfs handlers expose `interval_msec`, `num_segments`, `version`, write-only `brightness`, `led_rgb`, `sequence`, `program`, and `userspace_control`. Suspend/resume send lightbar suspend/resume EC commands unless userspace has control.

Control flow: probe only binds to the main `cros_ec` device name, verifies lightbar support, attempts to enable manual suspend control, and creates a `lightbar` sysfs group under the EC class device. Each sysfs operation throttles through `lb_throttle()` to limit command rate, builds an `EC_CMD_LIGHTBAR_CMD`, and sends it via `cros_ec_cmd_xfer_status()`. `program_store()` sends either one legacy program payload or chunks for v3 extended program writes. Remove removes the sysfs group and releases manual suspend control.

State and persistence: module-global state controls throttle interval, userspace ownership, manual-suspend capability, and detected version. These are not per EC instance. Lightbar sequence/brightness/program state persists in EC firmware/hardware. `userspace_control` affects PM behavior only.

Dependencies and integration points: platform `cros-ec-dev`, EC lightbar host commands, sysfs attribute groups, PM ops, and Chrome EC command offsets. It intentionally excludes `cros_pd`.

Risks and edge cases: globals make multiple EC/lightbar instances unsafe. Throttling sleeps in sysfs write/read context and can be interrupted. `led_rgb_store()` parses decimal/hex-style integers with `sscanf("%i")` and requires groups of four. Program sizing depends on EC max request and protocol version. Manual suspend detection treats `-EINVAL` as unsupported but other errors as supported failure path.

Test signals: sysfs group appears only on devices with lightbar support, version/segment reads, sequence by name and number, RGB writes in groups of four, program upload for v0/v3 devices, throttle behavior, userspace-control PM suppression, and cleanup restoring EC control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_lightbar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_lpc.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_lpc.c

Purpose: LPC transport driver for ChromeOS EC on x86/ACPI/DMI systems, including Microchip MEC variants and Framework Laptop quirks.

Important APIs, types, and functions: `struct lpc_driver_data` describes DMI/ACPI quirks. `struct cros_ec_lpc` stores memory-map base, optional ACPI fixed-memory mapping, and read/write callbacks. Transport functions include raw port IO, MEC-aware wrappers, direct MMIO wrappers, `cros_ec_pkt_xfer_lpc()` for v3, `cros_ec_cmd_xfer_lpc()` for v2, and `cros_ec_lpc_readmem()` for userspace readmem. `cros_ec_lpc_acpi_notify()` handles EC panic, MKBP, and wake notifications.

Control flow: module init checks ACPI devices (`GOOG0004`, `FRMWC004`) or DMI match, registers the platform driver, and creates a synthetic platform device for DMI-only systems. Probe applies quirk data, optionally remaps memory base, attaches a different ACPI companion, acquires an AML mutex for MEC, reads ACPI fixed-memory resources for direct MMIO, otherwise reserves IO regions and initializes MEC EMI. It probes EC ID first through MEC then fallback non-MEC IO, reserves remaining regions, allocates/registers the core EC device, optionally sets IRQ, and installs ACPI notify handler. Command transfers write request buffers/registers, trigger host command, poll busy status up to one second, validate result/checksum, and return response length.

State and persistence: static `cros_ec_lpc_acpi_device_found` controls synthetic-device cleanup. Driver quirk data is static. Per-device LPC state holds IO/MMIO access functions. Firmware shared memory is readable through `cmd_readmem`. ACPI notify can trigger system shutdown on EC panic.

Dependencies and integration points: ACPI, DMI, IO port access, optional fixed-memory resources, MEC helper file, core Chrome EC, platform devices, PM hooks, reboot/hw-protection path, and Framework/Chromebook DMI tables.

Risks and edge cases: IO region reservation differs for MEC vs non-MEC and can fail on partially exposed hardware. EC ID probing is the critical hardware-detection gate. ACPI panic notify triggers emergency log, notifier fanout, uevent, and orderly shutdown. Polling busy status uses a one-second timeout. `cros_ec_lpc_readmem()` rejects `offset >= EC_MEMMAP_SIZE - bytes`, which has edge behavior for zero-length string reads. Forced synchronous probe avoids ACPI child races.

Test signals: DMI-only and ACPI-backed probe paths, Framework quirk variants, MEC and non-MEC EC ID detection, v2/v3 host commands, readmem through chardev, ACPI MKBP and panic notifications, wake notification, suspend prepare/late/resume early/complete sequencing, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_lpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_lpc_mec.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_lpc_mec.c

Purpose: Microchip EC EMI access helper for the Chrome EC LPC transport. It provides range detection, byte/long auto-increment read/write through MEC EMI registers, and optional ACPI AML mutex coordination.

Important APIs, types, and functions: exported functions are `cros_ec_lpc_mec_init()`, `cros_ec_lpc_mec_acpi_mutex()`, `cros_ec_lpc_mec_in_range()`, and `cros_ec_lpc_io_bytes_mec()`. Internal helpers lock/unlock either a kernel mutex or AML mutex and program EMI address registers via `cros_ec_lpc_mec_emi_write_address()`.

Control flow: LPC probe initializes the MEC EMI base/end. For each range, `cros_ec_lpc_mec_in_range()` validates whether the requested offset lies wholly inside or outside the MEC window. `cros_ec_lpc_io_bytes_mec()` chooses byte access for misaligned/short operations or long auto-increment for aligned larger operations, locks, writes the EMI address, loops over data B0-B3 ports, adjusts access mode for misaligned tail writes, computes checksum, unlocks, and returns checksum or error.

State and persistence: file-static `mec_emi_base`/`mec_emi_end` define the active window. `aml_mutex` optionally replaces the local `io_mutex`, coordinating with ACPI AML code. No per-device storage, so only one MEC range/mutex is supported.

Dependencies and integration points: raw IO port access, ACPI mutex API, LPC driver wrappers, and definitions from the header. Used by `cros_ec_lpc.c` for memory-map and host-command bytes that fall in the MEC range.

Risks and edge cases: globals make multiple MEC instances unsafe. If unlock via AML mutex fails, the function returns an error after data transfer, which may confuse callers expecting checksum. Range checks warn and reject partial overlaps. Long access cannot be used for misaligned writes because B3 flushes, so mode switching is subtle.

Test signals: aligned and misaligned reads/writes, zero-length operations, boundary and partial-overlap range checks, AML mutex acquisition failures, checksum correctness, and concurrent access with ACPI firmware on Framework MEC systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_lpc_mec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_lpc_mec.h -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_lpc_mec.h

Purpose: private interface and register definitions for Microchip EC EMI support used by the Chrome EC LPC module.

Important APIs, types, and functions: defines `enum cros_ec_lpc_mec_emi_access_mode` for byte/word/long/long-auto-increment access, `enum cros_ec_lpc_mec_io_type` for read/write, register offset macros relative to an EMI base, and declarations for MEC init, ACPI mutex setup, range check, and byte IO.

Control flow: `cros_ec_lpc.c` includes this header, initializes base/end, checks whether offsets are MEC-mapped, and delegates read/write bytes to `cros_ec_lpc_io_bytes_mec()` when appropriate.

State and persistence: no storage in the header. Declared functions operate on static state in `cros_ec_lpc_mec.c`.

Dependencies and integration points: includes `linux/acpi.h`; intended only for Chrome EC LPC transport internals.

Risks and edge cases: register macros assume an eight-port EMI window. Long auto-increment semantics are hardware-specific and callers must preserve alignment/range requirements. Since implementation state is global, the API does not support independent per-device contexts.

Test signals: compile integration with the composite `cros_ec_lpcs` module and runtime checks through the MEC helper implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_lpc_mec.h -->
