<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busnv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busnv50.c

## Purpose
Implements NV50 I2C bit-banging over a fixed table of MMIO register addresses selected by BIOS drive index.

## Important APIs, Types, And Functions
Important functions are nv50_i2c_bus_drive_scl/sda, nv50_i2c_bus_sense_scl/sda, nv50_i2c_bus_init, and nv50_i2c_bus_new.

## Control Flow
Constructor validates drive against a 10-entry address table, initializes cached data to 0x7, and registers the bus. Init writes 0x7; drive callbacks update cached bits 0/1 and write the register; sense callbacks read bits 0/1.

## State, Persistence, Dependencies, And Integration
State includes selected register address and cached output data. Dependencies are bus.h, subdev/vga.h include, and MMIO helpers. Integration points are nv50/g94 pad constructors and BIOS CCB bus creation.

## Risks And Test Signals
Risks: only known drive indices are supported; cached data must stay synchronized with hardware writes. Test signals include EDID reads on each valid NV50 bus index and warning/-ENODEV for unknown bus indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busnv50.c -->
