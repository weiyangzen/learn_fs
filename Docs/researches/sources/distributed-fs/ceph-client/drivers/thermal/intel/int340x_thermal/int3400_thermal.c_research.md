# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int3400_thermal.c

## Purpose
ACPI INT3400 master thermal driver. It negotiates thermal policy UUIDs with firmware through `_OSC`, parses ACPI relationship tables, registers a fake-temperature thermal zone for notifications, exposes policy/data sysfs files, registers the relationship misc device, handles ACPI notifications, and supports ODVP/production-mode metadata.

## Important APIs, Types, and Functions
- `struct int3400_thermal_priv` stores ACPI/platform devices, thermal zone, ART/TRT arrays, supported/current UUID state, relationship misc registration result, data vault, ODVP data, OS UUID mask, production mode, and dynamic ODVP attributes.
- UUID arrays enumerate active, passive, critical, adaptive performance, emergency, virtual sensor, cooling mode, and duty-cycling policies.
- Sysfs handlers: `available_uuids_show()`, `current_uuid_show/store()`, `imok_store()`, `production_mode_show()`, and dynamic ODVP attributes.
- `int3400_thermal_run_osc()` executes ACPI `_OSC` for a UUID/capability bit and validates firmware response.
- `set_os_uuid_mask()` uses the newer OS capability UUID path for active/passive/critical policies.
- `int3400_thermal_get_uuids()` evaluates `IDSP` and builds supported UUID bitmap.
- `evaluate_odvp()` evaluates `ODVP`, allocates values and per-index sysfs files.
- `int3400_notify()` maps ACPI events to thermal events and emits uevents.
- `int3400_thermal_change_mode()` enables/disables the selected policy via `_OSC` and refreshes ODVP.
- Probe wires all pieces together; remove unwinds them.

## Control Flow
Probe requires an ACPI companion, allocates private state, reads supported UUIDs if `IDSP` exists, parses ART/TRT tables with device creation, stores drvdata, optionally captures GDDV data vault, evaluates ODVP, registers a tripless fake thermal zone, registers the ACPI relationship misc device, creates UUID and optional IMOK/data-vault sysfs, installs an ACPI notify handler, and initializes production mode sysfs if `DCFG` exists. Users select a current UUID via sysfs or set an OS UUID capability mask. Thermal mode changes run `_OSC` to enable/disable the selected policy and then refresh ODVP. ACPI notifications generate thermal uevents for table change, keep-alive, or ODVP change.

## State and Persistence
Private state tracks current UUID index or OS UUID mask, supported UUID bitmap, parsed ART/TRT arrays, ODVP values, production mode, and optional data vault. Firmware policy enablement persists in ACPI/firmware after `_OSC` until changed. The thermal zone always reports fake 20C.

## Dependencies and Integration Points
Depends on ACPI methods (`IDSP`, `_OSC`, `_ART`, `_TRT`, `GDDV`, `ODVP`, `IMOK`, `DCFG`), the ACPI relationship helper, thermal zone/uevent APIs, sysfs/bin attributes, ACPI notify handlers, and userspace policy daemons such as thermald.

## Risks and Edge Cases
- UUID matching in `current_uuid_store()` uses only a 7-character prefix, allowing ambiguous/partial inputs if prefixes collide.
- Fake temperature means the zone is an event/control endpoint, not a real sensor.
- Several `kasprintf()` calls in notify are unchecked before uevent.
- Error unwinding has many sysfs/misc/thermal steps; missing optional IMOK group removal is tolerated but should be reviewed.
- Global misc-device relationship helper limits multiple INT3400 instances.
- ODVP dynamic sysfs creation must clean up partially created attributes on failure.

## Test Signals
Tests should cover missing and malformed `IDSP`, UUID sysfs read/write, `_OSC` success/failure, OS UUID mask enable/disable, ART/TRT parse failures as nonfatal, GDDV data-vault creation, ODVP creation/update/cleanup, ACPI notification uevents, production-mode sysfs, and probe error unwinding at each stage.
