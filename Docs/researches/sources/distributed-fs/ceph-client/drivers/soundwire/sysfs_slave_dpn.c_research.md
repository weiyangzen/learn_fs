# sources/distributed-fs/ceph-client/drivers/soundwire/sysfs_slave_dpn.c

## Purpose

`sysfs_slave_dpn.c` builds per-data-port sysfs attribute groups for SoundWire slave devices. It exposes read-only `dpN_src` and `dpN_sink` directories under the slave device, with one attribute per `struct sdw_dpn_prop` capability such as word widths, channel counts, supported channel combinations, interrupt bits, async buffer size, block-pack mode, and port encoding.

The file is metadata publication code. It does not program SoundWire hardware; it converts the discovery-time `slave->prop.source_ports`, `slave->prop.sink_ports`, `src_dpn_prop`, and `sink_dpn_prop` arrays into sysfs files.

## Important APIs, types, and functions

- `struct dpn_attribute` embeds `struct device_attribute` and records the logical port number `N`, direction `dir`, and printf-style format string used by the generated show callback.
- `sdw_dpn_attr(field)` generates a scalar `field_show()`, a `field_dpn_show()` helper, and an allocator for each scalar DPN property.
- `sdw_dpn_array_attr(field)` does the same for variable-length arrays: `words`, `ch_combinations`, and `channels`.
- `add_all_attributes()` allocates the 15 attributes, verifies the hard-coded `SDW_DPN_ATTRIBUTES` count, creates an attribute group named `dp%d_src` or `dp%d_sink`, and registers it with `devm_device_add_group()`.
- `sdw_slave_sysfs_dpn_init()` is the exported initializer. It walks all source and sink port bits and invokes `add_all_attributes()`.

## Control flow

`sdw_slave_sysfs_dpn_init()` returns immediately when the slave has no source or sink ports. Otherwise it iterates set bits in the source-port mask and creates source groups, then does the same for sink ports. Each group contains all 15 attribute files.

At read time, a sysfs show callback recovers `struct sdw_slave` through `dev_to_sdw_dev()`, recovers the containing `struct dpn_attribute`, selects either `src_dpn_prop` or `sink_dpn_prop`, then iterates the corresponding port mask. The property-array index increments only for set ports, so bit number `N` maps to the dense DPN property entry for that advertised port.

## State and persistence behavior

All allocations are device-managed with `devm_kzalloc()`, `devm_kcalloc()`, `devm_kasprintf()`, and `devm_device_add_group()`. There is no independent persistence beyond the lifetime of the SoundWire slave device. Attribute values are read directly from `slave->prop`; if those properties changed after registration, sysfs would reflect the new in-memory values, but the normal model is static discovery data.

## Dependencies and integration points

The file depends on the SoundWire core types from `linux/soundwire/sdw.h`, `sdw_type.h`, local `bus.h`, and `sysfs_local.h`. It integrates with the slave sysfs setup path through `sdw_slave_sysfs_dpn_init()` and relies on `struct sdw_dpn_prop` layout matching the generated field names.

The sysfs ABI is the visible integration point: userspace can inspect per-port capability files under `dpN_src` and `dpN_sink`, while kernel code consumes only the initializer.

## Risks and edge cases

- `SDW_DPN_ATTRIBUTES` is manually maintained. The local mismatch check catches the final count, but only after allocation attempts.
- The array properties are printed one value per line and then an extra newline. Consumers should treat them as lists rather than single scalar values.
- The dense property-array indexing assumes the property arrays are ordered exactly by ascending set bits in `source_ports` and `sink_ports`.
- The generated show callbacks return `-EINVAL` if a group's recorded port number no longer appears in the mask. That should not happen in normal use.
- The code uses `sprintf()` into sysfs buffers. Values are small, but future larger arrays should keep sysfs page-size limits in mind.

## Test signals

Useful checks are compile coverage for `CONFIG_SOUNDWIRE`, boot/probe coverage with SoundWire slaves that advertise multiple sparse source and sink ports, and sysfs inspection confirming each `dpN_*` group contains exactly the 15 expected files. Negative tests should cover devices with no DPN ports and sparse masks such as ports 1 and 7 to validate property-array indexing.
