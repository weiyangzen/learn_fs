# sources/distributed-fs/ceph-client/drivers/soundwire/slave.c

## Purpose

`slave.c` creates and discovers Linux SoundWire slave devices. It allocates slave objects, names/registers them on the SoundWire bus, initializes completions and locks, preloads SDCA information, supports ACPI and device-tree discovery, detects duplicate ACPI unique IDs, and exports an OF node lookup helper.

## Important APIs, types, and functions

- `sdw_slave_add()` allocates/registers a slave and adds it to `bus->slaves`.
- `sdw_slave_type` defines the slave device type, release callback, and uevent callback.
- `sdw_acpi_find_slaves()` scans ACPI children under the master and registers matching slaves.
- `sdw_of_find_slaves()` scans DT children with `compatible = "sdw..."` and matching `reg` link id.
- `of_sdw_find_device_by_node()` finds a SoundWire device by OF node.
- ACPI helpers `find_slave()`, `sdw_acpi_check_duplicate()`, and `sdw_acpi_find_one()` parse ADR, apply optional DMI ADR override, match link id, and handle unique-id suppression.

## Control flow

Discovery calls either ACPI or OF scanning. ACPI walks child devices, skips unavailable children, reads local ADR, optionally overrides it, extracts link id and slave id, performs an O(N^2) duplicate check for identical manufacturer/part/class/unique ids, optionally ignores unique id when no duplicate requires it, and calls `sdw_slave_add()`. OF scanning parses the compatible string into SoundWire version/manufacturer/part/class, reads `reg` for link and unique id, filters by bus link id, and adds the slave.

`sdw_slave_add()` initializes identity, parent/fwnode/of_node, bus/type/groups, status, completions, port-ready completions, device number, probed/interrupt flags, and a device lock. It inserts the slave into `bus->slaves` under `bus_lock`, reads SDCA interface/function data before device registration, registers the device, and initializes debugfs. Failure removes the list node and drops the device reference.

## State and persistence behavior

Each `struct sdw_slave` persists as a Linux device until release, with state for status, dev_num, sticky enumeration, completions, probed flag, first interrupt, port readiness, SDCA information, firmware node, and list membership. No hardware state is directly programmed here; enumeration and attachment status are handled by bus/controller code.

## Dependencies and integration points

This file depends on ACPI, OF, SoundWire bus type, sysfs groups from `sysfs_slave.c`, debugfs helper declarations, SDCA lookup functions, and bus helpers for ID extraction/comparison. Slave drivers bind through `sdw_bus_type` after `device_register()`.

## Risks and edge cases

- ACPI duplicate detection is O(N^2), acceptable for small numbers but sensitive to firmware errors.
- ACPI unique id may be intentionally ignored when no duplicates require it, changing device names and match behavior.
- `sdw_slave_add()` ignores the return from `sdca_lookup_*` helpers and from debugfs init.
- OF compatible parsing is strict; malformed strings are skipped.
- If `device_register()` fails, the object is freed by release after `put_device()`, so no direct free is allowed.
- The initial status group exposes status/device number before attachment; users must handle `UNATTACHED` and `N/A`.

## Test signals

Test ACPI discovery with duplicate and unique IDs, DMI ADR override, unavailable ACPI children, OF compatible/reg parsing, device-register failure, SDCA function discovery, debugfs creation, slave release of OF node and mutex, and lookup by OF node. Device names should match ignored versus explicit unique-id cases.
