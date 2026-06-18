# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/hgsmi_base.c

## Purpose

`hgsmi_base.c` implements high-level guest-to-host HGSMI/VBVA commands for VirtualBox graphics: host flags location reporting, capability reporting, configuration queries, and cursor shape updates.

## Important APIs, Types, and Functions

- `hgsmi_report_flags_location`: tells the host where the guest-heap `hgsmi_host_flags` structure resides in VRAM.
- `hgsmi_send_caps_info`: sends VBVA capability bits and warns if the host reports failure.
- `hgsmi_test_query_conf`: probes query-config behavior by expecting a sentinel value round trip.
- `hgsmi_query_conf`: submits `VBVA_QUERY_CONF32` and returns the host-written value.
- `hgsmi_update_pointer_shape`: validates cursor image size, builds `vbva_mouse_pointer_shape`, submits it, and maps VirtualBox status codes to Linux errno.

## Control Flow

Each function allocates an HGSMI buffer from the guest heap with a channel and command id, fills the command structure, submits it through `hgsmi_buffer_submit`, reads back host-updated fields if needed, and frees the buffer. Cursor updates compute AND-mask plus XOR image length when a new shape is supplied and force the visible flag with shape uploads.

## State and Persistence Behavior

The file stores no local state. Persistent effects occur in the host and shared VRAM: capability flags, host flag location, cursor shape, and returned configuration values. Buffers are transient gen_pool allocations.

## Dependencies and Integration Points

It depends on `hgsmi_buffer_alloc/free/submit` from `vbox_hgsmi.c`, VirtualBox status codes from `linux/vbox_err.h`, HGSMI channels, setup commands, and VBVA protocol structures in `vboxvideo.h`. It is used by hardware init, connector mode probing, cursor plane updates, and IRQ setup.

## Risks and Edge Cases

- Host command failures are not always propagated; `hgsmi_send_caps_info` warns but returns success.
- Cursor size calculations must avoid overflow for invalid dimensions, though callers already restrict cursor size.
- `hgsmi_query_conf` returns success even if the host leaves an unsupported sentinel, leaving interpretation to callers.
- The cursor allocation keeps a historical four extra bytes for ABI compatibility; future changes should not remove it casually.

## Test Signals

Run under old and new VirtualBox hosts, verify mode-hint and cursor capability queries, test cursor shape upload with visibility-only and shape data paths, fault-inject HGSMI allocation failures, and confirm host flags location enables IRQ/hotplug processing.
