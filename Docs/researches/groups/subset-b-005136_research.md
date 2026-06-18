# subset-b-005136 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hdaps.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/hdaps.c

Purpose: implements the IBM/Lenovo ThinkPad Hard Drive Active Protection System driver for older models with the HDAPS accelerometer at ISA I/O ports `0x1600..0x162f`. It exposes raw position, variance, temperatures, keyboard/mouse activity, calibration, and axis inversion through sysfs and registers a polled input device reporting `ABS_X`/`ABS_Y` tilt relative to a rest calibration.

Important APIs/types/functions: `hdaps_device_init()` performs the hardware command sequence and latch waits; `__device_refresh_sync()`, `__hdaps_read_pair()`, and `hdaps_readb_one()` serialize port access through `hdaps_mtx`; `hdaps_mousedev_poll()` feeds input events; `DEVICE_ATTR()` entries implement `position`, `variance`, `temp1`, `temp2`, `keyboard_activity`, `mouse_activity`, `calibrate`, and `invert`; `hdaps_whitelist` uses DMI callbacks to gate loading and set default inversion.

Control flow: module init checks the DMI whitelist, reserves the ISA port range, registers a `platform_driver`, creates a simple platform device, creates sysfs files, calibrates, configures a polled input device, then registers it. Reads issue a synchronous refresh, sample ports, update `km_activity`, complete the device transaction, and apply optional axis inversion. Resume re-runs hardware initialization; exit unregisters input, sysfs, platform objects, and I/O region.

State and persistence: module globals hold the platform device, input device, `hdaps_invert`, latest keyboard/mouse activity, and rest calibration. The `invert` module parameter and writable sysfs file affect runtime readings but are not persisted by the driver; calibration is runtime-only.

Dependencies and integration: depends on DMI, platform bus, input polling, sysfs, x86 port I/O, and PM sleep hooks. Integration is hardware-specific and intentionally blocked on unsupported DMI systems.

Risks: direct port I/O has tight timing and only coarse error reporting. `hdaps_invert_store()` calls `hdaps_calibrate()` without taking `hdaps_mtx`, unlike other calibration paths. DMI ordering matters because prefix-like product strings could match broader models. Test signals are module load on whitelisted ThinkPads, sysfs read/write behavior, input event stability, suspend/resume reinitialization, and failure-path cleanup when device init or input registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hdaps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/Kconfig

Purpose: defines the HP submenu for x86 platform-specific drivers and the build-time feature gates for HP accelerometer, HP WMI extras, TC1100 tablet WMI extras, and HP BIOS configuration support.

Important APIs/types/functions: Kconfig symbols are `X86_PLATFORM_DRIVERS_HP`, `HP_ACCEL`, `HP_WMI`, `TC1100_WMI`, and `HP_BIOSCFG`. Their dependency/select clauses wire each driver to required kernel subsystems: ACPI, WMI, input, i8042/serio, rfkill, power supply, sparse keymap, platform profile, hwmon, firmware attributes class, and NLS.

Control flow: this file has no runtime control flow. At configuration time, enabling `X86_PLATFORM_DRIVERS_HP` reveals the submenu; individual tristate symbols decide whether object files are built-in, modular, or absent.

State and persistence: state is the generated kernel configuration. Defaults are `m` for the driver symbols when dependencies are met, making the HP support modules available without forcing built-in code.

Dependencies and integration: `HP_ACCEL` selects the LIS3LV02D sensor core plus LED classes; `HP_WMI` selects user-visible subsystems used by `hp-wmi.c`; `HP_BIOSCFG` selects firmware attribute class support for `hp-bioscfg`.

Risks and test signals: incorrect dependencies surface as build failures or missing symbols in the corresponding C files. Kconfig testing should cover `allmodconfig`, dependency-disabled configs, and modular/built-in combinations, especially `RFKILL=n`, `ACPI_WMI` absent, and non-32-bit TC1100 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/Makefile

Purpose: maps HP x86 platform Kconfig symbols to build objects in `drivers/platform/x86/hp`.

Important APIs/types/functions: build entries compile `hp_accel.o`, `hp-wmi.o`, `tc1100-wmi.o`, and descend into `hp-bioscfg/` when `CONFIG_HP_BIOSCFG` is enabled.

Control flow: there is no runtime behavior. Kbuild evaluates `obj-$(CONFIG_...)` lines to select objects or subdirectories.

State and persistence: no runtime state. The file participates in reproducible build graph generation based on `.config`.

Dependencies and integration: this is the folder-level Kbuild integration point for the HP drivers whose feature gates are declared in the adjacent `Kconfig`.

Risks and test signals: if object names diverge from module names or symbols, modular builds fail. Build tests should include HP symbols as modules and built-in. `hp-bioscfg/` owns its internal object composition, so this file should only point at the subdirectory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/Makefile

Purpose: defines the `hp-bioscfg` module composition.

Important APIs/types/functions: `obj-$(CONFIG_HP_BIOSCFG) := hp-bioscfg.o` and `hp-bioscfg-y := ...` link the common core, WMI set interface, typed attribute handlers, password/SPM handlers, and Sure Start support into one module.

Control flow: Kbuild links `bioscfg.o`, `biosattr-interface.o`, `enum-attributes.o`, `int-attributes.o`, `order-list-attributes.o`, `passwdobj-attributes.o`, `spmobj-attributes.o`, `string-attributes.o`, and `surestart-attributes.o` into the composite object. Runtime init is provided by `bioscfg.c`.

State and persistence: no runtime state in this file; build state is controlled by `CONFIG_HP_BIOSCFG`.

Dependencies and integration: all listed sources share `bioscfg.h` and the global `bioscfg_drv`. Missing an object here breaks cross-file symbol resolution, for example `hp_set_attribute()`, typed populate functions, or cleanup hooks.

Risks and test signals: object-list drift is the main risk. Compile/link testing with `CONFIG_HP_BIOSCFG=m` verifies all prototypes and exported internal helpers remain aligned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/biosattr-interface.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/biosattr-interface.c

Purpose: implements the HP BIOS WMI command interface used by hp-bioscfg to set BIOS attributes and perform secure/platform queries.

Important APIs/types/functions: `struct bios_args` is the flexible WMI input packet. `hp_set_attribute()` builds a UTF-16 attribute-name/value/security buffer and calls `hp_wmi_set_bios_setting()`. `hp_wmi_perform_query()` wraps `wmi_evaluate_method()` for `HP_WMI_BIOS_GUID`, validates returned ACPI buffers, copies output, and maps firmware return codes. `hp_ascii_to_utf16_unicode()` encodes strings with HP length prefixes. `hp_wmi_set_bios_setting()` invokes `HP_WMI_SET_BIOS_SETTING_GUID`. A small `wmi_driver` binds the BIOS GUID.

Control flow: sysfs stores in typed attribute files eventually call `hp_set_attribute()`. That function selects either SPM auth token or setup password, computes buffer sizes, appends UTF-16 strings plus security data, and sends the set command under `bioscfg_drv.mutex`. Generic secure queries allocate an input packet sized to `insize`, select the WMI method ID by output size, and free ACPI output and packet storage after translating errors.

State and persistence: firmware updates persist in BIOS, while credentials in memory are temporary and usually cleared by callers after store attempts. This file only registers/unregisters a WMI driver and uses the shared global driver state.

Dependencies and integration: depends on ACPI WMI, NLS UTF conversion, `spmobj-attributes.c` for security buffer helpers, and password data for setup credentials.

Risks: buffer sizing is security-sensitive; `kmalloc(buffer_size + 1)` allocates byte count for a `u16 *` buffer plus one odd byte, so reviewers should confirm all sizes are byte sizes. Test signals include mocked WMI return-code mapping, UTF-16 conversion of empty/nonempty strings, credential selection, and failure cleanup on malformed ACPI objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/biosattr-interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/bioscfg.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/bioscfg.c

Purpose: main hp-bioscfg module core. It creates the firmware-attributes class device, enumerates BIOS WMI attribute instances, parses package or buffer encodings, creates per-attribute kobjects, and tears everything down.

Important APIs/types/functions: global `bioscfg_drv` owns all runtime state. Parsing helpers include `hp_get_integer_from_buffer()`, `hp_get_string_from_buffer()`, `hp_get_common_data_from_buffer()`, and `hp_convert_hexstr_to_str()`. `hp_init_bios_attributes()` enumerates WMI instances by GUID; `hp_init_bios_package_attribute()` and `hp_init_bios_buffer_attribute()` create kobjects and dispatch to type-specific populate functions. `hp_wmi_error_and_message()` maps firmware codes to Linux errors. `hp_set_reboot_and_signal_event()` sets `pending_reboot` and emits a uevent.

Control flow: module init checks required HP WMI GUIDs, registers the attribute-set WMI interface, creates `hp-bioscfg` under `firmware_attributes_class`, creates `attributes` and `authentication` ksets, creates `pending_reboot`, then enumerates string, integer, enumeration, ordered-list, and password WMI GUIDs. It also adds synthetic SPM and Sure Start objects. Exit calls type-specific cleanup, destroys ksets, unregisters the class device, and unregisters the WMI driver.

State and persistence: in-kernel state mirrors firmware data in allocated typed arrays and kobjects. BIOS setting changes are persistent only when WMI set operations succeed; `pending_reboot` is an in-memory signal for settings that require physical presence/reboot.

Dependencies and integration: integrates ACPI WMI with `firmware_attributes_class`, sysfs kobjects, typed attribute source files, password/SPM/Sure Start helpers, and NLS conversion.

Risks: malformed firmware data can desynchronize element positions, especially optional prerequisite/value lists. Some per-attribute failures are logged but enumeration continues, so partially populated sysfs trees are possible. Test signals include WMI GUID absence, package and buffer object formats, duplicate attribute names, maximum count clamping, cleanup idempotence, and uevent emission on reboot-required writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/bioscfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/bioscfg.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/bioscfg.h

Purpose: shared contract for the hp-bioscfg module, defining constants, WMI GUIDs, data structures, macro-generated sysfs accessors, and cross-file prototypes.

Important APIs/types/functions: declares `struct common_data` plus typed state structs for string, integer, enumeration, ordered list, password, and secure platform data. `struct bioscfg_priv` is the module-wide state container. Enums define HP WMI commands, SPM/Sure Start command types, firmware error values, data types, and element positions. Macros such as `GET_INSTANCE_ID`, `ATTRIBUTE_PROPERTY_STORE`, `ATTRIBUTE_VALUES_PROPERTY_SHOW`, and property-show helpers generate repeated sysfs code.

Control flow: the header has no direct runtime flow, but `ATTRIBUTE_PROPERTY_STORE` defines the common write sequence for mutable BIOS settings: duplicate input, enforce one-line sysfs input, find instance, validate type-specific value, call `hp_set_attribute()`, update cached value, signal reboot if required, clear credentials, and return either error or byte count.

State and persistence: the declared `bioscfg_drv` external is the single shared state object. Fixed-size arrays bound values, encodings, prerequisites, and element lists; credentials and SPM tokens have dedicated fields.

Dependencies and integration: includes WMI, kernel device/module primitives, strings, types, and NLS. It binds all hp-bioscfg C files together.

Risks: macro-generated stores rely on locally defined functions with exact names, so refactors can silently break build linkage. Fixed limits require careful firmware clamping. Because credentials are stored in process memory before WMI submission, tests should verify clearing paths. Compile tests and sparse/static analysis are important signals for macro expansion and type correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/bioscfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/enum-attributes.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/enum-attributes.c

Purpose: handles HP BIOS enumeration attributes, exposing each enumerated BIOS setting as a sysfs directory with current value, possible values, display name, language code, and type.

Important APIs/types/functions: `hp_alloc_enumeration_data()`, `hp_populate_enumeration_package_data()`, `hp_populate_enumeration_buffer_data()`, and `hp_exit_enumeration_attributes()` are called by the core. `validate_enumeration_input()` accepts only values present in `possible_values`; `update_enumeration_value()` refreshes cached state after successful firmware writes. `expected_enum_types` validates ACPI package layout.

Control flow: allocation sizes the typed array from WMI instance count. Package parsing walks ordered ACPI elements, converts hex strings, validates expected types, handles optional prerequisite and possible-value lists, clamps counts, and fills `enumeration_data`. Buffer parsing reads the current value, common data, current value again, count, and value strings from the firmware buffer. Populate functions update permissions, derive friendly names, and create the attribute group.

State and persistence: cached current value and possible-value lists live in `bioscfg_drv.enumeration_data`; writes persist only through `hp_set_attribute()` from the shared store macro.

Dependencies and integration: depends on common parsing helpers, sysfs macros, firmware WMI enumeration GUID, and hp-bioscfg core enumeration.

Risks: package parsing has element-index adjustments for omitted zero-length lists, making off-by-one regressions likely. The possible-values package branch only copies when `size < MAX_VALUES_SIZE`, so exactly max-sized lists deserve review. Test signals include invalid value writes, readonly enforcement, package/buffer parsing with zero and oversized lists, and cleanup removing sysfs groups before freeing arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/enum-attributes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/int-attributes.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/int-attributes.c

Purpose: handles integer-valued BIOS settings for hp-bioscfg, exposing current value, lower/upper bounds, scalar increment, display metadata, and type through sysfs.

Important APIs/types/functions: `hp_alloc_integer_data()`, `hp_populate_integer_package_data()`, `hp_populate_integer_buffer_data()`, and `hp_exit_integer_attributes()` provide lifecycle hooks. `validate_integer_input()` parses decimal input and enforces readonly plus bounds. `update_integer_value()` refreshes cached integer state. `expected_integer_types` defines package layout validation.

Control flow: package parsing converts string and integer ACPI elements in order, supports optional prerequisites, converts the firmware current-value string with `kstrtoint()`, and stores bounds/increment. Buffer parsing reads a UTF-16 value string into temporary memory, converts it, then reads common data and numeric bounds. Populate functions attach the sysfs group and permission mode after parsing.

State and persistence: each instance stores current value and limits in `bioscfg_drv.integer_data`. Firmware persistence is delegated to the shared `ATTRIBUTE_PROPERTY_STORE` path and `hp_set_attribute()`.

Dependencies and integration: uses common buffer/string conversion helpers from `bioscfg.c`, macro accessors from `bioscfg.h`, and the integer WMI GUID.

Risks: `scalar_increment` is exported but not enforced in `validate_integer_input()`, so firmware may reject values the driver accepts. Temporary destination sizing in buffer parsing is tied to remaining UTF-16 buffer size. Test signals should cover lower/upper bound failures, readonly writes, non-numeric input, package type mismatches, malformed buffers, and cleanup after partial enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/int-attributes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/order-list-attributes.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/order-list-attributes.c

Purpose: supports ordered-list BIOS attributes, which represent ordered sequences such as boot orders. It exposes a semicolon-separated current value, available elements, display name, language code, and type.

Important APIs/types/functions: lifecycle functions are `hp_alloc_ordered_list_data()`, `hp_populate_ordered_list_package_data()`, `hp_populate_ordered_list_buffer_data()`, and `hp_exit_ordered_list_attributes()`. `replace_char_str()` translates comma and semicolon separators. `validate_ordered_list_input()` converts user semicolons to BIOS commas and leaves semantic validation to firmware.

Control flow: package parsing validates expected ACPI types, converts current value commas to semicolons for sysfs, handles common metadata and prerequisites, clamps element count, and splits comma-separated element data. Buffer parsing reads the current value, common data, element count, and element strings. Writes use the shared store macro; validation mutates the copied input into the firmware separator format before `hp_set_attribute()`.

State and persistence: cached ordered-list data lives in `bioscfg_drv.ordered_list_data`. Runtime cache updates follow successful WMI writes; BIOS owns persistent ordering.

Dependencies and integration: integrates with hp-bioscfg common parsing, firmware WMI ordered-list GUID, and sysfs attribute-group creation.

Risks: local validation does not check membership or duplicates, so user errors depend on firmware rejection. Package `ORD_LIST_ELEMENTS` conversion is complex because data may be hex-encoded comma-separated content. Test signals include separator conversion, list count clamping, malformed packages, empty lists, readonly mode, and user writes that firmware accepts or rejects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/order-list-attributes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/passwdobj-attributes.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/passwdobj-attributes.c

Purpose: implements password authentication objects for hp-bioscfg, including setup and power-on password metadata plus write-only credential staging files.

Important APIs/types/functions: `hp_alloc_password_data()`, `hp_populate_password_package_data()`, `hp_populate_password_buffer_data()`, and `hp_exit_password_attributes()` provide lifecycle. `hp_get_password_instance_for_type()` locates setup/power-on password entries. `hp_clear_all_credentials()` zeroes password buffers and frees SPM auth tokens. `store_password_instance()` backs `current_password` and `new_password` sysfs writes. `validate_password_input()` enforces length constraints.

Control flow: package/buffer parsers fill common metadata, password min/max lengths, encodings, and enabled state. Populate functions create the password attribute group under the authentication kset. Credential stores copy one-line input into the selected password field after validation; other attribute writes later consume current setup password in `hp_set_attribute()`.

State and persistence: password content is staged in memory only and should be cleared after any BIOS setting write. Firmware stores actual password state; the driver exposes only `is_enabled` and constraints.

Dependencies and integration: used by `biosattr-interface.c` for authentication and by shared store macros for credential cleanup. Password objects are part of the hp-bioscfg authentication sysfs subtree.

Risks: `new_password_store()` passes `true` to `store_password_instance()`, so it writes `current_password` rather than `new_password`; that is a notable behavior risk. Password buffers are wiped with `memset()` rather than an explicit no-elide helper. Test signals include current/new password staging, min/max validation, one-line rejection, credential clearing after attribute writes, and package/buffer parsing of encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/passwdobj-attributes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/spmobj-attributes.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/spmobj-attributes.c

Purpose: implements Secure Platform Management (SPM/Sure Admin) sysfs support for hp-bioscfg, including status reporting, signing/endorsement key provisioning, auth-token staging, and security buffer construction.

Important APIs/types/functions: `struct secureplatform_provisioning_data` mirrors WMI status data. `hp_calculate_security_buffer()` and `hp_populate_security_buffer()` build password or BEAM token authentication payloads. `update_spm_state()`, `statusbin()`, and `status_show()` query provisioning state. `sk_store()`, `kek_store()`, and `auth_token_store()` accept key/token writes. `hp_populate_secure_platform_data()` creates the SPM attribute group.

Control flow: SPM object creation initializes disabled state, queries firmware, clears key/token pointers, and creates sysfs files. Key stores copy the provided payload, send the matching secure-platform WMI command, update mechanism and reboot signal on success, then free the temporary key. Auth token store stages a token for the next BIOS setting update.

State and persistence: SPM keys provision firmware state; `auth_token` is in-memory and cleared by `hp_clear_all_credentials()`. `pending_reboot` is set after successful key changes.

Dependencies and integration: depends on `hp_wmi_perform_query()` from `biosattr-interface.c`, shared driver state, and the normal attribute set path that consumes `auth_token`.

Risks: `auth_token_store()` uses `kmemdup()` without appending a NUL byte, while later security-buffer helpers call `strlen()` on the token. Status output formats numeric key modulus bytes as text despite comments mentioning base64. Test signals include SPM absent/provisioned states, BEAM and UTF-prefix authentication buffer sizing, key provisioning return codes, token lifecycle, and reboot uevent emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/spmobj-attributes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/string-attributes.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/string-attributes.c

Purpose: handles string-valued BIOS settings for hp-bioscfg and exposes each as sysfs `current_value`, `min_length`, `max_length`, display metadata, language code, and type.

Important APIs/types/functions: `hp_alloc_string_data()`, `hp_populate_string_package_data()`, `hp_populate_string_buffer_data()`, and `hp_exit_string_attributes()` form the lifecycle. `validate_string_input()` enforces readonly and min/max length. `update_string_value()` refreshes cached state. `expected_string_types` validates ACPI package layout.

Control flow: the core allocates string data by WMI instance count, then dispatches package or buffer objects here. Package parsing walks expected elements, converts HP hex strings, handles optional prerequisite omission, fills common metadata and min/max lengths, then creates the sysfs group. Buffer parsing reads current value, common fields, and length bounds from a firmware buffer.

State and persistence: current value and constraints are cached in `bioscfg_drv.string_data`; persistent firmware state changes occur through the shared store macro and WMI set interface.

Dependencies and integration: uses common conversion/parsing helpers, `common_display_langcode`, friendly-name updates, and permission updates based on readonly state.

Risks: `strlen()` based validation measures bytes, not characters, while firmware strings are converted from UTF-16 but generally constrained to ASCII-like content. Optional prerequisite handling can shift element indices. Test signals include min/max failures, readonly writes, empty strings, buffer truncation, prerequisite lists at zero and maximum counts, and sysfs cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/string-attributes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/surestart-attributes.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/surestart-attributes.c

Purpose: adds the synthetic HP Sure Start sysfs object used to inspect firmware audit log availability and read audit log entries.

Important APIs/types/functions: `audit_log_entry_count_show()` returns count, entry size, and max entries. `audit_log_entries_show()` reads each log entry with `HPWMI_SURESTART_GET_LOG`. `hp_populate_sure_start_data()` creates the sysfs group; `hp_exit_sure_start_attributes()` removes it.

Control flow: the count file sends a Sure Start WMI query for log count. The entries file queries the count, rejects output larger than a page, then iterates 1-based log indices, requesting a 128-byte firmware buffer for each and copying the first 16 bytes into the sysfs output until failure or completion.

State and persistence: no persistent driver state except `bioscfg_drv.sure_start_attr_kobj`; logs live in firmware and are read-only through this driver.

Dependencies and integration: depends on `hp_wmi_perform_query()` and the synthetic object creation path in `bioscfg.c`.

Risks: sysfs binary-like output is constrained by `PAGE_SIZE`; future larger log formats would fail. `hp_exit_sure_start_attributes()` assumes the kobject exists. Test signals include zero logs, maximum logs, per-entry WMI failure returning partial data, page-size rejection, and removal during module exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/surestart-attributes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-wmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-wmi.c

Purpose: HP laptop WMI extras driver. It handles WMI hotkeys and switches, rfkill, legacy sensor sysfs files, camera shutter events, platform profiles for generic/OMEN/Victus systems, fan hwmon controls, and AC power-source profile restoration.

Important APIs/types/functions: `hp_wmi_perform_query()` is the central BIOS WMI method wrapper. Input handling uses `hp_wmi_keymap`, `hp_wmi_notify()`, and `hp_wmi_input_setup()`. Wireless control uses legacy rfkill and rfkill2 paths. Thermal/profile code includes OMEN/Victus DMI tables, `thermal_profile_setup()`, platform profile ops, and AC notifier callbacks. Hwmon support uses `struct hp_wmi_hwmon_priv`, `hp_wmi_apply_fan_settings()`, and hwmon read/write callbacks.

Control flow: module init checks event and BIOS GUIDs, detects zero-input-size firmware behavior, sets up input notify handling, registers a platform device/driver for BIOS features, detects board-specific thermal parameters, initializes rfkill, hwmon, and platform profile support, and optionally registers AC notifiers. WMI notifications decode event buffers into dock/tablet switches, sparse-keymap events, rfkill refreshes, platform-profile cycling, or camera shutter switch events. Exit unregisters notifiers, input devices, rfkill, hwmon keepalive, platform objects, and profile notifiers.

State and persistence: runtime globals track input devices, platform device, rfkill objects, platform profile state, zero-size-query quirk, board-specific profile parameters, and fan keepalive state. Some settings persist in firmware or EC, while `active_platform_profile` caches user intent because firmware may reject or revert performance mode on battery.

Dependencies and integration: ACPI WMI/EC, DMI, input sparse keymap, rfkill, power_supply, platform_profile, hwmon, workqueues, and sysfs device attributes.

Risks: the file mixes many hardware generations and DMI quirks, so regressions can be board-specific. WMI output parsing assumes HP buffer formats. Fan manual mode requires periodic keepalive. Test signals include WMI GUID combinations, hotkey events, rfkill2 device parsing, suspend/resume state refresh, platform-profile get/set on generic and OMEN/Victus boards, AC notifier behavior, and hwmon fan/pwm reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-wmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp_accel.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp_accel.c

Purpose: glue driver between HP ACPI BIOS accelerometer devices and the shared LIS3LV02D accelerometer core, with support for HP disk-protection LED and HPQ6000 keyboard-bus scan-code filtering.

Important APIs/types/functions: ACPI IDs `HPQ0004`, `HPQ6000`, and `HPQ6007` autoload the driver. `lis3lv02d_acpi_read()` and `lis3lv02d_acpi_write()` call ACPI methods `ALRD` and `ALWR`. DMI axis conversion tables populate `lis3_dev.ac`. `hpled_set()` drives ACPI method `ALED`. `hp_accel_i8042_filter()` suppresses accelerometer scan codes from the keyboard stream.

Control flow: probe attaches ACPI companion data to `lis3_dev`, optionally records IRQ, selects axis conversion from DMI or default, initializes the shared LIS3 device, installs the i8042 filter for HPQ6000, initializes deferred LED work, and registers the LED class device. Remove reverses filter, joystick, power, LED, work, and filesystem state. PM suspend powers off the sensor; resume powers it back on.

State and persistence: uses the global LIS3 core device plus a static delayed LED device. Axis mapping is runtime-detected; LED brightness is runtime state only.

Dependencies and integration: depends on ACPI, platform bus, i8042/serio, LED class, and `drivers/misc/lis3lv02d` core APIs.

Risks: DMI axis mappings are model-specific and incomplete; wrong mapping gives inverted/swapped motion. The i8042 filter uses static extended-prefix state and must not consume unrelated keyboard bytes. Test signals include ACPI read/write method failures, DMI axis logs, LED registration failure cleanup, HPQ6000 scan-code filtering, and suspend/resume power behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp_accel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/tc1100-wmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/tc1100-wmi.c

Purpose: legacy HP Compaq TC1100 tablet WMI extras driver exposing wireless and jogdial state toggles through sysfs.

Important APIs/types/functions: WMI GUID `C364AC71-36DB-495A-8494-B439D472A505` provides two block instances: wireless and jogdial. `get_state()` maps raw WMI integer values to booleans; `set_state()` maps booleans back to firmware values and calls `wmi_set_block()`. The `show_set_bool` macro defines `wireless` and `jogdial` device attributes. PM hooks save and restore both states.

Control flow: init checks the GUID, allocates/adds a simple platform device, then probes a platform driver to create the sysfs group. Sysfs reads query WMI block state; writes parse an integer with `simple_strtoul()` and set WMI block state. Suspend reads both states into `suspend_data`; resume writes them back.

State and persistence: runtime state is the platform device and optional saved suspend values. Actual wireless/jogdial configuration is in firmware.

Dependencies and integration: ACPI WMI, platform device/driver model, sysfs attributes, and PM core.

Risks: the macro treats positive Linux error returns as ACPI-style status in places, but negative errors still route to read/write failure output. Write parsing is permissive because any nonzero value becomes enabled. Test signals include absent GUID, invalid instance handling, sysfs read/write mapping, suspend/resume preservation, and cleanup after platform probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/hp/tc1100-wmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/huawei-wmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/huawei-wmi.c

Purpose: Huawei laptop WMI extras driver supporting hotkeys, mic mute LED, battery charge thresholds, Fn-lock state, and debugfs WMI calls.

Important APIs/types/functions: GUIDs are `HWMI_METHOD_GUID`, `HWMI_EVENT_GUID`, and legacy WMI0 GUIDs. `huawei_wmi_cmd()` is the main method wrapper, normalizing package and legacy buffer response formats. DMI quirks control battery reset, EC micmute, and brightness key reporting. Battery support uses an ACPI battery hook plus threshold sysfs files; input uses sparse keymap; LED support registers `platform::micmute`; debugfs exposes raw argument/call.

Control flow: init allocates global state, applies DMI and module-parameter quirks, registers a platform driver and device. Probe installs notify handlers for present event GUIDs. If the method GUID exists, it initializes the WMI mutex, LED, Fn-lock, battery threshold support, and debugfs. Notifications process either direct integer scan codes or legacy code `0x80` by querying the expensive WMI block.

State and persistence: global `huawei_wmi` holds availability flags, debugfs argument, LED device, mutex, and device pointer. Battery thresholds, Fn-lock, and LED state are firmware/EC-backed; debugfs argument is runtime-only.

Dependencies and integration: ACPI WMI, ACPI battery hooks, power_supply devices, LED class, input sparse keymap, debugfs, DMI, EC helpers, and platform bus.

Risks: `huawei_wmi_cmd()` temporarily advances `obj->buffer.pointer` before freeing `out.pointer`, which relies on freeing the original ACPI object pointer rather than the adjusted inner pointer. Battery threshold discovery scans for nonzero bytes and may be fragile across firmware formats. Test signals include both package and 0x104 buffer responses, double-call retry behavior, battery-reset quirk, Fn-lock get/set, EC and WMI micmute paths, brightness reporting quirk, legacy WMI0 hotkey translation, and debugfs cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/huawei-wmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/ibm_rtl.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/ibm_rtl.c

Purpose: IBM Premium Real Time Mode driver. It finds an `_RTL_` table in the BIOS EBDA and exposes sysfs controls to enter or exit PRTM/real-time mode by issuing the firmware-described I/O or MMIO command.

Important APIs/types/functions: `struct ibm_rtl_table` maps the packed firmware table. `ibm_rtl_init()` checks DMI/EFI, maps EBDA, scans for the signature, maps the command port, and creates a system bus. `ibm_rtl_write()` writes enter/exit commands, triggers the firmware port write with width 8/16/32, waits for completion, and checks `command_status`. Sysfs attributes are `version` and writable `state`.

Control flow: init optionally honors `force`, otherwise rejects EFI boot and non-IBM DMI systems, maps EBDA first to read size then fully, scans word-aligned offsets for `_RTL_`, reads command metadata, maps command address as I/O or MMIO, and registers sysfs. Writing `state` with `0` or `1` calls `ibm_rtl_write()`. Exit forces state `0`, tears down sysfs, and unmaps memory/ports.

State and persistence: globals hold mapped EBDA/table/command address and command type/width. Hardware mode can persist beyond process lifetime, so module exit explicitly exits PRTM.

Dependencies and integration: DMI, EFI detection, BIOS EBDA helper, ioport/ioremap accessors, sysfs bus registration, mutex serialization, and non-atomic 64-bit I/O helper for signature reads.

Risks: direct EBDA scanning and firmware command execution are platform-sensitive. `rtl_port_unmap()` calls `ioport_unmap()` when the address is NULL and command type is not MMIO, so failure cleanup deserves scrutiny. Test signals include forced load, no EBDA, malformed table, MMIO vs I/O command mapping, command timeout/status failures, sysfs permissions, and exit restoring non-PRTM state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/ibm_rtl.c -->
