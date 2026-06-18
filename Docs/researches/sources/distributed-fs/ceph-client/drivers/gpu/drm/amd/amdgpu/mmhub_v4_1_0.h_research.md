# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v4_1_0.h

## Purpose

`mmhub_v4_1_0.h` declares the MMHUB 4.1.0 function table for GMC v12 selection logic.

## Important APIs, Types, And Functions

It exposes `extern const struct amdgpu_mmhub_funcs mmhub_v4_1_0_funcs;` under the include guard `__MMHUB_V4_1_0_H__`.

## Control Flow

There is no executable logic. Runtime control begins after GMC assigns the function table to the device's MMHUB dispatch pointer.

## State And Persistence Behavior

The header does not store state. It references a static implementation table whose callbacks mutate MMHUB hardware registers and `adev->vmhub`.

## Dependencies And Integration Points

It is included by `gmc_v12_0.c` and relies on the AMDGPU build linking `mmhub_v4_1_0.o`. Includers must have a visible declaration of `struct amdgpu_mmhub_funcs`.

## Risks

The header provides no compile-time guard that the selected ASIC actually uses MMHUB 4.1.0. Incorrect caller selection is the main risk; declaration drift is caught by compile/link failures.

## Test Signals

Build/link coverage and a v4.1.0 probe path that selects `mmhub_v4_1_0_funcs` are the practical signals.
