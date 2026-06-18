# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/corebootdrm.c

## Purpose

`corebootdrm.c` implements a simple atomic DRM driver for framebuffers described by coreboot tables. It parses `lb_framebuffer` platform data, validates geometry/format/address, maps the firmware framebuffer, sets up a fixed-mode DRM pipeline, and exposes it through shmem GEM/fbdev helpers.

## Important APIs, Types, and Functions

- `struct corebootdrm_device`: embeds `drm_sysfb_device` plus primary plane, CRTC, encoder, connector, and format list.
- `corebootdrm_get_format_fb()`: maps coreboot bit masks to DRM formats through `pixel_format`.
- Geometry helpers: width, height, pitch, size, address, and orientation validators.
- `corebootdrm_mode_config_init()`: creates mode config, primary plane, CRTC, encoder, and connector, then applies panel orientation quirks.
- `corebootdrm_probe()`: full device creation, memory validation, aperture acquisition, mapping, DRM registration, and client setup.
- `corebootdrm_remove()`: unplug path.

## Control Flow

Probe allocates a managed DRM device, validates that platform data contains a usable LFB entry, resolves format/width/height/pitch/size/address/orientation, fills `drm_sysfb_device`, obtains and validates the platform memory resource, checks that the framebuffer aperture sits inside that resource, acquires the aperture, maps it write-combined, initializes the fixed-mode pipeline, resets mode config, registers the DRM device, and starts DRM clients.

## State and Persistence Behavior

Device state is devm/drmm-managed. The firmware framebuffer mapping persists for the DRM device lifetime through `sysfb->fb_addr`. Hardware scanout state is assumed to have been initialized by coreboot and is not reprogrammed except by CPU writes into the framebuffer. Remove calls `drm_dev_unplug()`.

## Dependencies and Integration Points

It depends on coreboot table structures, aperture helpers, platform devices, DRM shmem GEM helpers, DRM sysfb helpers, fixed-mode connector helpers, and DRM client setup. It binds to the `coreboot-framebuffer` platform device.

## Risks and Edge Cases

- Address validation rejects zero physical address and overflow, but relies on platform resource correctness.
- If `devm_request_mem_region()` fails, the driver warns and maps the resource anyway; this is intentional but can hide resource-description problems.
- Only listed RGB formats are supported; unusual coreboot masks fail.
- The driver assumes firmware keeps display hardware scanning out from the mapped buffer.

## Test Signals

Boot tests on coreboot systems should verify mode, format, orientation, fbdev handoff, aperture conflict handling with native GPU drivers, and damage updates. Fuzz-style tests should cover invalid dimensions, pitch overflow, address overflow, unsupported masks, and missing resources.
