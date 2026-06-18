# sources/distributed-fs/ceph-client/drivers/soundwire/mipi_disco.c

## Purpose

`mipi_disco.c` reads MIPI SoundWire DisCo firmware properties for masters and slaves from generic device properties/fwnodes. It populates bus, slave, DP0, DPn, lane mapping, and capability structures used by enumeration, stream setup, sysfs, and controller-specific policy.

## Important APIs, types, and functions

- `sdw_master_read_prop()` reads master revision, clock-stop modes, clock frequencies/gears, default frame rate/row/col, dynamic frame support, and error threshold.
- `sdw_slave_read_prop()` reads slave capabilities, source/sink port lists, SDCA interrupt register list, commit register support, DP0 properties, DPn source/sink properties, and lane mappings.
- `sdw_slave_read_lane_mapping()` parses `mipi-sdw-lane-N-mapping` strings into `slave->prop.lane_maps`.
- Internal helpers read firmware booleans encoded as u8 properties, DP0 properties, and per-port DPn properties.

## Control flow

Controller or bus code calls `sdw_master_read_prop()` during master registration/property read. It locates `mipi-sdw-link-N-subproperties`, reads optional properties, allocates arrays for clock frequencies/gears, derives `max_clk_freq` if missing, and releases the fwnode.

Slave drivers or bus code call `sdw_slave_read_prop()` after a slave device is created. The function reads top-level slave capabilities, optionally reads `mipi-sdw-dp-0-subproperties`, allocates arrays sized by source/sink port bit counts, reads each named `mipi-sdw-dp-N-source/sink-subproperties` child, and finally parses lane mappings.

## State and persistence behavior

The file fills `bus->prop` and `slave->prop` structures. Variable-sized arrays are devm-allocated against the bus device or slave device, so they persist for the relevant device lifetime. There is no hardware state or on-disk state.

## Dependencies and integration points

It depends on Linux firmware property APIs, SoundWire public structures, and the local bus header. The resulting properties feed sysfs (`master.c`, `sysfs_slave.c`), stream validation/configuration (`stream.c`), Intel/Qualcomm policy, and slave driver callbacks.

## Risks and edge cases

- Several helper calls ignore return values, especially DP0/DPn reads, so missing or malformed properties can leave zero/default fields without aborting.
- Boolean properties are read as u8 arrays rather than standard boolean presence, matching DisCo encoding but sensitive to firmware representation.
- `sdw_slave_read_dpn()` has a `count` parameter that is not used to bound writes; correctness depends on the port bitmask and allocation count matching.
- Some `fwnode_handle_put()` paths are missing on early return after read errors, which is a leak risk.
- `wake_capable` is inverted from `mipi-sdw-wake-up-unavailable`, which is easy to misread.
- Lane mapping parses the final character as a decimal manager lane and does not model peripheral-link letters described in the comment.

## Test signals

Use ACPI/DT fixtures with full, partial, and malformed DisCo properties. Verify clock frequency/gears allocation, max clock derivation, DP0 sysfs visibility, source/sink port property arrays, lane mappings, wake capability inversion, and error behavior when child nodes are missing. Static analysis should check fwnode put coverage and array bounds relative to port bit counts.
