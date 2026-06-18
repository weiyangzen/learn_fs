# Research: subset-b-005148

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/lenovo.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/lenovo.c

Purpose: Lenovo board-description shard for the x86 Android tablet quirk driver. It supplies DMI-selected `x86_dev_info` records for Yoga Book X90/X91, Yoga Tablet 2 830/1050/1380, and Yoga Tab 3 Pro YT3 systems whose ACPI tables omit or misdescribe I2C, SPI, GPIO, audio, charger, backlight, lid, and serial-device wiring.

Important APIs/types/functions: the file exports `lenovo_yogabook_x90_info`, `lenovo_yogabook_x91_info`, `lenovo_yoga_tab2_830_1050_info`, `lenovo_yoga_tab2_1380_info`, and `lenovo_yt3_info`. It fills `x86_i2c_client_info`, `x86_spi_dev_info`, `x86_serdev_info`, `platform_device_info`, software-node groups, LP8557 backlight platform data, bq24190 charger platform data, Arizona codec pdata, pinctrl maps, and optional init/exit hooks. Main init helpers are `lenovo_yb1_x90_init()`, `lenovo_yoga_tab2_830_1050_init_touchscreen()`, `lenovo_yoga_tab2_830_1050_init_codec()`, `lenovo_yoga_tab2_830_1050_init()`, `lenovo_yoga_tab2_1380_init()`, and `lenovo_yt3_init()`.

Control flow: the parent x86-android-tablets driver matches DMI and consumes these `x86_dev_info` objects to instantiate board-specific devices. Static tables describe clients and firmware properties; per-board init hooks handle side effects that cannot be expressed as client tables. Yoga Book X90 enables PMIC rails for touchscreens. Yoga Tablet 2 830/1050 reads a PMIC GPIO bootstrap to distinguish 8-inch and 10-inch hardware, adjusts touchscreen axis alignment and accelerometer software-node data, finds the WM5102 SPI codec device, registers a pinctrl mapping for its 32 kHz clock, attaches its software node, and registers an EFI-based power-off handler. Yoga Tablet 2 Pro 1380 reuses codec/poweroff setup and adds fast-charger and LC824206XA switch wiring. YT3 configures bq25892 charge-enable/OTG GPIOs, enables touchscreen regulators, and registers dual battery/charger plus WM5102 audio data.

State and persistence: there is no disk persistence. Most state is immutable `__initconst` board data consumed during boot. Mutable boot-time state includes `lenovo_yoga_tab2_830_1050_rmi_pdata`, the selected accelerometer software node, codec device/pinctrl/sys-off handler pointers for cleanup, and requested GPIO lines. Hardware state is persistent until reset for PMIC regulator bits, charge-enable pins, codec pinmux selection, and EFI poweroff behavior.

Dependencies/integration: depends on the shared x86 tablet infrastructure, GPIO software nodes for Bay Trail/Cherry Trail, `shared-psy-info` battery/charger nodes, I2C/SPI board-info instantiation, serdev link creation, PMIC MIPI sequence helpers, pinctrl mappings, sys-off handling, EFI reset services, bq24190/bq25890/bq275xx power-supply drivers, LP8557 backlight, RMI/Goodix/HiDeep touch, Arizona WM5102, and platform devices such as `intel-int3496` or Lenovo fast charger.

Risks: this file is mostly hardcoded board truth, so wrong GPIO chip labels, pin numbers, ACPI adapter paths, IRQ polarity, or software-node properties can make input, charging, touchscreen, audio, or poweroff fail only on a specific SKU. The Yoga Tablet 2 codec init has multi-step cleanup and must keep mapping, pinctrl, software-node, and device refcount lifetimes paired. The 830/1050 runtime hardware detection mutates global init data, so ordering matters. Charger/fuel-gauge `supplied-from` names must match registered power supplies. PMIC sequence writes and bq25892 GPIO overrides are board-sensitive.

Test signals: DMI boot on each Lenovo model should show the expected devices under I2C/SPI/platform/serdev, correct touchscreen orientation, working lid switch, backlight brightness range, fuel-gauge/charger relationships, WM5102 audio and headset buttons, Wi-Fi/Bluetooth enumeration where relevant, EFI poweroff without ACPI hang, and clean driver exit for codec/sys-off resources on module unload or failed init. Regression tests should include missing adapter/GPIO paths and both Yoga Tablet 2 830 vs 1050 bootstrap outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/lenovo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/other.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/other.c

Purpose: non-Lenovo board-description shard for the x86 Android tablet quirk driver. It provides `x86_dev_info` records and board hooks for assorted tablets with broken or incomplete DSDT data, including Advantech MICA-071, Chuwi Hi8, Cyberbook T116, CZC P10T, Medion Lifetab S10346, Nextbook Ares 8/8A, Peaq C1010, whitelabel TM800A550L, Vexia EDU ATLA 10 5V/9V, and Xiaomi Mi Pad 2.

Important APIs/types/functions: exports the matching `*_info` symbols declared in `x86-android-tablets.h`. It uses `software_node` and `property_entry` structures for GPIO keys, touchscreens, accelerometer mount matrices, batteries, LEDs, PMIC options, and firmware names; `x86_i2c_client_info` for manually instantiated I2C devices; `x86_serdev_info` for the Vexia Realtek UART device; and init hooks `chuwi_hi8_init()`, `czc_p10t_init()`, `vexia_edu_atla10_9v_init()`, `xiaomi_mipad2_init()`, plus `xiaomi_mipad2_brightness_set()` for the PWM LED class device.

Control flow: the parent quirk driver selects one `x86_dev_info` from DMI and then registers described I2C clients, GPIO key software nodes, platform devices, serdev links, or board init hooks. Chuwi Hi8 aborts its Android-mode workaround if the Windows touchscreen ACPI device is present. CZC P10T writes an EC I/O port to switch hardware buttons into Android scancode mode. Vexia 9V enables Wi-Fi with a GPIO and reprobes the SDIO PCI function so the module enumerates, while also instantiating EC battery, RT5640, accelerometer, touchscreen, PMIC, and Bluetooth serdev clients. Xiaomi Mi Pad 2 registers hidden fuel gauge and KTD2026 LED devices and creates a separate PWM-backed LED class device for touch-button backlight.

State and persistence: most state is boot-time immutable table data. Mutable state is limited to requested GPIOs, the global `xiaomi_mipad2_led_pwm` pointer, registered LED class device state, and hardware side effects such as the CZC EC mode byte, Vexia Wi-Fi enable line, and PWM duty cycle. There is no filesystem persistence.

Dependencies/integration: integrates with the core x86 tablet DMI infrastructure, ACPI presence checks, PCI reprobe, GPIO descriptors and software nodes, LED class and PWM APIs, I2C board-info registration, serdev binding, shared power-supply software nodes, `intel-int3496` platform-data from `shared-psy-info`, HID-over-I2C, Goodix/Silead/FT5x06/RMI touch drivers, Kionix/BMA/MMA accelerometer drivers, RT5640 audio, Crystal Cove PMIC, Vexia EC battery driver, Realtek UART Bluetooth, and KTD2026 multicolor LED binding.

Risks: table entries encode board-specific IRQ polarity and GPIO references that are difficult to validate generically. Some boards have conditional firmware behavior, such as Chuwi Windows vs Android DSDT and Xiaomi hidden devices under non-Android bootloaders. `czc_p10t_init()` writes a magic EC port with no feature discovery. Vexia Wi-Fi reprobe depends on PCI topology and a synchronous GPIO state change. Xiaomi LED PWM deliberately stays enabled to avoid a floating pin, which should be preserved when changing suspend or brightness behavior.

Test signals: validate each DMI entry by checking created I2C clients, GPIO keys, input events, touchscreen firmware/orientation, accelerometer mount matrix, power-supply links, Vexia Wi-Fi/BT enumeration, Xiaomi RGB and touch-button LEDs, and absence of duplicate devices when firmware already exposes a working ACPI node. Error-path signals include clean return from missing PCI SDIO, missing PWM, or Chuwi Windows-mode ACPI detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/other.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/shared-psy-info.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/shared-psy-info.c

Purpose: shared power-supply, battery, charger, regulator, and USB-ID platform data for x86 Android tablet board-description files. It avoids duplicating common simple-battery software nodes, fuel-gauge supplier links, bq24190 VBUS regulator setup, module preload lists, and generic `intel-int3496` platform-device properties.

Important APIs/types/functions: exports `tusb1211_chg_det_psy`, `bq24190_psy`, `bq25890_psy`, `fg_bq24190_supply_node`, `fg_bq25890_supply_node`, `generic_lipo_4v2_battery_node`, `generic_lipo_4v2_battery_swnodes`, `generic_lipo_hv_4v35_battery_node`, `generic_lipo_hv_4v35_battery_swnodes`, `bq24190_pdata`, `bq24190_modules`, and `int3496_pdevs`. Internally it defines OCV capacity tables for 4.2 V and 4.35 V LiPo packs and a regulator consumer supply that maps bq24190 VBUS to `intel-int3496`.

Control flow: no runtime control flow exists in this file; board files reference the exported arrays and nodes during DMI-selected device instantiation. When a bq24190 client is registered with `bq24190_pdata`, its VBUS regulator is exposed with constraints that allow status changes by the `intel-int3496` consumer. `int3496_pdevs` provides a ready-made platform device with Bay Trail GPIOs for VBUS, mux, and ID pin handling.

State and persistence: state is static kernel data. Battery OCV tables and software-node properties are read by downstream drivers at device registration time. Hardware persistence is indirect through regulator framework consumers and power-supply relationships.

Dependencies/integration: depends on Linux property/software-node APIs, regulator machine constraints, bq24190 charger platform data, platform-device info, GPIO software nodes from `x86-android-tablets`, and power-supply driver conventions for `supplied-from` and `monitored-battery`.

Risks: exported power-supply names must match actual driver names, especially `bq25890-charger-0` and `bq24190-charger`. OCV tables are generic approximations; using the wrong battery node can skew reported capacity. `int3496_pdevs` hardcodes Bay Trail GPIO references and is suitable only for boards with that wiring. Module preload strings must remain synchronized with driver names needed for IRQ and VBUS regulator availability.

Test signals: check that fuel gauges show correct `supplied_from` links, charger drivers bind with monitored-battery data, `intel-int3496` can enable/disable bq24190 VBUS, USB-ID role changes work on boards using `int3496_pdevs`, and battery capacity curves look plausible across charge/discharge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/shared-psy-info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/shared-psy-info.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/shared-psy-info.h

Purpose: declaration header for shared x86 Android tablet power-supply helper data exported by `shared-psy-info.c`.

Important APIs/types/functions: forward-declares `struct bq24190_platform_data`, `struct platform_device_info`, and `struct software_node`, then declares shared supplier-name arrays, fuel-gauge software nodes, generic battery nodes and node groups, `bq24190_pdata`, `bq24190_modules`, and `int3496_pdevs`.

Control flow: none; this is a compile-time interface used by board-description C files.

State and persistence: no state beyond external symbol declarations. The declared objects are static boot-time configuration data owned by `shared-psy-info.c`.

Dependencies/integration: included by x86 Android tablet board shards that need battery, charger, or USB-ID properties. It intentionally avoids pulling in heavy headers by using forward declarations.

Risks: declarations must stay exactly synchronized with definitions in `shared-psy-info.c`; constness and `__initconst` expectations matter because these symbols are consumed in init-only board tables. Missing declarations lead to duplicated ad hoc nodes in board files or compile failures.

Test signals: compile coverage of all board shards including this header, and successful linking of every declared shared symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/shared-psy-info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/vexia_atla10_ec.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/vexia_atla10_ec.c

Purpose: I2C power-supply class driver for the embedded controller on the Vexia EDU ATLA 10 9V tablet. It reimplements the useful ACPI battery access path for firmware that exposes LPSS I2C as PCI and therefore cannot use the broken ACPI battery device directly.

Important APIs/types/functions: key data types are packed `atla10_ec_battery_state`, `atla10_ec_battery_info`, and runtime `atla10_ec_data`. `atla10_ec_cmd()` reads EC SMBus blocks, `atla10_ec_update()` caches battery state for five seconds, `atla10_ec_psy_get_property()` implements power-supply properties, `atla10_ec_external_power_changed()` schedules a delayed refresh, and `atla10_ec_probe()` reads design info and registers `atla10_ec_battery`. The I2C ID is `vexia_atla10_ec`.

Control flow: probe allocates driver data, initializes mutex and autocancel delayed work, reads static battery info command `0x88`, then registers a battery `power_supply`. Property reads lock `update_lock`, refresh command `0x87` if the cache is invalid or stale, translate ACPI battery status bits into Linux status values, convert little-endian mAh/mV/mA/temperature fields into sysfs units, clamp `charge_now` to `charge_full` to hide an EC full-battery bug, and report fixed min design voltage and LiPo technology. External power changes wait 0.5 seconds, invalidate the cache, and notify userspace.

State and persistence: runtime state is an in-memory cache of battery info/state, `valid`, `last_update`, delayed work, and mutex. The EC owns true hardware state; the driver has no disk persistence. Cached dynamic state persists only until staleness timeout, external-power notification, or driver removal.

Dependencies/integration: depends on I2C SMBus block reads, power_supply core, delayed work, mutex guard helpers, byte-order conversion, and board instantiation from `other.c` using `x86_i2c_client_info`. The `supplied-from` relationship is supplied via the board software node, not by this driver.

Risks: `atla10_ec_cmd()` requires the EC to return exactly the expected block length; partial or longer reads fail as `-EIO`. Temperature conversion divides centi-degrees by 10 for power-supply deci-degree units, which assumes EC units are exactly centi-Celsius. `current_now` sign depends only on the discharging bit. The cache improves performance but can obscure rapid EC changes for up to five seconds except after external-power callbacks.

Test signals: verify probe reads command `0x88`, sysfs properties return expected units and negative discharge current, full-battery `charge_now` is clamped, external charger plug/unplug triggers delayed `power_supply_changed()`, SMBus read-length errors propagate, and repeated property reads within five seconds avoid extra EC traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/vexia_atla10_ec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/x86-android-tablets.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/x86-android-tablets.h

Purpose: central interface for the x86 Android tablet DMI quirk subsystem. It defines the board-description structures used by vendor shards and declares helper functions, GPIO software-node arrays, DMI IDs, and all exported `x86_dev_info` records.

Important APIs/types/functions: defines `enum x86_acpi_irq_type`, `enum x86_gpiochip_type`, `struct x86_acpi_irq_data`, `struct x86_i2c_client_info`, `struct x86_spi_dev_info`, `struct x86_serdev_info`, and `struct x86_dev_info`. Declares `x86_android_tablet_get_gpiod()` and `x86_acpi_irq_helper_get()`, the Bay Trail and Cherry Trail GPIO-chip software nodes, all board-info externs, and `x86_android_tablet_ids`.

Control flow: no implementation lives here, but it describes how the core driver consumes board records: optional modules and software-node groups are loaded/registered, I2C/SPI/platform/serdev devices are instantiated, GPIO button nodes are converted to gpio-keys devices, board init hooks run, and optional exit hooks clean up.

State and persistence: the header defines structure layouts for boot-time board data. Persistence is limited to the devices and GPIO/IRQ resources instantiated by the core driver based on these descriptors.

Dependencies/integration: includes GPIO consumer, I2C, IRQ domain, and SPI definitions because descriptor structs embed kernel board-info types. It is shared by all x86 tablet board files and by the core DMI driver that owns helper implementations.

Risks: this is a cross-file ABI inside the driver. Adding fields to `x86_dev_info` or changing IRQ semantics affects every board shard. `adapter_path`, `ctrl_path`, GPIO chip names, and ACPI/PCI serdev controller descriptors are string/topology contracts that must match helper lookup behavior. `__initconst` board records depend on the core copying or consuming data during init.

Test signals: all board shards compile against the header, DMI records resolve to the expected externs, GPIO/APIC/PMIC IRQ helper paths work for representative descriptors, and board init/exit hooks execute in the expected lifetime order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/x86-android-tablets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/xiaomi-wmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/xiaomi-wmi.c

Purpose: WMI input driver for Xiaomi laptop hotkey notification GUIDs. It converts firmware WMI events into Linux input key press/release sequences.

Important APIs/types/functions: `struct xiaomi_wmi` stores one input device, a mutex protecting key event sequences, and the key code for the bound GUID. `XIAOMI_DEVICE()` associates GUID strings with key codes in `xiaomi_wmi_id_table`. `xiaomi_wmi_probe()` allocates/registers the input device, and `xiaomi_wmi_notify()` reports a press and release. The active GUIDs map Fn to `KEY_PROG1` and Fn+F7 to `KEY_CUT`; other known GUID mappings are present but commented out.

Control flow: WMI core matches each GUID and passes the table context to probe. Probe rejects missing context, allocates state, initializes the mutex and input device, sets EV_KEY capability for the configured key, and registers the device. On notification, the driver locks, emits key down/sync and key up/sync, then unlocks.

State and persistence: state is per-WMI-device and in memory only. The mutex serializes event emission so overlapping WMI notifications do not interleave key sequences. There is no persistent configuration.

Dependencies/integration: depends on WMI bus, devm-managed input allocation, Linux input key codes, module WMI driver registration, and firmware exposing one of the GUIDs. `no_singleton = true` allows multiple GUID-backed WMI devices.

Risks: the payload is ignored and `min_event_size` is zero, so any notification on a matched GUID produces a key event. Commented GUIDs indicate some keys may be intentionally disabled to avoid duplicate or incorrect input reports. Synthetic press/release cannot represent key hold duration.

Test signals: WMI event injection or real hotkey use should create exactly one input event pair for each active GUID, multiple matched GUIDs should register independently, and disabled GUIDs should not produce events unless explicitly re-enabled and validated against duplicate firmware paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/xiaomi-wmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/xo1-rfkill.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/xo1-rfkill.c

Purpose: OLPC XO-1 platform rfkill driver that controls WLAN reset through the OLPC embedded controller.

Important APIs/types/functions: global `card_blocked` tracks the last successfully applied software block state. `rfkill_set_block()` sends `EC_WLAN_ENTER_RESET` or `EC_WLAN_LEAVE_RESET` via `olpc_ec_cmd()`. `xo1_rfkill_probe()` allocates/registers an `RFKILL_TYPE_WLAN` device, and `xo1_rfkill_remove()` unregisters/destroys it.

Control flow: platform probe creates the rfkill object with `rfkill_ops`. When userspace changes block state, `rfkill_set_block()` skips redundant commands, chooses the EC command for block/unblock, sends it, and updates `card_blocked` only on success. Remove tears down the rfkill object.

State and persistence: only `card_blocked` persists in memory across rfkill operations while the module is loaded. The EC controls actual WLAN reset state; there is no persistent storage.

Dependencies/integration: depends on platform-device registration under alias `platform:xo1-rfkill`, Linux rfkill core, and OLPC EC command support.

Risks: the initial `card_blocked` state is assumed false and not read back from EC, so software and hardware state can be out of sync after boot or failed commands. A single global state is adequate only for one device. EC command failures leave state unchanged and must be surfaced to rfkill callers.

Test signals: rfkill list should show a WLAN switch; blocking/unblocking should issue EC reset commands and affect the card; duplicate state writes should avoid EC traffic; EC failures should propagate; remove should unregister without dangling rfkill entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/xo1-rfkill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/xo15-ebook.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/xo15-ebook.c

Purpose: ACPI input driver for the OLPC XO-1.5 ebook/tablet-mode switch. It reports the firmware `EBK` method state as `SW_TABLET_MODE`.

Important APIs/types/functions: `ebook_device_ids` matches ACPI HID `XO15EBK`. `struct ebook_switch` stores the input device and physical path string. `ebook_send_state()` evaluates ACPI method `EBK` and reports `SW_TABLET_MODE` as the inverse of the returned state. `ebook_switch_notify()` handles ACPI fixed hardware and status notifications. `ebook_switch_add()` allocates/registers the input device and enables wakeup GPE if valid; `ebook_switch_remove()` unregisters it.

Control flow: ACPI add allocates state, matches the HID, sets ACPI device name/class, configures an input device with EV_SW/SW_TABLET_MODE, registers it, immediately sends current state, and enables wakeup if firmware marks the GPE as valid. Notifications and resume both call `ebook_send_state()` to refresh userspace-visible switch state.

State and persistence: runtime state is the allocated input device and path string. The authoritative switch state remains in ACPI firmware. Wakeup enable state is configured through ACPI/device PM and persists until device removal or system power change.

Dependencies/integration: uses ACPI driver framework, ACPI method evaluation, input subsystem switch events, PM sleep resume hook, and ACPI wakeup GPE handling.

Risks: `EBK` failure returns `-EIO` and prevents state update. The driver inverts firmware state, so semantic regressions are easy if firmware meaning is misread. Wakeup GPE is enabled directly when valid, so platforms with incorrect wake metadata may see unwanted wake behavior.

Test signals: initial state should match physical ebook/tablet mode, ACPI notification `0x80` should update `SW_TABLET_MODE`, resume should resend state, unsupported notification types should only debug-log, and wake from ebook switch should work when firmware exposes a valid wake GPE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/xo15-ebook.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/Kconfig

Purpose: top-level Kconfig menu for Linux PM domain drivers in this source tree.

Important APIs/types/functions: declares the `"PM Domains"` menu and sources subdirectory Kconfig files for Actions, Amlogic, Apple, ARM, Broadcom, i.MX, Marvell, MediaTek, Qualcomm, Renesas, Rockchip, Samsung, ST, StarFive, Sunxi, Tegra, T-Head, TI, and Xilinx.

Control flow: no runtime control flow. During kernel configuration it exposes child PM-domain driver symbols and their dependency logic.

State and persistence: configuration choices persist in `.config` and determine which PM-domain providers are built.

Dependencies/integration: pairs with `drivers/pmdomain/Makefile`, which descends into the same subdirectories and builds `core.o`/`governor.o`.

Risks: missing a subdirectory source hides all drivers below it. The ordering is mostly organizational, but bad paths break menuconfig and randconfig.

Test signals: `make olddefconfig`, menuconfig navigation under PM Domains, and randconfig coverage of every sourced subdirectory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/Makefile

Purpose: top-level Kbuild file for PM-domain support.

Important APIs/types/functions: unconditionally descends into PM-domain vendor subdirectories with `obj-y += <dir>/` and builds common `core.o` and `governor.o`.

Control flow: no runtime control flow. Kbuild uses child Makefiles and Kconfig-resolved `obj-*` entries to select built-in or modular objects.

State and persistence: persistent effect is build composition: common generic PM-domain core/governor objects plus enabled provider drivers.

Dependencies/integration: must stay aligned with the top-level Kconfig source list and the directory names under `drivers/pmdomain`.

Risks: stale or missing directory entries break builds for visible Kconfig symbols; building `core.o governor.o` here is central to genpd availability.

Test signals: `make drivers/pmdomain/` and randconfig builds with representative provider symbols enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/actions/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/actions/Kconfig

Purpose: Kconfig fragment for Actions Semiconductor Owl Smart Power System power-domain support.

Important APIs/types/functions: under `ARCH_ACTIONS || COMPILE_TEST`, defines hidden bool `OWL_PM_DOMAINS_HELPER` and user-visible bool `OWL_PM_DOMAINS`. The main symbol depends on `PM`, selects the helper and `PM_GENERIC_DOMAINS`, and describes S500/S700/S900 SPS power gating.

Control flow: no runtime flow. Configuration enables helper and platform provider objects.

State and persistence: symbol choices persist in `.config`.

Dependencies/integration: consumed by `drivers/pmdomain/actions/Makefile`, which builds `owl-sps-helper.o` for the helper and `owl-sps.o` for the provider.

Risks: the helper is exported for reuse, so it must be selected whenever the main driver builds. Missing `PM_GENERIC_DOMAINS` would cause unresolved genpd dependencies.

Test signals: compile with `ARCH_ACTIONS`, compile-test builds, and verifying `CONFIG_OWL_PM_DOMAINS=y` also sets `CONFIG_OWL_PM_DOMAINS_HELPER=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/actions/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/actions/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/actions/Makefile

Purpose: maps Actions Owl PM-domain Kconfig symbols to Kbuild objects.

Important APIs/types/functions: `CONFIG_OWL_PM_DOMAINS_HELPER` builds `owl-sps-helper.o`; `CONFIG_OWL_PM_DOMAINS` builds `owl-sps.o`.

Control flow: none at runtime.

State and persistence: build outputs reflect `.config`.

Dependencies/integration: synchronized with `actions/Kconfig`; `owl-sps.o` calls the helper exported by `owl-sps-helper.o`.

Risks: omitting the helper object would break `owl_sps_set_pg()` linkage; stale names make selected symbols unbuildable.

Test signals: build with helper only and with full `OWL_PM_DOMAINS`, including modular/allbuilt configurations if allowed by the tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/actions/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/actions/owl-sps-helper.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/actions/owl-sps-helper.c

Purpose: shared low-level register helper for Actions Owl Smart Power System power gates.

Important APIs/types/functions: exports `owl_sps_set_pg(void __iomem *base, u32 pwr_mask, u32 ack_mask, bool enable)`. It manipulates `OWL_SPS_PG_CTL` at offset 0, using separate request and acknowledgement masks.

Control flow: the helper reads current control state, returns immediately if ack already equals the requested state, sets or clears the power request bits, writes back, polls every 50 us up to about 5 ms for the ack bits to match, delays 10 us after success, and returns `-ETIMEDOUT` on failure.

State and persistence: no software state. Hardware power-gate and ack bits persist in the SPS register until changed by this or firmware/hardware.

Dependencies/integration: used by `owl-sps.c` and exported GPL for other Actions SPS users. Depends on MMIO access and delay helpers.

Risks: polling assumes ack polarity equals requested enable state and that 5 ms is sufficient. Concurrent writers to the same SPS register could race because this helper has no lock. Mask mistakes can alter unrelated power domains.

Test signals: power on/off each domain and verify ack transitions, timeout behavior on blocked hardware, and no unintended changes to neighboring bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/actions/owl-sps-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/actions/owl-sps.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/actions/owl-sps.c

Purpose: generic PM-domain provider for Actions Semi Owl S500, S700, and S900 Smart Power System power gates.

Important APIs/types/functions: `struct owl_sps_domain_info` describes name, request bit, ack bit, and genpd flags; `struct owl_sps_info` holds SoC domain tables; `struct owl_sps` owns MMIO base and `genpd_onecell_data`; `struct owl_sps_domain` wraps each `generic_pm_domain`. Runtime callbacks are `owl_sps_power_on()` and `owl_sps_power_off()`, both using `owl_sps_set_power()` and `owl_sps_set_pg()`. Probe is `owl_sps_probe()`, registered at `postcore_initcall()`.

Control flow: probe gets match data, allocates a flexible `owl_sps`, maps the SPS register resource with `of_io_request_and_map()`, prepares a onecell genpd provider, initializes each domain from the SoC table, and registers the provider. Genpd callbacks convert domain bit numbers to masks and call the shared helper. S500 has explicit ack bits and some CPU domains marked always-on; S700/S900 tables omit ack bits, leaving ack mask as bit 0 for entries without explicit ack, which is an important hardware-table detail.

State and persistence: per-domain software state is the genpd object plus static table pointer. Hardware state is SPS power-gate bits. No disk persistence.

Dependencies/integration: uses generic PM domains, OF match data, DT power binding indices for S500/S700/S900, early platform-driver registration, and `owl-sps-helper`.

Risks: table correctness is critical: request/ack bits and `GENPD_FLAG_ALWAYS_ON` prevent accidental CPU or fabric shutdown. The driver initializes all domains as powered off from genpd's reference perspective (`pm_genpd_init(..., false)` means not off), but actual hardware may differ. Lack of remove path is expected for early SoC provider but matters for hot-unbind assumptions.

Test signals: DT consumers can resolve each power-domain cell, power transitions return after ack, always-on CPU domains are not shut down, probe runs early enough for dependent devices, and S500/S700/S900 binding indices map to the intended names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/actions/owl-sps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/amlogic/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/amlogic/Kconfig

Purpose: Kconfig menu for Amlogic PM-domain providers.

Important APIs/types/functions: defines `MESON_EE_PM_DOMAINS` for AO/HHI register-controlled Meson Everything-Else domains and `MESON_SECURE_PM_DOMAINS` for secure-monitor controlled A1/C1-family domains. Both select generic PM-domain support and OF provider support; the secure driver depends on `MESON_SM` and `HAVE_ARM_SMCCC`.

Control flow: no runtime flow; selects which Amlogic provider implementation is built.

State and persistence: `.config` controls built-in/module state and defaults to enabled on `ARCH_MESON`.

Dependencies/integration: consumed by `amlogic/Makefile`; dependencies match use of regmap/syscon for EE domains and secure monitor firmware calls for secure domains.

Risks: missing secure monitor dependency would build an unusable secure driver; missing OF/genpd selections would break providers for DT consumers.

Test signals: randconfig with `ARCH_MESON`, compile-test builds, and module names `meson-ee-pwrc`/`meson-secure-pwrc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/amlogic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/amlogic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/amlogic/Makefile

Purpose: Kbuild mapping for Amlogic PM-domain drivers.

Important APIs/types/functions: builds `meson-ee-pwrc.o` for `CONFIG_MESON_EE_PM_DOMAINS` and `meson-secure-pwrc.o` for `CONFIG_MESON_SECURE_PM_DOMAINS`.

Control flow: no runtime flow.

State and persistence: build output follows `.config`.

Dependencies/integration: synchronized with `amlogic/Kconfig`.

Risks: stale object names cause Kconfig-visible drivers not to build.

Test signals: targeted `make drivers/pmdomain/amlogic/` with each symbol enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/amlogic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/amlogic/meson-ee-pwrc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/amlogic/meson-ee-pwrc.c

Purpose: generic PM-domain provider for Amlogic Meson “Everything-Else” domains controlled by AO sleep/isolation registers, HHI memory power registers, resets, and clocks. It supports Meson8/8b/8m2, GXBB, AXG, G12A, and SM1 domain layouts.

Important APIs/types/functions: descriptor types include `meson_ee_pwrc_mem_domain`, `meson_ee_pwrc_top_domain`, `meson_ee_pwrc_domain_desc`, and `meson_ee_pwrc_domain_data`. Runtime state is `meson_ee_pwrc_domain` and `meson_ee_pwrc`. Important callbacks are `meson_ee_pwrc_on()`, `meson_ee_pwrc_off()`, `meson_ee_pwrc_init_domain()`, `meson_ee_pwrc_probe()`, and `meson_ee_pwrc_shutdown()`. Domain tables define VPU, ETH, AUDIO, NNA, ISP, USB, PCIE, and GE2D memory/top domains per SoC.

Control flow: probe gets SoC match data, allocates onecell provider arrays, obtains HHI regmap from the parent syscon and AO regmap from `amlogic,ao-sysctrl`, copies each descriptor, initializes resets/clocks, sets genpd callbacks, detects bootloader-enabled clocked domains, and registers the provider. Power-on clears top sleep bits, clears memory power-down bits, asserts resets, clears isolation, deasserts resets, and enables clocks. Power-off sets top sleep, powers down memory slices, sets isolation, waits if needed, and disables clocks. Shutdown powers off any domain with status callback reporting still on.

State and persistence: software tracks per-domain descriptors, reset arrays, clocks, genpd status, and regmap handles. Hardware state persists in AO and HHI registers and in reset/clock controllers. Bootloader-enabled VPU-style domains can be marked always-on with clocks enabled to keep reference counts coherent.

Dependencies/integration: uses generic PM domains, OF onecell providers, syscon/regmap, reset controller consumers, bulk clock APIs, delay helpers, DT binding indices, and platform driver matching. Consumers reference the provider via power-domain cells in DT.

Risks: power sequencing is hardware-sensitive; wrong ordering of sleep, memory PD, isolation, reset, and clocks can hang display, USB, PCIe, or NNA blocks. Reset and clock counts are warned but tolerated, so bad DT can limp into runtime failures. Bootloader-enabled domains are protected by `GENPD_FLAG_ALWAYS_ON`; changing that risks disabling active display pipelines. Shutdown forcibly powers domains off if status says on, which can affect firmware handoff expectations.

Test signals: probe must find both AO and HHI regmaps; each compatible should expose the expected onecell domain count; VPU on/off should preserve display behavior; clocks and resets should pair cleanly; bootloader-on domains should become always-on; shutdown should not hang; and DT reset/clock count warnings should be treated as board-description test failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/amlogic/meson-ee-pwrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/amlogic/meson-secure-pwrc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/amlogic/meson-secure-pwrc.c

Purpose: secure-monitor backed generic PM-domain provider for newer Amlogic SoCs where power state is controlled through Meson secure firmware calls rather than direct MMIO.

Important APIs/types/functions: `meson_secure_pwrc_domain` wraps a genpd with firmware index and optional parent; `meson_secure_pwrc` owns the domain array, onecell data, and `meson_sm_firmware`; descriptor tables are built with `SEC_PD()` and `TOP_PD()` for A1, A4, A5, C3, S4, S6, S7, S7D, and T7. Runtime callbacks are `meson_secure_pwrc_on()`, `meson_secure_pwrc_off()`, `pwrc_secure_is_off()`, and `meson_secure_pwrc_probe()`.

Control flow: probe locates the global `amlogic,meson-gxbb-sm` secure-monitor node, gets firmware handle, allocates onecell/domain arrays, initializes every named descriptor as a genpd, powers on any always-on domain found off, initializes genpd with firmware-reported off/on state, wires parent-child relationships for descriptors with `parent != PWRC_NO_PARENT`, and registers the onecell provider. Power transitions call `meson_sm_call()` with `SM_A1_PWRC_SET`; status calls use `SM_A1_PWRC_GET`.

State and persistence: software state is the descriptor-derived domain index, flags, parent index, firmware handle, and genpd state. Actual persistence is in secure firmware and power controller hardware. Always-on domains are forced on during probe if firmware reports them off.

Dependencies/integration: depends on Meson secure monitor firmware (`MESON_SM`), ARM SMCCC availability, generic PM domains, DT binding IDs, and OF onecell provider registration. Parent-child genpd hierarchy models T7 subdomains such as DOS/GE2D/MALI/NNA under NIC/MIPI/NNA top domains.

Risks: all hardware control is opaque firmware ABI; failures are collapsed to `-EINVAL` after logging. The driver assumes the secure-monitor node compatible and `SM_A1_PWRC_*` commands work across all listed SoCs. Parent indices must be valid and initialized; incorrect descriptor tables can create broken genpd hierarchies. Always-on annotations protect UART, DMC, SRAM, NIC, ETH wake, DDR, and similar critical blocks.

Test signals: firmware GET/SET calls should succeed for every non-empty descriptor, always-on domains should be on after probe, DT power-domain cells should resolve to correct names, parent subdomains should appear in genpd hierarchy, and consumer drivers should survive suspend/resume and runtime PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/amlogic/meson-secure-pwrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/apple/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/apple/Kconfig

Purpose: Kconfig fragment for Apple SoC PMGR power-state control.

Important APIs/types/functions: defines `APPLE_PMGR_PWRSTATE` under `ARCH_APPLE || COMPILE_TEST`, depending on `PM` and selecting `REGMAP`, `MFD_SYSCON`, `PM_GENERIC_DOMAINS`, and `RESET_CONTROLLER`.

Control flow: no runtime flow; enables Apple PMGR genpd/reset provider.

State and persistence: `.config` controls build inclusion.

Dependencies/integration: consumed by `apple/Makefile` and matches `pmgr-pwrstate.c` use of syscon regmaps, genpd, and reset controller APIs.

Risks: missing reset or regmap selections would break build/link; bool-only configuration means no module build coverage here.

Test signals: compile-test and Apple architecture builds with `CONFIG_APPLE_PMGR_PWRSTATE=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/apple/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/apple/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/apple/Makefile

Purpose: Kbuild mapping for Apple PMGR PM-domain support.

Important APIs/types/functions: builds `pmgr-pwrstate.o` when `CONFIG_APPLE_PMGR_PWRSTATE` is enabled.

Control flow: no runtime flow.

State and persistence: build output follows `.config`.

Dependencies/integration: synchronized with `apple/Kconfig`.

Risks: stale object name would make the Kconfig option ineffective.

Test signals: targeted build with `CONFIG_APPLE_PMGR_PWRSTATE=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/apple/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/apple/pmgr-pwrstate.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/apple/pmgr-pwrstate.c

Purpose: Apple SoC PMGR power-state driver exposing each PMGR pwrstate node as a generic PM domain and reset controller.

Important APIs/types/functions: `struct apple_pmgr_ps` holds device, genpd, reset controller, parent syscon regmap, register offset, and optional minimum state. `apple_pmgr_ps_set()` writes target power state and optionally enables PMGR auto mode; `apple_pmgr_ps_is_active()` detects boot state; `apple_pmgr_ps_power_on/off()` implement genpd callbacks; `apple_pmgr_reset_assert/deassert/reset/status()` implement reset-controller operations; `apple_pmgr_ps_probe()` registers provider, parent domains, and reset controller.

Control flow: probe gets the parent syscon regmap, reads `label` and `reg`, configures IRQ-safe genpd callbacks, applies optional `apple,min-state`, detects active or auto-enabled state, handles `apple,always-on` by powering on if necessary and setting `GENPD_FLAG_ALWAYS_ON`, enables auto-PM for active domains, initializes genpd with current state, registers a simple provider, adds declared parent power domains as genpd subdomains, removes the platform device from regular PM participation, and registers one reset line. Power transitions clear sticky flags, set target state, poll actual state up to 100 us, and optionally enable auto mode. Reset assert disables device access then asserts reset under the genpd spinlock; deassert clears reset and device-disable.

State and persistence: software keeps one domain/reset provider per DT node. Hardware state is the PMGR register containing target/actual states, reset, auto-enable, min-state, parent-off, and sticky clock/power-gated flags. No disk persistence.

Dependencies/integration: depends on DT child nodes below a PMGR syscon, generic PM domains, OF genpd provider/subdomain APIs, regmap polling, and reset-controller framework. Consumers use both `power-domains` and reset phandles with zero reset cells.

Risks: resets only work while powered and clocked; the driver logs but does not prevent reset while off or poweroff with reset active. Poll timeout is short and hardware-sensitive. Parent-domain linking must handle probe deferral correctly. The driver deliberately removes the platform device from regular PM because hierarchy handles power, so changing that can double-manage domains.

Test signals: each DT node with label/reg registers a genpd and reset provider; active boot domains remain active and auto-enabled; always-on domains recover if off at boot; parent subdomain links succeed or defer; reset consumers see assert/deassert/status changes; power state polling reaches requested states without timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/apple/pmgr-pwrstate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/arm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/arm/Kconfig

Purpose: Kconfig fragment for ARM firmware-mediated power and performance domain providers.

Important APIs/types/functions: defines `ARM_SCMI_PERF_DOMAIN`, `ARM_SCMI_POWER_DOMAIN`, and `ARM_SCPI_POWER_DOMAIN`, each depending on the matching firmware protocol or compile-test with OF and selecting `PM_GENERIC_DOMAINS` when PM is enabled.

Control flow: no runtime flow; controls whether SCMI/SCPI genpd providers are built.

State and persistence: `.config` choices determine built-in/module objects.

Dependencies/integration: consumed by `arm/Makefile`; help text documents module names `scmi_perf_domain`, `scmi_pm_domain`, and `scpi_pm_domain`.

Risks: these drivers may be needed early for rootfs devices, so modular configuration can affect boot on some systems. Missing protocol dependencies would produce probe deferral or build errors.

Test signals: protocol-enabled builds, compile-test builds, and boot tests where storage/display/network devices use SCMI/SCPI power domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/arm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/arm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/arm/Makefile

Purpose: Kbuild mapping for ARM SCMI/SCPI PM-domain drivers.

Important APIs/types/functions: maps `CONFIG_ARM_SCMI_PERF_DOMAIN` to `scmi_perf_domain.o`, `CONFIG_ARM_SCMI_POWER_DOMAIN` to `scmi_pm_domain.o`, and `CONFIG_ARM_SCPI_POWER_DOMAIN` to `scpi_pm_domain.o`.

Control flow: no runtime flow.

State and persistence: object inclusion follows `.config`.

Dependencies/integration: synchronized with `arm/Kconfig`.

Risks: stale mapping breaks protocol provider builds.

Test signals: targeted builds for each symbol and module-name checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/arm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/arm/scmi_perf_domain.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/arm/scmi_perf_domain.c

Purpose: SCMI performance-domain provider that exposes firmware performance domains through genpd performance-state APIs and dynamic OPP tables.

Important APIs/types/functions: `struct scmi_perf_domain` wraps `generic_pm_domain` with SCMI perf ops, protocol handle, domain info, and domain ID. `scmi_pd_set_perf_state()` calls firmware `level_set`; `scmi_pd_attach_dev()` adds firmware-provided OPPs; `scmi_pd_detach_dev()` removes dynamic OPPs; `scmi_perf_domain_probe()` creates the provider; `scmi_perf_domain_remove()` tears it down.

Control flow: SCMI bus probe first requires a `#power-domain-cells` property, then obtains SCMI PERF protocol ops, queries domain count, allocates domains and onecell data, initializes each genpd as always-on with firmware OPP/dev-name flags and attach/detach/set-performance callbacks, registers the onecell provider, and stores driver data. Attach adds OPPs only for domains where firmware says performance can be set. Setting performance state rejects state 0 and warns on firmware failure.

State and persistence: per-domain state is firmware metadata and genpd/OPP registrations. Actual performance level state lives in SCMI firmware. Dynamic OPPs live only while devices are attached.

Dependencies/integration: depends on SCMI PERF protocol, genpd performance-state support, PM OPP core, OF onecell provider, and SCMI device matching for protocol `SCMI_PROTOCOL_PERF`.

Risks: the driver returns success for non-settable performance domains while still attaching devices, so consumers must handle lack of performance control. State 0 is invalid, which must match OPP mapping. Probe is skipped silently if the SCMI node is not a provider. Removal assumes registered domains exist only when probe completed.

Test signals: provider registration only with `#power-domain-cells`, correct domain count/names from firmware, dynamic OPP creation/removal on device attach/detach, successful nonzero performance-state changes, and clean removal with all genpds unregistered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/arm/scmi_perf_domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/arm/scmi_pm_domain.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/arm/scmi_pm_domain.c

Purpose: SCMI generic power-domain provider for firmware-controlled on/off power domains.

Important APIs/types/functions: `struct scmi_pm_domain` wraps a genpd with SCMI protocol handle, firmware name, and domain index. `scmi_pd_power()` calls `state_set`; `scmi_pd_power_on/off()` set generic ON/OFF states. `scmi_pm_domain_probe()` builds domains from SCMI POWER protocol; `scmi_pm_domain_remove()` removes provider and genpds.

Control flow: probe gets SCMI POWER ops, reads domain count, allocates arrays, loops over firmware domains, reads each current state, re-sends ON state for domains already on so OSPM ownership is registered with firmware, initializes genpd with `GENPD_FLAG_ACTIVE_WAKEUP` and current off/on state, and registers an OF onecell provider. Remove deletes the provider and removes non-null genpds.

State and persistence: software stores domain index/name and genpd state; actual power state and OSPM ownership are tracked by SCMI firmware. The global `power_ops` pointer is shared by driver instances.

Dependencies/integration: depends on SCMI POWER protocol, generic PM domains, OF provider registration, and SCMI device matching for `SCMI_PROTOCOL_POWER`.

Risks: failed `state_get()` skips a domain and leaves a null onecell slot; consumers for that index will fail. Global `power_ops` is simple but not instance-isolated. Reasserting ON ownership at probe is important; removing it could let firmware turn off a boot-enabled domain unexpectedly.

Test signals: firmware domain count and names appear in logs, existing-on domains remain available after probe, power on/off calls produce SCMI state changes, null-slot behavior is acceptable for failed state reads, and provider removal cleans all initialized genpds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/arm/scmi_pm_domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/arm/scpi_pm_domain.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/arm/scpi_pm_domain.c

Purpose: legacy SCPI generic power-domain provider for SCP firmware controlled device power states.

Important APIs/types/functions: `struct scpi_pm_domain` wraps genpd with `scpi_ops` and domain ID. `enum scpi_power_domain_state` maps ON to 0 and OFF to 3. `scpi_pd_power()` sets and verifies state; `scpi_pd_power_on/off()` are genpd callbacks; `scpi_pm_domain_probe()` registers a onecell provider from DT `num-domains`.

Control flow: platform probe obtains global SCPI ops, validates DT node and firmware power-state callbacks, reads `num-domains`, allocates domain arrays, creates a named genpd for each index, initializes all as off from genpd's reference-count perspective regardless of firmware state, and registers the onecell provider.

State and persistence: software state is per-domain index and SCPI ops pointer. Firmware owns actual power state. Genpd intentionally starts off to avoid Linux turning off firmware-enabled domains it did not request.

Dependencies/integration: depends on legacy SCPI protocol ops, OF platform matching `arm,scpi-power-domains`, DT `num-domains`, and generic PM domains.

Risks: SCPI power state values are not fully standardized; this driver hardcodes ON=0 and OFF=3. `of_genpd_add_provider_onecell()` return value is ignored, so provider registration failures are not propagated. Verification returns a boolean mismatch as an integer error, which may not preserve firmware error detail after set succeeds but get disagrees.

Test signals: probe defers until SCPI ops are ready, DT `num-domains` creates the expected slots, power set/get works with firmware state values, consumers resolve all indices, and provider registration failures should be caught by boot logs or follow-up checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/arm/scpi_pm_domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/Kconfig

Purpose: Kconfig menu for Broadcom PM-domain providers.

Important APIs/types/functions: defines `BCM2835_POWER`, `RASPBERRYPI_POWER`, `BCM_PMB`, and `BCM63XX_POWER`. Symbols select generic PM domains as needed; BCM2835 also selects reset controller, Raspberry Pi firmware domains require built-in `RASPBERRYPI_FIRMWARE=y`, BCM PMB targets BCMBCA, and BCM63xx targets BMIPS.

Control flow: no runtime flow; chooses which Broadcom provider implementations are built.

State and persistence: `.config` controls build inclusion and defaults for matching architectures.

Dependencies/integration: consumed by `bcm/Makefile`; help text warns that Raspberry Pi firmware-owned domains must use the firmware driver instead of direct BCM2835 PM register access.

Risks: selecting the wrong provider for firmware-owned Raspberry Pi domains can conflict with firmware. Built-in firmware dependency for `RASPBERRYPI_POWER` is intentional for early availability.

Test signals: architecture defconfig coverage, compile-test builds, and boot tests on BCM2835/Raspberry Pi/BCMBCA/BMIPS platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/Makefile

Purpose: Kbuild mapping for Broadcom PM-domain drivers.

Important APIs/types/functions: maps `CONFIG_BCM_PMB` to `bcm-pmb.o`, `CONFIG_BCM2835_POWER` to `bcm2835-power.o`, `CONFIG_BCM63XX_POWER` to `bcm63xx-power.o`, and `CONFIG_RASPBERRYPI_POWER` to `raspberrypi-power.o`.

Control flow: no runtime flow.

State and persistence: build output follows `.config`.

Dependencies/integration: synchronized with `bcm/Kconfig`.

Risks: stale object mapping prevents selected provider from building.

Test signals: targeted builds with each Broadcom PM-domain symbol enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/bcm-pmb.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/bcm-pmb.c

Purpose: Broadcom PMB (Power Management Bus) genpd provider for selected BCMBCA devices such as BCM4908 PCIe/USB and BCM63138 SATA.

Important APIs/types/functions: `struct bcm_pmb` stores MMIO base, endianness, spinlock, and onecell data; `bcm_pmb_pd_data` maps names/IDs to PMB bus/device addresses; `bcm_pmb_pm_domain` wraps genpd. Low-level accessors `bcm_pmb_bpcm_read/write()` call `bpcm_rd/wr()` with locking and endian conversion. Power helpers control BPCM zones/devices and SATA-specific registers; genpd callbacks are `bcm_pmb_power_on/off()`.

Control flow: probe maps PMB registers, initializes locking/endian mode, obtains the SoC table, sizes onecell slots by max binding ID, creates a genpd for each table entry initialized as off, and registers the provider. PCIe domains power zone 0 on/off. USB powers on all zones based on `BPCM_CAP_NUM_ZONES` and powers off device via zone 0. SATA powers zone 0 and toggles miscellaneous/SR control, but has no power-off implementation in the switch.

State and persistence: software state is static domain mapping and a spinlock protecting PMB transactions. Hardware state persists in BPCM zone control, power request, reset, memory, and SATA registers. No filesystem persistence.

Dependencies/integration: depends on `reset/bcm63xx_pmb.h` BPCM accessors, DT binding IDs from `bcm-pmb.h`, OF match data, generic PM domains, MMIO, endianness from DT, and built-in platform driver registration.

Risks: BPCM transactions are serialized only within this driver; external PMB users need compatible locking. Endianness mistakes corrupt control words. SATA power-off is unsupported and returns `-EINVAL` through the default path. USB all-zone power-on trusts capability bits. Incorrect bus/device IDs can affect unrelated SoC blocks.

Test signals: DT consumers resolve PCIe/USB/SATA indices, BPCM reads/writes succeed in both endian modes, PCIe zone state changes, USB powers all zones, SATA initializes correctly, unsupported power-off is handled by consumers, and time-sensitive devices enumerate after genpd on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/bcm-pmb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/bcm2835-power.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/bcm2835-power.c

Purpose: direct PM-register power-domain and reset-controller driver for Broadcom BCM2835-family multimedia/display domains, with ASB bridge handling and BCM2711/RPiVid differences.

Important APIs/types/functions: `struct bcm2835_power` owns PM, ASB, RPiVid ASB bases, onecell data, domain array, and reset controller. `struct bcm2835_power_domain` wraps genpd with domain ID and optional clock. Core helpers include `bcm2835_power_power_on/off()` for PM_GRAFX/IMAGE gates, `bcm2835_asb_control()`, `bcm2835_asb_power_on/off()`, `bcm2835_power_pd_power_on/off()`, `bcm2835_init_power_domain()`, reset ops `bcm2835_reset_reset()` and `bcm2835_reset_status()`, and `bcm2835_power_probe()`.

Control flow: probe obtains PM register bases from the parent `bcm2835_pm` MFD, validates ASB bridge IDs, allocates onecell data, initializes all named domains as initially off, adds parent-child dependencies such as image to H264/ISP/USB/CAM and grafx to V3D, registers reset controller, and registers provider on the parent OF node. Power-on dispatch handles raw PM gates with inrush ramp and memory repair, ASB-backed subdomains with clock/reset/bridge sequencing, and simple LDO/control domains for USB, DSI, CCP2TX, and HDMI. Power-off reverses each path. Reset ops power-cycle V3D/H264/ISP subdomains and report reset-line status bits.

State and persistence: software keeps genpd status, optional clocks, domain hierarchy, and reset controller state. Hardware state persists in PM password-protected registers, ASB bridge stop/ack bits, reset bits, LDO controls, and clock framework state. The driver treats domains as off at boot for Linux reference-count ownership even if firmware left hardware on.

Dependencies/integration: depends on BCM2835 PM MFD parent data, generic PM domains, reset-controller framework, optional clocks named by domain, DT binding indices, MMIO polling, and platform consumers for V3D, H264, ISP, USB, camera, DSI, CCP2TX, and HDMI.

Risks: direct PM access must not be used for domains owned by Raspberry Pi firmware. The inrush loop and memory-repair polling are timing-sensitive. ASB enable/disable ordering is critical to avoid AXI hangs. BCM2711/RPiVid paths intentionally skip legacy power gates. Some named domains such as CAM0/CAM1 exist in the xlate table but lack explicit switch cases, so consumers must match implemented domains or receive `-EINVAL`.

Test signals: ASB ID validation succeeds, all provider indices resolve, V3D/H264/ISP resets power-cycle correctly, USB/HDMI/DSI/CCP2TX register sequences enable hardware, parent-child genpd dependencies hold, memory repair reaches `PM_MRDONE`, and Raspberry Pi firmware-owned systems use `raspberrypi-power` instead when required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/bcm2835-power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/bcm63xx-power.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/bcm63xx-power.c

Purpose: simple MMIO bitmask power-domain controller for BCM6318, BCM6328, BCM6362, and BCM63268 SoCs.

Important APIs/types/functions: `struct bcm63xx_power` holds the register base, spinlock, domain objects, and onecell data; `struct bcm63xx_power_dev` wraps genpd with bit mask; `struct bcm63xx_power_data` maps domain name, bit, and flags. Runtime helpers are `bcm63xx_power_get_state()`, `bcm63xx_power_set_state()`, `bcm63xx_power_on/off()`, and `bcm63xx_power_probe()`.

Control flow: probe maps the single power-control register, selects the compatible table, calculates onecell size from the highest bit, allocates domain arrays, reads each domain's current state where a cleared bit means on, initializes genpd with that state and flags, stores each domain at its binding bit index, initializes the spinlock, and registers the onecell provider. Power on clears the domain bit; power off sets it under the spinlock.

State and persistence: software state is one genpd per table entry and a spinlock for read-modify-write serialization. Hardware state is the power-control register. Always-on flags protect rails or core domains such as LDOs, MIPS, peripheral, or pad power.

Dependencies/integration: uses DT binding IDs for BCM6318/6328/6362/63268, OF match data, generic PM domains, MMIO, and built-in platform registration.

Risks: onecell indices are sparse by bit number; consumers must use binding IDs, not compact table order. `is_on` can be uninitialized if `bcm63xx_power_get_state()` failed before `pm_genpd_init()`, though masks are always set for table entries. Raw MMIO access lacks endianness abstraction. Wrong always-on flags can shut down CPU/peripheral rails.

Test signals: each compatible reports expected domain count, power register bits toggle correctly, always-on domains are not disabled, sparse xlate slots resolve as intended, and concurrent domain toggles preserve unrelated bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/bcm63xx-power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/raspberrypi-power.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/raspberrypi-power.c

Purpose: Raspberry Pi firmware-mediated generic PM-domain provider. It controls domains through mailbox firmware properties rather than direct PM registers, including compatibility with the old firmware power-state interface for USB.

Important APIs/types/functions: `struct rpi_power_domain` wraps genpd with firmware domain ID, old/new interface flag, and firmware handle. `struct rpi_power_domains` owns onecell data and all domains. `rpi_firmware_set_power()` sends `RPI_FIRMWARE_SET_POWER_STATE` or `RPI_FIRMWARE_SET_DOMAIN_STATE`; `rpi_domain_on/off()` are genpd callbacks; `rpi_has_new_domain_support()` probes new interface support; `rpi_init_power_domain()` and `rpi_init_old_power_domain()` populate domains; `rpi_power_probe()` registers the provider.

Control flow: probe allocates provider data, obtains the firmware phandle and firmware handle, detects whether the new domain-state interface responds, initializes new-interface domains only when supported, always initializes USB with the old interface, then registers an OF onecell provider. Genpd callbacks build a two-word packet of firmware domain and boolean state and call the chosen mailbox tag.

State and persistence: software tracks firmware handle, per-domain firmware IDs, old/new mode, and genpd reference state. Domains are intentionally initialized as off from Linux's perspective because firmware may already keep hardware on, and Linux should only release references it acquired. Firmware/hardware owns actual persistent state.

Dependencies/integration: depends on built-in Raspberry Pi firmware driver, OF firmware phandle, generic PM domains, DT binding indices from `raspberrypi-power.h`, and platform consumers for I2C, HDMI, V3D, ISP, camera, DSI, USB, ARM, and media blocks.

Risks: firmware unknown-tag behavior requires sentinel detection; if detection is wrong, new-interface domains may be absent or miscontrolled. USB uses the old interface deliberately for compatibility. Firmware calls can fail asynchronously with platform firmware state. Direct BCM2835 PM driver must not race firmware ownership for the same domain.

Test signals: provider probes only with a valid firmware node, new-interface detection changes which domains are registered, USB power works on old firmware, mailbox set calls succeed for each consumer domain, and Linux genpd refcounts do not power off firmware-owned domains that Linux never enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/raspberrypi-power.c -->
