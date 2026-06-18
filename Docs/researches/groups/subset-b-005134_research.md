# Research: subset-b-005134

Grouped research for Dell/Compal/Dasharo x86 platform drivers. Each section preserves the source path and is intended to be split into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/compal-laptop.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/compal-laptop.c

Purpose: Provides vendor platform support for Compal-built laptops and several Dell Mini/Inspiron models using direct ACPI EC byte access. It exposes backlight control, rfkill devices, and, on selected DMI systems with `extra_features`, wakeup toggles, hwmon fan/temperature readings, and a battery `power_supply`.

Important APIs/types/functions: `struct compal_data` stores fan PWM state and cached battery strings. EC helpers (`ec_read_u8`, `ec_read_u16`, `ec_read_sequence`, `set_backlight_level`, `set_pwm`, `get_fan_rpm`) are the low-level dependency. User-facing integrations are `backlight_ops`, `rfkill_ops`, hwmon sysfs attributes, `power_supply_desc`, and the platform driver `compal_driver`. Init uses `module_param(force)` and DMI callbacks to decide whether to bind.

Control flow/state/persistence: `compal_init()` rejects non-ACPI or unrecognized systems unless forced, registers a vendor backlight only when ACPI video selects vendor control, registers the platform driver/device, then creates Wi-Fi and Bluetooth rfkill devices. `compal_probe()` is a no-op unless `extra_features` is true; then it creates platform wakeup attributes, hwmon groups, initializes battery identity strings from EC, and registers the battery supply. Runtime state is mostly in EC registers; driver state only caches current requested PWM and battery strings. Removal resets fan control to motherboard mode and tears down sysfs, power supply, backlight, and rfkill.

Dependencies/integration: Depends on ACPI EC transactions, DMI matching, backlight, rfkill, hwmon, and power_supply. It does not use Dell SMBIOS; it is a direct EC driver for Compal hardware.

Risks/test signals: EC addresses and PWM lookup table are model-specific and unsafe outside known systems; `force=1` should be tested carefully. Good tests are module load/unload on DMI-matched systems, `/sys/class/backlight/compal-laptop` brightness changes, rfkill hard/soft state polling, hwmon readings under `extra_features`, battery property reads, charge limit writes, and ensuring removal restores motherboard fan control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/compal-laptop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dasharo-acpi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/dasharo-acpi.c

Purpose: Implements a Dasharo ACPI hwmon driver for ACPI device `DSHR0001`, exposing firmware-described temperature, fan tachometer, and fan PWM channels through the standard hwmon interface.

Important APIs/types/functions: `enum dasharo_feature`, temperature/fan group enums, `struct dasharo_capability`, and `struct dasharo_data` define the capability map. ACPI methods `GFCP`, `GTMP`, `GFTH`, and `GFDC` are wrapped by `dasharo_get_feature_cap_count()` and `dasharo_read_channel()`. The hwmon callbacks are `dasharo_hwmon_read`, `dasharo_hwmon_read_string`, and `dasharo_hwmon_is_visible`.

Control flow/state/persistence: `dasharo_probe()` allocates `dasharo_data`, enumerates each feature/group with `dasharo_fill_feature_caps()`, and registers a fixed 24-channel-per-type hwmon template whose visibility is constrained by discovered capability counts. State is only the probed capability table; all sensor values are read live from ACPI on demand. There is no persistent storage or write path.

Dependencies/integration: Integrates with ACPI platform matching and `devm_hwmon_device_register_with_info()`. Unit conversion is limited to temperatures, converted from degrees to millidegrees.

Risks/test signals: `dasharo_fill_feature_caps()` assumes every group with a positive count has a non-NULL name; firmware returning unknown groups could produce malformed labels. It also truncates capability counts to 24. Test by loading on `DSHR0001`, checking hwmon visibility matches `GFCP`, validating temp/fan/pwm reads against firmware tools, and forcing ACPI failures to verify `-ENODEV`/`-EINVAL` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dasharo-acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/Kconfig

Purpose: Defines the Dell x86 platform driver menu and build-time feature matrix for Alienware WMI, Dell SMBIOS, laptop extras, airplane-mode switch, thermal profile, freefall, WMI hotkeys/sensors, and related Dell support modules.

Important APIs/types/functions: This is Kconfig metadata rather than C code. Important symbols include `X86_PLATFORM_DRIVERS_DELL`, `ALIENWARE_WMI` plus `ALIENWARE_WMI_LEGACY`/`WMAX`, `DCDBAS`, `DELL_LAPTOP`, `DELL_RBTN`, `DELL_PC`, `DELL_SMBIOS`, `DELL_SMBIOS_WMI`, `DELL_SMBIOS_SMM`, and `DELL_SMO8800`.

Control flow/state/persistence: Build selection gates which source files are compiled. Notable dependency constraints prevent built-in `DELL_SMBIOS` from depending on modular `DCDBAS` or `ACPI_WMI`, and select common services such as `ACPI_PLATFORM_PROFILE`, `POWER_SUPPLY`, `LEDS_CLASS`, `INPUT_SPARSEKMAP`, or `DELL_WMI_DESCRIPTOR` where required.

Dependencies/integration: Encodes relationships among Dell drivers: `DELL_LAPTOP` requires `DELL_SMBIOS`, SMBIOS optional backends depend on WMI or DCDBAS, and Alienware subdrivers are built into the composite `alienware-wmi` object.

Risks/test signals: Regression risk is mostly configuration reachability. Test with all relevant combinations as built-in/module/off, especially `DELL_SMBIOS=y` with backend dependencies, `ALIENWARE_WMI` suboptions, and `DELL_LAPTOP` with optional `DELL_WMI`/`RFKILL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/Makefile

Purpose: Maps Dell Kconfig symbols to kernel objects and composes multi-file drivers such as `alienware-wmi`, `dell-smbios`, and `dell-wmi`.

Important APIs/types/functions: Build variables include `obj-$(CONFIG_ALIENWARE_WMI) += alienware-wmi.o`, `alienware-wmi-y := alienware-wmi-base.o`, conditional additions for legacy/WMAX, and analogous `dell-smbios-y` plus WMI/SMM backend objects.

Control flow/state/persistence: The file has no runtime state. It determines link composition and therefore which init/exit entry points are present.

Dependencies/integration: Ties `DELL_SMO8800` to both `dell-smo8800.o` and the companion `dell-lis3lv02d.o`, includes `dell-wmi-sysman/` as a subdirectory object, and ensures backend helpers are linked into the parent module according to config.

Risks/test signals: Main risk is missing object inclusion when Kconfig changes. Test with `make M=drivers/platform/x86/dell` or full kernel builds across key configs, checking generated modules contain expected symbols and no unresolved references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/alienware-wmi-base.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/alienware-wmi-base.c

Purpose: Common Alienware WMI module core. It selects DMI quirks, chooses legacy or WMAX WMI backend, creates the shared `alienware-wmi` platform device, and exposes AlienFX LED brightness and RGB zone sysfs controls.

Important APIs/types/functions: Global `alienfx` points at quirk data and `alienware_interface` selects `LEGACY` or `WMAX`. `alienware_wmi_command()` wraps `wmidev_evaluate_method()` and validates integer replies. `parse_rgb`, `zone_*` sysfs handlers, `global_led_set/get`, `alienfx_probe`, and `alienware_alienfx_setup()` implement the platform LED/sysfs layer.

Control flow/state/persistence: `alienware_wmi_init()` resolves DMI quirks, registers the platform driver, then initializes the WMAX backend if `WMAX_CONTROL_GUID` exists, otherwise legacy. Backend probes call `alienware_alienfx_setup()` with WMI-specific operations; this registers a platform device whose probe allocates `alienfx_priv`. Runtime state is in `alienfx_priv`: per-zone RGB values, global brightness, and current lighting control state. Values are not persisted by the driver beyond memory; firmware receives WMI updates.

Dependencies/integration: Depends on DMI, ACPI WMI, platform devices, LED class, and attribute groups exported by WMAX when enabled. Used by both `alienware-wmi-legacy.c` and `alienware-wmi-wmax.c`.

Risks/test signals: `parse_rgb()` repacks a 24-bit hex value through a union and masks nibbles, so color interpretation needs hardware verification. Zone visibility depends on `alienfx->num_zones + 1` to include control state. Test DMI fallback, backend selection, LED class brightness, each `rgb_zones/zoneNN`, and cleanup when backend init fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/alienware-wmi-base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/alienware-wmi-legacy.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/alienware-wmi-legacy.c

Purpose: Legacy Alienware WMI backend for systems using `LEGACY_CONTROL_GUID`, primarily old AlienFX zone control without the newer WMAX/AWCC interface.

Important APIs/types/functions: `struct legacy_led_args` packages color, brightness, and state. `legacy_wmi_update_led()` sends either legacy power-control WMI calls or common `alienware_wmi_command()` calls. `legacy_wmi_probe()` passes legacy operations into `alienware_alienfx_setup()`.

Control flow/state/persistence: WMI driver probe creates the common platform AlienFX device. Zone writes from the base module call `legacy_wmi_update_led()` for `location + 1`; brightness writes refresh location 0. Driver state lives in the shared `alienfx_priv`; firmware is updated through WMI and no state is persisted locally across module reload.

Dependencies/integration: Depends on the base module's shared header, `LEGACY_CONTROL_GUID`, `LEGACY_POWER_CONTROL_GUID`, WMI core, and AlienFX platform setup.

Risks/test signals: The branch checking `legacy_args.state != LEGACY_RUNNING` starts from a zero-initialized state and therefore uses the power-control path before setting `state` from `priv`, which is subtle and hardware-sensitive. Test booting/running/suspend lighting states, per-zone color writes, global brightness, probe with multiple WMI devices because `no_singleton=true`, and unregister on module exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/alienware-wmi-legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/alienware-wmi-wmax.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/alienware-wmi-wmax.c

Purpose: WMAX/AWCC backend for newer Alienware and Dell G-series machines. It supports AlienFX WMAX LEDs, optional HDMI mux/amplifier/deep-sleep sysfs groups, AWCC hwmon sensors and fan boost controls, platform thermal profiles including G-Mode quirks, and debugfs diagnostics.

Important APIs/types/functions: WMAX method IDs cover LED, brightness, HDMI, amplifier, and deep sleep. AWCC method wrappers (`awcc_wmi_command`, `awcc_thermal_information`, `awcc_get_fan_sensors`, `awcc_op_*`) abstract firmware operations. `struct awcc_priv` stores system description, resource counts, fan/temp/profile mappings, hwmon device, and platform-profile device. `awcc_hwmon_*`, `awcc_platform_profile_*`, `awcc_debugfs_*`, `alienware_awcc_setup()`, `wmax_wmi_update_led()`, and `wmax_wmi_probe()` are the main flows.

Control flow/state/persistence: `alienware_wmax_wmi_init()` chooses `awcc` quirks from DMI or unsafe force parameters, then registers a WMI driver. Probe either initializes AWCC services when quirks are present, or falls back to common AlienFX platform setup. AWCC setup reads a packed system description, sanity-checks resource counts, initializes hwmon and platform profiles as enabled, and creates debugfs. Runtime state includes discovered fan data, temp bitmaps, supported profile IDs, and suspend-cached fan boost values. Firmware stores active thermal/profile/fan states; the driver only caches mappings and temporary suspend restore values.

Dependencies/integration: Integrates with the Alienware base module, ACPI WMI, DMI quirks, hwmon, platform_profile, PM callbacks, and debugfs. WMAX sysfs groups are exported to the base platform device through `alienware-wmi.h`.

Risks/test signals: AWCC firmware reports are model-specific and may overstate profile/resource counts; the code caps counts at 16 and tolerates early `-EBADRQC` for profiles. Force parameters bypass backend checks. Suspend clears fan boost and resumes cached nonzero boost. Test DMI quirk machines, forced hwmon/profile modes, sensor label/read visibility, fan boost read/write clamp, profile mapping including G-Mode toggling, debugfs GPIO writes, and PM restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/alienware-wmi-wmax.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/alienware-wmi.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/alienware-wmi.h

Purpose: Shared declarations for the composite Alienware WMI driver.

Important APIs/types/functions: Defines legacy/WMAX GUIDs, interface and control-state enums, `struct alienfx_quirks`, packed `struct color_platform`, `struct alienfx_priv`, `struct alienfx_ops`, and `struct alienfx_platdata`. It exports globals `alienware_interface` and `alienfx`, plus `alienware_wmi_command()` and `alienware_alienfx_setup()`.

Control flow/state/persistence: Header-only; it controls compile-time linkage. Inline stubs return `-ENODEV` when legacy or WMAX subdrivers are disabled. `WMAX_DEV_GROUPS` conditionally adds WMAX sysfs groups to the base platform driver.

Dependencies/integration: Bridges `alienware-wmi-base.c`, legacy backend, and WMAX backend. Includes LED, platform device, and WMI types.

Risks/test signals: ABI is internal to the module object but layout matters for packed WMI argument structures. Test by building all combinations of `ALIENWARE_WMI_LEGACY` and `ALIENWARE_WMI_WMAX` and checking base code handles disabled stubs cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/alienware-wmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dcdbas.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dcdbas.c

Purpose: Dell Systems Management Base driver. It exposes sysfs interfaces for SMI command buffers and host-control shutdown actions, and exports helper functions used by Dell SMBIOS SMM backend.

Important APIs/types/functions: Exports `dcdbas_smi_alloc()`, `dcdbas_smi_free()`, and `dcdbas_smi_request()`. Sysfs/bin attributes expose `smi_data`, `smi_data_buf_size`, `smi_data_buf_phys_addr`, `smi_request`, and host control knobs. WSMT support is handled by `dcdbas_check_wsmt()`, `check_eps_table()`, and protected buffer remapping. Host control uses `host_control_smi()` and a reboot notifier.

Control flow/state/persistence: `subsys_initcall_sync(dcdbas_init)` registers a platform driver/device early. Probe initializes host-control state, locates WSMT protected buffers when present, sets a 32-bit DMA coherent mask, creates sysfs, and registers reboot notification. `smi_data_lock` serializes buffer growth, sysfs reads/writes, and SMI requests. SMI requests run on CPU 0 via `smp_call_on_cpu()`. State persists only in module globals and firmware-provided buffers; host-control actions are consumed on shutdown.

Dependencies/integration: Depends on platform device core, DMA coherent memory, DMI/ACPI WSMT, RTC CMOS I/O, reboot notifier, and exports used by `dell-smbios-smm.c`.

Risks/test signals: This is privileged, firmware-facing code. Risks include incorrect DMA physical address handling, WSMT buffer mapping, SMI CPU affinity, and host-control port/CMOS sequences. Test sysfs buffer resize/read/write, raw and calling-interface SMI requests with valid magic, WSMT and non-WSMT systems, reboot notifier actions, and module unload after open sysfs references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dcdbas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dcdbas.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dcdbas.h

Purpose: Internal interface and firmware structure definitions for the Dell Systems Management Base driver and SMM callers.

Important APIs/types/functions: Defines SMI buffer limits, host-control action/type constants, port constants, SMI magic, SMM EPS signature, sysfs attribute macros, packed `struct smi_cmd`, `struct apm_cmd`, `struct smm_eps_table`, and `struct smi_buffer`. Declares `dcdbas_smi_request()`, `dcdbas_smi_alloc()`, and `dcdbas_smi_free()`.

Control flow/state/persistence: Header-only. The packed structures mirror firmware ABI and are written into DMA or firmware-provided buffers.

Dependencies/integration: Included by `dcdbas.c` and `dell-smbios-smm.c`; depends on Linux device/sysfs/types declarations.

Risks/test signals: Layout and packing are critical. Build-time checks are implicit; runtime test signal is successful SMM calls through `dell-smbios-smm` and valid host-control behavior. Any field changes require ABI review against Dell firmware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dcdbas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-laptop.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-laptop.c

Purpose: Dell laptop extras driver. It layers user-facing laptop controls over Dell SMBIOS: rfkill, vendor backlight, touchpad LED quirks, keyboard backlight LED/sysfs extensions, audio mute LEDs, and ACPI battery charge mode/threshold extensions.

Important APIs/types/functions: Uses `dell_send_request_for_tokenid()` and Dell SMBIOS tokens/classes. Major subsystems are rfkill (`dell_setup_rfkill`, `dell_update_rfkill`, i8042 filter, dell-rbtn notifier), display backlight (`dell_ops`), touchpad LED, keyboard backlight (`kbd_info`, `kbd_state`, `kbd_get_info`, `kbd_get_state`, `kbd_set_state_safe`, `kbd_led_*` sysfs/LED class), mute LEDs, and battery hooks (`dell_battery_*`, `acpi_battery_hook`).

Control flow/state/persistence: `late_initcall(dell_init)` ensures `dell-rbtn` is initialized first for built-in kernels. Init checks Dell laptop DMI, registers a platform device, sets up rfkill, quirk LEDs, keyboard LED, battery hook, debugfs, notifier, mute LEDs, and optional vendor backlight. Runtime state includes rfkill pointers, keyboard capability/state caches, previous keyboard level/mode, battery-supported mode bitmap, and registration flags. Actual settings persist in firmware/SMBIOS tokens; the driver caches only current LED class value and helper state.

Dependencies/integration: Depends heavily on `dell-smbios`, optional `dell-rbtn` exported notifiers, i8042 fallback, ACPI battery hook, power_supply, backlight, LED class, debugfs, and Dell WMI privacy helper to avoid duplicate mic-mute LED registration.

Risks/test signals: SMBIOS calls are model-specific and many quirks correct BIOS behavior. Rfkill is whitelist-limited to avoid regressions. Keyboard backlight has three control mechanisms and rollback-on-failure. Test on Latitude/Precision and quirked Inspiron/XPS models: rfkill events from `dell-rbtn` and i8042 fallback, backlight token reads/writes, keyboard brightness/timeout/triggers/ALS sysfs, battery charge types and custom thresholds with 5 percent spacing, mute LEDs, and complete unwind on partial init failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-laptop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-lis3lv02d.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-lis3lv02d.c

Purpose: Instantiates an I2C `lis3lv02d` accelerometer client for Dell ACPI SMO88xx freefall devices that expose a platform device without usable I2C resources.

Important APIs/types/functions: DMI table maps product names to I2C addresses. `detect_lis3lv02d()` probes WHO_AM_I values when `probe_i2c_addr=1` is used. `instantiate_i2c_client()` finds the main Intel I801 adapter and registers either a fixed-address or scanned I2C client. Bus notifier `i2c_bus_notify()` handles late adapter/client add/remove.

Control flow/state/persistence: Module init first confirms an SMO88xx platform device exists, then checks DMI or optional dangerous probing. It registers an I2C bus notifier and queues initial work. Global state tracks `i2c_addr`, created `i2c_dev`, and notifier registration. Exit unregisters notifier, cancels work, and unregisters the client.

Dependencies/integration: Integrates ACPI SMO IDs, DMI, I2C core, I801 adapter naming, workqueues, and the generic `lis3lv02d` driver.

Risks/test signals: Blind SMBus probing can be dangerous, hence opt-in. Adapter-name matching must avoid secondary IDF adapters. Test known DMI systems, unknown systems with no probing, opt-in scan at 0x29/0x1d, late I2C adapter registration, and cleanup when the client is removed externally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-lis3lv02d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-pc.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-pc.c

Purpose: Dell PC thermal-profile driver. It exposes Dell SMBIOS User Selectable Thermal Table modes through the generic `platform_profile` API for Dell systems, regardless of form factor.

Important APIs/types/functions: Thermal helpers `thermal_get_mode`, `thermal_get_supported_modes`, `thermal_get_acc_mode`, and `thermal_set_mode` use `CLASS_INFO`/`SELECT_THERMAL_MANAGEMENT`. Platform-profile callbacks map Dell bits to `BALANCED`, `PERFORMANCE`, `QUIET`, and `COOL`. A faux device (`dell_pc_fdev`) hosts devm platform-profile registration.

Control flow/state/persistence: `dell_init()` DMI-checks Dell vendors and creates the faux device. Probe verifies SMBIOS class support, reads supported modes, and registers platform profile ops. The probe also re-applies the current thermal mode to synchronize ACPI/firmware state. Runtime state is the supported mode bitmask; selected profile is kept in firmware.

Dependencies/integration: Depends on DMI, `dell-smbios`, `device/faux`, and `ACPI_PLATFORM_PROFILE`.

Risks/test signals: Thermal mode bit decoding must preserve AAC mode bits while setting the thermal mode. Test unsupported SMBIOS class, supported mode bitmap exposure, get/set for each profile, preserving ACC/AAC configuration, and coexistence with `dell-laptop`/Alienware profile providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-pc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-rbtn.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-rbtn.c

Purpose: Dell airplane-mode switch driver for ACPI devices `DELRBTN` and `DELLABCE`. It models hardware sliders as rfkill devices and toggle buttons as input hotkeys, and exports notifier hooks for other Dell drivers.

Important APIs/types/functions: ACPI methods `CRBT`, `GRBT`, and `ARBT` identify type, read state, and acquire/release events. `struct rbtn_data` tracks type, rfkill/input devices, and suspend filtering. Exported `dell_rbtn_notifier_register/unregister()` allows `dell-laptop` to receive slider events and optionally suppress duplicate rfkill devices.

Control flow/state/persistence: Probe acquires the ACPI device, initializes input or rfkill based on type, and installs an ACPI notify handler. Notify event `0x80` emits `KEY_RFKILL` for toggles or refreshes rfkill plus calls the notifier chain for sliders. Suspend marks notifications as ignored until an async resume work clears the flag. Module parameter `auto_remove_rfkill` controls whether notifier consumers temporarily remove this driver's rfkill devices.

Dependencies/integration: Depends on ACPI, platform driver core, rfkill, input, PM sleep, and is consumed by `dell-laptop.c`.

Risks/test signals: Resume notifications are intentionally suppressed to avoid false hotkeys. Notifier registration iterates existing devices and can remove/re-add rfkill devices. Test toggle and slider hardware, ACPI notification delivery, hard rfkill state, notifier auto-remove behavior with `dell-laptop`, suspend/resume, and ignored `DELLABC6` expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-rbtn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-rbtn.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-rbtn.h

Purpose: Small public header for Dell airplane-mode switch notifier integration.

Important APIs/types/functions: Forward-declares `struct notifier_block` and declares `dell_rbtn_notifier_register()` and `dell_rbtn_notifier_unregister()`.

Control flow/state/persistence: Header-only; no runtime state. Consumers use these functions to subscribe to slider events from `dell-rbtn.c`.

Dependencies/integration: Included by `dell-laptop.c` and implemented by `dell-rbtn.c`.

Risks/test signals: Since `dell-laptop.c` obtains these symbols dynamically, built-in init ordering is important and is handled by `late_initcall` in `dell-laptop`. Build and runtime tests should cover modular and built-in combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-rbtn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smbios-base.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smbios-base.c

Purpose: Common Dell SMBIOS calling interface. It discovers Dell DMI calling-interface tokens, registers available backend devices, arbitrates calls by priority, filters unsafe userspace calls, exposes token sysfs files, and provides helper APIs used by Dell platform drivers.

Important APIs/types/functions: Exports `dell_smbios_register_device`, `dell_smbios_unregister_device`, `dell_smbios_call_filter`, `dell_smbios_call`, `dell_fill_request`, `dell_send_request`, `dell_smbios_find_token`, laptop notifier helpers, and `dell_smbios_class_is_supported`. Internal state includes supported command bitmap, token array, backend list, token sysfs data, and mutex `smbios_mutex`.

Control flow/state/persistence: Init rejects non-Dell/Alienware DMI, walks DMI tables for type `0xda` calling-interface data, registers a `dell-smbios` platform device, initializes WMI and SMM backends, and builds a `tokens/` sysfs group if tokens exist. Calls choose the highest-priority registered backend. Filtering blacklists dangerous classes/tokens, whitelists selected calls for `CAP_SYS_ADMIN`, and requires `CAP_SYS_RAWIO` for non-whitelisted calls. State is built from DMI and lives in memory; firmware owns token values.

Dependencies/integration: Used by `dell-laptop`, `dell-pc`, WMI char-device backend, and SMM backend. Depends on DMI, platform devices, capabilities, sysfs, and backend init functions.

Risks/test signals: Security filtering is central; mistakes could expose manufacturing/diagnostic/write-once tokens. Duplicate token zeroing prevents sysfs name collisions. Test backend priority selection, no-backend failures, token sysfs permissions, blacklist/whitelist behavior under capabilities, notifier delivery, and init unwind when one backend fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smbios-base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smbios-smm.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smbios-smm.c

Purpose: SMM/SMI backend for the Dell SMBIOS calling interface, using DCDBAS to allocate a low 32-bit DMA buffer and raise firmware SMIs.

Important APIs/types/functions: `dell_smbios_smm_call()` copies a `calling_interface_buffer` into the SMI buffer, builds `struct smi_cmd`, calls `dcdbas_smi_request()`, and copies results back. `test_wsmt_enabled()` detects firmware that blocks SMM calls when WSMT is enabled. Init/exit functions register/unregister this backend with priority 0.

Control flow/state/persistence: Init allocates one page through DCDBAS, parses DMI type `0xda` for command address/code, tests WSMT behavior, creates a backend platform device, and registers with the base SMBIOS core. Calls are serialized by `smm_mutex`. State is the command port/code, SMI buffer, and platform device; all request state is transient.

Dependencies/integration: Depends on `dcdbas` exported functions and the Dell SMBIOS base. It is lower priority than the WMI backend.

Risks/test signals: SMM cannot work on some WSMT-protected systems and must disable itself. Test DMI command parsing, WSMT token behavior, successful token reads over SMM, serialization under concurrent callers, and cleanup freeing the SMI buffer on init failure and module exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smbios-smm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smbios-wmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smbios-wmi.c

Purpose: ACPI-WMI backend for Dell SMBIOS calls. It registers as the preferred SMBIOS backend and exposes a userspace misc character device at `wmi/dell-smbios` for filtered WMI SMBIOS calls.

Important APIs/types/functions: `struct wmi_smbios_priv` holds the WMI buffer, WMI device, requested buffer size, char device, and list node. `run_smbios_call()` invokes WMI method 1 under GUID `A80593CE-A997-11DA-B012-B622A1EF5492`. `dell_smbios_wmi_call()` implements kernel backend calls; `dell_smbios_wmi_do_ioctl()` implements userspace ioctl with `dell_smbios_call_filter()`.

Control flow/state/persistence: Init walks DMI type `0xb1` to require the ACPI WMI flag, then registers a WMI driver. Probe validates Dell WMI descriptor availability, reads required buffer size and hotfix flag, allocates pages, registers the misc char device, registers this backend with priority 1, and adds it to a global list. Calls use the first list entry and are serialized by `call_mutex`; list updates are protected by `list_mutex`.

Dependencies/integration: Depends on ACPI WMI, Dell WMI descriptor helpers, uapi WMI buffer definitions, miscdevice, and Dell SMBIOS base. Higher priority than SMM backend.

Risks/test signals: Buffer sizing and userspace filtering are key. Test descriptor deferral, 4K/32K buffer sizes, hotfix warning, ioctl length checks, copy failures, invalid/blacklisted calls, concurrent WMI calls, backend unregister while userspace char device exists, and multiple WMI devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smbios-wmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smbios.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smbios.h

Purpose: Shared interface for Dell SMBIOS clients and backend modules.

Important APIs/types/functions: Defines Dell SMBIOS classes/selects, kernel-reserved token IDs for brightness, keyboard backlight, battery modes, mic/mute LEDs, and thermal management. Defines packed DMI structures `calling_interface_token` and `calling_interface_structure`. Declares SMBIOS call helpers, token lookup, laptop notifier API, class support probe, and backend init/exit functions with stubs.

Control flow/state/persistence: Header-only; all state is provided by `dell-smbios-base.c` and backends. Conditional stubs make backend selection compile under different Kconfig combinations.

Dependencies/integration: Included by Dell laptop, PC, SMBIOS WMI/SMM backend files, and uses uapi WMI calling interface buffer types.

Risks/test signals: Token constants are shared contract; changing them can break platform features or userspace filtering. Test compile coverage with WMI backend only, SMM backend only, both, and neither selected as Kconfig permits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smbios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smo8800-ids.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smo8800-ids.h

Purpose: Shared ACPI ID table for Dell SMO88xx freefall/accelerometer devices.

Important APIs/types/functions: Defines `smo8800_ids` containing `SMO8800`, `SMO8801`, `SMO8810`, `SMO8811`, `SMO8820`, `SMO8821`, `SMO8830`, and `SMO8831`, and exports a module ACPI table.

Control flow/state/persistence: Header-only static table; no runtime state.

Dependencies/integration: Included by both `dell-smo8800.c` and `dell-lis3lv02d.c` to keep platform-device matching consistent.

Risks/test signals: Missing IDs would prevent binding or I2C companion instantiation. Test ACPI modalias/module autoloading and both platform/freefall and lis3lv02d companion flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smo8800-ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smo8800.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smo8800.c

Purpose: Dell Latitude ACPI SMO88xx freefall sensor driver. It exposes freefall events through `/dev/freefall` and logs interrupt detections.

Important APIs/types/functions: `struct smo8800_device` tracks IRQ, event counter, miscdevice, single-open flag, waitqueue, and device pointer. IRQ handlers `smo8800_interrupt_quick()` and `smo8800_interrupt_thread()` count/wake/log events. Misc operations implement blocking read, exclusive open, and release.

Control flow/state/persistence: Probe allocates state, registers a dynamic misc device named `freefall`, obtains IRQ 0 from the platform device, and requests a threaded rising-edge IRQ. The quick handler increments an atomic counter and wakes readers; `read()` waits for a nonzero counter, returns one byte capped at 255, and clears the count. Remove frees IRQ and deregisters the misc device. State is in memory only.

Dependencies/integration: Uses ACPI ID table from `dell-smo8800-ids.h`, platform IRQ resources, miscdevice, waitqueues, atomics, and threaded IRQs. It complements `dell-lis3lv02d.c` but does not directly instantiate the accelerometer.

Risks/test signals: `/dev/freefall` is single-open and blocking; event counts can coalesce and cap. Test IRQ resource absence, misc registration errors, blocking read interruption, concurrent open returning `-EBUSY`, freefall interrupt event delivery, and cleanup with an open device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smo8800.c -->
