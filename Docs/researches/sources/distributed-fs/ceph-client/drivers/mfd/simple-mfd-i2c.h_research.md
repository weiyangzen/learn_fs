# sources/distributed-fs/ceph-client/drivers/mfd/simple-mfd-i2c.h

## Purpose
`simple-mfd-i2c.h` defines the match-data contract used by the simple I2C MFD parent driver.

## Important APIs, Types, and Functions
`struct simple_mfd_data` contains an optional `const struct regmap_config *regmap_config`, an optional `const struct mfd_cell *mfd_cell`, and `size_t mfd_cell_size`.

## Control Flow
There is no runtime control flow in this header. `simple-mfd-i2c.c` reads this structure during probe to select regmap formatting and decide whether to register static child cells.

## State and Persistence
The structure is immutable match data for OF device IDs. It contains pointers to static config tables and no mutable state.

## Dependencies and Integration Points
The header depends on `linux/mfd/core.h` and `linux/regmap.h`. It is private to this driver directory and couples OF match entries to MFD child registration.

## Risks and Edge Cases
The structure does not encode validation, so mismatched `mfd_cell_size`, stale cell names, or an incorrect regmap config fail only at runtime.

## Test Signals
Compile coverage, correct designated initializers, and successful probe of each compatible using static `simple_mfd_data` exercise this header.
