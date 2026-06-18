# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_0.h

## Purpose

This header declares the UMC v6.0 function table used by generation dispatch code.

## Important APIs, Types, and Functions

The only public symbol is `extern const struct amdgpu_umc_funcs umc_v6_0_funcs`.

## Control Flow

There is no control flow. Including this header lets platform setup bind the v6.0 `.init_registers` callback implemented in `umc_v6_0.c`.

## State and Persistence Behavior

The header stores no state and defines no persistent data. It exposes a const callback table that drives hardware register initialization elsewhere.

## Dependencies and Integration Points

It includes `soc15_common.h` and `amdgpu.h` for AMDGPU types and register infrastructure. It integrates with common UMC setup, not with the newer RAS `amdgpu_umc_ras` interface.

## Risks

The main risk is dispatch mismatch if ASIC setup selects v6.0 functions for hardware with a different register layout.

## Test Signals

Compile-time symbol resolution and successful UMC initialization on v6.0 devices are the relevant signals.
