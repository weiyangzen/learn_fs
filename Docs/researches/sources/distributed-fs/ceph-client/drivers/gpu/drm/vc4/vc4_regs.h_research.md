# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_regs.h

Purpose: Provides register offsets, field masks, field helper macros, HVS display-list field definitions, and hardware constants for VC4/V3D display, render, HDMI/audio/CEC, pixel valve, HVS4/5/6, and scaler blocks.

Important APIs/types/functions: `VC4_MASK()`, `VC4_SET_FIELD()`, `VC4_GET_FIELD()`, `VC6_SET_FIELD()`, and `VC6_GET_FIELD()` are the primary bitfield helpers. Register groups cover `V3D_*` command lists/interrupts/perf counters, `PV_*` pixel valve timing, `SCALER_*` HVS4/5 control/status/display-list fields, `SCALER6*`/`SCALER6D*` HVS6 variants, HDMI audio/video/CEC fields, `enum hvs_pixel_format`, pixel order constants, CSC coefficients, tiling/scaling fields, and pointer/pitch fields.

Control flow: No executable flow, but the VC6 helper macros conditionally choose C vs D register layouts based on `hvs->vc4->gen`, so includers must have an `hvs` variable in scope for those macros.

State and persistence: No runtime state. Constants encode the hardware programming model and are persistent ABI between driver code and MMIO/display-list hardware.

Dependencies and integration points: Includes Linux bitfield/bitops helpers. Used broadly by VC4 V3D, HVS, HDMI, pixel valve, TXP, plane, perfmon, and validation/render code. `vc4_plane.c` consumes the display-list fields and CSC coefficients; `vc4_v3d.c` and `vc4_perfmon.c` consume V3D/perf counter registers; `vc4_txp.c` uses `VC4_SET_FIELD()`.

Risks: The header mixes multiple hardware generations and duplicate-looking fields; accidentally using HVS5 fields on HVS6 or C-layout fields on D-layout can silently corrupt MMIO programming. `VC4_SET_FIELD()` warns on overflow, so tests that hit warnings indicate invalid caller math or masks. Register constants are not self-validating.

Test signals: Runtime smoke tests should cover V3D ID reads, perf counters, HVS display-list programming, HDMI/audio/CEC paths, PV timing, and TXP writes. KUnit or compile-time tests can exercise field helpers with boundary values. Hardware debugfs register dumps provide integration evidence.
