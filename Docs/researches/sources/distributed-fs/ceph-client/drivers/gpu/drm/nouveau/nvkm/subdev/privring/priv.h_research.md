# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/privring/priv.h

## Purpose
Declares shared private-ring interrupt helpers for Nouveau privring chip files.

## Important APIs, Types, And Functions
Exports `gf100_privring_intr()` and `gk104_privring_intr()` and includes the public `subdev/privring.h` interface.

## Control Flow
Chip implementations include this header and install the exported interrupt functions in their `nvkm_subdev_func` tables.

## State, Persistence, And Dependencies
No runtime state is stored here; it is a private compile-time contract.

## Integration Points
Integrates GF117, GM200, and GP10B wrappers with the shared GF100/GK104 interrupt decoders.

## Risks
Prototype drift breaks multiple chip files. The header intentionally keeps the private API narrow.

## Test Signals
Compile-time coverage of all privring variants is the main signal.
