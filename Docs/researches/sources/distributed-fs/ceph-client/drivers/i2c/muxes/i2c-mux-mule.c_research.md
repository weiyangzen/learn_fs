# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-mule.c

Purpose: Theobroma Systems Mule I2C device mux driver. It selects downstream emulated devices by writing a configuration register in the parent Mule MCU regmap.

Important APIs/types: `struct mule_i2c_reg_mux` stores the parent regmap. Constants define config register `0xff` and default device `0`.

Control flow: probe counts child nodes, gets the parent I2C client and regmap, allocates an `I2C_MUX_LOCKED` mux core, writes and reads back the default device to detect older firmware without mux support, registers devm cleanup, then iterates child nodes. Each child `reg` is selected to verify support before a child adapter is added. Unsupported channels on old or limited firmware are warned and skipped. Remove action deletes adapters and returns the mux to default.

State and persistence: selected device is stored in the Mule config register. The driver keeps only the regmap pointer and child adapter registrations. Cleanup always attempts to deselect to default.

Dependencies and integration: depends on parent regmap from the Mule device, OF child nodes, I2C mux core, and platform driver binding `tsd,mule-i2c-mux`.

Risks: old firmware accepts writes but readback stays `0xff`, so only default device can be safely exposed. Per-child selection probes can alter active device during probe. Missing parent regmap blocks operation.

Test signals: readback-based firmware detection, unsupported-child warnings, adapter creation for supported `reg` values, cleanup deselect, and parent regmap error propagation.
