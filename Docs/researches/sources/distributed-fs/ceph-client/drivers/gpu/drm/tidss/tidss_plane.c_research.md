# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_plane.c

## Purpose

`tidss_plane.c` implements DRM plane objects for TIDSS. It validates atomic plane state against DRM helper constraints and DISPC hardware limits, programs visible planes through DISPC, disables invisible planes, reports FIFO underflows, and creates zpos/color/alpha/blend properties.

## Important APIs, Types, and Functions

- `tidss_plane_error_irq()` logs underflow errors for the hardware plane ID.
- `tidss_plane_atomic_check()` handles detached planes, invokes `drm_atomic_helper_check_plane_state()`, validates chroma subsampling alignment, and calls `dispc_plane_check()` for visible states.
- `tidss_plane_atomic_update()` calls `dispc_plane_setup()` for visible planes or disables invisible planes.
- `tidss_plane_atomic_enable()` and `_disable()` toggle DISPC plane enable bits.
- `tidss_plane_create()` allocates `struct tidss_plane`, initializes a universal plane, installs primary or overlay helper funcs, and creates zpos, color encoding/range, alpha, and blend-mode properties.

## Control Flow

KMS setup creates primary planes first and overlays later. During atomic check, the plane ensures source coordinates and width align to format subsampling, visible states satisfy generic scaling/position constraints, and DISPC accepts the requested scaling/CSC. During commit, update writes plane registers while enable/disable toggles the hardware layer state. Primary planes additionally expose `get_scanout_buffer` through DMA framebuffer helpers.

## State and Persistence Behavior

`struct tidss_plane` stores the persistent DRM plane and immutable hardware plane ID. Atomic state remains DRM-managed. Plane hardware state persists until the next atomic update, disable, or DISPC reset. Object destruction calls `drm_plane_cleanup()` and frees the allocation.

## Dependencies and Integration Points

The file depends on DRM atomic helpers, blend/color properties, DMA scanout helpers, FourCC format metadata, and `tidss_dispc` plane APIs. It integrates with `tidss_kms.c` for creation and `tidss_irq.c` for underflow reporting.

## Risks and Edge Cases

- `drm_atomic_helper_check_plane_state()` is called with `INT_MAX` scaling limits, so true scaler limits rely on the later DISPC check.
- The update path trusts that invalid scaling was rejected during check.
- The custom `drm_plane_destroy()` name shadows a common DRM concept; local static scope avoids symbol conflict but can confuse readers.
- Allocation uses plain `kzalloc_obj()` and manual free rather than drmm allocation, so error and cleanup paths must stay correct.
- Color properties are created for all planes regardless of hardware lite/non-lite differences; DISPC validation is the effective guard.

## Test Signals

Plane tests should cover detach visibility reset, subsampling-aligned and misaligned YUV source rectangles, lite-plane scaling rejection, scaler limit rejection, CSC property combinations, zpos ordering, alpha/blend modes, primary scanout buffer export, underflow IRQ logging, and cleanup on property creation failures.
