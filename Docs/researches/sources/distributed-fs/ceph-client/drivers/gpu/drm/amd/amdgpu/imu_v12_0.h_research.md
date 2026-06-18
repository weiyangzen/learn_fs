# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v12_0.h

## Purpose
`imu_v12_0.h` declares the GFX12.0 IMU callback table.

## Important APIs, Types, And Functions
It exposes `extern const struct amdgpu_imu_funcs gfx_v12_0_imu_funcs;`.

## Control Flow
No runtime control flow is present. Include sites use the extern to select v12.0 IMU operations.

## State And Persistence
No state is owned by the header. Firmware and hardware state are managed by `imu_v12_0.c`.

## Dependencies And Integration Points
It depends on include context for `struct amdgpu_imu_funcs` and integrates with GFX IP initialization.

## Risks
The header risk is limited to stale declaration or missing include context.

## Test Signals
Build coverage and runtime selection on GFX12.0 devices are the main signals.
