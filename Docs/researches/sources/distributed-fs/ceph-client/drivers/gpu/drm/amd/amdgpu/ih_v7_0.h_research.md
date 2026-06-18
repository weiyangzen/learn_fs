# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v7_0.h

## Purpose
`ih_v7_0.h` declares the IH v7.0 amdgpu IP block object.

## Important APIs, Types, And Functions
It exposes `extern const struct amdgpu_ip_block_version ih_v7_0_ip_block;`.

## Control Flow
The header has no control flow. It supports inclusion by IP block tables or device-family initialization code.

## State And Persistence
No state is owned here. The const descriptor is defined in `ih_v7_0.c`.

## Dependencies And Integration Points
Consumers must have the amdgpu IP block type in scope. The declaration links IH v7.0 support into the broader IP framework.

## Risks
Risk is limited to stale symbol declarations or missing implementation linkage.

## Test Signals
Build/link coverage and runtime selection of IH v7.0 hardware are sufficient signals for this header.
