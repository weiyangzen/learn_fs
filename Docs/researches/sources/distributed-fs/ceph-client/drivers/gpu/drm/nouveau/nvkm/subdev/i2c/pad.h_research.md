<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/pad.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/pad.h

## Purpose
Declares pad identifiers, modes, backend function table, constructors, generation-specific pad constructors, ANX9805 pad constructor, and logging macros.

## Important APIs, Types, And Functions
Important definitions are NVKM_I2C_PAD_HYBRID/CCB/EXT, enum nvkm_i2c_pad_mode, nvkm_i2c_pad_func with bus_new_0/bus_new_4/aux_new_6/mode, and pad constructor declarations.

## Control Flow
No executable flow exists. The header defines how base.c asks pads to create buses/AUX objects and how bus/aux code arbitrates pin mode.

## State, Persistence, Dependencies, And Integration
State is API contract. Dependencies are priv.h. Integration points are all pad*.c, bus*.c, aux*.c, and external encoder code.

## Risks And Test Signals
Risks: ID namespaces must not collide; mode callbacks must be valid for shared pads. Test signals are compile coverage and correct pad IDs in trace logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/pad.h -->
