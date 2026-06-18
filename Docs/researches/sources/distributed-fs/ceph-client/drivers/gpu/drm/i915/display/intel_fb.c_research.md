<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb.c

## Purpose
This file is the i915 display framebuffer validation and view-construction layer. It maps DRM format modifiers to Intel tiling/compression capabilities, validates framebuffer layout against object and plane constraints, derives normal/rotated/remapped GTT views, creates DPT mappings when required, and wires framebuffer lifetime/dirty handling into frontbuffer tracking.

## Important APIs, Types, and Functions
Important tables include modifier-specific format overrides for SKL CCS, Gen12 CCS, Gen12 CCS with clear color, flat CCS clear color, and `intel_modifiers[]`. `struct intel_modifier_desc` records modifier, display-version range, format overrides, plane capability bits, and CCS auxiliary/clear-color plane masks.

Major public helpers include modifier predicates, `intel_fb_plane_get_modifiers()`, `intel_fb_plane_supports_modifier()`, `intel_fb_get_format_info()`, CCS plane mapping helpers, tile dimension/row/alignment helpers, DPT predicates, subsampling helpers, offset alignment helpers, remap/rotation size helpers, `intel_fill_fb_info()`, `intel_fb_fill_view()`, `intel_plane_compute_gtt()`, `intel_framebuffer_init()`, `intel_user_framebuffer_create()`, `intel_framebuffer_create()`, and `intel_fb_bo()`.

## Control Flow
Framebuffer creation looks up the GEM object, initializes frontbuffer state before BO framebuffer setup to avoid tiling races, validates format/modifier support, stride limits, zero plane-0 offset, shared handles across planes, per-plane stride alignment, Gen12 CCS auxiliary stride, and total object size. It then fills derived `intel_framebuffer` view information, optionally creates a DPT, and registers DRM framebuffer callbacks.

View construction converts framebuffer plane offsets to x/y positions, checks CCS intra-tile x/y compatibility with main planes, computes aligned tile offsets, builds normal views, optionally builds rotated views for supported Y/Yf tiling, and optionally builds remapped views for DPT power-of-two stride requirements. Plane GTT computation selects remapping when visible planes exceed hardware stride limits, otherwise copies the precomputed framebuffer view and rotates source coordinates for 90/270-degree scanout.

## State and Persistence Behavior
`struct intel_framebuffer` persists DRM framebuffer state, frontbuffer tracking, panic buffer, min alignment, VT-d guard, optional DPT object, and precomputed GTT views. Dirty handling ties DMA reservation fences to deferred frontbuffer flushes, invalidating first and flushing when the fence signals. Destroy tears down the DRM framebuffer, optional DPT, BO framebuffer state, frontbuffer reference, panic allocation, and the framebuffer object.

## Dependencies and Integration Points
The file depends on DRM GEM/framebuffer helpers, DMA fences/reservations, Intel BO hooks, frontbuffer tracking, display platform/version helpers, parent DPT/frontbuffer/panic interfaces, plane capability callbacks, rotation/remapped GTT view structures, and modifier definitions. It is directly coupled with `intel_fb_pin.c`, plane atomic checks, and DPT suspend/resume.

## Risks
This is a high-risk validation boundary exposed to userspace `ADDFB`. Modifier descriptors, CCS plane masks, tile dimensions, and stride rules must match hardware exactly. Remapping cannot be used with CCS hash modes and has cursor/pre-gen restrictions. Offset arithmetic and object-size checks must avoid overflow and permit only layouts the hardware can scan out. DPT creation error cleanup must destroy the DPT without leaking frontbuffer or BO state. Dirty fence callbacks must handle already-signaled fences and allocation failures.

## Test Signals
Signals include IGT framebuffer modifier tests, invalid stride/offset/handle rejection, CCS auxiliary stride validation, object-too-small rejection, 90/270 rotation tests on supported modifiers, DPT/remapped-view scanout on ADL-P/display version 14+, dirtyfb/frontbuffer flush behavior with pending fences, suspend/resume of DPT-backed framebuffers, and leak/error-path tests for framebuffer creation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb.c -->
