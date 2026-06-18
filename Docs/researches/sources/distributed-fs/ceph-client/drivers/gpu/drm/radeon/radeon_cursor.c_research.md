# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_cursor.c

## Purpose

`radeon_cursor.c` implements hardware cursor programming for Radeon CRTCs. It handles legacy, AVIVO, and DCE4+ cursor register layouts, pins GEM cursor images into VRAM, updates cursor dimensions, hot spots, surface addresses, and positions, hides cursors when out of bounds, and restores cursor state after modeset or reset events.

## Important APIs, Types, and Functions

- `radeon_lock_cursor()` toggles ASIC-specific cursor update-lock bits so multi-register updates are grouped.
- `radeon_hide_cursor()` disables cursor display for DCE4, AVIVO, or legacy CRTC registers.
- `radeon_show_cursor()` writes the pinned cursor address and enables the hardware cursor, including high address registers on newer AVIVO hardware.
- `radeon_cursor_move_locked()` updates cached x/y, applies CRTC offsets and hot-spot origins, handles AVIVO pre-DCE6 boundary workarounds, programs position/hot-spot/size registers, and manages out-of-bounds hide/show transitions.
- `radeon_crtc_cursor_move()` wraps movement with cursor update locking.
- `radeon_crtc_cursor_set2()` validates cursor size, looks up and pins a GEM BO in VRAM, updates geometry/hot spot, shows the cursor, unpins the previous BO, and handles disable via zero handle.
- `radeon_cursor_reset()` reprograms an existing cursor after CRTC reset or modeset restoration.

## Control Flow

Move requests lock cursor updates, cache logical coordinates, translate them for AVIVO or legacy hardware, compute origins for negative coordinates, optionally shrink AVIVO pre-DCE6 cursor width near frame and 128-pixel boundaries when multiple CRTCs are enabled, then either write registers or hide the cursor and mark it out of bounds.

Set requests with handle zero hide the cursor and unpin the old BO. Nonzero handles are dimension checked, looked up as GEM objects, reserved, and pinned into VRAM. Legacy hardware uses a 27-bit address restriction; newer hardware has no such limit. After pinning, the function locks cursor updates, adjusts position if hot spot or size changed, updates cursor metadata, shows the cursor, unlocks, and releases the old object.

Reset requests simply replay the cached move and show operations if a cursor BO is still assigned.

## State and Persistence Behavior

Per-CRTC cursor state persists in `struct radeon_crtc`: cursor position, size, hot spot, pinned GPU address, cursor BO, out-of-bounds flag, max cursor dimensions, CRTC offset/id, and legacy display-base address. The assigned cursor BO remains pinned in VRAM until replaced or disabled. Cursor registers persist until another cursor update, modeset, reset, or CRTC disable.

## Dependencies and Integration Points

The file integrates with DRM CRTC cursor hooks, GEM object lookup/reference release, Radeon BO reserve/pin/unpin APIs, Radeon register macros, ASIC generation predicates, CRTC mode/position state, and legacy display-base state for old cursor offsets.

## Risks and Edge Cases

- Cursor serialization relies on hardware update-lock bits plus external DRM/KMS locking.
- If old-BO reserve fails during unpin, the code still drops its GEM reference, relying on broader BO cleanup behavior.
- Legacy cursor BOs must be pinned below the 27-bit cursor offset limit.
- AVIVO pre-DCE6 right-edge and 128-pixel-boundary workarounds are subtle and can hide cursors near display edges.
- Width/height are checked only against maximums, not explicitly against zero.
- `radeon_show_cursor()` is gated by `cursor_out_of_bounds`, so a move back into bounds must clear that state before the cursor reappears.

## Test Signals

Tests should cover disable, bad dimensions, missing GEM handles, reserve/pin failures, successful pin/show, old BO unpin/release, hot-spot position adjustment, negative and out-of-bounds moves, re-entry from out of bounds, DCE4/AVIVO/legacy register programming, legacy doublescan y scaling, AVIVO dual-CRTC edge cases, and cursor reset with and without an assigned BO.
