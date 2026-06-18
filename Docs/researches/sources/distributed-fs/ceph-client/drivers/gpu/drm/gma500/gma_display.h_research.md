<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_display.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_display.h

## Purpose

This header defines shared GMA display clock data structures and declares common CRTC/encoder/display helper functions.

## Important APIs, Types, And Functions

Types include `struct gma_clock_t` for PLL divisors and derived dot/vco values, `struct gma_range_t`, `struct gma_p2_t`, `struct gma_limit_t` with a `find_pll` callback, and `struct gma_clock_funcs` with clock/limit/validation callbacks. It declares shared pipe, base, LUT, DPMS, CRTC lifecycle, page flip, save/restore, encoder lifecycle, `gma_crtc_funcs`, `gma_limit()`, `gma_pll_is_valid()`, and `gma_find_best_pll()`.

## Control Flow

There is no executable flow. Per-chip display code installs `gma_clock_funcs` and CRTC helper callbacks using these declarations; shared display code calls chip clock callbacks through the structs.

## State And Persistence

The structs are transient calculation contracts for PLL selection. Function declarations operate on persistent DRM CRTC/encoder/framebuffer objects and hardware registers.

## Dependencies And Integration Points

It includes PM runtime and DRM vblank headers and connects Cedarview/Poulsbo/Oaktrail display code with shared GMA display helpers.

## Risks And Test Signals

Risks include legacy helper API drift, non-atomic display assumptions, and PLL range structs allowing invalid per-chip values if not carefully initialized. Test signals are compile coverage, per-chip mode setting, PLL search results, page flips, and CRTC save/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gma_display.h -->
