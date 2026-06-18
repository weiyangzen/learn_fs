# sources/distributed-fs/ceph-client/drivers/soundwire/sysfs_slave.c

## Purpose

`sysfs_slave.c` defines sysfs attributes for SoundWire slave devices. It exposes modalias, generic DisCo slave properties, optional DP0 properties, and basic live status/device-number attributes.

## Important APIs, types, and functions

- Macro-generated slave property attributes expose fields from `slave->prop`.
- `modalias_show()` formats the SoundWire modalias for driver matching/user inspection.
- `sdw_attr_groups` contains the modalias group, `dev-properties`, and conditional `dp0`.
- DP0 attributes expose max/min word length, supported word lengths, BRA flow control, simple channel prepare, and implementation-defined interrupts.
- `sdw_slave_status_attr_groups` contains live `status` and `device_number`.
- `dp0_attr_visible()` and `dp0_group_visible()` hide DP0 files when `slave->prop.dp0_prop` is absent.

## Control flow

When a slave device is registered, `slave.c` initially attaches status groups. After properties are available, full groups can expose the DisCo data. Reading an attribute fetches current values from `struct sdw_slave` or `slave->prop`. `device_number_show()` reports `N/A` when the slave is unattached and the numeric dev number otherwise.

## State and persistence behavior

This file owns static `attribute` and `attribute_group` definitions. It does not mutate state. Attribute values reflect current in-memory `struct sdw_slave` fields and property arrays allocated by DisCo parsing, plus live `slave->status` and `slave->dev_num` updated by enumeration.

## Dependencies and integration points

It depends on Linux sysfs/device APIs, SoundWire public types, `sdw_slave_modalias()`, and property data populated by `mipi_disco.c` and controller enumeration. `sysfs_local.h` exports the groups for use by slave setup.

## Risks and edge cases

- Several show functions assume property pointers and arrays are valid when groups are visible; exposing full groups too early can dereference null pointers.
- `device_number_show()` omits a trailing newline for both `N/A` and numeric values, which is unusual for sysfs.
- `status_show()` indexes `slave_status[]` by enum value; invalid status values would read out of bounds.
- Output uses `sprintf` into sysfs buffers; current values are small, but future list attributes should preserve bounds.

## Test signals

Validate sysfs output for unattached, attached, alert, and reserved statuses; DP0 group absence/presence; modalias format; all DisCo property fields after parsing; word list formatting; and behavior after device removal. A targeted style/regression test should check whether `device_number` should include a newline.
