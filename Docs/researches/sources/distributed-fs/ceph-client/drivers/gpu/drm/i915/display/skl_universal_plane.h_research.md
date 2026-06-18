# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_universal_plane.h

Purpose: declares the public interface for the Skylake universal plane implementation. It exposes plane construction, initial plane readout/fixup, format conversion, surface offset calculation, NV12 plane linkage, HDR/Y-plane classification, and AUX distance calculation to the rest of the i915 display subsystem.

Important APIs/types/functions: `skl_universal_plane_create()` allocates and initializes a platform-specific `intel_plane`. `skl_get_initial_plane_config()` and `skl_fixup_initial_plane_config()` support firmware framebuffer takeover. `skl_format_to_fourcc()` maps hardware format bits plus RGB order/alpha state to DRM fourcc codes. `skl_calc_main_surface_offset()` computes main-surface GGTT/DPT offsets and adjusted x/y coordinates. `icl_link_nv12_planes()` links ICL+ Y and UV plane states. `icl_is_nv12_y_plane()`, `icl_hdr_plane_mask()`, and `icl_is_hdr_plane()` expose generation-specific plane-role classification. `skl_plane_aux_dist()` computes the programmed distance from a main surface to its AUX plane.

Control flow: callers include display plane initialization, initial framebuffer readout, atomic plane checking, and watermark/plane programming code. The header avoids exposing implementation-local register packing and keeps external dependencies to forward declarations plus `linux/types.h`.

State and persistence behavior: the header itself has no state. Its functions operate on persistent `intel_plane`, `intel_crtc`, `intel_display`, `intel_initial_plane_config`, `intel_plane_state`, `skl_ddb_entry`, and `skl_wm_level` objects owned elsewhere.

Dependencies and integration points: it is included by display initialization and other i915 display files that need to create or inspect SKL-style planes. It bridges CRTC state, initial plane config, watermark DDB data, and plane state without requiring those users to include the full implementation details.

Risks: the API assumes callers pass generation-appropriate plane IDs and states. `skl_calc_main_surface_offset()` mutates coordinate outputs, so misuse can desynchronize source rectangles and surface view state. NV12 linkage helpers are only meaningful on ICL+ plane layouts.

Test signals: compile coverage from all include sites, plane creation on each display generation, initial plane takeover tests, NV12 Y/UV pairing checks, and unit-style validation for format-to-fourcc mappings are the main signals.
