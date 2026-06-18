# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_crtc.c

Purpose: implements DRM CRTC setup, atomic CRTC validation/enable/disable/flush, vblank control, event handling, mode validation/fixup, clock management, and bridge attachment for Komeda pipelines.

Important APIs/types/functions: exported `komeda_crtc_get_color_config()`, `komeda_crtc_get_aclk()`, `komeda_kms_setup_crtcs()`, `komeda_kms_add_crtcs()`, `komeda_crtc_handle_event()`, and `komeda_crtc_flush_and_wait_for_flip_done()`. Helper funcs implement DRM CRTC atomic hooks and CRTC funcs.

Control flow: atomic check updates clock ratio on modesets, builds display data flow for active CRTCs, then releases unclaimed resources. Enable resumes runtime PM, changes D71 opmode, sets clocks, enables vblank, and flushes. Flush updates affected pipelines and queues writeback jobs before chip flush. Disable performs one- or two-phase component disable, waits for flip completion, disables vblank/clocks, and drops runtime PM. IRQ events deliver vblank, writeback completion, and pending flip events.

State and persistence: `komeda_crtc_state` stores affected/active pipes, clock ratio, and slave z-order. `komeda_dev->dpmode` is protected by mutex. `disable_done` temporarily tracks disable completion.

Dependencies/integration: depends on DRM atomic helpers, vblank, bridge, runtime PM, clocks, Komeda pipeline state, and chip funcs.

Risks: flip timeout path can leave user-visible stalls. Dual-link mode halves horizontal timings and pixel clock, so bridge/mode tests matter. Opmode/clock transitions are serialized but error handling continues after some clock failures. Test signals: atomic modeset/page-flip tests, dual display and dual-link modes, suspend/resume, vblank enable/disable, writeback completion, hotplug/bridge attach, and two-phase disable regression tests.
