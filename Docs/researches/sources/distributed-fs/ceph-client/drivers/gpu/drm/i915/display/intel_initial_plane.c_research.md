# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_initial_plane.c

Purpose: reconstructs BIOS or firmware-programmed primary plane framebuffer state during driver takeover so i915 can preserve boot display contents when possible and avoid inconsistent active planes without framebuffers.

Important APIs/types/functions: `intel_initial_plane_config()` is the main entry. `intel_initial_plane_vblank_wait()` delegates vblank waits to the display parent interface. `intel_find_initial_plane_obj()` chooses or constructs the framebuffer object and plane state. `intel_alloc_initial_plane_obj()` validates supported modifiers and asks the parent `initial_plane` implementation to allocate backing storage. `intel_reuse_initial_plane_obj()` reuses an already reconstructed plane object when multiple active heads share the same surface base. `plane_config_fini()` releases temporary config resources.

Control flow: for each active CRTC, the display hook `get_initial_plane_config()` populates an `intel_initial_plane_config`. The code attempts to allocate a GEM object for supported linear/X/Y/4-tiled modifiers, otherwise searches active CRTCs for a matching base address. On success it fills plane rotation, framebuffer view, source/destination rectangles, framebuffer reference, CRTC association, hardware state, and frontbuffer bits. If setup fails, it disables the primary plane non-atomically to prevent later code from seeing a visible plane with no framebuffer. Platform hook `fixup_initial_plane_config()` can request a vblank wait before cleanup.

State and persistence behavior: persistent runtime state is the primary plane's DRM and i915 plane state, framebuffer references, GGTT VMA, and frontbuffer tracking. Temporary `intel_initial_plane_config` objects are finalized after each CRTC. No durable storage is used.

Dependencies and integration points: depends on display parent initial-plane callbacks (`alloc_obj`, `setup`, `config_fini`, `vblank_wait`), platform display hooks (`get_initial_plane_config`, `fixup_initial_plane_config`), framebuffer helpers, frontbuffer tracking, plane state conversion, and CRTC readout state.

Risks: unsupported modifiers or allocation failures disable inherited planes, causing visible boot transition changes. Shared framebuffer detection is based on base address, so unusual BIOS layouts can be missed. Comments call out unhandled failures when initial config readout fails and non-page-aligned surface bases. Reference handling must distinguish full framebuffers from stubs.

Test signals: fastboot/smooth boot tests, multi-head shared BIOS framebuffer takeover, unsupported modifier fallback, primary plane disabled on reconstruction failure, frontbuffer bit correctness, and vblank wait when platform fixups adjust live plane state.
