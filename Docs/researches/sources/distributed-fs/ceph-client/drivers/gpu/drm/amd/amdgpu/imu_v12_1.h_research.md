# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v12_1.h

## Purpose
`imu_v12_1.h` declares the GFX12.1 IMU callback table.

## Important APIs, Types, And Functions
It exposes `extern const struct amdgpu_imu_funcs gfx_v12_1_imu_funcs;`.

## Control Flow
The header has no control flow. It lets device/GFX initialization select the v12.1 IMU implementation.

## State And Persistence
No state is owned here; per-XCC firmware and partition state are owned by the implementation and `amdgpu_device`.

## Dependencies And Integration Points
It depends on include context for `struct amdgpu_imu_funcs` and integrates with amdgpu GFX setup code.

## Risks
Risk is declaration drift or missing implementation linkage.

## Test Signals
Compile/link coverage and runtime callback-table selection on GFX12.1 hardware cover this header.
