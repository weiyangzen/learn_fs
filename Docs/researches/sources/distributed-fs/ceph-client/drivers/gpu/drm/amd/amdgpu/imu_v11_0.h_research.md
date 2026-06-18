# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0.h

## Purpose
`imu_v11_0.h` declares the GFX11 IMU function table for the amdgpu GFX/IMU initialization path.

## Important APIs, Types, And Functions
It declares `extern const struct amdgpu_imu_funcs gfx_v11_0_imu_funcs;`.

## Control Flow
No control flow is present. Consumers include this header to assign the v11 IMU callbacks.

## State And Persistence
No state is owned here; mutable firmware and hardware state lives in `imu_v11_0.c` and `amdgpu_device`.

## Dependencies And Integration Points
The header assumes `struct amdgpu_imu_funcs` is available at inclusion sites. It integrates v11 IMU support with the amdgpu GFX IP setup code.

## Risks
Stale extern declarations result in build/link errors. Behavioral risk is in the implementation rather than this declaration.

## Test Signals
Build coverage and runtime callback-table selection for GFX11 devices cover this header.
