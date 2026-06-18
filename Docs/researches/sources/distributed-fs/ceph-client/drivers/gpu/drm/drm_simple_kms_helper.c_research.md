# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_simple_kms_helper.c

Purpose: provides simple display pipe helpers for DRM drivers with one primary plane, one CRTC, and one encoder, forwarding atomic operations to optional driver callbacks.

Important APIs/types/functions: `drm_simple_encoder_init()` and `__drmm_simple_encoder_alloc()` create simple encoders. Internal CRTC helper funcs handle mode validation, atomic check, enable, and disable. CRTC funcs handle reset, state duplicate/destroy, config, page flip, and vblank. Plane helper funcs handle prepare/cleanup framebuffer, begin/end access, atomic check/update. `drm_simple_display_pipe_attach_bridge()` attaches bridges, and `drm_simple_display_pipe_init()` wires plane, CRTC, encoder, optional connector, formats, and modifiers.

Control flow: pipe init stores connector/functions, registers plane helper and universal primary plane, registers CRTC helper and CRTC with the plane, initializes encoder possible CRTCs, creates encoder, and optionally attaches the connector. Atomic CRTC check ensures enabled CRTCs have a primary plane and adds affected planes. Plane check enforces no scaling and calls driver `check` only when visible. Enable/update/disable and framebuffer access paths forward to pipe callbacks when present, otherwise default GEM prepare is used for GEM drivers.

State and persistence behavior: state is embedded in `struct drm_simple_display_pipe` and standard DRM plane/CRTC/encoder objects. Atomic state duplication/reset can be default or driver-supplied.

Dependencies and integration points: integrates DRM atomic helpers, GEM plane helpers, bridge attach, probe helper mode validation, encoder/plane/CRTC init, and optional simple display pipe callback table.

Risks: this helper assumes a linear simple pipeline and no scaling. Non-GEM drivers without custom `prepare_fb` hit warnings. Format modifier support defaults to linear only. Partial init failures return immediately but callers must handle cleanup through normal DRM object cleanup or managed allocation patterns.

Test signals: simple driver modeset smoke tests, atomic check without primary plane, visible/invisible plane callback behavior, GEM prepare fallback, bridge attach, connector attach, vblank callback forwarding, format modifier rejection except linear, and init failure injection.
