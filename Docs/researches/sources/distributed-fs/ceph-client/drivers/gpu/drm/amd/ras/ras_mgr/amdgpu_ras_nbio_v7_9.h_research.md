# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.h

## Purpose

`amdgpu_ras_nbio_v7_9.h` declares the NBIO v7.9 AMDGPU RAS system-function table.

## Important APIs, Types, And Functions

The public symbol is `extern const struct ras_nbio_sys_func amdgpu_ras_nbio_sys_func_v7_9;`.

## Control Flow, State, And Persistence

The header has no runtime behavior. It is a binding point for manager NBIO configuration.

## Dependencies And Integration Points

It relies on consumers already knowing `struct ras_nbio_sys_func` from `ras.h` and is included by `amdgpu_ras_mgr.c` and the NBIO implementation.

## Risks And Test Signals

Risks are type visibility assumptions and missing object linkage. Test signals include build coverage and correct manager callback selection for NBIO 7.9.x.
