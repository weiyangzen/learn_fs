# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_wm.h

## Purpose

`i9xx_wm.h` is the internal interface for the legacy Intel display watermark implementation. It exposes the small set of cross-file entry points needed by display initialization, atomic commit, and CxSR management while hiding the platform-specific computation and register programming details in `i9xx_wm.c`.

## Important APIs, Types, And Functions

The header forward declares `struct intel_display`, `struct intel_crtc_state`, and `struct intel_plane_state`. Under `I915`, it declares `ilk_disable_cxsr()`, `ilk_wm_sanitize()`, `intel_set_memory_cxsr()`, and `i9xx_wm_init()`. Without `I915`, it provides no-op inline stubs returning safe defaults, so non-i915 builds can include shared display headers without linking the legacy watermark implementation.

## Control Flow

The header has no runtime control flow of its own. Callers use `i9xx_wm_init()` during display setup to install platform watermark callbacks. Commit and plane update paths can call `intel_set_memory_cxsr()` or `ilk_disable_cxsr()` before register updates that must not occur while the hardware is in self-refresh or low-power watermark modes. Hardware readout paths can call `ilk_wm_sanitize()` after initial state reconstruction.

## State And Persistence Behavior

No state is stored in the header. The functions it declares manipulate `display->wm`, per-CRTC watermark state, and display hardware registers through the implementation file. The no-op stubs preserve build-time behavior by avoiding state changes when the i915 implementation is not compiled.

## Dependencies And Integration Points

The header depends only on `<linux/types.h>` and forward declarations. It integrates the legacy watermark code with broader Intel display code while avoiding exposure of register macros or private watermark structures. The compile-time `I915` guard is the main integration boundary.

## Risks And Edge Cases

Because the non-I915 stubs silently return false or do nothing, call sites must not assume CxSR was actually disabled unless they are in a real i915 build. Any signature drift between this header and `i9xx_wm.c` would break platform initialization or suspend/resume sanitize paths. The declarations include `intel_crtc_state` and `intel_plane_state` forward declarations even though this header currently exports only display-level functions, so cleanup should verify whether those declarations remain necessary.

## Test Signals

Build coverage with and without `I915`, link coverage for all exported symbols, and boot tests on pre-SKL display platforms are the relevant signals. Static analysis should verify that callers handle the boolean return from CxSR helpers appropriately.
