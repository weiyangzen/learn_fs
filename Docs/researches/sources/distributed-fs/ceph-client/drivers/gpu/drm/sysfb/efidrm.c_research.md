# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/efidrm.c

## Purpose

`efidrm.c` implements a DRM driver for EFI-provided framebuffers. It parses `sysfb_display_info`/`screen_info`, maps the EFI framebuffer using cache attributes from the EFI memory map, creates a fixed-mode atomic DRM pipeline, and registers DRM clients.

## Important APIs, Types, and Functions

- `struct efidrm_device`: embeds `drm_sysfb_device` and mode objects.
- `efidrm_get_format_si()`: maps `screen_info` pixel masks to supported DRM formats.
- `efidrm_get_mem_flags()`: determines usable EFI cache attributes for the framebuffer range.
- `efidrm_device_create()`: parses metadata, maps memory with WC/UC/WT/WB behavior, initializes plane/CRTC/encoder/connector, and resets mode config.
- `efidrm_probe()` / `efidrm_remove()`: platform bind/unplug flow.

## Control Flow

Device creation requires platform data and `VIDEO_TYPE_EFI`. It allocates a DRM device, validates format, width, height, memory resource, stride, and visible size through sysfb helpers, stores optional firmware EDID, acquires the aperture, optionally requests the memory region, maps memory based on EFI attributes, initializes a one-plane fixed-mode pipeline, attaches EDID property when available, and returns the device for registration.

## State and Persistence Behavior

State is managed by devm/drmm. EFI firmware initializes display hardware; this driver only writes pixels into the mapped framebuffer. The chosen memory mapping persists for the device lifetime. Remove calls `drm_dev_unplug()`.

## Dependencies and Integration Points

It depends on EFI memory map helpers, sysfb platform data, `screen_info`, aperture helpers, DRM shmem/fbdev helpers, EDID helpers, and `drm_sysfb_helper`. It binds to `efi-framebuffer` platform devices.

## Risks and Edge Cases

- Cache attribute selection falls back to WC/UC when EFI memmap lookup fails; incorrect attributes can affect performance or coherency.
- The driver maps `resource_size(mem)` after acquiring only visible size; if `mem` is the larger firmware resource this maps beyond the visible region intentionally but should match resource ownership.
- Only one EDID block is consumed through the shared connector helper.
- Requires `VIDEO_TYPE_EFI`; malformed sysfb platform data is ignored with `-ENODEV`.

## Test Signals

Boot tests should cover UEFI systems with WC, UC, WT, and WB mappings where possible, EDID-present and EDID-absent cases, aperture handoff to native drivers, XRGB8888 emulation, and invalid screen_info values.
