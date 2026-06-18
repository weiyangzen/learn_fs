# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_1.h

## Purpose

`mmhub_v3_0_1.h` is the public declaration header for the MMHUB 3.0.1 backend. It gives other AMDGPU compilation units, primarily GMC setup code, a stable symbol for selecting the implementation in `mmhub_v3_0_1.c`.

## Important APIs, Types, And Functions

The only exported symbol is `extern const struct amdgpu_mmhub_funcs mmhub_v3_0_1_funcs;`. The header relies on includers already knowing `struct amdgpu_mmhub_funcs`, normally via `amdgpu.h` or adjacent driver headers. It defines an include guard `__MMHUB_V3_0_1_H__`.

## Control Flow

There is no runtime control flow in this header. Its compile-time role is to make the function table visible to device-family selection logic. At runtime, callers assign `adev->mmhub.funcs = &mmhub_v3_0_1_funcs` and invoke callbacks through the generic MMHUB interface.

## State And Persistence Behavior

The header stores no state. It exposes an immutable function table allocated by the C file. Any hardware or device state lives in `amdgpu_device`, `amdgpu_vmhub`, and MMHUB registers initialized by that function table.

## Dependencies And Integration Points

The header integrates with `gmc_v11_0.c`, which includes it and selects `mmhub_v3_0_1_funcs` for matching ASIC/IP combinations. Its correctness depends on the C object being built into the AMDGPU module, as listed in the driver `Makefile`.

## Risks

The main risk is declaration/definition drift. If the function table is renamed, removed from the build, or its type changes, GMC selection will fail at build or link time. Because the header contains no version checks, wrong backend selection must be prevented by the caller.

## Test Signals

Build coverage is the main signal: compile AMDGPU with the header included by `gmc_v11_0.c` and ensure the final module links `mmhub_v3_0_1_funcs`. Runtime coverage comes indirectly from probing a device that selects this table and completing MMHUB init/GART enable.
