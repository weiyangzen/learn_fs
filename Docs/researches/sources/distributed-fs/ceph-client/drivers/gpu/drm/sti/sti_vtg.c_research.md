# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_vtg.c

## Purpose
`sti_vtg.c` implements the STMicroelectronics VTG video timing generator platform driver used by the STI DRM stack. It programs display window timing, hsync/vsync timing outputs for HDMI/HDDCS/HDF/DVO, handles VTG field interrupts, and exposes notifier registration so display blocks can receive top/bottom field events.

## Important APIs, Types, and Functions
- `struct sti_vtg`: persistent device state with MMIO base, IRQ, cached IRQ status, raw notifier chain, CRTC pointer, and per-output sync parameters.
- `of_vtg_find`: resolves a device-tree node to the bound VTG instance.
- `sti_vtg_set_config`: programs a `drm_display_mode`, resets the VTG, and enables top/bottom interrupts.
- `sti_vtg_get_line_number` and `sti_vtg_get_pixel_number`: convert visible coordinates into VTG timing-domain line/pixel positions.
- `sti_vtg_register_client` and `sti_vtg_unregister_client`: manage raw notifier subscribers for VTG events.
- `vtg_probe`: maps registers, obtains IRQ, initializes notifier state, and registers a threaded IRQ.

## Control Flow, State, and Persistence
Probe allocates `struct sti_vtg`, maps the register resource, obtains the IRQ, initializes a raw notifier head, and installs a hard IRQ plus thread. Mode programming runs through `sti_vtg_set_config`, which calls `vtg_set_mode`; that writes clock-per-line, half-lines-per-field, active output window, delayed sync positions for four outputs, and `VTG_MODE_MASTER`, then triggers reset and IRQ setup. The IRQ handler snapshots and clears `VTG_HOST_ITS`; the threaded handler translates the cached status into `VTG_TOP_FIELD_EVENT` or `VTG_BOTTOM_FIELD_EVENT` and calls notifier clients with the registered CRTC.

The only persistent state is device lifetime state in `struct sti_vtg`, including cached sync parameters and `crtc`. Hardware register contents persist until the next mode set or reset. The notifier list is raw and has no internal sleeping protection.

## Dependencies and Integration Points
The file depends on Linux platform, IRQ, OF, MMIO, and raw notifier APIs plus DRM display modes and logging. It integrates with STI display code through `sti_vtg.h`, `sti_drv.h`, device-tree compatible `st,vtg`, and notifier clients that consume field events for vblank/display synchronization.

## Risks and Test Signals
Risks include progressive-only programming despite helper awareness of interlaced line numbering, raw notifier lifetime rules, possible event ambiguity if both top and bottom IRQ bits are set, and direct register writes without read-back validation. Tests should cover mode-to-register calculations, negative/positive sync delays wrapping around `htotal`, IRQ clear/thread notification behavior, client register/unregister ordering, OF lookup lifetime, and real hardware vblank stability across HDMI/DVO paths.
