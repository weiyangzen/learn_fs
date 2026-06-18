# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_mp1_v13_0.h

## Purpose

`amdgpu_ras_mp1_v13_0.h` declares the MP1 v13.0 AMDGPU RAS system-function table.

## Important APIs, Types, And Functions

The only public symbol is `extern const struct ras_mp1_sys_func amdgpu_ras_mp1_sys_func_v13_0;`.

## Control Flow, State, And Persistence

The header has no runtime behavior. It allows manager configuration to bind rascore MP1 operations to the v13.0 implementation.

## Dependencies And Integration Points

It includes `ras.h` for `struct ras_mp1_sys_func` and is consumed by `amdgpu_ras_mgr.c`.

## Risks And Test Signals

Risks are missing object linkage or version-selection drift in the manager. Test signals include build coverage and successful callback installation for supported MP1 versions.
