# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_ddc.h

## Purpose
Declares the mgag200 DDC adapter creation API.

## Important APIs, types, and functions
- Forward declares `struct i2c_adapter` and `struct mga_device`.
- Declares `struct i2c_adapter *mgag200_ddc_create(struct mga_device *mdev);`.

## Control flow
No runtime control flow. Connector initialization calls the declared function to get an I2C adapter for DDC.

## State and persistence
No state is stored in the header. The implementation creates DRM-managed adapter state.

## Dependencies and integration points
Included by VGA connector files and `mgag200_mode.c`. Keeps DDC implementation details private.

## Risks
Signature drift would break connector initialization at build time.

## Test signals
Build coverage and successful EDID probing through connectors using `mgag200_ddc_create()`.
