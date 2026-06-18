# subset-b-005437 Research

Grouped source research for Intel thermal drivers under `sources/distributed-fs/ceph-client/drivers/thermal/intel`. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int3402_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int3402_thermal.c

## Purpose

`int3402_thermal.c` is the ACPI INT3402 participant driver for memory temperature reporting. It binds INT3402 ACPI platform devices that expose `_TMP`, creates a shared INT340x thermal zone, and forwards firmware thermal notifications to the Linux thermal core.

## Important APIs, Types, and Functions

Key state is `struct int3402_thermal_data`, which stores the ACPI handle and `struct int34x_thermal_zone`. `int3402_thermal_probe()` validates the ACPI companion and `_TMP`, allocates driver data, calls `int340x_thermal_zone_add()`, installs `int3402_notify()`, and stores platform drvdata. `int3402_notify()` handles `INT3402_THERMAL_EVENT` by calling `int340x_thermal_zone_device_update(..., THERMAL_TRIP_VIOLATED)`. `int3402_thermal_remove()` removes the ACPI notify handler and thermal zone.

## Control Flow

Probe succeeds only with an ACPI companion and temperature method. After registration, ACPI device notifications are the runtime trigger: event `0x90` refreshes thermal-zone policy evaluation, while performance-change event `0x80` is intentionally ignored. Removal unwinds notify registration before unregistering the thermal zone.

## State and Persistence Behavior

State is device-managed except for the shared thermal zone object allocated by the INT340x helper and explicitly removed. No values are persisted; the zone reads firmware temperature and trips on demand through ACPI.

## Dependencies and Integration Points

The driver depends on ACPI, platform bus, thermal core, and `int340x_thermal_zone.c`. It integrates with DPTF-style firmware via INT3402 notifications and Linux userspace via the registered thermal zone.

## Risks and Test Signals

Risks are missing `_TMP`, notify-handler registration failure after zone creation, firmware event storms, and assuming every INT3402 device is memory temperature capable. Test signals include module probe/remove on INT3402 ACPI nodes, `_TMP` conversion through the shared zone, ACPI notify `0x90` causing `thermal_zone_device_update()`, and error unwinding after forced notify install failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int3402_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int3403_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int3403_thermal.c

## Purpose

`int3403_thermal.c` supports ACPI INT3403/INTC thermal participants. Depending on firmware type, it registers either a sensor-backed INT340x thermal zone or a charger/battery cooling device controlled through ACPI performance methods.

## Important APIs, Types, and Functions

`struct int3403_priv` records the platform device, ACPI device, participant type, and private sensor/cooling object. `int3403_sensor_add()` creates an INT340x zone and ACPI notify handler. `int3403_cdev_add()` evaluates `PPSS`, derives `max_state`, and registers a thermal cooling device with `int3403_cooling_ops`. Cooling callbacks use `PPPC` for current state and `SPPC` for setting state. `int3403_notify()` reacts to thermal event `0x90` and trip-point-changed event `0x81`.

## Control Flow

Probe first tries `_TMP`; success implies a sensor participant. Without `_TMP`, it reads `PTYP` and dispatches chargers and batteries to cooling-device setup. Sensor notifications update the thermal zone on violations and reread trips on performance trip changes. Removal chooses the matching teardown path by participant type.

## State and Persistence Behavior

State is per platform device and devm-managed except registered thermal objects. Firmware owns actual temperature, trip, and performance state; this driver only mirrors it through ACPI and Linux thermal abstractions.

## Dependencies and Integration Points

Dependencies are ACPI methods `_TMP`, `PTYP`, `PPSS`, `PPPC`, `SPPC`, Linux thermal zones/cooling devices, and `int340x_thermal_zone`. The ACPI ID table includes INT3403 plus several INTC IDs for newer platform participants.

## Risks and Test Signals

Risks include malformed `PPSS` packages, unsupported `PTYP`, missing notify removal on partial setup, and treating package count minus one as max cooling state without validating full package contents. Test signals include sensor and cooling-device probe variants, ACPI notify `0x81` trip refresh, `PPPC`/`SPPC` state round trips, and removal after both participant classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int3403_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int3406_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int3406_thermal.c

## Purpose

`int3406_thermal.c` exposes an ACPI display participant as a thermal cooling device by limiting raw backlight brightness according to firmware-provided brightness bounds.

## Important APIs, Types, and Functions

`struct int3406_thermal_data` stores ACPI brightness levels, lower/upper indexes, raw backlight device, and cooling device. Cooling callbacks map thermal cooling state to ACPI brightness levels and then to raw backlight brightness. `int3406_thermal_get_limit()` reads `DDDL` and `DDPC` to update brightness bounds. `int3406_notify()` refreshes limits on event `INT3406_BRIGHTNESS_LIMITS_CHANGED`.

## Control Flow

Probe requires an ACPI handle, a raw backlight device, and ACPI video brightness levels. It computes limits, registers a cooling device named by the ACPI BID, then installs a notify handler. Setting cooling state clamps against `upper_limit - lower_limit` and applies an indexed brightness. Reading current state converts raw brightness back to ACPI percent and selects the nearest firmware level above it.

## State and Persistence Behavior

The driver persists only runtime limit indexes and the allocated brightness table. Hardware state is the backlight brightness owned by the backlight subsystem; ACPI owns the limit policy.

## Dependencies and Integration Points

It depends on ACPI video brightness (`acpi_video_get_levels()`), raw backlight devices, ACPI notify, and thermal cooling devices. It bridges firmware DPTF display throttling with the native graphics/backlight stack.

## Risks and Test Signals

Risks include no raw backlight device at probe time, non-monotonic ACPI brightness levels, division by `max_brightness`, missing notify-handler removal in `remove()`, and ambiguous percent-to-raw mapping. Test signals include cooling state max/current/set behavior, `DDDL`/`DDPC` bound changes, backlight brightness updates, and probe failure paths that free the brightness table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int3406_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int340x_thermal_zone.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int340x_thermal_zone.c

## Purpose

`int340x_thermal_zone.c` is the shared thermal-zone implementation for INT340x ACPI participants. It converts ACPI temperature/trip methods into Linux thermal zone operations, including optional LPAT raw-to-temperature conversion.

## Important APIs, Types, and Functions

Exports are `int340x_thermal_zone_add()`, `int340x_thermal_zone_remove()`, and `int340x_thermal_update_trips()`. `int340x_thermal_get_zone_temp()` reads `_TMP`, converts through LPAT when present, otherwise converts deci-Kelvin to millicelsius. `int340x_thermal_set_trip_temp()` writes active/passive auxiliary trip methods `PATn`. `int340x_thermal_read_trips()` collects critical, hot, passive, and active ACPI trips. `int340x_update_one_trip()` refreshes existing trip temperatures.

## Control Flow

Add allocates `struct int34x_thermal_zone`, reads auxiliary trip count from `PATC`, pre-creates writable passive trips, appends standard ACPI trips, reads hysteresis from `GTSH`, obtains an LPAT table, registers a no-hwmon thermal zone with trips, and enables it. Update iterates each registered trip and refreshes its temperature from ACPI, invalidating trips that are no longer available.

## State and Persistence Behavior

The helper owns the zone object, LPAT conversion table, and registered thermal-zone lifetime. Trip data is copied into the thermal core during registration. Firmware remains the source of temperature and trip values; no file-backed persistence exists.

## Dependencies and Integration Points

It depends on ACPI thermal helpers, ACPI LPAT, thermal zone APIs, and unit conversion helpers. INT3402, INT3403, and processor thermal drivers use it to avoid duplicating ACPI zone logic.

## Risks and Test Signals

Risks include trip-count bounds when firmware reports many `PATC` entries, `PATn` name generation limited to indexes 0-9, LPAT conversion failures, and dynamic trip disappearance. Test signals include zones with every ACPI trip type, LPAT and non-LPAT `_TMP` conversion, writable active/passive trip writes, `GTSH` hysteresis, and update behavior after ACPI notifies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int340x_thermal_zone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int340x_thermal_zone.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int340x_thermal_zone.h

## Purpose

`int340x_thermal_zone.h` declares the common INT340x thermal-zone contract shared by ACPI participant drivers.

## Important APIs, Types, and Functions

Constants define ten active trips plus critical/hot/passive defaults. `struct active_trip` describes a candidate active trip. `struct int34x_thermal_zone` stores the ACPI device, auxiliary trip count, Linux thermal zone, caller private data, and LPAT table. Prototypes expose add/remove/update helpers. Inline helpers set/get private data and wrap `thermal_zone_device_update()`.

## Control Flow

The header has no runtime control flow. It establishes the call contract used by individual participant drivers during probe, notification handling, and remove.

## State and Persistence Behavior

The structure is runtime-only state allocated by `int340x_thermal_zone_add()` and released by `int340x_thermal_zone_remove()`. The private-data pointer lets caller drivers associate their own context without changing the shared helper.

## Dependencies and Integration Points

The header depends on `acpi/acpi_lpat.h` and thermal-core declarations from included users. It is the integration point between INT340x participant drivers and the shared zone implementation.

## Risks and Test Signals

Risks are ABI-like local coupling: changes to `struct int34x_thermal_zone` or inline update helpers affect all participant drivers. Test signals are compile coverage across INT3402/INT3403/processor users and runtime update calls through the inline wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int340x_thermal_zone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/platform_temperature_control.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/platform_temperature_control.c

## Purpose

`platform_temperature_control.c` exposes Processor Thermal Device platform temperature control MMIO registers as sysfs and debugfs controls for target temperature, enable, tolerance/gain, and debug temperature override.

## Important APIs, Types, and Functions

`struct mmio_reg` describes bitfields and units. `struct ptc_data` stores per-instance offset, PCI device, sysfs group, attributes, and group name. Exported APIs are `proc_thermal_ptc_add()` and `proc_thermal_ptc_remove()`. `ptc_mmio_show()`, `ptc_store()`, and `ptc_mmio_write()` implement field access under `ptc_lock`. Debugfs `temperature_0..2` files write override values via `ptc_temperature_write()`.

## Control Flow

When the PTC feature bit is present, add initializes three instances at offsets `0x5B20`, `0x5B28`, and `0x5B30`, creates per-instance sysfs groups named `ptc_N_control`, and creates a global debugfs directory. Sysfs reads extract bitfields and scale 0.5C units to millicelsius-like integer values; writes validate input against field masks and write back through read-modify-write.

## State and Persistence Behavior

The file has static global `ptc_instance[]` and `ptc_debugfs`. Hardware register values persist in the processor thermal MMIO block until changed or reset. The mutex serializes concurrent read-modify-write sequences.

## Dependencies and Integration Points

It depends on PCI driver data being `struct proc_thermal_device` with valid `mmio_base`, sysfs/debugfs, and the processor thermal feature mask. It is invoked by `proc_thermal_mmio_add()` and removed by `proc_thermal_mmio_remove()`.

## Risks and Test Signals

Risks include global static instances shared across devices, ignoring `ptc_create_groups()` failures, debugfs override bypassing sysfs visibility, unit truncation on writes, and write-shift overflow if inputs exceed masks. Test signals include PTC feature probe, three sysfs groups, read/write validation, debugfs override enable/disable with zero/nonzero writes, and concurrent sysfs access under lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/platform_temperature_control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_device.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_device.c

## Purpose

`processor_thermal_device.c` is the common Processor Thermal Reporting Device core. It registers ACPI-backed thermal zones, exposes PPCC power-limit metadata, controls TCC offset, and dispatches optional MMIO feature setup for RAPL, RFIM, PTC, workload, power-floor, and SoC slider support.

## Important APIs, Types, and Functions

Exports include `proc_thermal_add()`, `proc_thermal_remove()`, `proc_thermal_suspend()`, `proc_thermal_resume()`, `proc_thermal_mmio_add()`, and `proc_thermal_mmio_remove()`. `proc_thermal_read_ppcc()` parses ACPI `PPCC` packages into two `power_config` entries. `proc_thermal_get_zone_temp()` computes max core temperature using `intel_tcc_get_temp()`. Sysfs attributes expose power limits, power-floor status/enable, and `tcc_offset_degree_celsius`.

## Control Flow

`proc_thermal_add()` binds ACPI state, parses PPCC, chooses `_TMP` or TCC fallback temperature source, registers an INT340x zone, installs ACPI notification, and creates sysfs files/groups. ACPI event `0x83` refreshes PPCC and emits a thermal power capability change. MMIO add maps BAR0 only when needed, then creates feature interfaces in dependency order with error unwinding. Suspend saves TCC offset and slider state; resume refreshes PPCC and restores saved hardware state.

## State and Persistence Behavior

Per-device state lives in `struct proc_thermal_device`; TCC offset save is a static global. Power-limit values mirror firmware PPCC and are refreshed on notify/resume. MMIO features manipulate persistent hardware registers but store minimal driver-side policy.

## Dependencies and Integration Points

Dependencies include ACPI, Intel TCC library, INT340x zone helper, PCI MMIO, sysfs, and feature-specific processor thermal modules. PCI frontends call this file from legacy and newer probe paths.

## Risks and Test Signals

Risks include malformed PPCC packages, partial sysfs creation unwind order, global TCC save across devices, optional feature cleanup asymmetry, and fallback temperature availability on CPU hotplug. Test signals include PPCC parsing, `_TMP` and TCC fallback zones, ACPI event `0x83`, TCC offset permission checks, suspend/resume restore, and MMIO feature-add failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_device.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_device.h

## Purpose

`processor_thermal_device.h` centralizes PCI IDs, feature flags, shared structures, mailbox command constants, and cross-module function prototypes for the Processor Thermal Device family.

## Important APIs, Types, and Functions

It defines `struct power_config`, `struct proc_thermal_device`, and `struct rapl_mmio_regs`. Feature flags include RAPL, FIVR, DVFS, workload request/hint, DLVR, power floor, MSI support, PTC, and SoC power slider. It declares RAPL, RFIM, workload, mailbox, power-floor, core add/remove, PM, MMIO, PTC, and slider functions. When MMIO RAPL is disabled, inline stubs return success/no-op.

## Control Flow

There is no executable flow except configuration-dependent inline stubs. The header controls which feature modules can be called from the PCI/core drivers and how driver data is shared.

## State and Persistence Behavior

The header defines in-memory state layout only. `struct proc_thermal_device` is the common persistent runtime object stored as PCI or device driver data.

## Dependencies and Integration Points

It depends on `linux/intel_rapl.h` and forward declarations/types from PCI and INT340x users. It is the internal ABI among the processor thermal modules and imports/export namespaces in those modules.

## Risks and Test Signals

Risks include mismatched feature bit interpretation between PCI ID tables and feature modules, duplicate PCI IDs with different naming, and build-configuration drift around RAPL stubs. Test signals are allmodconfig/allyesconfig builds, namespace import checks, and probe coverage for each feature-mask combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_device_pci.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_device_pci.c

## Purpose

`processor_thermal_device_pci.c` is the PCI frontend for newer Processor Thermal Devices. It maps processor thermal MMIO, registers a package thermal zone, handles threshold/workload/power-floor interrupts, and enables optional feature modules based on PCI ID driver data.

## Important APIs, Types, and Functions

`struct proc_thermal_pci` tracks PCI device, core private data, MMIO thermal zone, delayed threshold work, stored threshold, and whether legacy ACPI setup failed. MMIO helper tables describe package temp, TjMax, threshold, interrupt enable, and status registers. `proc_thermal_irq_handler()` classifies MSI/shared interrupts and schedules work or wakes the threaded handler. `sys_get_curr_temp()` and `sys_set_trip_temp()` implement the `TCPU_PCI` zone.

## Control Flow

Probe enables PCI, maps feature MMIO, attempts legacy ACPI `proc_thermal_add()` but continues without it, registers one writable passive trip for package threshold, selects MSI when supported or requested, requests IRQs, then enables the zone. Threshold interrupts disable MMIO interrupt enable, delay notification for rate control, update the zone, and re-enable interrupt. Threaded IRQ callbacks notify workload and power-floor sysfs listeners and clear SoC status bits.

## State and Persistence Behavior

Runtime state includes `stored_thres`, delayed work, static MSI IRQ map, and static `msi_irq`. Hardware threshold and interrupt-enable registers persist across runtime until remove or suspend/resume rewrites them. Probe stores `proc_thermal_device` as PCI drvdata.

## Dependencies and Integration Points

It integrates PCI, thermal core, optional MSI/MSI-X, processor thermal core/MMIO features, workload hint/request, power-floor, and INT340x. PCI ID driver data encodes the feature mix for ADL, LNLM, MTLP, ARL, RPL, PTL, WCL, and NVL variants.

## Risks and Test Signals

Risks include global MSI state with multiple devices, resume restoring `stored_thres / 1000` instead of the TjMax-relative register value used by set_trip, continuing after legacy ACPI failure, IRQ status races, and feature cleanup paths. Test signals include shared IRQ and MSI modes, threshold set/clear/resume, workload/power-floor interrupts, feature-mask matrix probes, and delayed-work cancellation on remove/offline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_device_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_device_pci_legacy.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_device_pci_legacy.c

## Purpose

`processor_thermal_device_pci_legacy.c` is the PCI frontend for older Processor Thermal Devices. It combines the common ACPI processor thermal zone with optional legacy SoC DTS sensors and optional MMIO RAPL/workload support.

## Important APIs, Types, and Functions

`proc_thermal_pci_probe()` enables the PCI device, allocates `struct proc_thermal_device`, calls `proc_thermal_add()`, optionally initializes IOSF DTS sensors for Braswell, and calls `proc_thermal_mmio_add()`. `proc_thermal_pci_msi_irq()` forwards MSI interrupts to `intel_soc_dts_iosf_interrupt_handler()`. PM callbacks delegate to common suspend/resume.

## Control Flow

Probe must complete the common ACPI path first. For BSW, it attempts auxiliary IOSF DTS enumeration and MSI IRQ registration but does not fail the whole driver if auxiliary DTS support is absent. MMIO features are added after DTS setup. Remove exits DTS/MSI, removes MMIO features, and unregisters the common thermal zone.

## State and Persistence Behavior

Per-device state is the common `proc_thermal_device`; auxiliary DTS state lives in `proc_priv->soc_dts`. MSI IRQ state is tied to the PCI device and freed on remove. No file persistence exists.

## Dependencies and Integration Points

It depends on PCI, ACPI processor thermal core, optional IOSF SoC DTS, MSI, and feature flags from `processor_thermal_device.h`. PCI IDs cover Haswell/Broadwell/Baytrail/Braswell/Broxton/Cannonlake/CoffeeLake/GeminiLake/IceLake/JasperLake/Skylake/TigerLake.

## Risks and Test Signals

Risks include auxiliary DTS failure being intentionally nonfatal, an empty `else` branch for non-BSW devices, ordering of `pci_set_drvdata()` relative to common setup, and MMIO add failure after DTS setup. Test signals include BSW MSI DTS interrupt handling, non-BSW probe, MMIO RAPL feature IDs, suspend/resume delegation, and remove cleanup after partial auxiliary setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_device_pci_legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_mbox.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_mbox.c

## Purpose

`processor_thermal_mbox.c` implements a serialized MMIO mailbox for Processor Thermal Device commands, mainly workload type request/hint and interrupt configuration.

## Important APIs, Types, and Functions

Exports are `processor_thermal_send_mbox_read_cmd()`, `processor_thermal_send_mbox_write_cmd()`, and `processor_thermal_mbox_interrupt_config()`. `wait_for_mbox_ready()` polls the interface busy bit. Internal read/write helpers program data and command registers at offsets `0x5810` and `0x5818`. A global `mbox_lock` serializes mailbox transactions.

## Control Flow

Each public command locks the mailbox, waits for ready, writes command/data, and waits for ready again. Read commands return either 32-bit workload data or 64-bit data depending on command ID. Interrupt configuration performs read-modify-write on Camarillo interrupt config, optionally updating time-window bits and one enable bit.

## State and Persistence Behavior

Driver state is only the mutex. Hardware mailbox registers hold transient command state and interrupt configuration persists in device registers.

## Dependencies and Integration Points

The mailbox requires PCI drvdata to be `struct proc_thermal_device` with valid `mmio_base`. It is called by workload request, workload hint, RFIM mailbox attributes, and power-floor configuration.

## Risks and Test Signals

Risks include busy polling without delay, returning the last `ret` value if the retry loop exhausts, global serialization across devices, and command-specific 32/64-bit response assumptions. Test signals include busy mailbox failure, read/write command success, interrupt config enable/disable/time-window update, and concurrent sysfs users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_power_floor.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_power_floor.c

## Purpose

`processor_thermal_power_floor.c` exposes and notifies the processor thermal power-floor condition, where hardware has reduced power to a minimum possible level.

## Important APIs, Types, and Functions

Exports include `proc_thermal_read_power_floor_status()`, `proc_thermal_power_floor_set_state()`, `proc_thermal_power_floor_get_state()`, `proc_thermal_check_power_floor_intr()`, and `proc_thermal_power_floor_intr_callback()`. It reads status and interrupt-active bits from `SOC_WT_RES_INT_STATUS_OFFSET`, and enables interrupt reporting via `processor_thermal_mbox_interrupt_config()`.

## Control Flow

Userspace toggles reporting through the common `power_limits/power_floor_enable` sysfs attribute. Enabling/disabling is serialized by `pf_lock` and updates a global `enable_state`. IRQ top-half checks the active bit; threaded callback sends `sysfs_notify()` for `power_limits/power_floor_status`.

## State and Persistence Behavior

`enable_state` is static global driver state, while hardware status is read from MMIO. Interrupt configuration persists in mailbox-controlled hardware registers until disabled or reset.

## Dependencies and Integration Points

It depends on the processor thermal mailbox, PCI device conversion from `proc_priv->dev`, common power-limit sysfs group, and the newer PCI IRQ path.

## Risks and Test Signals

Risks include global enable state across possible devices, no local check for feature presence in callbacks, and notification depending on threaded IRQ clearing elsewhere. Test signals include sysfs enable idempotence, mailbox failure propagation, interrupt-active check from IRQ context, and `sysfs_notify()` on power-floor transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_power_floor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_rapl.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_rapl.c

## Purpose

`processor_thermal_rapl.c` registers an Intel RAPL powercap interface backed by Processor Thermal Device MMIO registers instead of MSRs.

## Important APIs, Types, and Functions

It defines MMIO masks and `rpi_mmio[]` primitive metadata for power limits, energy, locks, time windows, thermal spec, throttled time, and policy. `rapl_mmio_default` maps package and DRAM domain registers relative to `mmio_base`. `rapl_mmio_read_raw()` and `rapl_mmio_write_raw()` implement raw RAPL accessors. Exports are `proc_thermal_rapl_add()` and `proc_thermal_rapl_remove()`.

## Control Flow

Add populates the global `rapl_mmio_priv` register pointers from the device MMIO base, registers a powercap control type named `intel-rapl-mmio`, checks for an existing package 0 domain, and adds package 0. Remove finds and removes package 0, then unregisters the powercap control type.

## State and Persistence Behavior

`rapl_mmio_priv` is static global state. RAPL limits and counters are hardware register state; the driver persists only mapping metadata and the powercap control-type registration.

## Dependencies and Integration Points

It depends on the Intel RAPL core namespace, powercap framework, and processor thermal MMIO mapping. The common MMIO add path invokes it when `PROC_THERMAL_FEATURE_RAPL` is set.

## Risks and Test Signals

Risks include package-0-only registration, global state unsuitable for multiple instances, missing locking around read-modify-write raw writes, and drift from RAPL primitive expectations. Test signals include powercap tree creation, package/DRAM domain attributes, duplicate add returning `-EEXIST`, remove idempotence, and register read/write validation on RAPL-capable PCI IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_rapl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_rfim.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_rfim.c

## Purpose

`processor_thermal_rfim.c` exposes RF interference mitigation controls for FIVR, DLVR, and DVFS through sysfs groups backed by processor thermal MMIO, mailbox commands, and selected PCI config fields.

## Important APIs, Types, and Functions

`struct mmio_reg` describes attribute bitfields; `struct mapping_table` maps special integer/string values. Generated `RFIM_SHOW` and `RFIM_STORE` callbacks implement many sysfs attributes. Additional attributes include mailbox-backed `rfi_restriction` and `ddr_data_rate`. Exports are `proc_thermal_rfim_add()` and `proc_thermal_rfim_remove()`.

## Control Flow

Add creates `fivr`, `dlvr`, and/or `dvfs` sysfs groups based on feature flags. DLVR register tables are selected by PCI device ID, with LNL/PTL/WCL using narrow mapped frequency values and NVL using alternate offsets plus PCI-config DDR data rate. Attribute reads choose a table, read MMIO or mailbox/config, apply bit extraction and optional string mapping. Writes reject read-only fields, parse mapped or numeric input, and perform read-modify-write.

## State and Persistence Behavior

Static globals hold the selected DLVR table, mapping, and DDR register. Hardware MMIO/mailbox/config values persist in platform registers. No per-device locking is used for MMIO RMW in this file.

## Dependencies and Integration Points

It depends on processor thermal MMIO, PCI IDs, sysfs, mailbox helpers, and feature masks from the common header. It is invoked by the core MMIO add/remove path.

## Risks and Test Signals

Risks include static per-platform table selection across devices, read-modify-write races, string matching using prefix lengths, incomplete cleanup if DVFS group creation fails without FIVR/DLVR, and no range check before shifting inputs into MMIO fields. Test signals include sysfs group creation for each feature combination, mapped DLVR values, mailbox `rfi_restriction`, NVL `ddr_data_rate`, read-only attribute rejection, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_rfim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_soc_slider.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_soc_slider.c

## Purpose

`processor_thermal_soc_slider.c` integrates the Processor Thermal Device SoC efficiency slider with Linux platform profiles, translating performance/balanced/low-power profiles into a firmware slider register.

## Important APIs, Types, and Functions

Exports are `proc_thermal_soc_power_slider_add()`, `proc_thermal_soc_power_slider_suspend()`, and `proc_thermal_soc_power_slider_resume()`. Module parameters `slider_balance` and `slider_offset` tune the balanced slider value and firmware offset. `set_soc_power_profile()` programs the 64-bit register at offset `0x5B38`. Platform profile callbacks convert between `enum platform_profile_option` and slider values.

## Control Flow

Add programs the default balanced profile and registers a platform profile provider named `SoC Power Slider` with low-power, balanced, and performance choices. Profile set locks parameter state, applies the latest balanced parameter, converts the requested profile, sets slider bits, sets enable bit, and optionally sets offset. Profile get reads the current register and maps it back to a supported profile.

## State and Persistence Behavior

Static globals hold slider value policy, offset, and one saved register image for suspend. Hardware slider state persists in the MMIO register and is restored on resume.

## Dependencies and Integration Points

It depends on PCI MMIO, `platform_profile`, bitfield helpers, and common processor thermal feature detection. The newer PCI driver enables it on PTL/WCL/NVL feature masks.

## Risks and Test Signals

Risks include static saved state across devices, possible mismatch between module parameter get and pending balanced parameter, unsupported firmware slider values causing profile_get failure, and offset rules tied to exact min/max slider values. Test signals include platform profile registration, profile get/set round trips, module parameter validation, suspend/resume restore, and feature-mask probe on supported IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_soc_slider.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_wt_hint.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_wt_hint.c

## Purpose

`processor_thermal_wt_hint.c` exposes firmware-predicted workload type hints and notification controls through a `workload_hint` sysfs group.

## Important APIs, Types, and Functions

Attributes are `workload_type_index`, `workload_hint_enable`, `workload_slow_hint_enable`, and `notification_delay_ms`. Exports include `proc_thermal_check_wt_intr()`, `proc_thermal_wt_intr_callback()`, `proc_thermal_wt_hint_add()`, and `proc_thermal_wt_hint_remove()`. `workload_hint_enable()` programs mailbox interrupt config for fast or slow prediction bits.

## Control Flow

Add creates the sysfs group and marks it created. Users enable prediction through mailbox config with a programmable time window. Reads of workload index require at least one hint mode enabled, then extract bits 47:40 from the shared status register. IRQ top-half checks active bit 2; threaded callback sends `sysfs_notify()` for `workload_hint/workload_type_index`. Remove disables the fast hint if enabled and removes the group.

## State and Persistence Behavior

Static globals track enable states, notification delay encoding, notification delay in milliseconds, and group creation. Hardware prediction status and interrupt config live in MMIO/mailbox registers.

## Dependencies and Integration Points

It depends on mailbox helpers, PCI drvdata, newer Processor Thermal PCI IRQ handling, and common `SOC_WT_RES_INT_STATUS_OFFSET`. Attribute visibility hides slow hints on selected platforms.

## Risks and Test Signals

Risks include global enable/delay state, remove disabling only the fast hint path, concurrent IRQ/status reads around sysfs changes, and rounding delay values to powers of two. Test signals include sysfs enable/disable, slow-hint visibility by PCI ID, notification delay encoding bounds, workload status extraction, interrupt notification, and cleanup after enabled hints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_wt_hint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_wt_req.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_wt_req.c

## Purpose

`processor_thermal_wt_req.c` exposes user-requested workload type selection through a `workload_request` sysfs group backed by processor thermal mailbox commands.

## Important APIs, Types, and Functions

The workload type table includes `none`, `idle`, `semi_active`, `bursty`, `sustained`, and `battery_life`. Attributes are `workload_available_types` and read/write `workload_type`. Exports are `proc_thermal_wt_req_add()` and `proc_thermal_wt_req_remove()`.

## Control Flow

Add first probes mailbox read support and returns success without sysfs if unsupported. When supported, it creates the group. Writing parses a string, maps it to an index, sets valid/AC-DC bits for nonzero types, and sends a mailbox write. Reading sends mailbox read, masks to 8 bits, validates range, and prints the workload string.

## State and Persistence Behavior

Only `workload_req_created` is stored in the driver. Requested workload state persists in firmware/mailbox-controlled hardware until changed.

## Dependencies and Integration Points

It depends on processor thermal mailbox helpers and common MMIO setup. The core MMIO add path selects this feature when `PROC_THERMAL_FEATURE_WT_REQ` is set and no hint-only path is used.

## Risks and Test Signals

Risks include returning `false` instead of a negative errno on mailbox read/write failure, static group-created state across devices, and silently treating unsupported mailbox as successful feature add. Test signals include available type formatting, all workload writes, readback validation, unsupported mailbox probe, and group removal after creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_wt_req.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_bxt_pmic_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_bxt_pmic_thermal.c

## Purpose

`intel_bxt_pmic_thermal.c` handles thermal interrupts from the Broxton Whiskey Cove PMIC and forwards matching PMIC sensor events to Linux thermal zones.

## Important APIs, Types, and Functions

`struct trip_config_map` maps PMIC IRQ/status/enable registers to thermal trip numbers. `struct thermal_irq_map` maps ACPI/thermal-zone names such as `STR0` to trip configs. `pmic_thermal_irq_handler()` resolves active PMIC thermal IRQ bits, updates the named thermal zone, and clears IRQ bits. `pmic_thermal_probe()` maps platform IRQs to regmap IRQ virqs, requests threaded IRQs, and unmasks PMIC thermal interrupt bits.

## Control Flow

Probe obtains parent `intel_soc_pmic`, regmap, and regmap IRQ chip data, then requests every platform IRQ until `-ENXIO`. It then iterates configured thermal maps and clears mask bits to enable thermal interrupts. Runtime IRQ handling walks all maps/trips, reads IRQ registers, reads event status, updates the corresponding thermal zone by name, and clears the matched IRQ.

## State and Persistence Behavior

The driver has static mapping tables and no per-device heap state. PMIC interrupt masks and latched event bits live in PMIC registers and persist until changed/cleared.

## Dependencies and Integration Points

It depends on MFD `intel_soc_pmic`, regmap/regmap-irq, platform IRQ resources, and thermal zones already registered for names like `STR0`. The platform ID `bxt_wcove_thermal` selects mapping data.

## Risks and Test Signals

Risks include thermal zone lookup by fixed string, ignoring `evt_stat` contents after reading, clearing IRQ with `reg_val & mask`, and no cleanup to re-mask interrupts on remove. Test signals include virq mapping, IRQ request count, interrupt unmask register writes, each STR sensor update, and regmap read/write error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_bxt_pmic_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_hfi.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_hfi.c

## Purpose

`intel_hfi.c` implements Intel Hardware Feedback Interface support. It allocates HFI tables per package, enables hardware when thermal netlink clients are present, processes package thermal HFI update interrupts, and publishes CPU performance/efficiency capabilities to userspace.

## Important APIs, Types, and Functions

Important types are `struct hfi_cpu_data`, `struct hfi_hdr`, `struct hfi_instance`, `struct hfi_features`, and per-CPU `struct hfi_cpu_info`. Public functions are `intel_hfi_init()`, `intel_hfi_online()`, `intel_hfi_offline()`, and `intel_hfi_process_event()`. `hfi_parse_features()` reads CPUID leaf 6. `update_capabilities()` emits `thermal_genl_cpu_capability_event()` in chunks. Syscore and thermal notifier callbacks enable/disable HFI across suspend and netlink bind/unbind.

## Control Flow

Initialization parses feature layout, allocates package instances and cpumasks, creates a workqueue, registers thermal netlink notifier, and syscore PM ops. CPU online links the CPU to a package instance, allocates hardware/local tables for first package use, initializes locks/work, and enables HFI when clients exist. Interrupt processing acknowledges only new timestamps, copies the hardware table under locks, clears the package HFI status bit, and queues delayed netlink publication.

## State and Persistence Behavior

Global state tracks package instances, feature layout, client count, and workqueue. Per-package state owns hardware table pages, local copy, cpumask, and locks. Hardware table pages are intentionally not freed on normal CPU offline because some processors remember table addresses.

## Dependencies and Integration Points

It depends on CPUID/MSRs, topology package IDs, CPU hotplug calls from `therm_throt.c`, package thermal interrupt clearing, syscore PM, and thermal generic netlink. `thermal_interrupt.h` supplies package status clear.

## Risks and Test Signals

Risks include package/die topology assumptions, memory retained for hardware table reuse, client-count underflow on notifier imbalance, delayed work after offline/suspend, and concurrent table copy versus netlink reads. Test signals include HFI CPUID parsing, CPU online/offline package transitions, thermal netlink bind/unbind enabling, package HFI interrupt ack with duplicate timestamp, suspend/resume, and multi-package capability event chunking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_hfi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_hfi.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_hfi.h

## Purpose

`intel_hfi.h` declares the HFI hooks used by the x86 thermal interrupt/hotplug code and provides no-op stubs when HFI thermal support is not enabled.

## Important APIs, Types, and Functions

The API surface is `intel_hfi_init()`, `intel_hfi_online()`, `intel_hfi_offline()`, and `intel_hfi_process_event()`. Under `CONFIG_INTEL_HFI_THERMAL` these are external declarations; otherwise static inline stubs compile away callers.

## Control Flow

The header contains no runtime flow beyond configuration-conditional no-op behavior. It allows `therm_throt.c` to call HFI hooks unconditionally.

## State and Persistence Behavior

No state is defined in the header. Runtime HFI state lives in `intel_hfi.c` when compiled.

## Dependencies and Integration Points

It integrates x86 thermal interrupt code with optional HFI support without forcing every build to include the HFI implementation.

## Risks and Test Signals

Risks are build-configuration drift and missing declarations if HFI call sites change. Test signals include builds with and without `CONFIG_INTEL_HFI_THERMAL`, CPU hotplug paths compiling with stubs, and HFI interrupt calls compiling under both configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_hfi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_pch_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_pch_thermal.c

## Purpose

`intel_pch_thermal.c` registers PCI PCH thermal sensors as Linux thermal zones, reads PCH temperature/trips from MMIO, and adds suspend-time cooling delay logic for S0ix reliability.

## Important APIs, Types, and Functions

`struct pch_thermal_device` stores BAR mapping, PCI device, thermal zone, and whether BIOS already enabled the sensor. `pch_thermal_get_temp()` reads WPT temperature. `intel_pch_thermal_probe()` enables PCI, maps BAR0, enables the thermal sensor if not locked, reads critical/hot trips, optionally reads ACPI passive `_PSV`, registers a board-named thermal zone, and enables it. PM callbacks disable/reenable non-BIOS sensors and delay suspend if PCH is hotter than threshold.

## Control Flow

Probe follows PCI enable/request/map, sensor enable, trip read, zone register. During noirq suspend, non-BIOS-enabled sensors are shut down; BIOS-enabled sensors during s2idle compare current temperature against the TSPM threshold and loop with sleeps until cooled, wakeup pending, or timeout. Resume reenables sensors that the driver enabled.

## State and Persistence Behavior

Driver state is per PCI device. Hardware sensor enable and trip registers persist in PCH MMIO. Module parameters `delay_timeout` and `delay_cnt` tune suspend cooling behavior.

## Dependencies and Integration Points

It depends on PCI, ACPI passive trip helpers, thermal core, PM suspend state, and many Intel PCH PCI IDs. Board IDs determine thermal-zone names.

## Risks and Test Signals

Risks include suspend delays in noirq context, unit conversion differences between raw and displayed temps, inability to enable locked sensors, no interrupts, and reliance on BIOS TSPM threshold. Test signals include probe on supported IDs, BIOS-enabled versus driver-enabled sensor paths, critical/hot/passive trips, s2idle cooling loop with wake abort, and resume re-enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_pch_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_powerclamp.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_powerclamp.c

## Purpose

`intel_powerclamp.c` registers a thermal cooling device that reduces package power by injecting forced idle time across selected CPUs, using idle injection and package C-state feedback.

## Important APIs, Types, and Functions

State is held in `struct powerclamp_data`, calibration array `cal_data[]`, cpumask, duration/window/max-idle parameters, and idle-inject device `ii_dev`. Cooling callbacks expose max/current/set state. `powerclamp_idle_injection_register()`, `trigger_idle_injection()`, `idle_inject_update()`, and `powerclamp_adjust_controls()` manage runtime idle injection and compensation. Debugfs exposes calibration data.

## Control Flow

Init checks Intel MWAIT and package C-state counters, allocates default CPU mask, registers cooling device, sets duration, and creates debugfs. Setting cooling state from zero starts idle injection; changing nonzero state adjusts runtime; setting zero stops and unregisters idle injection. The update callback periodically computes package C-state ratio, recalibrates compensation, and may skip an idle cycle when the package already meets target.

## State and Persistence Behavior

All state is in-memory module state. Module parameters persist only as runtime settings. Hardware feedback comes from package C-state MSRs; cooling action is scheduled idle injection.

## Dependencies and Integration Points

It depends on x86 MWAIT, package residency MSRs, `idle_inject`, thermal cooling devices, CPU masks, debugfs, and module parameters. Thermal governors can bind this cooling device to thermal zones.

## Risks and Test Signals

Risks include CPU mask/max-idle constraints, mutex trylock behavior in idle callback, delayed work after stop, calibration instability under external interrupts, and strong package topology assumptions. Test signals include module load gating, cpumask/max_idle/duration/window parameter validation, cooling state transitions, package C-state ratio reporting, debugfs creation, and unload while clamping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_powerclamp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_quark_dts_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_quark_dts_thermal.c

## Purpose

`intel_quark_dts_thermal.c` supports the Intel Quark X1000 digital thermal sensor through IOSF sideband registers, registering one polled thermal zone with hot and critical trips.

## Important APIs, Types, and Functions

`struct soc_sensor_entry` stores lock status, saved trip/enable registers, and thermal zone. `soc_dts_enable()`/`soc_dts_disable()` toggle DTS enable when unlocked. `get_trip_temp()` and `update_trip_temp()` read/write PTPS trip thresholds with the Quark temperature base. Thermal callbacks implement get temp, set trip, and change mode. `alloc_soc_dts()` initializes state and zone; `free_soc_dts()` restores saved registers.

## Control Flow

Module init verifies CPU ID and IOSF availability, then allocates the sensor. Allocation checks lock state, saves defaults when writable, sets writable trip flags only when unlocked, reads trips, registers a polling zone, and enables it. Set-trip clamps unsafe thresholds to 105C before programming. Exit restores enable/PTPS if writable and unregisters the zone.

## State and Persistence Behavior

The global `soc_dts` points to one runtime sensor entry. The driver saves original DTS enable and PTPS registers and restores them on exit unless locked. Polling delay is a module parameter.

## Dependencies and Integration Points

It depends on Quark CPU matching, IOSF MBI, thermal core, and polling thermal zones. It is separate from the newer Baytrail/SoC DTS helper.

## Risks and Test Signals

Risks include Celsius versus millicelsius expectations in trip/temp callbacks, locked register behavior, unsafe threshold clamping, IOSF failures under the shared mutex, and no interrupt support. Test signals include Quark-only module load, locked/unlocked register paths, trip read/write and restore, mode enable/disable, polling updates, and safe threshold clamp.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_quark_dts_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_soc_dts_iosf.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_soc_dts_iosf.c

## Purpose

`intel_soc_dts_iosf.c` is the shared IOSF sideband implementation for Intel SoC digital thermal sensors, registering two sensor zones and handling programmable thresholds and interrupts.

## Important APIs, Types, and Functions

Exports are `intel_soc_dts_iosf_init()`, `intel_soc_dts_iosf_exit()`, and `intel_soc_dts_iosf_interrupt_handler()`. `update_trip_temp()` writes PTPS/PTMC/TE registers with rollback. `sys_get_curr_temp()` converts DTS distance-to-TjMax into millicelsius. `add_dts_thermal_zone()` registers `soc_dts0`/`soc_dts1`. `set_trip()` initializes thermal trip descriptors.

## Control Flow

Init checks IOSF and TjMax, allocates `struct intel_soc_dts_sensors`, initializes locks, resets trip slots, configures passive or critical trips, and registers/enables each DTS zone. Interrupt handling deasserts APIC status, checks sticky trip bits, clears them, and updates both thermal zones. Exit unregisters zones, restores saved enable state, resets trips, and frees memory.

## State and Persistence Behavior

Per-instance state records TjMax, interrupt type, locks, and two sensor entries with saved enable state. Firmware/PMC registers hold actual sensor enable, threshold, status, and interrupt enable bits.

## Dependencies and Integration Points

It depends on IOSF MBI, Intel TCC, thermal core, and callers such as `intel_soc_dts_thermal.c` and legacy processor thermal PCI DTS support. Interrupt type controls whether APIC and/or MSI bits are set.

## Risks and Test Signals

Risks include rollback writing `store_te_out` to PTMC in one error path, shared threshold programming across sensors, BIOS-used trip slots becoming read-only, interrupt sticky clearing races, and TjMax dependency. Test signals include two-zone registration, writable/read-only trip selection, APIC/MSI interrupt config, interrupt handler zone updates, exit restore, and IOSF error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_soc_dts_iosf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_soc_dts_iosf.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_soc_dts_iosf.h

## Purpose

`intel_soc_dts_iosf.h` declares the shared data structures and APIs for Intel SoC DTS sensors accessed through IOSF sideband registers.

## Important APIs, Types, and Functions

It defines `SOC_MAX_DTS_SENSORS` as 2 and `SOC_MAX_DTS_TRIPS` as 2. `enum intel_soc_dts_interrupt_type` distinguishes none, APIC, MSI, SCI, and SMI. `struct intel_soc_dts_sensor_entry` stores ID, saved status, thermal zone, and backpointer. `struct intel_soc_dts_sensors` stores TjMax, locks, interrupt type, and sensor entries. Prototypes expose init, exit, and interrupt handler.

## Control Flow

The header contains no executable flow. It defines how platform-specific callers instantiate and interact with the IOSF DTS core.

## State and Persistence Behavior

The defined structures represent runtime state. Saved register status is used by the implementation to restore hardware state during exit.

## Dependencies and Integration Points

It depends on `linux/thermal.h` and is included by standalone SoC DTS and legacy processor thermal PCI code.

## Risks and Test Signals

Risks are structural coupling with the implementation and callers assuming exactly two sensors/trips. Test signals include compile coverage for APIC and MSI callers and runtime init/exit using the saved-state fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_soc_dts_iosf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_soc_dts_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_soc_dts_thermal.c

## Purpose

`intel_soc_dts_thermal.c` is the platform module that enables IOSF SoC DTS thermal zones and APIC threshold interrupts on supported Intel Atom Silvermont/Baytrail systems.

## Important APIs, Types, and Functions

Module parameter `crit_offset` sets the critical trip offset from TjMax. `soc_irq_thread_fn()` forwards threshold IRQs to `intel_soc_dts_iosf_interrupt_handler()`. `intel_soc_thermal_init()` matches CPU IDs, initializes IOSF DTS with APIC interrupts and critical trips, registers the fixed GSI, and requests a threaded IRQ. Exit frees IRQ/GSI and exits the DTS core.

## Control Flow

Init is CPU gated. It creates DTS zones first so polling remains usable even if IRQ setup fails. It then maps the fixed APIC GSI 86 and requests a threaded interrupt, warning but not failing if IRQ request fails. Exit unwinds IRQ/GSI and sensor state.

## State and Persistence Behavior

Static globals store the GSI, Linux IRQ, and DTS sensor pointer. DTS register persistence/restoration is handled by the shared IOSF implementation.

## Dependencies and Integration Points

It depends on ACPI GSI registration, x86 CPU matching, IRQ APIs, and `intel_soc_dts_iosf`. It is the APIC-interrupt frontend for the shared IOSF DTS core.

## Risks and Test Signals

Risks include fixed GSI assumptions, IRQ flag requirements matching firmware defaults, nonfatal interrupt setup leaving polling-only behavior, and `crit_offset` values that create invalid critical trips. Test signals include CPU match gating, DTS init with critical trips, GSI register/unregister, threaded IRQ forwarding, and cleanup after IRQ request failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_soc_dts_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_tcc.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_tcc.c

## Purpose

`intel_tcc.c` is a library for Intel Thermal Control Circuitry MSR access. It provides model-specific masks for TCC offset and temperature readouts, TjMax lookup, TCC offset get/set, and current core/package temperature reads.

## Important APIs, Types, and Functions

`struct temp_masks` stores per-model bitmasks. `intel_tcc_init()` selects masks during `subsys_initcall`. Exports are `intel_tcc_get_offset_mask()`, `intel_tcc_get_tjmax()`, `intel_tcc_get_offset()`, `intel_tcc_set_offset()`, and `intel_tcc_get_temp()`. `get_temp_mask()` chooses core or package digital readout mask.

## Control Flow

Early init matches a long CPU model table and copies matching masks, otherwise defaults are used. Getters read MSRs on any CPU or a specified CPU. Setting offset validates support/range, checks the MSR lock bit, updates bits 24+ with the model mask, and writes back. Temperature reads require valid status bit and return `TjMax - digital_readout` in Celsius.

## State and Persistence Behavior

The selected `intel_tcc_temp_masks` is `__ro_after_init`. Hardware TCC offset persists in `MSR_IA32_TEMPERATURE_TARGET` until changed/reset. No dynamic allocation occurs.

## Dependencies and Integration Points

It depends on x86 CPU matching, MSR helpers, Intel family IDs, and exports namespace `INTEL_TCC`. Processor thermal, DTS, TCC cooling, and package temperature drivers use it.

## Risks and Test Signals

Risks include model mask table drift, MSR access failures on offline CPUs, lock-bit denial, invalid status bit returning `-ENODATA`, and unit expectations by callers. Test signals include model-specific mask selection, TjMax zero handling, offset set range/lock checks, core/package temp reads, and builds for namespace imports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_tcc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_tcc_cooling.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_tcc_cooling.c

## Purpose

`intel_tcc_cooling.c` registers a thermal cooling device that throttles processors by programming the TCC offset register through the Intel TCC library.

## Important APIs, Types, and Functions

The cooling callbacks are `tcc_get_max_state()`, `tcc_get_cur_state()`, and `tcc_set_cur_state()`, which map state directly to TCC offset degrees. `tcc_cooling_init()` checks supported CPU IDs, platform programmability bit, temperature target MSR, lock bit, and registers cooling device `TCC Offset`.

## Control Flow

Module init is gated by CPU model, `MSR_PLATFORM_INFO` bit 30, and `MSR_IA32_TEMPERATURE_TARGET` lock bit. On success, thermal governors can set cooling state; set calls `intel_tcc_set_offset(-1, state)`. Exit unregisters the cooling device.

## State and Persistence Behavior

Only the global cooling-device pointer is stored. Hardware TCC offset persists in the MSR until another component changes it or reset occurs.

## Dependencies and Integration Points

It depends on the Intel TCC namespace, thermal cooling device framework, x86 CPU matching, and MSR helpers. Thermal zones may bind it as an active cooling device.

## Risks and Test Signals

Risks include direct global TCC offset changes affecting all CPUs, CPU model whitelist maintenance, lock/prog bit mismatch, and no saved/restore of previous offset. Test signals include init gating, cooling max/current/set callbacks, governor binding, lock-bit rejection, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_tcc_cooling.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/therm_throt.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/therm_throt.c

## Purpose

`therm_throt.c` is the x86 Intel thermal interrupt and throttling event core. It configures local APIC thermal vectors and MSR interrupt enables, counts/logs core/package thermal and power-limit events, exposes per-CPU sysfs counters, and calls platform/HFI threshold callbacks.

## Important APIs, Types, and Functions

Key state types are `_thermal_state` and per-CPU `struct thermal_state`. Exported callback pointers are `platform_thermal_notify`, `platform_thermal_package_notify`, and `platform_thermal_package_rate_control`. Public functions include `thermal_clear_package_intr_status()`, `intel_thermal_interrupt()`, `x86_thermal_enabled()`, `therm_lvt_init()`, and `intel_init_thermal()`. CPU hotplug callbacks initialize work, HFI, APIC unmasking, and sysfs groups.

## Control Flow

CPU thermal initialization verifies APIC/ACPI/clock-modulation support, respects BIOS SMI ownership, masks the APIC vector, initializes clear masks, enables threshold/power-limit/HFI MSR interrupts, enables TM1, and marks throttling enabled. Device init later registers CPU hotplug if enabled. Runtime interrupt handling clears HWP status, reads core/package thermal MSRs, notifies platform threshold handlers, tracks throttling/power-limit state transitions, and forwards HFI updates. Delayed work rate-limits logs while throttling remains active.

## State and Persistence Behavior

Per-CPU counters, timestamps, rate-control fields, and work items persist while CPUs are online. Sysfs exposes counts and throttle durations. APIC LVT and MSR interrupt configuration are per-CPU hardware state.

## Dependencies and Integration Points

It depends on x86 APIC/MSR features, CPU hotplug, sysfs CPU devices, HFI hooks, package temp thermal callbacks, and weak HWP notification override. `thermal_interrupt.h` exposes callback and clear APIs to peer drivers.

## Risks and Test Signals

Risks include BIOS SMI ownership detection, interrupt clear-mask correctness, APIC mask/unmask ordering with HFI, delayed work on CPU offline, platform callback rate control, and optional `int_pln_enable` changing power-limit behavior. Test signals include boot thermal init, CPU online/offline sysfs lifecycle, threshold interrupts, package temp callback integration, HFI event forwarding, throttling duration counters, and HWP status clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/therm_throt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/thermal_interrupt.h -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/thermal_interrupt.h

## Purpose

`thermal_interrupt.h` declares the shared x86 Intel thermal interrupt interfaces used by throttling, HFI, and package temperature drivers.

## Important APIs, Types, and Functions

It defines `CORE_LEVEL` and `PACKAGE_LEVEL`, declares platform threshold callback pointers, declares the rate-control callback, declares weak-overridable `notify_hwp_interrupt()`, and declares `thermal_clear_package_intr_status()`.

## Control Flow

There is no runtime flow in the header. It provides the common contract that lets independent drivers register callbacks and clear thermal status bits without circular includes.

## State and Persistence Behavior

The callback pointers are extern state defined in `therm_throt.c`. The header itself owns no storage.

## Dependencies and Integration Points

It integrates `x86_pkg_temp_thermal.c`, `intel_hfi.c`, and `therm_throt.c`. Core/package level constants must match the implementation's MSR selection.

## Risks and Test Signals

Risks include global callback pointer ownership, missing synchronization around callback updates, and callers passing incorrect level/bit masks. Test signals include builds of all users, package temp callback registration/removal, HFI status clear calls, and HWP override linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/thermal_interrupt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/x86_pkg_temp_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/intel/x86_pkg_temp_thermal.c

## Purpose

`x86_pkg_temp_thermal.c` registers per-package/die thermal zones using package temperature MSRs and handles package threshold interrupts through the global Intel thermal interrupt callback mechanism.

## Important APIs, Types, and Functions

`struct zone_device` stores target CPU, delayed work state, saved package interrupt MSR, thermal zone, and package CPU mask. `sys_get_curr_temp()` uses `intel_tcc_get_temp(..., pkg=true)`. `sys_set_trip_temp()` programs threshold 0/1 in `MSR_IA32_PACKAGE_THERM_INTERRUPT`. `pkg_thermal_notify()` is assigned to `platform_thermal_package_notify`. CPU hotplug callbacks create/remove package zones.

## Control Flow

Module init matches Intel PTS, allocates a zone pointer array sized by packages times dies, registers CPU hotplug state, and installs package notification callbacks. First CPU in a package creates an `x86_pkg_temp` zone with writable passive trips based on CPUID threshold count and saved MSR thresholds. Package threshold interrupt disables threshold interrupts and schedules delayed work. Work clears sticky status, reenables valid threshold interrupts, and updates the zone. CPU offline migrates work target or unregisters/frees the zone for the last CPU.

## State and Persistence Behavior

Global `zones[]`, debug counters, and callback pointers persist while loaded. Each zone saves the original package interrupt MSR and restores it when the last CPU in the package exits. Delayed work state is protected by raw spinlock and zone mutex.

## Dependencies and Integration Points

It depends on Intel TCC library, CPU hotplug, topology logical die IDs, thermal core, debugfs, MSR threshold definitions, and `thermal_interrupt.h` callback hooks.

## Risks and Test Signals

Risks include hotplug/work/interrupt races, callback pointer synchronization, package/die indexing, threshold unit conversion against TjMax, interrupt remaining disabled if work migration fails, and debugfs-only observability for interrupt/work counts. Test signals include CPU hotplug package creation/migration/removal, trip set/clear MSR writes, threshold interrupt rate control, work cancellation on offline, MSR restore on last CPU, and module unload callback cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/intel/x86_pkg_temp_thermal.c -->
