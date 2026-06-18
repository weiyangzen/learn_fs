# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_3.h

## Purpose

`mmhub_v3_3.h` exposes the MMHUB 3.3 function table to AMDGPU GMC setup code. It is the public selection header for the implementation in `mmhub_v3_3.c`.

## Important APIs, Types, And Functions

The header declares `extern const struct amdgpu_mmhub_funcs mmhub_v3_3_funcs;` and wraps it with `__MMHUB_V3_3_H__`. It intentionally contains no register definitions; those stay in generated IP headers included by the C file.

## Control Flow

The header has no control flow. Runtime behavior begins when a device-family switch assigns `mmhub_v3_3_funcs` to `adev->mmhub.funcs`.

## State And Persistence Behavior

The header stores no mutable state. The function table it declares causes later code to write MMHUB registers, populate `adev->vmhub`, and install client-id tables.

## Dependencies And Integration Points

It integrates with `gmc_v11_0.c` and the AMDGPU module build. Its declaration depends on the surrounding include graph providing `struct amdgpu_mmhub_funcs`.

## Risks

The main risks are stale symbol names and unsupported selection. Because the header does not expose `mmhub_v3_3` sub-variant details, all exact IP-version behavior is hidden in the C implementation.

## Test Signals

Build/link coverage ensures the symbol exists. Runtime probe coverage on MMHUB 3.3/3.4 hardware confirms the selection path reaches the function table and the C callbacks complete MMHUB bring-up.
