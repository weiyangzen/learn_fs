# sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_ethtool.c

## Purpose

This file implements ethtool statistics support for SJA1105/SJA1110 switch ports. It maps hardware diagnostic counter registers into DSA ethtool string, count, and value callbacks. First-generation E/T devices expose MAC and high-level counters, while later devices add Ethernet statistics.

## Important APIs, Types, and Data

- `enum sja1105_counter_index` gives stable array indexes for MAC, high-level 1, high-level 2, and P/Q/R/S-only ETHER counters.
- `struct sja1105_port_counter` describes one exported counter: stats area, ethtool name, register offset, bit range, and whether the counter spans 64 bits.
- `sja1105_port_counters[]` is the central hardware-to-ethtool mapping.
- `sja1105_port_counter_read()` reads the relevant register area through SPI and unpacks the requested bitfield.
- `sja1105_get_ethtool_stats()`, `sja1105_get_strings()`, and `sja1105_get_sset_count()` are wired into `dsa_switch_ops`.

## Control Flow

The DSA ethtool callbacks choose a maximum counter index based on `priv->info->device_id`: E/T stops at `__MAX_SJA1105ET_PORT_COUNTER`; all other supported chips use `__MAX_SJA1105PQRS_PORT_COUNTER`. Empty names are skipped, allowing sparse enum positions. Stats reading loops through the selected counters, calls `sja1105_port_counter_read()`, and fills the output array in the same order as `get_strings()` and `get_sset_count()`.

The low-level read computes the base register from `priv->info->regs->stats[c->area][port]`, adds the counter offset, reads 4 or 8 bytes with `sja1105_xfer_buf()`, and unpacks the configured bit range into a 64-bit value.

## State and Persistence Behavior

This file has no persistent software state. It reads hardware counters in place and reports the current values. It does not clear counters, cache values, or preserve values across switch reset; reset behavior is entirely determined by hardware.

## Dependencies and Integration Points

The code depends on register base arrays in `struct sja1105_regs`, SPI helper `sja1105_xfer_buf()`, and packing helper `sja1105_unpack()`. It integrates with DSA through `.get_ethtool_stats`, `.get_strings`, and `.get_sset_count` in `sja1105_main.c`.

## Risks and Edge Cases

- Counter layout differs by generation; using the wrong max counter limit or register map would expose invalid names or read reserved locations.
- Some counters are subfields within one 32-bit word; incorrect start/end bits would produce plausible but wrong values.
- The stats loop logs and stops at the first SPI read error, leaving later output entries unchanged by this callback.
- 64-bit counters require an 8-byte SPI read, so SPI master transfer limits and chunking must support that path.

## Test Signals

`ethtool -S <port>` should show the same number and order of names as `get_sset_count()` reports. On E/T, ETHER-only counters should be absent; on P/Q/R/S/SJA1110 they should be present. Traffic generation should increment RX/TX frame and byte counters, while error injection or VLAN drops should move the corresponding diagnostic counters. SPI failures should produce a driver error message and not crash the stats path.
