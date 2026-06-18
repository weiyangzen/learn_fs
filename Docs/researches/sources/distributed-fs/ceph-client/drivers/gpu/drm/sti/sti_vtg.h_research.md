# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_vtg.h

## Purpose
`sti_vtg.h` is the public interface for the STI video timing generator driver. It forward-declares the VTG object and exposes timing configuration, coordinate conversion, OF lookup, and notifier-client APIs to the rest of the STI DRM subsystem.

## Important APIs, Types, and Functions
- `VTG_SYNC_ID_*` macros: assign IDs for HDMI, HDDCS, HDF, and DVO sync outputs. The C implementation indexes these as `id - 1`.
- `VTG_TOP_FIELD_EVENT` and `VTG_BOTTOM_FIELD_EVENT`: top and bottom field notification event values.
- `of_vtg_find`: obtains a `struct sti_vtg *` from a device-tree node.
- `sti_vtg_set_config`: applies a DRM mode to the VTG hardware.
- `sti_vtg_register_client` and `sti_vtg_unregister_client`: subscribe/unsubscribe notifier blocks, with registration also storing the CRTC pointer used as notifier data.
- `sti_vtg_get_line_number` and `sti_vtg_get_pixel_number`: convert visible coordinates to timing-generator coordinates.

## Control Flow, State, and Persistence
The header does not own state; it defines the cross-file contract for `sti_vtg.c` clients. The key stateful behavior implied by the interface is that registration stores a single `drm_crtc *` in the VTG object and notification clients receive it when IRQ events fire. Callers must ensure the VTG instance remains bound while holding the returned pointer from `of_vtg_find`.

## Dependencies and Integration Points
It depends on `linux/types.h` and forward declarations for DRM and notifier types. The interface is used by STI CRTC/output code that needs shared timing, vblank-like field notifications, and coordinate conversions matching the VTG register model.

## Risks and Test Signals
The sync IDs are one-based while arrays are zero-based, so callers must not pass arbitrary IDs into internal code. The notifier API permits multiple clients but only one stored CRTC pointer. Tests should compile all STI users after signature changes, verify register/unregister behavior with multiple clients, and compare coordinate helper results against known progressive and interlaced modes.
