<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padgf119.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padgf119.c

## Purpose
Defines GF119 pad constructors using GF119 bus and AUX backends while reusing G94 shared-pad mode programming.

## Important APIs, Types, And Functions
Important APIs are gf119_i2c_pad_s_new and gf119_i2c_pad_x_new.

## Control Flow
Shared pad constructor supplies gf119_i2c_bus_new, gf119_i2c_aux_new, and g94_i2c_pad_mode; external pad constructor supplies bus/AUX constructors without mode hook.

## State, Persistence, Dependencies, And Integration
State is inherited nvkm_i2c_pad state. Dependencies are pad.h, auxch.h, bus.h, and G94 mode helper. Integration points are GF119/GK constructors.

## Risks And Test Signals
Risks: assumes G94 pad mode registers apply to GF119 shared pads. Test signals are DDC/AUX operation and mode switching on GF119 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padgf119.c -->
