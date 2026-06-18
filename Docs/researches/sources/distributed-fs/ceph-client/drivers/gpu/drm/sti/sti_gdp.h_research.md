# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_gdp.h

Purpose: Exposes the GDP plane constructor to the compositor.

Important API: `sti_gdp_create()` takes the DRM device, parent device, STI plane descriptor, register base, possible-CRTC mask, and DRM plane type, returning the registered `struct drm_plane *`.

Control/state: The implementation hides command-node banks, clocks, and VTG callbacks behind the returned DRM plane. The `type` argument lets the compositor create the first GDP planes as primaries and later GDPs as overlays.

Dependencies/integration: Includes DRM plane definitions and forward declares device/DRM types. Callers must pass a descriptor from `enum sti_plane_desc` and a valid compositor register offset.

Risks/test signals: Wrong possible-CRTC masks or plane type assignment changes user-visible KMS topology. KMS plane listing and atomic commit tests cover the constructor contract.
