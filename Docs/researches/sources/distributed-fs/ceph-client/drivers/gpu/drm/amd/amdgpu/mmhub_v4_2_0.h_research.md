# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v4_2_0.h

## Purpose

`mmhub_v4_2_0.h` declares the public MMHUB 4.2.0 function table used by GMC v12 selection code.

## Important APIs, Types, And Functions

The header exports `extern const struct amdgpu_mmhub_funcs mmhub_v4_2_0_funcs;` and uses the include guard `__MMHUB_V4_2_0_H__`. It does not declare the `mmhub_v4_2_0_xcp_funcs` object defined by the C file.

## Control Flow

No executable control flow is present. The exported table is assigned by platform setup and later invoked through generic MMHUB callbacks.

## State And Persistence Behavior

The header is stateless. Per-instance VM hub state and MMHUB register state are managed in the C implementation.

## Dependencies And Integration Points

It is included by `gmc_v12_0.c` and depends on the surrounding AMDGPU include graph for the `amdgpu_mmhub_funcs` type. The build must include `mmhub_v4_2_0.o`.

## Risks

If XCP users need `mmhub_v4_2_0_xcp_funcs`, this header does not provide the declaration, so integration must rely on another declaration or local extern. Wrong ASIC selection is the main runtime risk.

## Test Signals

Compile and link AMDGPU with `gmc_v12_0.c`, then probe a v4.2.0 device and confirm `mmhub_v4_2_0_funcs` dispatches successfully. XCP build paths should also be checked for symbol visibility.
