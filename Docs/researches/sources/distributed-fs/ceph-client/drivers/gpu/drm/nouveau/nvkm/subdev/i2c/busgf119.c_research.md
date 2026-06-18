<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busgf119.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busgf119.c

## Purpose
Implements GF119-style I2C line control via MMIO registers at 0x00d014 + drive*0x20.

## Important APIs, Types, And Functions
Important functions are gf119_i2c_bus_drive_scl, gf119_i2c_bus_drive_sda, gf119_i2c_bus_sense_scl, gf119_i2c_bus_sense_sda, gf119_i2c_bus_init, and gf119_i2c_bus_new.

## Control Flow
Init writes 0x7 to the bus register. Drive functions set bits 0/1 for SCL/SDA outputs; sense functions read bits 4/5; transfers use nvkm_i2c_bit_xfer through the common bus core.

## State, Persistence, Dependencies, And Integration
State includes per-bus register address and inherited bus state. Dependencies are bus.h and nvkm MMIO helpers. Integration points are GF119/GK/GM pad constructors and DCB-created bus instances.

## Risks And Test Signals
Risks: drive index directly selects register offset without range validation. Test signals include DDC transfer on GF119-class busses and correct line high/low sensing under i2c-algo-bit/internal bit-bang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/busgf119.c -->
