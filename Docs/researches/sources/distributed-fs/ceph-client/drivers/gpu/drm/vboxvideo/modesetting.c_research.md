# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/modesetting.c

## Purpose

`modesetting.c` contains HGSMI protocol helpers for display mode state outside DRM object setup: reporting per-display screen info, updating absolute input mapping, and querying host-provided mode hints.

## Important APIs, Types, and Functions

- `hgsmi_process_display_info`: sends `VBVA_INFO_SCREEN` with display index, origin, framebuffer offset, pitch, dimensions, bpp, and screen flags.
- `hgsmi_update_input_mapping`: sends `VBVA_REPORT_INPUT_MAPPING` for host pointer/tablet coordinate mapping.
- `hgsmi_get_mode_hints`: sends `VBVA_QUERY_MODE_HINTS` and copies returned `vbva_modehint` entries.

## Control Flow

Each helper allocates a VBVA-channel HGSMI command buffer, fills the protocol structure, submits it, and frees it. Mode hints allocate one command large enough for the query header plus the returned hint array, then check the host return code before copying results.

## State and Persistence Behavior

Persistent state is on the host side: current virtual display layout, input mapping rectangle, and last mode hints. The guest copies hints into `vbox->last_mode_hints` through callers. Allocated command buffers are transient.

## Dependencies and Integration Points

Used by `vbox_mode.c` during atomic modesets and connector probing, and by `vbox_irq.c` hotplug work when host mode hints change. It depends on `hgsmi_buffer_alloc/free/submit`, VBVA structures, and VirtualBox status codes.

## Risks and Edge Cases

- `hgsmi_process_display_info` silently returns if allocation fails, potentially leaving host display state stale.
- Mode hint size is `screens * sizeof(struct vbva_modehint)`; callers clamp screen count to avoid unbounded allocation.
- Host-provided hints require validation before KMS uses positions.

## Test Signals

Validate display info updates during enable, disable, framebuffer offset changes, and disconnected screens; verify input mapping after multi-monitor layout changes; and test mode hint retrieval, unsupported-host failures, and allocation failures.
