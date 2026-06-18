# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ih.h

## Purpose
`amdgpu_ih.h` declares AMDGPU Interrupt Handler ring sizes, register layout, ring state, timestamp comparison helpers, hardware callback table, and common IH helper prototypes.

## Important APIs, types, and functions
Important definitions are `AMDGPU_IH_MAX_NUM_IVS`, `IH_RING_SIZE`, `IH_SW_RING_SIZE`, `struct amdgpu_ih_regs`, `struct amdgpu_ih_ring`, timestamp macros `amdgpu_ih_ts_after()` and `amdgpu_ih_ts_after_or_equal()`, and `struct amdgpu_ih_funcs`. Macros dispatch `get_wptr`, `decode_iv`, `decode_iv_ts`, and `set_rptr` through `adev->irq.ih_funcs`.

## Control flow
The header has no standalone execution. Hardware-specific IH code installs `amdgpu_ih_funcs`, and common processing calls those callbacks while walking IH rings.

## State and persistence behavior
`struct amdgpu_ih_ring` represents volatile ring buffers, GPU/CPU pointer shadows, doorbell configuration, waitqueue state, processed timestamp, and overflow flag. No persistent state is defined.

## Dependencies and integration points
It integrates with AMDGPU IRQ dispatch, GMC fault timestamp filtering, retry CAM software ring use, reset handling, and hardware IH register programming.

## Risks and edge cases
The `amdgpu_ih_decode_iv` macro references `ih` as an implicit argument name, so call-site naming must match expected usage. Timestamp helpers assume 48-bit IH timestamps. Function pointer availability must be checked where optional, as done for `decode_iv_ts`.

## Test signals
Build coverage, IH callback installation, timestamp wrap tests, IV dispatch tests, software ring tests, and interrupt overflow tests validate this header.
