# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_2.h

## Purpose

`mmhub_v3_0_2.h` declares the public MMHUB 3.0.2 function table used by GMC v11 device setup. It is a narrow connector between ASIC selection code and the implementation file.

## Important APIs, Types, And Functions

It exports `extern const struct amdgpu_mmhub_funcs mmhub_v3_0_2_funcs;` and defines the include guard `__MMHUB_V3_0_2_H__`. It declares no local structures, macros, or inline functions.

## Control Flow

There is no executable control flow. Runtime dispatch happens after another file assigns the exported function table into `adev->mmhub.funcs`.

## State And Persistence Behavior

No state is stored in this header. The referenced table is read-only and all mutable state is in the device structure or MMHUB registers managed by `mmhub_v3_0_2.c`.

## Dependencies And Integration Points

The header is included by `gmc_v11_0.c` and depends on the AMDGPU core type declarations visible to includers. Linkage depends on `mmhub_v3_0_2.o` being part of the AMDGPU module build.

## Risks

Risks are limited to compile/link integration: stale declarations, missing object inclusion, or accidental use by unsupported hardware. The header itself cannot enforce that v3.0.2-specific SR-IOV behavior is selected only for the right IP.

## Test Signals

Compile the AMDGPU driver with `gmc_v11_0.c` and confirm it links. Runtime signal is a device path that selects `mmhub_v3_0_2_funcs` and successfully completes MMHUB initialization and GART enable.
