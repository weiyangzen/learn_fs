# sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vmmdev.h

## Purpose
`vmmdev.h` defines the private VirtualBox VMMDev guest-host protocol structures and constants used by the vboxguest driver. It captures MMIO layout, event bits, guest capabilities, request headers, guest information/status packets, memory balloon requests, heartbeat packets, and HGCM request formats.

## Important APIs, types, and functions
Important protocol types include `struct vmmdev_memory`, `struct vmmdev_request_header`, `struct vmmdev_mouse_status`, `struct vmmdev_host_version`, `struct vmmdev_mask`, `struct vmmdev_events`, `struct vmmdev_guest_info`, `struct vmmdev_guest_info2`, `struct vmmdev_guest_status`, `struct vmmdev_memballoon_info`, `struct vmmdev_memballoon_change`, `struct vmmdev_heartbeat`, `struct vmmdev_hgcmreq_header`, `struct vmmdev_hgcm_connect`, `struct vmmdev_hgcm_disconnect`, `struct vmmdev_hgcm_call`, and `struct vmmdev_hgcm_cancel2`. Event and capability macros define valid masks.

## Control flow
This header does not execute code. The core and utilities allocate these structures, fill the common request header, write the physical request address to the VMMDev port, and interpret host-mutated output fields. The ISR relies on `vmmdev_memory.have_events` and `VMMDEVREQ_ACKNOWLEDGE_EVENTS` packets to drain host events.

## State and persistence
The structures describe on-wire/in-memory ABI state shared with the host. Driver state persists only as allocated request packets, MMIO content, and host-maintained event/capability state while the VM is running.

## Dependencies and integration points
It depends on Linux types, sizes, bit helpers, and `linux/vbox_vmmdev_types.h` for shared request enums and HGCM parameter definitions. It is tightly integrated with VirtualBox host expectations and the Linux guest core.

## Risks and test signals
Risks are ABI layout drift, incorrect packing/alignment, wrong valid masks, truncation of physical addresses such as the 32-bit cancel field, and changing comments/constants without matching host behavior. Test signals include `VMMDEV_ASSERT_SIZE` build checks, cross-architecture builds, host request compatibility tests, event mask negotiation, HGCM calls, heartbeat, balloon requests, and mouse/status packets against multiple VirtualBox host versions.
