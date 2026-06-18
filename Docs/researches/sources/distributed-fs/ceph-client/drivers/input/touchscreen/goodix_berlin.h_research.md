# sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix_berlin.h

## Purpose
`goodix_berlin.h` is the private interface between the Goodix Berlin common core and its I2C/SPI transport drivers. It defines per-IC register metadata and exports the shared probe, PM operations, and sysfs attribute groups.

## Important APIs, types, and functions
- `GOODIX_BERLIN_FW_VERSION_INFO_ADDR_A/D` and `GOODIX_BERLIN_IC_INFO_ADDR_A/D` define revision-specific firmware-version and IC-info addresses.
- `struct goodix_berlin_ic_data` passes transport/chip metadata into the core: firmware version address, IC-info address, and SPI read dummy/prefix lengths.
- `goodix_berlin_probe()` is the core entry point called by both bus drivers with a `struct device`, IRQ, input ID, regmap, and IC data.
- `goodix_berlin_pm_ops` and `goodix_berlin_groups` are exported from the core for direct use in the I2C and SPI driver structs.

## Control flow
Bus-specific probe creates a regmap and selects a `goodix_berlin_ic_data` table from device match data, then hands control to `goodix_berlin_probe()`. PM and dev_groups in the transport drivers are shared through the declarations in this header.

## State and persistence
The header itself stores no state. Its IC data tables determine which on-chip addresses are read during core probe and how much prefix/dummy data the SPI regmap transport strips from reads.

## Dependencies and integration points
This file depends only on forward declarations plus `<linux/pm.h>`, keeping the bus drivers decoupled from core structure internals. It integrates the core module with `goodix_berlin_i2c.c` and `goodix_berlin_spi.c`.

## Risks
- I2C IC data leaves SPI prefix/dummy lengths zero by design; core code must not assume those fields are valid for all buses.
- Wrong firmware/IC-info addresses in a table make the core reject the device as checksum-invalid or dummy data.
- The exported attribute group includes raw register access; transport drivers inherit that surface automatically.

## Test signals
- Build all three Berlin modules together.
- Probe GT9916 over I2C and GT9897/GT9916 over SPI to validate IC-data table addresses and transport-specific prefix lengths.
- Check that module unload/order resolves exported `goodix_berlin_pm_ops`, `goodix_berlin_groups`, and `goodix_berlin_probe()`.
