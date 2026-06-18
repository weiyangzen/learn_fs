# subset-b-001028 research

Grouped research for ACPI SMBus host controller, namespace scanning, sleep, SPCR, sysfs, table, thermal, tiny power button, and utility sources. Each section preserves the source path and is bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/sbshc.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/sbshc.c

## Purpose

This file implements the ACPI Smart Battery System SMBus host-controller driver for devices matching `ACPI0001` and `ACPI0005`. It exposes small exported SMBus read/write and alarm-callback APIs used by smart battery support while hiding the transport details of the ACPI Embedded Controller query and register window.

## Important APIs, types, and functions

The private `struct acpi_smb_hc` stores the backing `struct acpi_ec`, a transaction mutex, wait queue, EC register offset, EC query bit, alarm callback/context, and a `done` flag. `union acpi_smb_status` decodes the host-controller status byte into status, alarm, and done bits. `enum acpi_smb_status_codes` and `enum acpi_smb_offset` define status values and offsets inside the EC operation region. Exported APIs are `acpi_smbus_read()`, `acpi_smbus_write()`, `acpi_smbus_register_callback()`, and `acpi_smbus_unregister_callback()`. The platform-driver entry points are `acpi_smbus_hc_probe()` and `acpi_smbus_hc_remove()`.

## Control flow

Probe retrieves the ACPI companion, evaluates `_EC`, allocates and initializes `struct acpi_smb_hc`, derives the EC offset from the high byte and the EC query bit from the low byte, and registers `smbus_alarm()` with `acpi_ec_add_query_handler()`. A transaction takes `hc->lock`, verifies the protocol register is idle, writes command/data/address/protocol registers, waits up to one second for `hc->done`, and reads response bytes for read protocols. EC query handling enters `smbus_alarm()`, reads status, completes the wait on successful done status, clears alarm status, filters alarms to SBS charger/manager/battery addresses, and schedules `acpi_smbus_callback()` through `acpi_os_execute()`.

## State and persistence

Runtime state is per platform device and is freed at remove. Transaction serialization is by mutex; completion is via wait queue and `hc->done`. Callback state is mutable under the same mutex and unregister waits for pending ACPI OS callbacks to complete. EC registers hold transient firmware/device state; no persistent kernel configuration is written.

## Dependencies and integration points

The driver depends on the ACPI EC core (`ec_read()`, `ec_write()`, query handlers), ACPI platform-device matching, ACPICA async execution, and the public declarations in `sbshc.h`. It integrates with smart battery code through exported GPL symbols and with the ACPI device model through `module_platform_driver()`.

## Risks

The transaction path ignores individual EC write failures after the initial protocol read, so fault diagnosis can be coarse. Timeout handling depends on firmware delivering the EC query reliably. Callback unregister must remain synchronized with queued ACPI notification work to avoid use-after-free. Misparsing `_EC` would point at the wrong EC register window or query bit.

## Test signals

Useful signals include module build coverage, ACPI platform probing for `ACPI0001`/`ACPI0005`, successful smart-battery SMBus read/write protocols, timeout behavior when no completion query arrives, alarm callback delivery for SBS charger/manager/battery addresses, and remove/unregister tests with pending notify work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/sbshc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/sbshc.h -->
# sources/distributed-fs/ceph-client/drivers/acpi/sbshc.h

## Purpose

This header is the small public contract for the ACPI SBS SMBus host-controller driver. It lets smart-battery code refer to SMBus protocol IDs, well-known SBS device addresses, the opaque host-controller object, and the exported read/write/callback functions without depending on the driver's private EC implementation.

## Important APIs, types, and functions

`struct acpi_smb_hc` is forward-declared as an opaque handle. `enum acpi_smb_protocol` defines ACPI SMBus protocol values for quick, byte, word, block, process-call, and block-process-call operations. `enum acpi_sbs_device_addr` defines charger, manager, and battery addresses. `smbus_alarm_callback` is the callback signature. The prototypes are `acpi_smbus_read()`, `acpi_smbus_write()`, `acpi_smbus_register_callback()`, and `acpi_smbus_unregister_callback()`.

## Control flow

The header has no executable control flow. Callers obtain or receive an `acpi_smb_hc *` from the SBS/HC integration path, issue protocol-specific reads or writes, and optionally register an alarm callback that `sbshc.c` dispatches from EC query context.

## State and persistence

No state is defined here beyond compile-time enum values and function types. The opaque pointer deliberately keeps lock, wait queue, EC offset, query bit, and callback storage private to `sbshc.c`.

## Dependencies and integration points

The declarations require ACPI/Linux integer types such as `u8` from included kernel headers in users. This header is included by `sbshc.c` and smart battery clients that need ACPI SBS transport access.

## Risks

Protocol enum values are ABI-like within the driver family and must stay aligned with the ACPI SMBus host-controller protocol register. Address enum values are 7-bit SBS addresses; callers must not pass already-shifted bus addresses because `sbshc.c` shifts the address when writing the EC address register.

## Test signals

Compile users against the header, exercise each protocol value through `acpi_smbus_read()`/`write()`, and verify callback registration/unregistration remains type-correct for smart battery users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/sbshc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/scan.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/scan.c

## Purpose

`scan.c` turns ACPI namespace nodes into Linux `struct acpi_device` objects, attaches ACPI scan handlers and regular device drivers, coordinates hotplug/eject, tracks dependency deferral, and performs ACPI-specific DMA/IOMMU and resource setup. It is one of the core files connecting ACPICA namespace data to the Linux driver model.

## Important APIs, types, and functions

Global state includes `acpi_dep_list`, `acpi_scan_lock`, `acpi_scan_handlers_list`, `acpi_device_lock`, `acpi_wakeup_device_list`, the hotplug context lock, and a deferred system-device resource list. Exported scan/lifetime APIs include `acpi_scan_lock_acquire()`, `acpi_scan_lock_release()`, `acpi_initialize_hp_context()`, `acpi_fetch_acpi_dev()`, `acpi_get_acpi_dev()`, `acpi_device_hid()`, `acpi_bus_scan()`, `acpi_bus_trim()`, `acpi_bus_register_early_device()`, dependency helpers, DMA helpers, and reconfiguration notifier registration. Key internal flows are `acpi_add_single_object()`, `acpi_bus_check_add()`, `acpi_bus_attach()`, `acpi_scan_postponed()`, and `acpi_device_hotplug()`.

## Control flow

Initialization in `acpi_scan_init()` registers ACPI subsystem scan handlers, handles STAO/SPCR UART hiding, applies masked GPE settings, then scans from `ACPI_ROOT_OBJECT` under `acpi_scan_lock`. `acpi_bus_scan()` performs a two-pass walk: first it creates devices without unmet dependencies and records dependency-blocked branches, then it initializes MIPI CSI-2 software nodes, attaches created devices, and scans postponed branches. Device creation initializes PNP IDs, status, properties, flags, power/wakeup data, DMA coherency, and Linux device registration. Attachment evaluates `_EJD`, status, readiness, EC opregions, scan handlers, driver binding, platform-device default enumeration, and child recursion. Hotplug events run under both device-hotplug and ACPI scan locks, map ACPI notify codes to bus/device checks or eject, offline physical devices, detach handlers/drivers, evaluate `_LCK`/`_EJ0`, post `_OST`, and rescan if needed.

## State and persistence

ACPI device objects are dynamically allocated, attached to namespace handles with `acpi_attach_data()`, reference-counted through the Linux device model, and invalidated with `INVALID_ACPI_HANDLE` during namespace deletion. Bus ID allocation is tracked with per-HID IDAs. Wake-capable devices are linked into `acpi_wakeup_device_list`. `_DEP` records persist in `acpi_dep_list` until suppliers clear them or postponed scanning marks them for deletion. Power resource lists, PNP IDs, software-node properties, and physical-node links are owned by each `struct acpi_device` and released through `acpi_device_release()`.

## Dependencies and integration points

This file integrates with ACPICA namespace walking/evaluation, Linux device core, platform and auxiliary buses, ACPI power resources, EC opregions, dock/container/memory/processor/PCI init, MIPI DisCo for Imaging, IORT/RIMT/VIOT IOMMU configuration, DMA mapping, sysfs hotplug profiles, and ACPI reconfiguration notifiers. It also consumes `sleep.h` globals for wakeup device lists and power-resource resume.

## Risks

The highest-risk areas are lock ordering (`acpi_scan_lock`, device hotplug lock, dependency lock, physical-node lock), asynchronous deletion of namespace-backed devices, dependency deferral races, and hotplug eject rollback. Enumeration policy is full of platform exceptions: SPCR/STAO UART hiding, serial-bus slaves enumerated by parents, Apple property-based bus hints, ACPI video auxiliary devices, and ignored/honored `_DEP` HIDs. DMA/IOMMU setup intentionally ignores most IOMMU errors except probe deferral; changing that can break boot on partially described firmware.

## Test signals

Signals include boot-time ACPI namespace enumeration, hotplug bus/device/eject events with `_OST` status, dependency deferral and supplier-clear ordering, driver binding for scan-handler and platform-device paths, ACPI wakeup list population, DMA range parsing from `_DMA`, IOMMU probe deferral behavior, SPCR UART hiding when STAO requests it, and resource reservation after PCI BAR claiming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/sleep.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/sleep.c

## Purpose

`sleep.c` implements ACPI system sleep, hibernation, s2idle, and power-off integration. It maps Linux PM states to ACPI S-states, prepares firmware through ACPI methods and wake vectors, manages ACPI wake devices and GPEs, handles NVS save/restore quirks, and registers platform suspend/hibernation/sys-off operations.

## Important APIs, types, and functions

Important globals include `acpi_no_s5`, `sleep_states[]`, `acpi_target_sleep_state`, `pwr_btn_event_pending`, NVS and old-ordering quirk booleans, `s2idle_wakeup`, saved BM_RLD state, and hibernation FACS signature storage. Exported or externally used functions include `acpi_sleep_state_supported()`, `acpi_target_system_state()`, `acpi_nvs_nosave()`, `acpi_nvs_nosave_s3()`, `acpi_old_suspend_ordering()`, `acpi_sleep_no_blacklist()`, s2idle callbacks, `acpi_s2idle_wakeup()`, and `acpi_sleep_init()`. Platform PM callback tables define suspend, old suspend, s2idle, hibernation, and old hibernation behavior.

## Control flow

`acpi_sleep_init()` applies DMI quirks, marks S0, initializes syscore BM_RLD preservation, registers suspend and hibernation ops if ACPI supports those S-states, registers S5 sys-off handlers, prints supported states, and registers a reboot notifier for `_TTS`. Suspend begins by allocating NVS storage if required, checking sleep-state support, setting firmware suspend mode, calling `_TTS`, and taking `acpi_scan_lock`. Preparation sets the S3 wake vector when needed, enables wake devices, calls `acpi_enter_sleep_state_prep()`, disables GPEs, blocks EC transactions, and saves NVS. Enter executes S1 directly or calls architecture low-level S3 code, restores SCI/GPE programming, handles fixed power-button wake status, unblocks EC transactions, and restores NVS. Finish disables wake devices, calls ACPI leave-sleep, clears waking vector, resumes power resources, and emits a delayed power-button wakeup event. s2idle arms SCI wake, enables wake GPEs, differentiates fixed-event/custom-handler/non-EC/EC wake sources, rearms SCI if needed, then restores runtime GPE and EC state.

## State and persistence

Sleep support is initialized once and records supported ACPI states in `sleep_states[]`. The current target state is global across each PM transition and reset to S0 in finish/end paths. NVS memory snapshots are temporary per suspend/hibernate cycle. DMI and kernel command-line settings persist for the boot. Hibernation records FACS hardware signature for warning or swsusp validation. s2idle tracks whether ACPI wake configuration is armed.

## Dependencies and integration points

The file depends on ACPICA sleep methods/registers, architecture wakeup code (`acpi_suspend_lowlevel`, wakeup address), Linux suspend/hibernation/s2idle/sys-off frameworks, EC transaction blocking, GPE/event management, DMI quirks, reboot notifiers, syscore operations, and ACPI power-resource resume from `sleep.h`/power code.

## Risks

Ordering is critical: `_TTS`, `_PTS`/sleep prep, device suspend, GPE disabling, EC blocking, and NVS save/restore all interact with firmware expectations. Old-ordering and NVS DMI quirks are bug-compatibility paths and can regress specific machines if changed. s2idle wake detection must avoid treating stale SCI/EC activity as a real wake or losing genuine wakeups. Failure paths must release `acpi_scan_lock` and reset target state.

## Test signals

Test S1/S3 suspend-resume, s2idle cycles, S4 hibernation and restore, S5 poweroff, reboot prepare `_TTS`, DMI quirk coverage, NVS save/restore command-line modes, fixed power-button wake event generation, SCI/GPE wake source handling, EC transaction blocking/unblocking, and unsupported S-state reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/sleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/sleep.h -->
# sources/distributed-fs/ceph-client/drivers/acpi/sleep.h

## Purpose

This internal header shares ACPI sleep and wake coordination declarations between the sleep implementation and other ACPI core files. It exposes wake-device list locks, power-resource resume, waking-vector setup, and s2idle hooks without exporting the full implementation details of `sleep.c`.

## Important APIs, types, and functions

The header declares `acpi_enable_wakeup_devices()`, `acpi_disable_wakeup_devices()`, `acpi_check_wakeup_handlers()`, `acpi_wakeup_device_list`, `acpi_device_lock`, `acpi_resume_power_resources()`, `acpi_set_waking_vector()`, all ACPI s2idle callbacks, and `acpi_s2idle_setup()`. It also exposes `acpi_sleep_default_s3`, with a compile-time default of true when `CONFIG_ACPI_SLEEP` is disabled.

## Control flow

There is no runtime control flow except the inline `acpi_set_waking_vector()`, which forwards a 32-bit wakeup address to `acpi_set_firmware_waking_vector()` with a zero 64-bit vector. Callers in sleep, scan, and wakeup code use the declarations to prepare and tear down wake state around PM transitions.

## State and persistence

The header declares, but does not allocate, the wakeup device list and ACPI device lock. `acpi_sleep_default_s3` reflects either runtime DMI/boot policy from `sleep.c` or a constant fallback when sleep support is absent.

## Dependencies and integration points

It integrates ACPI scan/wakeup code with the PM implementation. The declarations depend on ACPICA types such as `acpi_status` and Linux list/mutex definitions included by consumers.

## Risks

Because this is an internal contract, signature drift must be synchronized with `sleep.c`, wakeup-device code, and scan/power-resource users. The inline waking-vector wrapper is architecture-sensitive; changing its argument handling can break S3 resume.

## Test signals

Build coverage under `CONFIG_ACPI_SLEEP`, `CONFIG_SUSPEND`, and reduced PM configurations is the main signal, plus suspend/resume tests that validate wakeup device enablement and firmware waking-vector setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/sleep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/spcr.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/spcr.c

## Purpose

`spcr.c` parses the ACPI Serial Port Console Redirection table and turns it into Linux early console and preferred console configuration. It also detects UART-specific firmware errata for Qualcomm QDF2400/QDF2432 PL011-compatible hardware and APM/HPE X-Gene 16550-compatible UARTs.

## Important APIs, types, and functions

The exported global `qdf2400_e44_present` informs the PL011 driver about the Qualcomm busy-bit erratum. `qdf2400_erratum_44_present()` checks SPCR OEM fields for affected Qualcomm SoCs. `xgene_8250_erratum_present()` checks OEM fields for X-Gene 16550 register alignment issues. The public init function is `acpi_parse_spcr(bool enable_earlycon, bool enable_console)`.

## Control flow

`acpi_parse_spcr()` exits if ACPI is disabled or the SPCR table is missing. It derives `iotype` from the GAS address-space and access-width fields, maps the SPCR interface type to a console driver name (`pl011`, `uart`, or `sbi`), derives baud rate from precise baud rate or the encoded baud-rate field, applies Qualcomm and X-Gene errata overrides, formats a static console option string, optionally calls `setup_earlycon()`, optionally calls `add_preferred_console()`, and releases the table with `acpi_put_table()`.

## State and persistence

The console option buffer is static init storage. `qdf2400_e44_present` persists after parsing so later UART probing can apply the workaround even if the console itself is not using SPCR. No ACPI table data is retained after `acpi_put_table()`.

## Dependencies and integration points

The file depends on ACPICA table access, ACPI DBG2/SPCR constants, Linux console and earlycon registration, serial core naming conventions, and UART drivers that consume the chosen names and erratum flag.

## Risks

Wrong interface mapping or iotype selection can make early console unusable, which is especially costly for bring-up and headless systems. Access-width validation must remain conservative around broken firmware. Erratum detection is OEM-field based and may miss new affected revisions or overmatch if firmware reuses IDs incorrectly.

## Test signals

Boot with SPCR-specified PL011, 16550, SBSA, BCM2835, and RISC-V SBI consoles; verify earlycon and preferred console strings; test unsupported interface/baud paths; confirm QDF2400/QDF2432 and X-Gene erratum platforms select the expected workaround behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/spcr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/sysfs.c

## Purpose

`sysfs.c` builds the ACPI userspace sysfs interface. It exposes ACPICA debug and trace parameters, ACPI table binary files, selected raw table data regions, interrupt/GPE counters and controls, the ACPI preferred PM profile, and hotplug profile controls.

## Important APIs, types, and functions

Under `CONFIG_ACPI_DEBUG`, it defines debug-layer/level descriptors and trace parameter setters/getters. Table exposure uses `struct acpi_table_attr`, `struct acpi_data_attr`, `acpi_table_show()`, `acpi_table_attr_init()`, `acpi_sysfs_table_handler()`, and `acpi_tables_sysfs_init()`. Raw data support handles BERT and CCEL regions through `acpi_data_show()`. Interrupt statistics use `struct event_counter`, `acpi_global_event_handler()`, `counter_show()`, `counter_set()`, `acpi_gpe_apply_masked_gpes()`, and `acpi_irq_stats_init()`. Hotplug profile support is provided by `acpi_sysfs_add_hotplug_profile()`. Initialization entry is `acpi_sysfs_init()`.

## Control flow

Debug parameter reads format current ACPICA bitmasks; writes update ACPICA global debug state and trace method selection while temporarily disabling tracing. Table sysfs init creates `/sys/firmware/acpi/tables`, `data`, and `dynamic`, iterates existing ACPI tables by index, creates binary attributes with instance suffixes as needed, and emits kobject events. Dynamic table installs create entries under `dynamic`. Interrupt stats initialization allocates counters and attributes for all GPEs, fixed events, SCI totals, and error counters, then installs a global ACPI event handler. Counter writes can reset totals, enable/disable/clear/mask/unmask GPEs, enable/disable/clear fixed events, or set counts. `acpi_sysfs_init()` also creates hotplug and `pm_profile` attributes.

## State and persistence

Sysfs kobjects and attribute lists persist for the lifetime of the ACPI core. Table attributes reference ACPICA tables by signature/instance at read time rather than copying table contents. Raw BERT/CCEL attributes map physical memory on each read. Interrupt counters are in memory and resettable through sysfs. Boot parameter `acpi_mask_gpe=` stores an init bitmap that is applied during scan initialization.

## Dependencies and integration points

This file integrates with ACPICA debug globals, ACPICA table manager and dynamic table events, ACPI OS memory mapping, GPE/fixed-event APIs, the global `acpi_kobj`, scan hotplug profiles, kernel parameter infrastructure, and the lockdown/table-upgrade paths indirectly through table visibility.

## Risks

Sysfs layout is a user ABI. Table instance naming must avoid collisions and respect ACPICA reference lifetimes. Raw physical data reads must validate size/address and map only the requested firmware-defined regions. Interrupt control writes can affect system wake and event delivery; invalid handler/status handling must remain strict. Trace method name storage uses a fixed early-boot buffer and requires careful length checks.

## Test signals

Verify table files under `/sys/firmware/acpi/tables`, dynamic table install visibility, BERT/CCEL data reads, ACPICA debug/trace parameter read-write behavior, GPE/fixed-event counter increments, sysfs enable/disable/clear/mask/unmask operations, `acpi_mask_gpe=` boot behavior, hotplug profile creation, and rejected `force_remove=1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/tables.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/tables.c

## Purpose

`tables.c` provides early ACPI table discovery, parsing helpers, MADT entry logging, initrd/builtin ACPI table upgrade support, custom DSDT override hooks, table memory reservation, and boot parameters controlling MADT instance, checksum verification, and 32-bit FADT addresses.

## Important APIs, types, and functions

Core parsing APIs include `acpi_table_print_madt_entry()`, `acpi_table_parse_entries_array()`, `acpi_table_parse_cedt()`, `acpi_table_parse_entries()`, `acpi_table_parse_madt()`, and `acpi_table_parse()`. Early table lifecycle APIs are `acpi_table_upgrade()`, `acpi_os_physical_table_override()`, `acpi_os_table_override()`, `acpi_locate_initial_tables()`, `acpi_reserve_initial_tables()`, `acpi_table_init_complete()`, and `acpi_table_init()`. State includes `initial_tables[]`, `acpi_apic_instance`, `acpi_verify_table_checksum`, and, when enabled, initrd table storage metadata.

## Control flow

Early boot may call `acpi_table_upgrade()` to scan initrd or builtin initramfs files under `kernel/firmware/acpi/`, validate recognized signatures, length, and checksum, reject overrides under lockdown, allocate low physical memory, reserve it, and copy tables in early-mapped chunks. ACPICA calls the physical override hook to replace matching tables only when signature/OEM IDs match and revision increases; remaining non-RSDT/XSDT tables can be installed as additional tables. `acpi_locate_initial_tables()` configures checksum validation and calls `acpi_initialize_tables()`. `acpi_table_init_complete()` installs initrd tables and checks for multiple MADTs. Parse helpers fetch a table instance, call common subtable parsing or a whole-table handler, and release the table.

## State and persistence

Initial table descriptors are `__initdata` used during early boot. Upgraded tables are copied into reserved physical memory and persist as firmware table replacements/additions. The bitmap `acpi_initrd_installed` prevents the same initrd table from being both an override and an install. Kernel taint records unsafe custom DSDT override. `acpi_apic_instance` and checksum/FADT boot-parameter settings persist for boot-time parsing.

## Dependencies and integration points

The file depends on ACPICA table management, memblock and architecture memory reservation, early initrd/cpio scanning, security lockdown policy, kmemleak, ACPI library export macros, APIC/MADT users, and architecture/platform code that registers ACPI probe entries.

## Risks

This is early boot code with little recovery room. Incorrect table validation, copy sizing, or physical reservation can corrupt memory or install bad firmware descriptions. Override policy is security-sensitive and must honor lockdown. MADT instance selection affects interrupt controller topology. Disabling checksum verification is intentional for early mapping limits, but forcing verification can expose firmware checksum defects.

## Test signals

Exercise boot with normal firmware tables, multiple MADT instances, `acpi_apic_instance=`, `acpi_force_table_verification`, `acpi_force_32bit_fadt_addr`, initrd table upgrades with valid/invalid checksum and revision, lockdown rejection, custom DSDT builds, and parse helper users for MADT/CEDT subtables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/tables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/thermal.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/thermal.c

## Purpose

`thermal.c` is the ACPI thermal zone platform driver. It evaluates ACPI thermal-zone methods, registers Linux thermal zones and trips, binds ACPI-listed cooling devices, handles thermal notifications, applies DMI/module-parameter quirks, and drives thermal-zone updates through a dedicated workqueue.

## Important APIs, types, and functions

Module parameters `act`, `crt`, `tzp`, `off`, and `psv` alter active, critical, polling, disable, and passive behavior. Private state is held in `struct acpi_thermal`, which stores the ACPI device, current/last deci-Kelvin temperatures, polling frequency, trip data, thermal zone pointer, Kelvin offset, work item, mutex, and refcount. Trip metadata is stored in `struct acpi_thermal_trip`, `struct acpi_thermal_passive`, `struct acpi_thermal_active`, and `struct acpi_thermal_trips`. Main functions include temperature/polling readers, trip initialization/update helpers, thermal-zone callbacks, notify handler, AML dependency workaround, offset heuristic, probe/remove, PM prepare/complete, DMI callbacks, and module init/exit.

## Control flow

Probe allocates state, sets active cooling mode with `_SCP`, pre-evaluates AML methods in firmware-safe order, reads passive/active/critical/hot trips, reads `_TMP`, determines `_TZP` or parameter polling, guesses the Kelvin conversion offset, builds a thermal trip table, registers and enables a thermal zone, initializes async check work, logs the zone, and installs an ACPI notify handler. Temperature notifications queue work; threshold/device notifications update trip temperatures or handle lists via thermal-core trip iteration, update thermal trip temperatures, queue a check, and emit netlink events. The work item serializes `thermal_zone_device_update()`. Remove unregisters notify, flushes work, unregisters the thermal zone, frees handle lists, and frees state.

## State and persistence

Thermal-zone state persists per platform device. ACPI trip temperatures are stored in firmware deci-Kelvin while Linux thermal trips use millicelsius after offset conversion. Cooling-device binding state is the ACPI handle lists from `_PSL` and `_ALx`. Workqueue and module parameters persist for module lifetime. DMI quirks adjust module parameter defaults during init.

## Dependencies and integration points

The file depends on ACPI thermal methods (`_TMP`, `_TZP`, `_SCP`, `_CRT`, `_HOT`, `_PSV`, `_ACx`, `_PSL`, `_ALx`, `_TC1`, `_TC2`, `_TFP`, `_TSP`), helper functions from `thermal_lib.c`, ACPI handle-list helpers from `utils.c`, Linux thermal framework, platform driver matching on `ACPI_THERMAL_HID`, ACPI netlink events, sysfs links, PM callbacks, and DMI.

## Risks

Firmware thermal data is often wrong or order-dependent, hence the AML dependency workaround and validity filtering. Critical-trip overrides or disabling can affect system safety. Asynchronous update coalescing must avoid stale trips while preventing unbounded queued work. Cooling-device binding assumes ACPI handle identity with `cdev->devdata`. Changing Kelvin offset heuristics can alter visible temperatures and trip behavior.

## Test signals

Validate thermal-zone registration for ACPI thermal devices, current temperature reads, active/passive/hot/critical trip creation, cooling-device binding from `_PSL`/`_ALx`, threshold/device notification updates, PM flush/update behavior, module parameters and DMI quirks, no-trip firmware handling, and critical/hot netlink plus thermal-core actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/thermal_lib.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/thermal_lib.c

## Purpose

`thermal_lib.c` provides reusable helpers for reading ACPI thermal trip-point temperatures from firmware. It centralizes ACPI method evaluation, sanity-range filtering, and conversion between ACPI deci-Kelvin and Linux thermal millicelsius APIs.

## Important APIs, types, and functions

`acpi_trip_temp()` is the private evaluator and validator. Namespaced GPL exports for ACPI thermal internals are `acpi_active_trip_temp()`, `acpi_passive_trip_temp()`, `acpi_hot_trip_temp()`, and `acpi_critical_trip_temp()`, returning deci-Kelvin or `THERMAL_TEMP_INVALID`. Generic thermal exports are `thermal_acpi_active_trip_temp()`, `thermal_acpi_passive_trip_temp()`, `thermal_acpi_hot_trip_temp()`, and `thermal_acpi_critical_trip_temp()`, returning millicelsius. Constants `TEMP_MIN_DECIK` and `TEMP_MAX_DECIK` bound plausible firmware values.

## Control flow

Each public helper builds or supplies the ACPI object name (`_ACx`, `_PSV`, `_HOT`, `_CRT`), evaluates it as an integer, treats evaluation failure as `-ENODATA`, marks out-of-range values invalid, and optionally converts valid deci-Kelvin temperatures to millicelsius.

## State and persistence

The file has no mutable persistent state. It only returns evaluated firmware values to callers.

## Dependencies and integration points

It depends on `acpi_evaluate_integer()`, ACPI device handles, `THERMAL_TEMP_INVALID`, and unit conversion helpers. `thermal.c` imports the `ACPI_THERMAL` namespace for deci-Kelvin helpers; other thermal drivers can use the generic millicelsius wrappers.

## Risks

Range filtering is policy: too narrow a range can hide valid platform trips, while too broad a range can expose bogus firmware values to thermal policy. `_ACx` IDs are limited to 0 through 9 to match ACPI active trip naming. Callers must distinguish evaluation failure from an invalid but successfully evaluated temperature.

## Test signals

Unit or mocked ACPI evaluations should cover valid trips, out-of-range trips, missing methods, invalid active IDs, conversion to millicelsius, and integration with `thermal.c` trip initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/thermal_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/tiny-power-button.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/tiny-power-button.c

## Purpose

This tiny ACPI power-button driver sends a configured signal to init when an ACPI power-button event occurs. It is a minimal alternative to the larger ACPI button input path for configurations that want power button delivery through `kill_cad_pid()`.

## Important APIs, types, and functions

The module parameter `power_signal` defaults to `CONFIG_ACPI_TINY_POWER_BUTTON_SIGNAL`. The ACPI ID table matches both regular and fixed power-button HIDs. Event handling is split between `acpi_tiny_power_button_notify()` for device notify events, `acpi_tiny_power_button_event()` for fixed hardware events, and `acpi_tiny_power_button_notify_run()` to run fixed events in ACPI notify-handler context. Probe/remove install and remove either a fixed event handler or a device notify handler.

## Control flow

Probe obtains the ACPI companion. If the ACPI device type is the fixed power button, it installs `acpi_tiny_power_button_event()` for `ACPI_EVENT_POWER_BUTTON`; otherwise it installs an ACPI device notify handler. Fixed event callbacks schedule notify work with `acpi_os_execute()` and return `ACPI_INTERRUPT_HANDLED`. The common notify path calls `kill_cad_pid(power_signal, 1)`. Remove unregisters the matching handler and waits for pending ACPI events to complete.

## State and persistence

The only persistent module state is the configurable signal number. Handler registration is per probed platform device and removed on driver detach.

## Dependencies and integration points

The driver depends on ACPI button HIDs, ACPI fixed-event and notify-handler APIs, ACPICA deferred execution, platform-device matching, and the kernel CAD/init signaling helper.

## Risks

Every notify event for the matched device sends the signal; there is no filtering by event code. An invalid or surprising `power_signal` value changes user-visible init behavior. Remove must wait for pending ACPI callbacks to avoid executing after driver detach.

## Test signals

Test fixed and namespace power-button devices, signal delivery to init, module parameter changes, handler removal with pending events, and coexistence expectations with other ACPI button handling in tiny configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/tiny-power-button.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/utils.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/utils.c

## Purpose

`utils.c` is a collection of ACPI core helper APIs for evaluating common AML objects, extracting ACPI packages, managing ACPI handle lists, formatting ACPI handle logs, checking device presence and matches, evaluating hotplug/control methods, handling `_DSM`, parsing boot parameters, and matching platform OEM table descriptors.

## Important APIs, types, and functions

Major exported helpers include `acpi_extract_package()`, `acpi_evaluate_integer()`, `_ADR` readers, `acpi_get_subsystem_id()`, `acpi_evaluate_reference()`, ACPI handle-list equal/replace/free helpers, `acpi_device_dep()`, `acpi_get_physical_device_location()`, `acpi_evaluate_ost()`, `acpi_handle_printk()`, dynamic-debug handle logging, `acpi_evaluation_failure_warn()`, `acpi_has_method()`, `acpi_execute_simple_method()`, `_EJ0`/`_LCK`/`_REG` evaluators, `_DSM` evaluation/check helpers, UID conversion, ACPI device found/present/match iterators, `acpi_reduced_hardware()`, `acpi_video_backlight_string`, and `acpi_match_platform_list()`.

## Control flow

Package extraction validates the requested format string, computes packed head/tail output storage, allocates or validates the caller buffer, and copies integers, strings, buffers, or references. Evaluation helpers wrap `acpi_evaluate_object()` with type checks and standardized logging. Reference-list helpers evaluate package references and manage allocated handle arrays. Hotplug helpers build method arguments for `_OST`, `_EJ0`, `_LCK`, and `_REG`. `_DSM` helpers evaluate function 0 to check support bitmasks or evaluate requested functions. Device-presence helpers search the ACPI bus by HID/UID/HRV after scan initialization. Platform matching reads table headers and compares OEM fields and revision predicates.

## State and persistence

Most helpers are stateless. `acpi_video_backlight_string` stores the `acpi_backlight=` boot parameter. Some helpers allocate caller-owned memory, including extracted package buffers, subsystem ID strings, PLD structures, `_DSM` objects, and ACPI handle-list arrays. Device match iterators transfer references that callers must release with `acpi_dev_put()`.

## Dependencies and integration points

The file is used broadly across ACPI scan, hotplug, thermal, video/backlight, platform quirks, device drivers, and logging code. It depends on ACPICA object evaluation/name/table APIs, Linux ACPI bus state from `scan.c`, dynamic debug, and `sleep.h` for reduced-hardware/sleep-related declarations.

## Risks

Memory ownership and type validation are the main risks: callers must free allocated buffers and handle `ERR_PTR`/NULL/`AE_*` returns correctly. `acpi_extract_package()` does not support nested packages. Logging with ACPI paths cannot run path lookup in interrupt context. Device-presence helpers require ACPI scan to have completed and only describe a point-in-time state for hotpluggable devices. `_DSM` support bit interpretation must preserve compatibility with integer and buffer returns.

## Test signals

Test malformed and valid ACPI packages, integer/reference evaluation, handle-list replacement/free paths, hotplug `_OST`/`_EJ0`/`_LCK` calls, `_DSM` integer and buffer support masks, device match helpers with HID/UID/HRV combinations, PLD decoding, `acpi_backlight=` storage, platform OEM matching, and dynamic-debug handle logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/utils.c -->
