# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_overlay.c

## Purpose
Implements the i915 backend for the legacy hardware overlay plane parent interface, including overlay register storage, command submission for on/continue/off flips, frontbuffer tracking, framebuffer pinning, and cleanup.

## Important APIs, types, and functions
Exports `i915_display_overlay_interface`. Private `struct i915_overlay` tracks context, current/old VMA, frontbuffer, register BO/iomap, flip address, active bits, and `i915_active last_flip`. Key functions are `i915_overlay_on()`, `i915_overlay_continue()`, `i915_overlay_off()`, `i915_overlay_release_old_vid()`, `i915_overlay_pin_fb()`, `i915_overlay_obj_lookup()`, `i915_overlay_setup()`, and `i915_overlay_cleanup()`.

## Control flow
Setup allocates overlay state, uses RCS0 kernel context, initializes active tracking, allocates a stolen or internal page for overlay registers, pins/iomaps it, and stores either physical or GGTT flip address. On/continue/off allocate requests on the kernel context, emit `MI_OVERLAY_FLIP` and wait commands, update frontbuffer/VMA tracking, and wait for `last_flip` when synchronous completion is needed. Retire callbacks release old VMAs, signal frontbuffer flips, clear active bits on off, and restore i830 clock gating.

## State and persistence
`i915->overlay` persists while setup is active. Overlay register memory persists in `reg_bo`; current and old frame VMAs are pinned across flips; frontbuffer tracking persists for invalidation; `frontbuffer_bits` indicates active overlay ownership.

## Dependencies and integration points
Depends on GEM internal/stolen allocation, GGTT pinning/iomap, RCS requests/ring commands, i915_active retirement, WW locking for display-plane pinning, frontbuffer tracking, PCI config clock-gating workaround, and display overlay parent interface.

## Risks
Legacy overlay sequencing is hardware-sensitive. Old VMAs must not be unpinned before flip completion. Signal interruptions must make forward progress by waiting on the active tracker. Tiled overlay images are rejected. i830 requires clock-gating workarounds. Cleanup assumes display teardown has disabled the overlay.

## Test signals
Exercise legacy overlay ioctls on supported gen2/3 hardware, on/continue/off transitions, signal interruption recovery, old-frame release with and without pending ISR bit, tiled-buffer rejection, stolen/internal register allocation fallback, and module unload after overlay teardown.
