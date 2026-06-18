# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4.h

## Purpose

This header exposes the GFX 9.4 RAS descriptor implemented in `gfx_v9_4.c` so the broader GFX 9.0 initialization code can attach the correct RAS operations for supported ASICs.

## Important APIs, types, and functions

- `extern struct amdgpu_gfx_ras gfx_v9_4_ras`: descriptor containing `struct amdgpu_ras_block_hw_ops` callbacks for GFX 9.4 error-count query, counter reset, and error-status query.

## Control flow and integration

There is no executable control flow. `gfx_v9_0.c` includes this header and assigns `adev->gfx.ras = &gfx_v9_4_ras` for matching devices. After that, generic AMDGPU RAS flows call through the ops table in the descriptor.

## State and persistence behavior

The header stores no state. The exported object it declares owns callback wiring only; the callbacks mutate or read hardware RAS counters in `gfx_v9_4.c`.

## Dependencies

The declaration depends on `struct amdgpu_gfx_ras` being defined by included AMDGPU headers in the consumer. The header is intentionally minimal and uses include guards to avoid duplicate declarations.

## Risks

Because the exported descriptor is mutable rather than `const`, accidental writes from another translation unit are possible in C, although current code treats it as static driver wiring. Any mismatch between this declaration and the definition would be caught at build or link time.

## Test signals

Build coverage, successful GFX 9.4 RAS registration, and runtime RAS sysfs/debugfs operations reaching `gfx_v9_4.c` callbacks validate this header's integration.
