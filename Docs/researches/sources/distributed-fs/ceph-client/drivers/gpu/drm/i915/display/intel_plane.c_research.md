# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_plane.c

## Purpose
`intel_plane.c` provides the common Intel display plane implementation used by i915 atomic modesetting. It owns Intel-specific plane state allocation, duplication, destruction, user-API-to-hardware state translation, visibility and bandwidth accounting, plane update ordering, framebuffer preparation/cleanup, panic scanout support, NV12 auxiliary Y-plane linking, joiner-pipe affected-plane expansion, and final atomic plane validation.

This file is a central integration layer between DRM atomic plane helpers and generation-specific plane implementations such as i9xx, cursor, and SKL universal planes. The generation-specific hooks live in `struct intel_plane` function pointers; this file coordinates when those hooks run and how their results affect `struct intel_crtc_state`.

## Important APIs, Types, And Functions
The exported lifecycle functions are `intel_plane_alloc()`, `intel_plane_free()`, `intel_plane_destroy()`, `intel_plane_duplicate_state()`, and `intel_plane_destroy_state()`. They allocate `struct intel_plane` plus `struct intel_plane_state`, reset default scaler state, duplicate DRM atomic state, manage framebuffer references in `plane_state->hw.fb`, and assert that pinned GGTT/DPT VMAs have been unpinned before destruction.

The exported validation and accounting helpers are `intel_plane_atomic_check()`, `intel_plane_atomic_check_with_state()`, `intel_plane_check_clipping()`, `intel_plane_check_src_coordinates()`, `intel_plane_set_invisible()`, `intel_plane_pixel_rate()`, `intel_plane_data_rate()`, `intel_adjusted_rate()`, and `intel_plane_add_affected()`. These functions derive enabled/active/scaled/NV12/C8/async plane masks, per-plane data rates, minimum CDCLK requirements, clipping, scaling, sub-sampling alignment, and affected plane state coverage.

The exported commit helpers are `intel_crtc_planes_update_noarm()`, `intel_crtc_planes_update_arm()`, `intel_plane_update_noarm()`, `intel_plane_update_arm()`, `intel_plane_disable_arm()`, and `intel_plane_async_flip()`. They dispatch to per-plane hooks and tracepoints while respecting async-flip and SKL+ DDB overlap ordering.

`intel_plane_copy_uapi_to_hw_state()` and `intel_plane_copy_hw_state()` are key state-transfer helpers. They separate logical UAPI state from `hw` state, handle joiner-secondary CRTC mapping, copy color properties, and maintain framebuffer references. `intel_plane_copy_uapi_plane_damage()` merges DRM damage into `plane_state->damage` on display version 12 and newer.

Framebuffer helper hooks are installed by `intel_plane_helper_add()`. Primary planes get `get_scanout_buffer` and `panic_flush` handlers in addition to prepare/cleanup hooks; non-primary planes only get prepare/cleanup.

## Control Flow
Atomic validation begins in `intel_plane_atomic_check()`. It first expands state coverage through `intel_add_affected_planes()` so joined pipes and linked planar planes have matching state objects. Then each new plane runs `plane_atomic_check()`, which copies damage from the relevant primary/joiner plane, copies UAPI fields into Intel hardware state, and calls `intel_plane_atomic_check_with_state()`.

`intel_plane_atomic_check_with_state()` resets the plane’s contribution, exits early for fully detached old/new state, calls the generation-specific `plane->check_plane()`, sets CRTC bitmasks for enabled, active, scaled, NV12, C8, and update planes, computes data-rate arrays for RGB or NV12 Y/UV planes, and then calls `intel_plane_atomic_calc_changes()`. That final step handles SKL scaler allocation, disabled CRTC invisibility, frontbuffer bits, CxSR disable requirements, async flip eligibility, and update flags.

Commit sequencing is split into no-arm and arm phases. `intel_crtc_planes_update_noarm()` writes non-arming registers before the arm phase unless the CRTC is doing an async flip. `intel_crtc_planes_update_arm()` dispatches to a SKL+ path or an i9xx path. The SKL+ path repeatedly chooses a plane with `skl_next_plane_to_commit()` so old and new DDB allocations do not overlap with already committed planes; the older path walks planes directly. Visible planes, and SKL Y planes, arm updates; invisible planes disable.

Framebuffer preparation flows through DRM plane helper `.prepare_fb`. `intel_prepare_plane_fb()` optionally chains fences from the old framebuffer on modesets, pins the new framebuffer, runs DRM GEM prepare, promotes fence priority for display, triggers RPS vblank boost, and marks the display workload interactive. Cleanup reverses the interactive mark and unpins the old framebuffer.

## State And Persistence Behavior
`struct intel_plane_state` carries both DRM UAPI state and Intel `hw` state. The file carefully manages `hw.fb` references independently from `uapi.fb` and clears/preserves `ggtt_vma`, `dpt_vma`, flags, damage, color blobs, and linked-plane metadata across state duplication and copy operations.

CRTC state is the persistent aggregation target during atomic check. Plane visibility mutates `enabled_planes`, `active_planes`, `scaled_planes`, `nv12_planes`, `c8_planes`, `async_flip_planes`, `update_planes`, `fb_bits`, `data_rate[]`, `data_rate_y[]`, `rel_data_rate[]`, `rel_data_rate_y[]`, and `plane_min_cdclk[]`. `unlink_nv12_plane()` and `link_nv12_planes()` keep those aggregates consistent when planar YUV uses a separate hidden Y plane.

Hardware-facing state is intentionally separated from logical UAPI state. Joiner secondary planes may have a logical `uapi.crtc` pointing at the primary CRTC, while `hw.crtc` is set to the actual secondary CRTC. This distinction is critical for joined-pipe updates and for framebuffer reference lifetime.

Panic scanout support temporarily exposes current primary-plane framebuffers as `drm_scanout_buffer` objects. For fbdev framebuffers it reuses the fbdev map and cache flushes; for other framebuffers it may use Intel parent panic setup and, for DPT tiled scanout, records a tiling offset callback in the framebuffer.

## Dependencies And Integration Points
This file depends heavily on DRM atomic helpers, GEM framebuffer helpers, DMA fences/reservations, DRM damage helpers, and DRM format metadata. Within i915 it integrates with Intel framebuffer pinning, CDCLK, RPS, parent-fence priority, FBC dirty updates, PSR2 selective fetch, SKL scalers/watermarks/DDB allocation, cursor unpin work, color pipeline/colorop blobs, and frontbuffer tracking.

Generation-specific behavior enters through `struct intel_plane` hooks: `check_plane`, `min_cdclk`, `can_async_flip`, `async_flip`, `update_noarm`, `update_arm`, `disable_arm`, `disable_tiling`, and `format_mod_supported`. The common code assumes these hooks populate fields such as `ctl`, `color_ctl`, `view`, and `decrypt` consistently before commit.

## Risks And Edge Cases
State lifetime is refcount-sensitive. Missing `drm_framebuffer_get()` or `drm_framebuffer_put()` in copy/clear/destroy paths would leak or prematurely free scanout buffers. The destroy path warns if VMAs are still pinned, making framebuffer pin/unpin ordering a key risk.

Atomic aggregation is sensitive to stale bitmasks. NV12 Y-plane link/unlink paths must update active, enabled, update, and data-rate masks together, or watermarks and commit order can be computed for the wrong plane set. Joiner pipes add another risk because all joined pipes must have the same affected plane coverage.

Async flips are intentionally restricted. Semiplanar YUV and C8 are rejected, and SKL+ first async flips may be forced through sync commit so watermarks/modifiers can update. Regressions here could produce missed flip completions, wrong selective fetch damage, or unsupported hardware programming.

Clipping and source-coordinate validation are format, rotation, modifier, and display-version dependent. The DISPLAY_VER >= 20 semiplanar exceptions and Wa_16023981245 are especially easy to break by simplifying subsampling checks.

Panic scanout code has hardware-format risk: only supported tiled DPT layouts have tiling callbacks, and unsupported tiling/modifier combinations return `-EOPNOTSUPP`. Incorrect tiling offsets would corrupt panic output.

## Test Signals
Useful test signals include DRM atomic/KMS tests for plane enable/disable, scaling, rotation, clipping, C8, NV12, async flips, joined-pipe modes, and modesets with old framebuffer fences. IGT-style coverage should inspect watermark/DDB updates across multi-plane SKL+ commits, cursor unpin after vblank, damage propagation on display version 12+, and invalid subsampling coordinates.

Runtime signals include `drm_dbg_atomic()` plane visibility logs, tracepoints `trace_intel_plane_update_noarm`, `trace_intel_plane_update_arm`, `trace_intel_plane_disable_arm`, and `trace_intel_plane_async_flip`, plus warnings for stale pinned VMAs, unexpected old visibility on disabled CRTCs, and panic scanout unsupported formats.
