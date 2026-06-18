# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/ofdrm.c

## Purpose

`ofdrm.c` implements a DRM driver for Open Firmware display nodes. It parses OF framebuffer properties, handles endian-specific formats, heuristically locates the framebuffer resource, maps the scanout buffer, optionally maps model-specific color-map hardware, exposes gamma/color management, and registers a fixed-mode DRM pipeline.

## Important APIs, Types, and Functions

- `enum ofdrm_model`: identifies supported firmware display models such as Mach64, Rage128, Radeon, GXT2000, Avivo, and QEMU.
- `struct ofdrm_device_funcs`: optional color-map mapping and write callbacks.
- `struct ofdrm_device`: embeds `drm_sysfb_device`, model funcs, color-map base, EDID buffer, and mode objects.
- Display parsing helpers: width, height, depth, linebytes, address, EDID, endian, and model detection.
- PCI helpers: find/enable PCI device and release it without managed PCI helpers to avoid native-driver conflicts.
- Color-map helpers for Mach64, Rage128, Rage Mobility M3 A/B, Radeon, GXT2000, Avivo, and QEMU.
- `ofdrm_device_create()`: full probe construction and mode setup.
- `ofdrm_crtc_helper_atomic_flush()`: reloads hardware gamma on color-management changes.

## Control Flow

Probe calls `ofdrm_device_create()`. Creation allocates DRM state, enables a matching PCI device if present, detects the OF display model, chooses color-map funcs, parses endian, width, height, depth, and linebytes, maps depth to a DRM format, computes framebuffer size, chooses a base address from the `address` property plus platform resources or the largest usable resource, acquires and maps the framebuffer range, optionally maps color-map hardware, reads optional EDID, fills `drm_sysfb_device`, creates the fixed primary-plane/CRTC/encoder/connector pipeline, enables CRTC color management if a color-map is available, and resets mode config. Atomic flush writes gamma values through model-specific callbacks when color state changes.

## State and Persistence Behavior

The firmware-initialized framebuffer and display hardware persist while the driver is bound. `cmap_base` persists only if model-specific mapping succeeds. Gamma/palette state is hardware state written on color-management changes. PCI enablement is tied to platform-device lifetime through a devm action so native drivers can later take ownership.

## Dependencies and Integration Points

It depends on OF address/property APIs, optional PCI APIs, aperture helpers, DRM shmem/fbdev helpers, DRM color management, EDID, and sysfb modeset helpers. It binds to OF nodes compatible with `"display"` under platform driver name `of-display`.

## Risks and Edge Cases

- Framebuffer address discovery is heuristic because OF lacks a standard; wrong resources can map the wrong BAR/region.
- `is_avivo()` contains a condition comparing the constant `PCI_VENDOR_ID_ATI_R600 >= 0x9400`, which is always true; model detection should be reviewed.
- `ofdrm_find_fb_resource()` loops with `for (i = 0; pdev->num_resources; ++i)` and relies on `platform_get_resource()` returning NULL to break; the loop condition ignores `i`.
- Some color-map mappings may fail; the driver continues without gamma support.
- Big-endian format translation and `quirk_addfb_prefer_host_byte_order` are subtle cross-architecture behavior.
- `devm_request_mem_region()` failure is fatal here, unlike some other sysfb drivers.

## Test Signals

Test on PPC/Open Firmware machines and QEMU OF VGA. Cover big- and little-endian format parsing, missing `address`, multiple resources, each model-specific palette path, gamma LUT load/fill, EDID parsing, aperture handoff, and native-driver takeover after unplug.
