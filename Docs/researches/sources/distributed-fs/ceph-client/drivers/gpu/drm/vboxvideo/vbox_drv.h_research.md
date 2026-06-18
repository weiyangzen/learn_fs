# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_drv.h

## Purpose

`vbox_drv.h` is the central private header for the VirtualBox DRM driver. It declares driver identity, shared constants, `struct vbox_private`, DRM object wrappers, internal function prototypes, and the VBE I/O-port write helper.

## Important APIs, Types, and Functions

- Driver metadata: `DRIVER_NAME`, `DRIVER_DESC`, and version macros.
- VRAM layout macros: `GUEST_HEAP_OFFSET`, `GUEST_HEAP_SIZE`, `GUEST_HEAP_USABLE_SIZE`, and `HOST_FLAGS_OFFSET`.
- `struct vbox_private`: DRM device plus guest heap, VBVA buffer mappings, gen_pool, per-CRTC state, VRAM sizes, host mode hints, hardware lock, hotplug work, input mapping, and cursor data.
- `struct vbox_connector`, `struct vbox_crtc`, and `struct vbox_encoder`: wrappers over DRM connector/CRTC/encoder.
- Internal prototypes for hardware init, mode init, IRQ, memory manager, HGSMI buffer transport, and capability reporting.
- `vbox_write_ioport`: writes VBE index/data pairs with `outw`.

## Control Flow

All implementation files include this header to share the private object model. `vbox_private` is allocated by `devm_drm_dev_alloc`; mode, IRQ, HGSMI, and memory-manager code then fill and consume its fields.

## State and Persistence Behavior

The header defines the driver's long-lived state layout. `hw_mutex` protects mode and acceleration accesses; `hotplug_work` defers mode-hint processing; `cursor_data` caches formatted cursor images; CRTC fields cache last mode geometry for disabled CRTC updates and input mapping.

## Dependencies and Integration Points

It includes Linux genalloc/I/O/IRQ headers, DRM GEM/encoder/VRAM helpers, and VirtualBox protocol headers. It is the integration point between PCI driver glue, hardware setup, HGSMI/VBVA helpers, IRQ handling, and atomic modesetting.

## Risks and Edge Cases

- `struct vbox_private` embeds `struct drm_device` first; changing that requires custom release/container handling.
- VRAM layout macros depend on host protocol assumptions about the adapter information area at the end of VRAM.
- `vbox_write_ioport` performs raw port I/O and must only run on supported x86/PCI systems.
- Shared mutable fields require `hw_mutex` discipline; new callers should not update host mode/VBVA state unlocked.

## Test Signals

Build coverage across all driver objects, lockdep around `hw_mutex`, VRAM layout validation on hosts with different VRAM sizes, and compile checks for container macros and prototype drift.
