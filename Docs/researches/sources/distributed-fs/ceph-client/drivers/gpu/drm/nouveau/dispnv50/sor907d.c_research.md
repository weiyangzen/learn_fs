
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/sor907d.c

## Purpose
Provides SOR control and capability probing for NV907D-era display core channels.

## Important APIs, types, and functions
- `sor907d_ctrl()` emits `NV907D_SOR_SET_CONTROL(or)` with the caller-provided control word.
- `sor907d_get_caps()` reads the display sync notifier BO with `NVBO_RV32()` and extracts the SOR DP interlace capability bit.
- `const struct nv50_outp_func sor907d` publishes the callbacks.

## Control flow
Unlike the 507D backend, this control function does not patch in polarity/depth from the head atom; it assumes the caller's `ctrl` already encodes the required state for the 907D class. Capability probing reads per-OR notifier capability data at `or * 2`.

## State and persistence
The file persists only hardware SOR control state. It also caches the discovered DP interlace capability in `nouveau_encoder->caps`.

## Dependencies and integration points
Uses `core.h`, `nvif/class.h`, `nvif/push507c.h`, `cl907d.h`, and `nouveau_bo.h`. It depends on the core notifier buffer being initialized with capability data before `get_caps` runs.

## Risks
Capability extraction depends on notifier layout and `or * 2` indexing; wrong offsets produce false capability reports. Omitting head atom-derived polarity/depth is correct only if higher-level code supplies class-appropriate bits.

## Test signals
Boot logs and encoder capabilities should reflect per-SOR DP interlace support. Runtime modesets should verify no regressions in polarity/depth on 907D-class hardware.
