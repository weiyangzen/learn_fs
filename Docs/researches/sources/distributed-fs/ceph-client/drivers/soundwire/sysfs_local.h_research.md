# sources/distributed-fs/ceph-client/drivers/soundwire/sysfs_local.h

## Purpose

`sysfs_local.h` declares local SoundWire sysfs groups and the DPn sysfs initialization helper shared by slave setup and sysfs implementation files.

## Important APIs, types, and functions

- `sdw_slave_status_attr_groups` exposes basic slave status and device number at device creation.
- `sdw_attr_groups` exposes generic SoundWire slave attributes, device properties, and DP0 attributes.
- `sdw_slave_sysfs_dpn_init()` initializes additional device-managed DPn sysfs properties after slave driver probe.

## Control flow

`slave.c` assigns `sdw_slave_status_attr_groups` to newly created slave devices. Other SoundWire driver paths use `sdw_attr_groups` and `sdw_slave_sysfs_dpn_init()` when full property exposure is appropriate after property discovery/probe.

## State and persistence behavior

The header has no state. The declared groups are static data owned by sysfs implementation files. DPn sysfs state is device-managed by the implementation.

## Dependencies and integration points

It depends on `struct sdw_slave` and is consumed by `slave.c`, `sysfs_slave.c`, and the DPn sysfs implementation in the same driver directory.

## Risks and edge cases

- The split between status-only groups and full attribute groups must match slave lifecycle; full attributes should not be exposed before properties are populated.
- Header declarations must remain synchronized with the implementation files.

## Test signals

Compile all SoundWire sysfs files together and verify slave devices expose status attributes immediately, full properties after property setup, and DPn groups after `sdw_slave_sysfs_dpn_init()`.
