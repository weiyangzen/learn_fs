# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bo.h

## Purpose
`intel_bo.h` declares the display buffer-object adapter API implemented by `intel_bo.c`. It lets display code query and operate on DRM GEM objects without including parent memory-manager internals.

## Important APIs, Types, and Functions
The header declares BO property predicates, protected key check, framebuffer mmap, page read, object description, framebuffer init/fini, and framebuffer GEM lookup. It forward-declares DRM and i915 display types used in those signatures.

## Control Flow
Display framebuffer and debug paths include this header and call wrappers when they need parent BO behavior. Actual dispatch occurs in `intel_bo.c`.

## State and Persistence
No state is stored here. State belongs to DRM GEM objects, framebuffer data, and the parent BO implementation.

## Dependencies and Integration Points
It includes `linux/types.h` for fixed-width integer types and forward-declares `drm_file`, `drm_gem_object`, `drm_mode_fb_cmd2`, `seq_file`, `vm_area_struct`, and display/framebuffer structs. It integrates with framebuffer setup, mmap, diagnostics, and scanout object validation.

## Risks
The API assumes parent callbacks exist where the implementation does not guard them. Header users must pass objects associated with an i915 display DRM device so `to_intel_display()` resolves correctly in the implementation.

## Test Signals
Compile coverage detects signature drift. Runtime tests should cover framebuffer lookup/init/fini, mmap, protected object checks, tiled/userptr/shmem object predicates, and debug description output.
