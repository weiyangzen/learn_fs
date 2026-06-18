# subset-b-005145 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/oxpec.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/oxpec.c

Purpose: This is a DMI-gated platform driver for OneXPlayer, AOKZOE, and OrangePi handheld systems. It exposes EC-backed fan tachometer/PWM control through hwmon, turbo-button takeover and turbo LED controls through sysfs attributes on the platform device, and charge-control extensions on ACPI battery power supplies for supported boards.

Important APIs, types, and functions: `enum oxp_board` records the matched board family; `dmi_table` maps vendor/board names to that enum. `read_from_ec()` and `write_to_ec()` serialize EC access with the ACPI global lock and call `ec_read()`/`ec_write()`. `oxp_ec_hwmon_ops` implements `hwmon` reads/writes for `fan_input`, `pwm_input`, and `pwm_enable`. `tt_toggle_show/store` and `tt_led_show/store` expose board-specific EC bits as `tt_toggle` and `tt_led`. `oxp_psy_ext` plugs `POWER_SUPPLY_PROP_CHARGE_BEHAVIOUR` and `POWER_SUPPLY_PROP_CHARGE_CONTROL_END_THRESHOLD` into batteries via `devm_battery_hook_register()`.

Control flow: `oxp_platform_init()` finds a DMI match, rejects old Intel OneXPlayer boards that reuse AMD DMI strings, stores the board enum globally, and creates a bundled platform device/driver. Probe registers the `oxp_ec` hwmon device and, when `oxp_psy_ext_supported()` matches the board, registers the ACPI battery hook. Runtime operations choose EC register addresses by board enum, read or write EC bytes, and scale the exported PWM range to the native EC range for OrangePi, OXP2/X1/G1i, and older mini AMD boards.

State and persistence: Persistent hardware state lives in EC registers: fan manual/auto mode, PWM duty, turbo takeover bit, turbo LED value, charge limit, and charge-inhibit masks. Driver process state is limited to global `board`, `oxp_dev`, `oxp_mutex`, and the platform device pointer. There is no software persistence across module unload; EC settings can outlive the driver depending on firmware behavior.

Dependencies and integration points: The driver depends on ACPI EC access, DMI, hwmon, platform devices, processor vendor data, and ACPI battery hooks. User-visible integration is through `/sys/class/hwmon/...`, platform device attributes, and battery power-supply properties. It also relies on the standard `pwm_enable` semantics where 0 is full speed, 1 is manual, and 2 is auto.

Risks and edge cases: `read_from_ec()` can return on an `ec_read()` failure before releasing the ACPI global lock, which is a critical lock-lifetime risk. Multi-byte fan reads construct `*val` with a shifting pattern that deserves review against expected little-endian EC layout. Board-specific register tables are firmware-sensitive; a wrong DMI mapping can write to unrelated EC locations. `pwm_enable` read infers full-speed state by reading fan speed and comparing it to 255, which appears suspicious because fan tachometer units are not PWM duty. Battery charge behavior masks are shared across boards with comments noting model-specific differences.

Test signals: Useful validation includes loading only on known DMI strings, checking hwmon fan/PWM attributes, verifying PWM scaling on each board family, toggling turbo takeover/LED where visible, checking battery extension properties on X1/G1/Fly boards, and testing EC failure paths for lock release. Suspend/resume behavior should be checked manually because the driver does not restore settings explicitly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/oxpec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/p2sb.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/p2sb.c

Purpose: This file provides exported support for retrieving the BAR0 memory resource of Intel Primary-to-Sideband (P2SB) bridge functions, including devices hidden by firmware. It lets other drivers call `p2sb_bar()` without temporarily exposing the hidden PCI device during later sysfs rescans.

Important APIs, types, and functions: `p2sb_bar()` is the exported GPL API. `p2sb_get_devfn()` chooses the default P2SB devfn, with Goldmont/Goldmont Plus overrides. `struct p2sb_res_cache` stores a bus id and copied resource per PCI function. `p2sb_cache_resources()` runs at `fs_initcall_sync`, hides/unhides the device under `pci_lock_rescan_remove()`, and caches BAR0. `p2sb_read_from_cache()` and `p2sb_read_from_dev()` serve callers depending on whether BIOS hid the bridge.

Control flow: Early init finds bus 0/domain 0, verifies the P2SB devfn is not an unrelated device by checking class code, records whether BIOS set `P2SBC_HIDE`, and if hidden clears the hide bit, scans the P2SB function, copies BAR0, optionally scans Goldmont SPI function, removes the temporary devices, and hides P2SB again. Later `p2sb_bar()` resolves a bus and devfn, then returns either cached resource data or live PCI resource data.

State and persistence: State is global and static: `p2sb_resources[]`, `p2sb_hidden_by_bios`, and a cached bus pointer in `p2sb_get_bus()`. It persists for the kernel lifetime and is not revalidated after PCI topology changes. Copied resources intentionally avoid pointer fields because scanned devices are removed immediately.

Dependencies and integration points: The code integrates with PCI core scanning/removal locks, x86 CPU matching, Intel family identifiers, and `linux/platform_data/x86/p2sb.h`. Downstream users include sideband, GPIO, SPI, and PMC-related drivers that need the P2SB BAR.

Risks and edge cases: The cache assumes PCI bus identity remains valid and only covers eight functions. Failure to cache hidden resources early leaves later callers without a safe way to expose P2SB. The init code avoids touching a different device at the same devfn by class check, but firmware/platform quirks can still make BAR validity fragile. The comment notes a duplicated PCI-function-count constant.

Test signals: Boot logs and callers of `p2sb_bar()` should be tested on hidden and visible P2SB systems, especially Goldmont where SPI is also cached. PCI rescan/sysfs stress should verify no deadlock and no transient exposed P2SB device remains. Unit-style checks can validate `p2sb_valid_resource()` behavior for unset resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/p2sb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/panasonic-laptop.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/panasonic-laptop.c

Purpose: This ACPI platform driver supports Panasonic Let's Note hotkeys, vendor brightness control, optional optical-drive power control, mute/sticky-key/eco-mode settings, and related sysfs state on MAT0012/MAT0013/MAT0018/MAT0019 ACPI devices.

Important APIs, types, and functions: `struct pcc_acpi` stores the ACPI handle, SINF table, input device, backlight device, optical-drive platform device, and cached settings restored on resume. `acpi_pcc_write_sset()`, `acpi_pcc_get_sqty()`, and `acpi_pcc_retrieve_biosdata()` wrap the vendor `SSET`, `SQTY`, and `SINF` ACPI methods. Backlight integration uses `pcc_backlight_ops`; input uses `sparse_keymap` and `acpi_pcc_generate_keyinput()`. Sysfs attributes expose `numbatt`, `lcdtype`, `mute`, `sticky_key`, `eco_mode`, brightness registers, and `cdpower`.

Control flow: Probe reads `SQTY`, allocates an extra SINF slot for firmware off-by-one packages, initializes input, retrieves BIOS data, registers a vendor backlight only when ACPI video selects vendor backlight, resets sticky key mode, caches settings, creates sysfs attributes, installs ACPI notification handling, and optionally creates a separate `panasonic` platform device for optical drive power. Notifications query `HINF` and report sparse key events, suppressing brightness keys if ACPI video already handles them. Resume replays cached SSET values.

State and persistence: Firmware state is in ACPI methods and the SINF package. Software caches `sticky_key`, `eco_mode`, mute, AC/DC/current brightness for resume restoration. `sleep_keydown_seen` is a static workaround for firmware that sends missing sleep/hibernate key-down events. Optical-drive power is queried and set through global ACPI paths.

Dependencies and integration points: The driver integrates with ACPI companion devices, the input subsystem, i8042 serio filtering for duplicate volume keys, ACPI video backlight arbitration, backlight class, platform devices, and sysfs. Optional optical-drive support uses `\_SB.STAT`, `\_SB.FBAY`, `\_SB.CDDI`, and `\_SB.CDDR`.

Risks and edge cases: ACPI packages and SINF indices vary by model, so visibility checks gate only some attributes. Several store paths accept out-of-range values by silently doing nothing and still returning `count`. Optical-drive paths are hard-coded and one notifier path is model-specific. The i8042 filter is global and static state must not leak across unrelated devices. Probe has many manual unwind labels, so lifecycle regressions are likely if features are added.

Test signals: Validate hotkey event mapping, brightness keys with and without ACPI video handling, vendor backlight registration, sysfs visibility based on `num_sifr`, resume restoration, i8042 duplicate filtering for volume keys, and optical-drive power if ACPI methods exist. Firmware error tests should cover bad `SQTY`, malformed `SINF`, and notification events other than `0x80`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/panasonic-laptop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/pcengines-apuv2.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/pcengines-apuv2.c

Purpose: This module creates board-specific GPIO, LED, and polled-key platform devices for PC Engines APU2/APU3/APU4 boards using the AMD FCH GPIO controller. It turns DMI-detected board wiring into standard `gpio-amd-fch`, `leds-gpio`, and `gpio-keys-polled` devices.

Important APIs, types, and functions: `board_apu2` is `amd_fch_gpio_pdata` describing FCH GPIO registers and names. Software nodes (`apu2_gpiochip_node`, LED child nodes, key node) describe firmware-like properties for GPIO consumers. `apu_create_pdev()` wraps `platform_device_register_full()`. `apu_board_init()` gates on `apu_gpio_dmi_table`, registers software nodes, then creates GPIO, LED, and key devices.

Control flow: Module init DMI-matches several legacy/mainline BIOS naming variants, registers a software-node hierarchy, registers the AMD FCH GPIO platform device with board pdata, then registers the `leds-gpio` and `gpio-keys-polled` consumers. Failure unwinds in reverse order. Module exit unregisters keys, LEDs, GPIO, and software nodes.

State and persistence: State is static platform-device pointers and software-node data. Hardware state belongs to GPIO/LED child drivers after instantiation. There is no persistent configuration or runtime mutation inside this file.

Dependencies and integration points: The module depends on DMI, `gpio-amd-fch` platform data, generic software-node property handling, LED GPIO binding semantics, GPIO keys polled binding semantics, and `MODULE_SOFTDEP` to load required platform drivers first.

Risks and edge cases: DMI matching uses string-prefix-like board-name variants, and the comment warns APU1 is incompatible. GPIO register order must match the line indexes referenced by software-node GPIO properties. Because it creates global platform devices, partial registration failure must unwind exactly or stale software nodes/GPIO consumers may remain.

Test signals: Test on APU2, APU3, and APU4 DMI variants; verify named GPIO lines, active-low front LEDs, and front-button `KEY_RESTART` events. Failure-injection should confirm each unwind label unregisters previously created devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/pcengines-apuv2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/pmc_atom.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/pmc_atom.c

Purpose: This is the Intel Atom SoC Power Management Controller support code for Bay Trail and Cherry Trail. It maps PMC registers, exports `pmc_atom_read()`, registers debugfs status files, configures PMC wake bits, optionally provides `pm_power_off`, registers PMC platform clocks, and hooks s2idle diagnostics.

Important APIs, types, and functions: `struct pmc_dev` holds the global PMC MMIO mapping, register map, debugfs directory, and init flag. `struct pmc_reg_map` and `struct pmc_bit_map` define status/disable/pss bit names for Bay Trail and Cherry Trail. `pmc_atom_read()` is the exported read helper. `pmc_power_off()` writes ACPI PM1 control S5 bits. `pmc_dbgfs_register()` creates `dev_state`, `pss_state`, and `sleep_state`. `pmc_s2idle_check()` reports devices/clocks blocking low-power idle.

Control flow: `pmc_atom_init()` scans all PCI devices for VLV/CHT PMC IDs instead of binding a PCI driver, because another driver owns the multifunction device. `pmc_setup_dev()` reads ACPI/PMC base addresses from PCI config, maps PMC MMIO, installs poweroff if possible, writes `PMC_S0IX_WAKE_EN`, creates debugfs, registers `clk-pmc-atom` platform data with DMI critical-clock quirks, registers s2idle checks, and marks the singleton initialized.

State and persistence: State is a singleton `pmc_device` plus `acpi_base_addr` and `pmc_clk_is_critical`. Register writes change platform wake and clock behavior. Debugfs output and s2idle checks are live views of PMC registers. There is no module exit path shown because initialization is by `device_initcall`.

Dependencies and integration points: Dependencies include PCI, ACPI, debugfs, suspend/LPS0 hooks, DMI, the `clk-pmc-atom` platform clock driver, and Siemens DMI parsing helpers. It interacts with `pm_power_off` and can affect system shutdown behavior.

Risks and edge cases: The singleton assumes one PMC. It returns the clock-registration error even after successfully mapping and initializing the PMC, so a clock failure can make init report failure despite partial side effects. There is no explicit unmap/debugfs cleanup in this initcall-style driver. DMI critical-clock logic mutates global `pmc_clk_is_critical`, including Siemens-specific negative cases. Incorrect false-positive masks could over-report s2idle blockers.

Test signals: Validate debugfs files on Bay Trail and Cherry Trail, `pmc_atom_read()` before/after init, poweroff path with nonzero ACPI base, clock registration and critical-clock DMI quirks, and s2idle diagnostics on systems with known D0 blockers. PCI scan should verify only supported device IDs initialize the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/pmc_atom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/portwell-ec.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/portwell-ec.c

Purpose: This Portwell embedded-controller driver exposes EC temperature/voltage sensors through hwmon, eight EC GPIOs through gpiolib, and an EC watchdog through the watchdog framework for boards such as NANO-6064.

Important APIs, types, and functions: `struct pwec_sensor_prop` describes label/register/scale metadata. `struct pwec_board_info` selects visible temp/input channels. `pwec_read()`/`pwec_write()` access fixed I/O space, while `pwec_read16_stable()` protects 16-bit ADC reads from rollover. GPIO methods implement get/set/direction reporting, watchdog methods implement start/stop/ping/set_timeout/get_timeleft, and `pwec_hwmon_ops` provides sensor values and labels.

Control flow: Module init checks DMI unless `force` is set, registers a platform driver, and creates a `portwell-ec` platform device carrying board-info data. Probe reserves I/O region `0xe300-0xe3ff`, verifies the firmware vendor string `PWG`, registers a GPIO chip, registers hwmon when reachable, sets the watchdog parent, and registers the watchdog. Suspend stops an active watchdog and resume restarts it.

State and persistence: Hardware state includes GPIO value/direction registers, watchdog enable and countdown registers, and ADC sensor registers. Software state is mostly static metadata and a single static `watchdog_device`. The watchdog timeout is retained in `ec_wdt_dev.timeout`; suspend/resume toggles the EC watchdog around sleep.

Dependencies and integration points: It integrates with DMI, platform devices, I/O port resource management, gpiolib, hwmon, watchdog, and PM sleep ops. The `force` parameter permits full sensor-channel exposure without DMI validation.

Risks and edge cases: EC access has no explicit lock around GPIO and watchdog/hwmon accesses, so concurrent read-modify-write GPIO operations could race. Direction changing is deliberately unsupported because of board issues. A static watchdog device limits the design to one instance. Forced load on non-Portwell hardware can touch fixed I/O ports after only the firmware-vendor check. Suspend stopping an active watchdog may weaken expected watchdog coverage during sleep.

Test signals: Verify DMI-gated and forced probe, vendor string rejection, hwmon labels/scale calculations, stable ADC read behavior under changing registers, GPIO get/set for eight pins without direction changes, watchdog timeout range and timeleft stability, and watchdog restart after suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/portwell-ec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/quickstart.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/quickstart.c

Purpose: This ACPI Direct App Launch driver supports PNP0C32 quickstart buttons. It exposes a generic input key with a user-space-remappable scancode and publishes the vendor-defined GHID button role through a read-only sysfs attribute.

Important APIs, types, and functions: `struct quickstart_data` stores the device, input lock, input device, formatted names, and GHID id. `quickstart_get_ghid()` evaluates ACPI `GHID` as a byte/word/dword little-endian buffer. `quickstart_notify()` handles runtime notify event `0x80`, reports scancode `0x1` through sparse-keymap, and generates an ACPI netlink event. `button_id_show()` exposes the decoded GHID.

Control flow: Probe obtains the ACPI handle, allocates state and mutex, enables wakeup before evaluating `GHID` because the method can emit pending wake notifications, creates and registers an input device, installs an ACPI notify handler, and registers a devm cleanup action. Notifications lock `input_lock`, report a press/release event with autorelease, and then send netlink notification.

State and persistence: State is per-device and devm-managed. The decoded GHID is cached in `data->id`. Wake capability is enabled on the device. The button's semantic role is intentionally left to user space via hwdb remapping.

Dependencies and integration points: The driver integrates with ACPI PNP0C32, input sparse-keymap, sysfs attribute groups, device wakeup, and ACPI netlink event generation. It uses `PROBE_PREFER_ASYNCHRONOUS`.

Risks and edge cases: `quickstart_get_ghid()` leaks the ACPI buffer if `buffer.pointer` is NULL after a successful evaluation, though that path is unusual. Unknown GHID buffer lengths fail probe. Only runtime event `0x80` is acted on; the pre-boot/off event is indirectly consumed by GHID evaluation. Because all keys report `KEY_UNKNOWN`, user-space mapping is required for useful behavior.

Test signals: Test PNP0C32 probe, GHID lengths of 1/2/4 bytes, invalid GHID lengths, wake-button pending notification behavior, sysfs `button_id`, input event generation, and cleanup of notify handler on driver detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/quickstart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/redmi-wmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/redmi-wmi.c

Purpose: This WMI driver handles Xiaomi Redmibook keyboard events identified by GUID `46C93E13-EE9B-4262-8488-563BCA757FEF`. It maps vendor WMI payloads to Linux input keys and ignores firmware events that other components handle.

Important APIs, types, and functions: `redmi_wmi_keymap` maps 32-bit scancodes to input keycodes or ignores. `struct redmi_wmi` stores an input device and a mutex protecting key-event sequences. `redmi_wmi_probe()` allocates state and registers the input device. `redmi_wmi_notify()` validates WMI buffer events, decodes the first little-endian u32 payload, looks up the sparse keymap entry, and reports it.

Control flow: The WMI core binds the driver by GUID and minimum event size. Probe sets up `Redmibook WMI keys`. Notify rejects non-buffer or too-short events, decodes payload, ignores unknown events at debug level, applies the AI-key press/release quirk, and reports the event under `key_lock`.

State and persistence: State is per-WMI-device and devm-managed. There is no persistent hardware state; all behavior is event translation. AI key value state is derived from `AI_KEY_VALUE_MASK`.

Dependencies and integration points: Dependencies include WMI, ACPI object buffers, input sparse-keymap, mutexes, and Linux input-event codes. `no_singleton = true` permits multiple matching WMI devices.

Risks and edge cases: Payload matching relies on exact 32-bit values and a hard-coded minimum length of 32 bytes. Unknown events are debug-only and can be missed during field validation. AI key behavior disables autorelease, so incorrect payload bit handling can leave the key logically stuck.

Test signals: Feed known payloads for screenshot, app launcher, config, video mode, refresh toggle, vendor key, Fn keys, ignored keyboard-backlight/power/Fn-lock events, and both AI key positions. Validate bad ACPI object types and short buffers are rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/redmi-wmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/samsung-galaxybook.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/samsung-galaxybook.c

Purpose: This modern Samsung Galaxy Book platform driver supports SAM0426-SAM0430 ACPI devices. It exposes keyboard backlight LEDs, battery charge threshold extension, platform performance profiles, firmware-attributes controls, camera/microphone block-recording state, ACPI hotkeys, and selected i8042-filtered hotkeys.

Important APIs, types, and functions: `struct samsung_galaxybook` is the central per-device state. `struct sawb` is the packed Samsung ACPI command buffer used by `CSFI` and `CSXI`. `galaxybook_acpi_method()` validates typed buffer responses, success flag `0xaa`, and failure code `0xff`. Feature initializers include `galaxybook_kbd_backlight_init()`, `galaxybook_battery_threshold_init()`, `galaxybook_platform_profile_init()`, `galaxybook_fw_attrs_init()`, `galaxybook_input_init()`, and `galaxybook_i8042_filter_install()`.

Control flow: Probe obtains the ACPI companion, allocates state, enables the ACPI device via `SDLS`, installs all-notify handling, enables notifications and power-management features, initializes platform profile, battery threshold, keyboard backlight, input, firmware attributes, and optional i8042 filtering in a deliberate order. ACPI notifications cycle platform profile, schedule keyboard-backlight work, report mic mute, toggle or report camera-lens-cover state, and generate netlink events. Work items perform ACPI writes outside interrupt/notify context.

State and persistence: Firmware state includes power-on-lid-open, USB charging, block-recording, keyboard backlight, performance mode, and battery charge threshold. Software caches feature availability booleans, platform-profile-to-performance-mode mapping, work items, input device, locks, battery hook, and firmware-attribute kobjects. Devm cleanup disables ACPI, removes handlers, unregisters firmware-attribute ksets/devices, and removes i8042 filters/work.

Dependencies and integration points: The driver integrates with ACPI methods/notifications, firmware attributes class, LED class, platform-profile framework, input subsystem, i8042 serio filter, power-supply extension API, ACPI battery hooks, sysfs/kobjects, GUID export, and workqueues.

Risks and edge cases: The packed ACPI buffer protocol is firmware-sensitive; response length/status validation is strong but command semantics are model-specific. Platform profile probing indexes `buf.iobs[i]` starting at 1 while comments describe `iob1-iobX`, so boundary expectations should be checked against the packed layout. `platform_profile_cycle()` is global and may affect other platform-profile providers. Firmware attributes manually create sysfs groups under a kset, so error cleanup and duplicate registration matter. i8042 filtering uses a static `extended` flag in a callback shared by installations.

Test signals: Test on each SAM042x ID with feature permutations: absent keyboard backlight, absent block recording, absent performance modes, and supported battery threshold. Validate `CSFI`/`CSXI` failure codes, platform profile mapping, firmware-attributes read/write, input `KEY_MICMUTE` and `SW_CAMERA_LENS_COVER`, i8042 hotkey filtering, work cancellation on remove, and ACPI notification netlink emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/samsung-galaxybook.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/samsung-laptop.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/samsung-laptop.c

Purpose: This legacy Samsung laptop driver accesses Samsung BIOS SABI/SMI interfaces to provide backlight, wireless rfkill, performance level, battery life extender/charge type, USB charging, lid handling, keyboard backlight LED, debugfs SABI access, and some model quirks on non-EFI Samsung laptops.

Important APIs, types, and functions: `struct sabi_config` describes SABI v2/v3 signatures, header offsets, command IDs, performance-level names, and brightness bounds. `struct samsung_laptop` holds mapped BIOS memory, SABI interface mapping, platform/backlight/rfkill/LED/debug/battery state, quirks, and PM notifier. `sabi_command()` is the core SMI transaction wrapper. Subsystem initializers include `samsung_sabi_init()`, `samsung_sysfs_init()`, `samsung_backlight_init()`, `samsung_rfkill_init()`, `samsung_leds_init()`, `samsung_lid_handling_init()`, `samsung_battery_hook_init()`, and `samsung_debugfs_init()`.

Control flow: Module init rejects EFI boot, DMI-gates unless forced, allocates state, selects vendor backlight handling based on ACPI video, creates a platform device, maps the `0xf0000` BIOS segment, searches for `SECLINUX` or `SwSmi@`, derives the SABI interface pointer, maps it, optionally enables Linux mode, detects brightness stepping quirks, then registers sysfs, backlight, rfkill, LEDs, lid handling, battery extension, debugfs, and a PM notifier. Exit reverses those registrations and disables Linux/lid modes.

State and persistence: Firmware state is changed through SABI commands: brightness, backlight power, wireless status, performance level, battery extender, USB charge, lid handling, keyboard backlight, and Linux mode. Software state includes mapped regions, rfkill devices, LED workqueue, quirks, debug command/data, SABI diagnostic string, and PM notifier. Battery extender is exposed both as a deprecated sysfs attribute and as a power-supply charge-type extension.

Dependencies and integration points: The driver integrates with DMI, direct BIOS memory mapping, I/O ports/SMI, platform device, backlight class, LED class, rfkill, power-supply and ACPI battery hooks, ACPI video backlight arbitration, debugfs, PM notifier, and module parameters `force`/`debug`.

Risks and edge cases: This is high-risk hardware access: it maps low BIOS memory, writes to SMI ports, and can call arbitrary SABI commands through debugfs. It is disabled on EFI due to known risk. `sabi_command()` uses a mutex, but many feature detections call hardware from sysfs visibility. The platform-device pointer is global and only one instance is supported. The LED workqueue must be destroyed after pending work is drained; current teardown unregisters the LED then destroys the queue. Quirk tables are DMI-sensitive.

Test signals: Validate DMI/force/EFI gating, SABI signature detection for v2 and v3, Linux mode on/off, brightness stepping workaround, backlight with ACPI-video arbitration, rfkill status and fallback, sysfs visibility for optional commands, charge-type extension, keyboard backlight workqueue, PM post-hibernation restoration, debugfs command path, and full error-unwind coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/samsung-laptop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/samsung-q10.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/samsung-q10.c

Purpose: This small legacy backlight driver supports Samsung Q10/Q20/Q25 and Dell Latitude X200 systems by driving brightness through embedded-controller ACPI query methods.

Important APIs, types, and functions: `ec_handle` stores the ACPI EC handle. `samsungq10_bl_set_intensity()` implements backlight updates by repeatedly evaluating `_Q63` to step down to minimum, then `_Q64` to step up to the requested brightness. `samsungq10_probe()` registers a `BACKLIGHT_PLATFORM` device named `samsung`. DMI entries gate supported systems unless `force` is set.

Control flow: Module init checks DMI or `force`, obtains the EC handle via `ec_get_handle()`, and creates a bundled platform device/driver. Probe registers the backlight device with max brightness 7. Update status performs step-down then step-up ACPI method calls. Exit unregisters the platform device and driver.

State and persistence: The driver has no cached brightness; hardware state is modified by EC ACPI query methods. Brightness may persist in firmware. Software state is just the EC handle and platform device pointer.

Dependencies and integration points: It integrates with ACPI EC, DMI, platform device bundle creation, and the backlight class.

Risks and edge cases: Brightness setting is destructive stepping rather than absolute hardware write; if `_Q63` or `_Q64` semantics differ, brightness can drift or fail. There is no `get_brightness`, so the backlight core cannot query actual state. Forced load can execute EC methods on unsupported systems if an EC exists.

Test signals: Test DMI and forced loading, EC handle absence, backlight registration/removal, all brightness values 0-7, and ACPI method failure propagation from `_Q63`/`_Q64`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/samsung-q10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/sel3350-platform.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/sel3350-platform.c

Purpose: This ACPI platform driver supports SEL-3350 computers with the b2093 mainboard. It maps Broxton GPIOs to standard LEDs and exposes two mains power supplies using detect/good GPIOs.

Important APIs, types, and functions: GPIO lookup tables `sel3350_leds_table` and `sel3350_gpios_table` map Broxton pinctrl device names to LED and power-supply lines. `sel3350_power_get_property()` reports `HEALTH`, `PRESENT`, and `ONLINE` from GPIO values. `sel3350_probe()` registers lookup tables, creates the `leds-gpio` platform device, obtains power GPIOs, and registers two power supplies.

Control flow: The platform driver binds ACPI ID `SEL0003`. Probe adds GPIO lookup tables, creates the LED child platform device, gets A/B detect and good GPIO descriptors, registers `sel_ps_a` and `sel_ps_b`, and unwinds lookup tables/LED device on errors. Remove unregisters the LED platform device and removes both lookup tables.

State and persistence: Runtime state is `struct sel3350_data`, containing the LED child platform device, power-supply handles, and GPIO descriptor pairs. Hardware state is sampled from GPIOs; LED state is handled by `leds-gpio`.

Dependencies and integration points: It depends on ACPI, Broxton pinctrl GPIO providers, gpiolib lookup tables, `leds-gpio`, and power-supply class. `MODULE_SOFTDEP` requests `pinctrl_broxton` and `leds-gpio` before this module.

Risks and edge cases: Static lookup tables have global dev_ids; duplicate device instances would conflict. The driver adds lookup tables before all resource acquisition, so error paths must always remove them. GPIO polarity is active-low for power signals but `sel3350_power_get_property()` operates on logical gpiod values, which is correct only if lookup polarity matches hardware.

Test signals: Validate ACPI binding, LED registration and names, power supply A/B present/online/health transitions under GPIO changes, lookup table removal on probe failure and module remove, and module soft dependency loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/sel3350-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/serdev_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/serdev_helpers.h

Purpose: This header provides helper functions for x86 platform drivers that need to find a serdev controller created for an ACPI-described UART whose serial bus resource was broken or skipped. It bridges from an ACPI serial controller HID/UID to the eventual serdev-controller `struct device`.

Important APIs, types, and functions: `get_serdev_controller()` looks up an ACPI device by HID/UID, gets its first physical node, and calls `get_serdev_controller_from_parent()`. `get_serdev_controller_from_parent()` walks three device-name levels: host child `parent:0`, UART port `parent.port`, and final `serdev_ctrl_name`. It returns a referenced `struct device *` or `ERR_PTR(-ENODEV)`.

Control flow: The helper obtains a strong reference to the physical parent with `get_device()`, drops the ACPI device reference, and then walks child devices with `device_find_child_by_name()`. Each loop drops the previous `ctrl_dev` reference after finding the next child. The returned controller carries a reference that callers must eventually put.

State and persistence: There is no persistent module state. The main behavioral state is device reference ownership during traversal.

Dependencies and integration points: It integrates with ACPI lookup, physical-node mapping, device core child lookup, and serdev controller naming conventions used after ACPI skips default serial enumeration.

Risks and edge cases: The traversal is tightly coupled to kernel device names and assumes exactly three levels. On failure after `device_find_child_by_name()` returns NULL, the current parent reference has already been put, which is intentional. Callers must understand they own the returned device reference. A null `serdev_ctrl_name` would fault because `strscpy()` is called unconditionally.

Test signals: Test HID/UID lookup failure, missing physical node, missing child at each level, successful traversal with reference accounting, and callers releasing the returned controller with `put_device()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/serdev_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/serial-multi-instantiate.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/serial-multi-instantiate.c

Purpose: This pseudo-driver instantiates multiple I2C or SPI client devices from one ACPI fwnode when firmware represents several serial-bus clients under a single ACPI device. It is used for sensor and audio amplifier packages such as Bosch sensors, TPS6598x, Cirrus amps, and TAS2781.

Important APIs, types, and functions: `struct smi_instance` records client type and IRQ resource flags/index. `struct smi_node` records bus type and instance array. `smi_get_irq()` resolves GPIO, APIC/platform, auto, and optional IRQs. `smi_i2c_probe()` creates clients with `i2c_acpi_new_device()`. `smi_spi_probe()` allocates ACPI SPI devices, fills modalias/irq/init_name, and calls `spi_add_device()`. `smi_devs_unregister()` removes instantiated clients.

Control flow: Probe looks up ACPI match data, allocates `struct smi`, and chooses I2C, SPI, or auto-detect. Auto-detect tries I2C first for compatibility and only attempts SPI when no I2C serial resources exist. Each bus probe counts ACPI resources, allocates a device-pointer array, loops over resources and instance entries, resolves IRQs, creates devices, and fails if the resource count exceeds the instance list. Remove unregisters all created children.

State and persistence: Per-platform-device state is the count and arrays of created I2C/SPI children. No hardware settings are persisted by this driver; it delegates runtime behavior to instantiated client drivers.

Dependencies and integration points: It integrates with ACPI serial resource helpers, I2C core, SPI core, platform IRQs, GPIO IRQ translation, and ACPI ID tables. The comment notes new device IDs must also be added to ACPI scan ignore lists so this pseudo-driver owns enumeration.

Risks and edge cases: A mismatch between ACPI resource count and instance array aborts and unregisters all children. Dummy instance names are used for alias or nonexistent resources and require matching no-op behavior elsewhere. IRQ auto-detect treats nonpositive IRQs carefully, with optional IRQ support only for flagged instances. SPI init names are stack buffers copied through `init_name` before `spi_add_device()`, which is acceptable only because device registration consumes the name immediately.

Test signals: Test each ACPI ID mapping, I2C and SPI creation, auto-detect precedence, GPIO/APIC/optional IRQ resolution, resource-count mismatch cleanup, remove cleanup, and coordination with `drivers/acpi/scan.c` ignore-list entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/serial-multi-instantiate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/Kconfig

Purpose: This Kconfig file defines build options for Siemens SIMATIC IPC x86 platform support. It separates the central identification/class driver from CMOS battery monitoring implementations for multiple GPIO backends.

Important APIs, types, and functions: The key config symbols are `SIEMENS_SIMATIC_IPC`, `SIEMENS_SIMATIC_IPC_BATT`, `SIEMENS_SIMATIC_IPC_BATT_APOLLOLAKE`, `SIEMENS_SIMATIC_IPC_BATT_ELKHARTLAKE`, and `SIEMENS_SIMATIC_IPC_BATT_F7188X`. Dependency expressions tie battery monitoring to `HWMON`, the class driver, and appropriate pinctrl/GPIO drivers.

Control flow: The class driver can be built independently. Battery core defaults to the class-driver choice, and per-platform battery drivers default to battery core while adding hardware-provider dependencies.

State and persistence: Kconfig state controls which modules or built-ins exist; it does not manage runtime state.

Dependencies and integration points: It integrates with the top-level platform/x86 Kconfig, hwmon, Broxton/Elkhart Lake/Alder Lake pinctrl, and Nuvoton `GPIO_F7188X`.

Risks and edge cases: Defaulting subdrivers to parent symbols can enable multiple backend modules when dependencies are present. Dependency choices must match the platform-device names selected by `simatic-ipc.c`; otherwise the central driver can instantiate a child for a module that is unavailable.

Test signals: Build test all `y/m/n` combinations, especially `SIEMENS_SIMATIC_IPC_BATT=m` with backend modules and missing pinctrl dependencies. Confirm generated modules have names promised in help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/Makefile

Purpose: This Makefile maps Siemens SIMATIC IPC Kconfig symbols to object files for the central platform driver and CMOS battery monitor variants.

Important APIs, types, and functions: It builds `simatic-ipc.o`, `simatic-ipc-batt.o`, `simatic-ipc-batt-apollolake.o`, `simatic-ipc-batt-elkhartlake.o`, and `simatic-ipc-batt-f7188x.o` according to their `CONFIG_` symbols.

Control flow: Kbuild includes each object when the corresponding symbol is `y` or `m`. There are no composite objects in this file.

State and persistence: Build configuration is the only state; runtime state belongs to the compiled drivers.

Dependencies and integration points: The file integrates with Kbuild and the Kconfig symbols in the same directory.

Risks and edge cases: Object names must stay aligned with platform aliases and `request_module()`/softdep strings used by the source files. A rename here without matching module aliases would break automatic child-driver binding.

Test signals: Run targeted builds for each config symbol and confirm module filenames match Kconfig help and `MODULE_ALIAS("platform:" KBUILD_MODNAME)` expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc-batt-apollolake.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc-batt-apollolake.c

Purpose: This backend module supplies Apollo Lake GPIO lookup data for SIMATIC IPC CMOS battery monitoring, specifically the 127E device mode, and delegates logic to the shared battery core.

Important APIs, types, and functions: `simatic_ipc_batt_gpio_table_127e` maps three GPIOs from `apollolake-pinctrl.0` and `.1` to indexed battery signals. `simatic_ipc_batt_apollolake_probe()` calls `simatic_ipc_batt_probe()`, and remove calls `simatic_ipc_batt_remove()`.

Control flow: The platform driver binds by module/platform name, registers through `module_platform_driver()`, and relies on `simatic-ipc.c` to create a platform device named with the `_batt_apollolake` suffix for matching devmode.

State and persistence: The only local state is the static lookup table. Runtime GPIO state and hwmon registration are owned by the shared battery core.

Dependencies and integration points: It depends on `simatic-ipc-batt.h`, gpiolib machine lookup tables, the Apollo Lake pinctrl provider, and the central SIMATIC platform driver. Softdeps request `simatic-ipc-batt` and `apollolake-pinctrl`.

Risks and edge cases: GPIO chip names and line numbers must match the kernel's Apollo Lake pinctrl device naming. The shared core mutates `table->dev_id` during probe, so the static table is effectively single-instance.

Test signals: Probe on 127E hardware, verify all three GPIOs resolve, hwmon battery voltage states change correctly, and lookup table is removed on module unload or probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc-batt-apollolake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc-batt-elkhartlake.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc-batt-elkhartlake.c

Purpose: This backend module supplies Elkhart Lake GPIO lookup data for SIMATIC IPC CMOS battery monitoring on BX-21A device mode systems and delegates monitoring to the shared core.

Important APIs, types, and functions: `simatic_ipc_batt_gpio_table_bx_21a` maps two status GPIOs and one meter GPIO from `INTC1020` pinctrl devices. Probe and remove are thin wrappers around `simatic_ipc_batt_probe()` and `simatic_ipc_batt_remove()`.

Control flow: The module platform driver binds to a platform device created by `simatic-ipc.c` with the `_batt_elkhartlake` suffix. Probe installs the lookup table through the core; remove removes it.

State and persistence: Local persistent state is the static lookup table. The core owns the cached battery state and GPIO descriptors.

Dependencies and integration points: It depends on Elkhart Lake pinctrl, gpiolib lookup tables, and the shared SIMATIC battery core. Softdeps request `simatic-ipc-batt` and `elkhartlake-pinctrl`.

Risks and edge cases: The table's GPIO initial output polarity interacts with shared core logic that initializes the meter line low for BX-21A. Wrong GPIO chip names or indexes will fail probe or report false battery status.

Test signals: Validate BX-21A platform-device creation, GPIO resolution, meter GPIO polarity, hwmon values for full/critical/empty, and cleanup on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc-batt-elkhartlake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc-batt-f7188x.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc-batt-f7188x.c

Purpose: This backend module selects Nuvoton F7188x and companion pinctrl GPIO lookup tables for SIMATIC IPC CMOS battery monitoring on 227G, BX-39A, and BX-59A device modes.

Important APIs, types, and functions: Three lookup tables describe 227G, BX-39A, and BX-59A GPIO wiring. `batt_lookup_table` stores the selected table globally. `simatic_ipc_batt_f7188x_probe()` reads `struct simatic_ipc_platform` platform data, switches on `devmode`, and delegates to `simatic_ipc_batt_probe()`.

Control flow: Probe selects a table according to `SIMATIC_IPC_DEVICE_227G`, `SIMATIC_IPC_DEVICE_BX_39A`, or `SIMATIC_IPC_DEVICE_BX_59A`, rejects all other modes, and calls the shared core. Remove passes the selected global table back to the core.

State and persistence: `batt_lookup_table` is global and supports one active instance. The selected static lookup table is mutated by the shared core with `dev_id`. Battery state caching is in the core.

Dependencies and integration points: It depends on `GPIO_F7188X`, Alder Lake/Elkhart Lake pinctrl where applicable, the central SIMATIC platform data, and the shared battery core. Softdeps request `gpio_f7188x` and pinctrl providers.

Risks and edge cases: The global selected table is not per-device, so multiple instances would conflict. The three table variants combine F7188x and Intel pinctrl GPIOs; missing either provider causes probe failures. Device-mode mapping in `simatic-ipc.c` must remain synchronized.

Test signals: Test each supported `devmode`, reject unsupported modes, verify GPIO lookup names and indexes, confirm meter-line polarity for BX-59A, and unload/reload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc-batt-f7188x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc-batt.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc-batt.c

Purpose: This shared Siemens SIMATIC IPC CMOS battery monitor exposes battery condition through hwmon. It supports GPIO-based status lines for most models and an I/O-port status register for IPC227E.

Important APIs, types, and functions: The exported `simatic_ipc_batt_probe()` and `simatic_ipc_batt_remove()` are used by backend GPIO modules. Static `priv` stores devmode, cached current state, up to three GPIO descriptors, and cache timestamp. `simatic_ipc_batt_read_gpio()` samples empty/low/meter GPIOs. `simatic_ipc_batt_read_io()` reads I/O port `0x404d`. `simatic_ipc_batt_ops` implements `in_input` and `in_lcrit`.

Control flow: Probe reads platform data `devmode`, optionally assigns and adds a supplied lookup table, gets required empty/low GPIOs and optional meter GPIO, or skips GPIO for IPC227E. It registers a hwmon device and immediately samples once to warn about aging batteries. Reads are cached for 24 hours to avoid frequent battery measurement.

State and persistence: Battery level is reported as millivolt-like constants: full 3000, critical 2750, empty 0. `priv.current_state` and `last_updated_jiffies` cache the result globally. Hardware state is sampled from GPIOs or a single I/O port. The optional meter GPIO is pulsed during reads.

Dependencies and integration points: It integrates with platform data from `simatic-ipc.c`, gpiolib lookup tables/consumers, hwmon, jiffies, I/O port resource arbitration, and backend modules through exported symbols.

Risks and edge cases: `priv` is a global singleton, so multiple devices would overwrite each other. `simatic_ipc_batt_remove()` unconditionally calls `gpiod_remove_lookup_table(table)` even with NULL in the IO wrapper, which deserves API-behavior review. Cached state can remain stale for up to 24 hours. GPIO reads sleep and meter GPIO timing is fixed at 150 ms. Error path removes lookup tables even when some GPIO descriptors are devm-managed.

Test signals: Test GPIO and IPC227E I/O modes, cache refresh after 24 hours, immediate warning on low/empty battery, hwmon `in0_input`/`in0_lcrit`, missing GPIO failures and cleanup, request-muxed-region failures, and backend module probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc-batt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc-batt.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc-batt.h

Purpose: This header declares the shared probe/remove entry points used by SIMATIC IPC CMOS battery backend modules.

Important APIs, types, and functions: `simatic_ipc_batt_probe(struct platform_device *pdev, struct gpiod_lookup_table *table)` registers the shared hwmon battery monitor with backend-specific GPIO lookup data. `simatic_ipc_batt_remove(struct platform_device *pdev, struct gpiod_lookup_table *table)` removes the lookup table.

Control flow: Backend modules include this header and pass their static lookup table to the shared core during platform-driver probe/remove.

State and persistence: The header has no state. It exposes the shared core's singleton behavior to backend modules.

Dependencies and integration points: It depends on declarations for `struct platform_device` and `struct gpiod_lookup_table` being available through including translation units. It is tightly coupled to `simatic-ipc-batt.c`.

Risks and edge cases: The header does not include the type-defining headers itself, relying on include order in users. API users must pass the same table on remove that they passed on probe.

Test signals: Compile each backend independently and with different include-order changes; validate exported symbol availability when built as modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc-batt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc.c

Purpose: This is the central Siemens SIMATIC IPC platform identification driver. It reads Siemens DMI station IDs and creates model-specific child platform devices for LEDs, watchdogs, and CMOS battery monitoring, plus requests companion sensor/watchdog modules.

Important APIs, types, and functions: `device_modes[]` maps station IDs to LED, watchdog, battery devmodes, and up to two extra module names. `register_platform_devices()` creates child devices with `struct simatic_ipc_platform` platform data and names selected by devmode. `request_additional_modules()` requests extra modules. `simatic_ipc_init_module()` gates on Siemens DMI and uses `simatic_ipc_find_dmi_entry_helper()`.

Control flow: Init checks the DMI vendor whitelist, walks DMI for the OEM station ID, requests model-specific extra modules, and registers battery, LED, then watchdog platform devices if their modes are not `NONE`. Exit unregisters all three child pointers. Unsupported station IDs warn and return an error after attempting no child devices.

State and persistence: Static global platform-device pointers track created child devices. `platform_data` is a static structure reused and modified before each `platform_device_register_data()` call; registration copies it into each device.

Dependencies and integration points: It depends on Siemens platform data headers, DMI station-id parsing helpers, platform-device autoloading by module aliases, and downstream LED/watchdog/battery drivers. It also interacts with module autoloading through `request_module()`.

Risks and edge cases: Error handling does not unwind previously registered child devices if a later child registration fails, potentially leaking a battery or LED child on partial failure. The static `platform_data` reuse is safe only because platform core copies data. Device-mode-to-platform-name mapping must remain synchronized with backend module names and aliases. Init returns 0 when Siemens vendor matches but station ID is missing, so absence can be quiet except for a warning.

Test signals: Test all station IDs in `device_modes`, platform-device names and platform data contents, requested extra modules, unsupported station ID behavior, partial registration failure cleanup, and module exit after partial or full initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/silicom-platform.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/silicom-platform.c

Purpose: This Silicom MEC170x platform driver supports Cordoba network appliances. It exposes multicolor front-panel LEDs, named GPIOs, fan speed, temperature, and sysfs controls/status for MEC efuse, firmware version, and power-cycle command through fixed I/O ports.

Important APIs, types, and functions: `struct silicom_platform_info` holds DMI-selected platform wiring. `silicom_mec_port_get()` and `silicom_mec_port_set()` perform indirect MEC I/O under `mec_io_mutex`. Multicolor LED callbacks map subled channels to active-low MEC bits. GPIO callbacks expose named channels and enforce direction based on register offset. `silicom_mc_leds_register()` deep-copies `__initdata` LED descriptors into devm allocations. `silicom_fan_control_hwmon_ops` exposes fan/temp labels and values.

Control flow: DMI callbacks select the platform info and assign global initdata pointers. `silicom_platform_init()` requires a DMI match, then creates a bundled platform device/driver. Probe reserves MEC I/O ports, checks magic value `0x5a`, registers DMI-selected multicolor LEDs, registers the GPIO chip with channel map, and registers hwmon. Sysfs reads and writes perform indirect EC register selection and data access.

State and persistence: Hardware state lives in MEC I/O registers for GPIO/LED outputs, fan/temp readings, efuse status, uC version, and power-cycle command. Software globals cache `efuse_status`, `mec_uc_version`, `power_cycle`, and selected platform wiring pointers. All MEC access is serialized by `mec_io_mutex`.

Dependencies and integration points: It integrates with DMI, platform bundle creation, I/O port resource management, multicolor LED class, gpiolib, hwmon, sysfs attribute groups, bitfield helpers, and mutex-protected port I/O.

Risks and edge cases: Selected wiring pointers are marked `__initdata`; they are used during init/probe only and copied before init memory is freed, so ordering matters. GPIO direction is inferred from encoded channel offset and can reject legitimate direction changes if mappings are wrong. Active-low LED/GPIO output semantics differ between LED and GPIO paths and need careful validation. The `power_cycle` sysfs write triggers hardware reset behavior for any positive input.

Test signals: Test DMI variants `80300-0214-G`, `80500-0214-G`, and `80300-0222-G`; bad magic rejection; LED colors and active-low behavior; named GPIO input/output direction enforcement; fan RPM and temperature scaling; sysfs efuse/version/power-cycle; concurrent sysfs/GPIO/LED/hwmon access under the mutex; and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/silicom-platform.c -->
