# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.h

## Purpose

`mmhub_v9_4.h` declares the MMHUB 9.4 backend and its RAS descriptor for GMC v9/Arcturus integration.

## Important APIs, Types, And Functions

It exports `extern const struct amdgpu_mmhub_funcs mmhub_v9_4_funcs;` and `extern struct amdgpu_mmhub_ras mmhub_v9_4_ras;`. The include guard is `__MMHUB_V9_4_H__`.

## Control Flow

The header has no executable flow. GMC code selects the function table, and RAS setup attaches the `amdgpu_mmhub_ras` block to the device.

## State And Persistence Behavior

The header stores no state. The declared RAS object contains pointers to RAS operations, while mutable RAS counts and hardware state live in device registers and AMDGPU RAS data structures.

## Dependencies And Integration Points

It is included by `gmc_v9_0.c` and KFD Arcturus integration code. Includers must have the AMDGPU MMHUB and RAS types visible. Linkage requires `mmhub_v9_4.o`.

## Risks

Declaration drift affects both memory-management and RAS paths. Because the RAS object is non-const, accidental external mutation would affect RAS behavior. Runtime correctness depends on only Arcturus/MMHUB 9.4 paths selecting these symbols.

## Test Signals

Build/link coverage for `mmhub_v9_4_funcs` and `mmhub_v9_4_ras` plus runtime GMC v9 probing and MMHUB RAS registration are the primary signals.
