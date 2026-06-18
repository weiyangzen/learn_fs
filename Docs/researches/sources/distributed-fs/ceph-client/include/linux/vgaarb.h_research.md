# sources/distributed-fs/ceph-client/include/linux/vgaarb.h

## Purpose
This header declares the VGA arbiter interface for coordinating legacy VGA IO and memory decode among multiple PCI VGA devices.

## Important APIs, types, and functions
Important resource bits are `VGA_RSRC_LEGACY_IO`, `VGA_RSRC_LEGACY_MEM`, `VGA_RSRC_NORMAL_IO`, and `VGA_RSRC_NORMAL_MEM`. APIs include `vga_set_legacy_decoding()`, `vga_get()`, `vga_put()`, default-device getters/setters, `vga_remove_vgacon()`, `vga_client_register()`, and `vga_get_interruptible()`.

## Control flow, state, and persistence
Drivers acquire VGA resources before accessing legacy ranges and release them afterward; clients can register decode callbacks and default device selection. Runtime state is arbiter ownership and decode routing. Disabled builds return permissive no-ops.

## Dependencies and integration points
It depends on video VGA constants and PCI devices. It integrates DRM/fbdev/VGA console drivers and PCI resource arbitration.

## Risks and test signals
Risks include deadlocks if resources are not released, allowing simultaneous legacy decode, and disabled-config assumptions. Tests should cover multi-GPU arbitration, interruptible acquire, default-device changes, vgacon removal, and client decode callbacks.
