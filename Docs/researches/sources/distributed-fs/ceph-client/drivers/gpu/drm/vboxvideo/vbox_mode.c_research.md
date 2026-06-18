# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_mode.c

## Purpose

`vbox_mode.c` implements the VirtualBox DRM atomic modesetting objects and host update paths. It creates CRTCs, primary/cursor planes, encoders, connectors, synthetic EDID/modes, and atomic callbacks that report modes, framebuffer views, damage rectangles, cursor images, and input mapping to the host through HGSMI/VBVA.

## Important APIs, Types, and Functions

- `vbox_do_modeset`: programs legacy VBE registers for CRTC 0 when possible and sends `VBVA_INFO_SCREEN`.
- `vbox_set_view`: sends `VBVA_INFO_VIEW` describing a CRTC's framebuffer/command-buffer view.
- `vbox_set_up_input_mapping`: decides whether outputs share one framebuffer and computes host pointer mapping dimensions.
- `vbox_crtc_set_base_and_mode`: central locked path that updates cached CRTC geometry, view, mode, and input mapping.
- Plane callbacks: `vbox_primary_atomic_check/update/disable` and `vbox_cursor_atomic_check/update/disable`.
- Object constructors: `vbox_create_plane`, `vbox_crtc_init`, `vbox_encoder_init`, and `vbox_connector_init`.
- Connector helpers: `vbox_get_modes`, `vbox_connector_detect`, and `vbox_fill_modes`.
- `vbox_mode_init` and `vbox_mode_fini`: initialize and clean up DRM mode configuration.

## Control Flow

Mode init configures DRM mode limits and creates one CRTC, encoder, and VGA connector per host-reported screen. Primary plane updates call `vbox_crtc_set_base_and_mode`, then send each damage clip as a VBVA command record in the CRTC's ring buffer. Cursor updates validate ARGB8888 size, copy pixels plus a one-bit alpha mask into `vbox->cursor_data`, and upload cursor shape to the host; cursor disable hides the host cursor when no CRTC still has it enabled. Connector probing reports host flags location, capabilities on CRTC 0, adds no-EDID modes plus a preferred CVT mode based on hints, updates synthetic EDID, and publishes suggested X/Y properties.

## State and Persistence Behavior

Persistent state includes CRTC cached dimensions, framebuffer offsets, cursor enabled flags, input mapping width/height, single-framebuffer mode, connector mode hints, and synthetic EDID properties. Host state is updated through VBE registers, `VBVA_INFO_SCREEN`, `VBVA_INFO_VIEW`, cursor shape commands, input mapping commands, and VBVA damage records.

## Dependencies and Integration Points

The file uses DRM atomic helpers, GEM VRAM and shadow plane helpers, framebuffer damage helpers, EDID/mode helpers, HGSMI/VBVA protocol helpers, and shared `vbox_private` state. It depends on `vbox_main.c` having initialized guest heap and VBVA buffers and on `vbox_irq.c` updating mode hints.

## Risks and Edge Cases

- `vbox_primary_atomic_update` assumes `new_state->fb` is non-null; disable uses a separate callback.
- Cursor image copy does not clear `cursor_data` before building the one-bit mask, so stale mask bits are possible if smaller cursors follow larger ones unless the buffer is otherwise overwritten.
- `vbox_create_plane` returns `ERR_PTR(-EINVAL)` even when `drm_universal_plane_init` failed with another error.
- Input mapping and cross-CRTC modesets rely on cached disabled-CRTC geometry; stale values can resize host windows unexpectedly.
- Host protocols are updated under `hw_mutex`; new callbacks must preserve locking.

## Test Signals

Atomic enable/disable/pageflip tests, multi-monitor layout changes, single large framebuffer vs per-output framebuffer behavior, dirty rectangle propagation, cursor size/hotspot validation, synthetic EDID preferred modes, connector hotplug hint updates, and lockdep around `hw_mutex` during KMS commits.
