<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_display.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_display.c

## Purpose

This file implements shared legacy CRTC, plane-base, cursor, gamma, DPMS, page-flip, save/restore, encoder, connector, and PLL-search helpers for the GMA500 driver family.

## Important APIs, Types, And Functions

Exported functions include `gma_pipe_has_type()`, `gma_wait_for_vblank()`, `gma_pipe_set_base()`, `gma_crtc_load_lut()`, `gma_crtc_dpms()`, `gma_crtc_prepare()`, `gma_crtc_commit()`, `gma_crtc_disable()`, `gma_crtc_destroy()`, `gma_crtc_page_flip()`, `gma_crtc_save()`, `gma_crtc_restore()`, `gma_encoder_prepare()`, `gma_encoder_commit()`, `gma_encoder_destroy()`, `gma_best_encoder()`, `gma_connector_attach_encoder()`, `gma_pll_is_valid()`, and `gma_find_best_pll()`. It defines `gma_crtc_funcs`.

## Control Flow

Base setting powers the device, pins the new framebuffer GEM object, writes stride and pixel format, programs base/surface registers differently for PSB versus other chips, and unpins the old framebuffer. DPMS enables or disables DPLL, plane, pipe, vblank, palette, self-refresh/watermarks, and FIFO arbitration in the required order. Cursor set looks up and pins the cursor GEM, optionally copies into physical cursor memory, writes cursor control/base, and unpins the old cursor. Page flip assigns the new primary fb, optionally arms a vblank event, calls mode_set_base, and restores the previous fb on failure. Save/restore capture pipe, plane, timing, DPLL, and palette registers. PLL search brute-forces divisors within `gma_limit_t` ranges.

## State And Persistence

Persistent software state includes `gma_crtc->active`, cursor object/address, page-flip event, saved CRTC state, gamma store, and framebuffer GEM pin counts. Hardware state includes pipe/plane/DPLL/timing/palette/cursor registers and GTT/MMU mappings. Old framebuffers are unpinned only after the new base is programmed.

## Dependencies And Integration Points

It depends on DRM CRTC/fourcc/framebuffer/vblank helpers, PSB IRQ vblank helpers, GEM/GTT pinning, power gating (`gma_power_begin/end`), chip ops watermarks/self-refresh, and per-chip register maps.

## Risks And Test Signals

Risks include legacy mutable `crtc->primary->fb` semantics, missing full clipping/scaling validation, fixed 20 ms vblank wait, cursor size limited to 64x64, page-flip event cleanup races, palette fallback storing pipe 0 even for other pipes, and display power failures returning success in some paths. Test signals are mode set, pan/page flip with and without events, vblank events, cursor enable/move/disable, gamma updates, suspend/resume restore, PSB versus CDV base programming, and PLL validation edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_display.c -->
