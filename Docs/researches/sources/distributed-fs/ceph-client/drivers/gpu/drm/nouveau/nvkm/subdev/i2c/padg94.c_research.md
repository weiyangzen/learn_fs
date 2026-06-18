<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padg94.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padg94.c

## Purpose
Implements G94 pad mode programming and pad constructors for shared/native and external pads.

## Important APIs, Types, And Functions
Important APIs are g94_i2c_pad_mode, g94_i2c_pad_s_new, and g94_i2c_pad_x_new.

## Control Flow
Mode programming selects OFF/I2C/AUX by writing 0x00e500 and 0x00e50c offsets based on hybrid pad id. Shared pads provide bus_new_4, aux_new_6, and mode; external pads provide bus/AUX constructors without mode hook.

## State, Persistence, Dependencies, And Integration
State is pad mode and hardware selection bits. Dependencies are pad.h, auxch.h, bus.h, nv50_i2c_bus_new, and g94_i2c_aux_new. Integration points are G94/GF119 constructors and DCB shared pad entries.

## Risks And Test Signals
Risks: base calculation assumes HYBRID id namespace. Test signals are successful switching between DDC I2C and DP AUX on shared G94 pads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padg94.c -->
