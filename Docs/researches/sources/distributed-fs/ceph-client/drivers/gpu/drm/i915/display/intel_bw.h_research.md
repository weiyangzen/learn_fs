# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bw.h

## Purpose

`intel_bw.h` is the public display-bandwidth interface for the i915 display code. It hides the private `struct intel_bw_state` layout and exposes lifecycle, atomic-check, commit sequencing, and PM Demand accessors used by modeset, watermark, and power-management code.

## Important APIs, Types, And Functions

The header forward-declares `struct intel_bw_state` plus the atomic, CRTC, display, and global-state types needed by callers. It declares state conversion and lookup helpers: `to_intel_bw_state()`, `intel_atomic_get_old_bw_state()`, `intel_atomic_get_new_bw_state()`, and `intel_atomic_get_bw_state()`. Lifecycle and readout APIs are `intel_bw_init_hw()`, `intel_bw_init()`, `intel_bw_update_hw_state()`, and `intel_bw_crtc_disable_noatomic()`. Validation and commit APIs are `intel_bw_atomic_check()`, `icl_sagv_pre_plane_update()`, and `icl_sagv_post_plane_update()`. PM Demand helpers are `intel_bw_pmdemand_needs_update()`, `intel_bw_can_enable_sagv()`, and `intel_bw_qgv_point_peakbw()`.

## Control Flow And Integration

Callers initialize the global bandwidth object with `intel_bw_init()`, populate hardware capability tables with `intel_bw_init_hw()`, then call `intel_bw_atomic_check()` as part of display atomic validation. If a commit changes QGV restrictions, the modeset sequence calls `icl_sagv_pre_plane_update()` before plane updates and `icl_sagv_post_plane_update()` afterward. PM Demand code queries whether the bandwidth state changed and reads the selected QGV peak bandwidth through this header without depending on the private state layout.

## State And Persistence

The header deliberately keeps `struct intel_bw_state` opaque. The only persistent object it exposes is the global state handle returned through atomic helper APIs. This keeps callers from mutating fields directly except through functions implemented in `intel_bw.c`.

## Dependencies, Risks, And Test Signals

The header includes `<drm/drm_atomic.h>` and otherwise relies on forward declarations to avoid broad include coupling. Interface risks are mostly ordering and lifetime related: callers must only use old/new accessors when corresponding global state exists in the atomic transaction, and SAGV pre/post functions must be called in the correct commit phases. Compile coverage should catch signature drift; runtime coverage should include modeset commits where `intel_bw_atomic_check()` creates or does not create a new global bandwidth state, plus PM Demand checks on MTL+.
