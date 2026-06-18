<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busnv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busnv04.c

## Purpose
Implements legacy NV04 I2C bit-banging through VGA CRTC registers for drive and sense lines.

## Important APIs, Types, And Functions
Important functions are nv04_i2c_bus_drive_scl/sda, nv04_i2c_bus_sense_scl/sda, and nv04_i2c_bus_new.

## Control Flow
Drive callbacks modify VGA register bits 0x20/0x10 and set enable bit 0x01; sense callbacks read bits 0x04/0x08 from the sense register. Transfers use nvkm_i2c_bit_xfer.

## State, Persistence, Dependencies, And Integration
State includes drive and sense register indices from BIOS CCB entries. Dependencies are subdev/vga.h, bus.h, and VGA register access helpers. Integration points are nv04_i2c_pad_new and legacy DDC/VBIOS I2C.

## Risks And Test Signals
Risks: VGA register access must be valid for the device and head; no range validation on BIOS-provided drive/sense values. Test signals include EDID reads on NV04-era hardware and no stuck line errors during VBIOS I2C use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busnv04.c -->
