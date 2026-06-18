# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_initial_plane.c

## Purpose
Adopts firmware/GOP-programmed initial scanout buffers into i915 GEM/framebuffer state so fbdev and display takeover can reuse the boot framebuffer instead of immediately reallocating or corrupting it.

## Important APIs, types, and functions
Exports `i915_display_initial_plane_interface`. Key helpers are `initial_plane_memory_type()`, `initial_plane_phys()`, `initial_plane_vma()`, `i915_alloc_initial_plane_obj()`, `i915_initial_plane_setup()`, `i915_plane_config_fini()`, and `i915_initial_plane_vblank_wait()`.

## Control flow
The allocation path chooses local, stolen-local, or stolen-system memory based on platform, reads the GGTT PTE for the firmware plane base, validates presence/locality/range, creates a preallocated GEM object over the physical memory, sets cache coherency, applies tiling metadata from the framebuffer modifier, then pins a GGTT VMA. It first tries a low GGTT address to avoid high GOP placements conflicting with GuC top reservations, reserving the original range to prevent overlapping PTE corruption, then falls back to the original address if needed. Setup pins and references the VMA in plane state and pins a fence if required.

## State and persistence
State is carried in `struct intel_initial_plane_config`: physical base, memory region, framebuffer, and VMA. The created GEM object represents pre-existing memory and the VMA remains pinned for scanout until plane config cleanup. `preserve_bios_swizzle` is set when a non-linear modifier is inherited.

## Dependencies and integration points
Depends on GGTT entry decoding, GEM memory regions, stolen/local memory helpers, framebuffer initialization, display initial-plane parent interface, fbdev stolen-size preference, fenceability checks, and vblank wait through display CRTC helpers.

## Risks
Incorrect PTE locality/range validation can map the wrong physical memory. Moving GOP framebuffers in GGTT must avoid overlap with active scanout PTEs. Tiled objects must be map-and-fenceable when fences are needed. Large stolen boot framebuffers may be discarded intentionally to preserve stolen memory for other features.

## Test signals
Boot with firmware framebuffer on integrated, stolen-local, and dGFX/local-memory systems; verify takeover without flicker, fbdev reuse, no GuC-top GGTT conflicts, correct behavior with tiled and linear boot FBs, and cleanup on failed `intel_framebuffer_init()`.
