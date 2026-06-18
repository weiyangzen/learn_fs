<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busnv4e.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busnv4e.c

## Purpose
Implements NV4E-era I2C line control using an MMIO address derived from 0x600800 + BIOS drive offset.

## Important APIs, Types, And Functions
Important functions are nv4e_i2c_bus_drive_scl/sda, nv4e_i2c_bus_sense_scl/sda, and nv4e_i2c_bus_new.

## Control Flow
Drive callbacks mask low control bits for SCL/SDA; sense callbacks read high status bits 0x00040000/0x00080000. Transfers use nvkm_i2c_bit_xfer.

## State, Persistence, Dependencies, And Integration
State is the calculated register address. Dependencies are bus.h and nvkm MMIO helpers. Integration points are nv4e_i2c_pad_new and DCB I2C buses for NV4E-style hardware.

## Risks And Test Signals
Risks: BIOS drive offset is trusted; wrong offset can touch unrelated MMIO. Test signals include DDC transfers on NV4E devices and correct -ETIMEDOUT behavior for clock-stretch/stuck bus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busnv4e.c -->
