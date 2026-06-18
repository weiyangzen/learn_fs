# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/simpledrm.c

## Purpose

`simpledrm.c` implements a DRM driver for `simple-framebuffer` platform devices. It parses either platform data or device-tree properties, keeps firmware-required clocks/regulators/power domains active, maps the framebuffer from reserved memory or I/O memory resources, creates a fixed-mode atomic pipeline, and registers DRM clients.

## Important APIs, Types, and Functions

- `struct simpledrm_device`: embeds `drm_sysfb_device`, optional clocks/regulators/power-domain handles, and mode objects.
- Simplefb parsing helpers for width, height, stride, and format from platform data or OF.
- `simplefb_get_memory_of()`: prefers `memory-region` reserved memory over `reg`.
- Clock helpers: initialize and release clocks referenced by the simplefb node.
- Regulator helpers: discover `*-supply` properties, enable regulators, and release them.
- Generic power-domain helpers: attach/link multiple domains and detach them on cleanup.
- `simpledrm_device_create()`: full hardware resource retention, metadata parsing, memory mapping, and mode setup.
- `simpledrm_probe()` / `simpledrm_remove()`: registration and unplug flow.

## Control Flow

Device creation first allocates a managed DRM device and initializes clocks, regulators, and power domains when using OF rather than platform data. It parses geometry and format from platform data or OF properties, optionally reads panel physical size, computes fallback stride when absent, stores fixed framebuffer metadata, maps reserved system memory via `memremap` when `memory-region` is present or maps an I/O resource with `ioremap_wc` otherwise, initializes one primary plane, CRTC, encoder, and connector, and resets mode config. Probe registers the DRM device and starts clients.

## State and Persistence Behavior

The driver preserves bootloader-programmed display hardware by keeping referenced resources enabled for its lifetime. Clocks/regulators/power-domain attachments are released by devm actions. The framebuffer mapping persists in `sysfb->fb_addr`; scanout contents are updated by shared sysfb blit helpers. Remove unplugs the DRM device.

## Dependencies and Integration Points

It depends on aperture helpers, OF address/reserved-memory/clock APIs, regulators, generic PM domains, simplefb platform data, DRM shmem/fbdev helpers, and `drm_sysfb_helper`. It binds to `simple-framebuffer` platform/OF devices and interacts with `SYSFB_SIMPLEFB` boot-time device creation.

## Risks and Edge Cases

- Clock/regulator errors other than probe deferral are logged but generally non-fatal; display may fail later if firmware/DT descriptions are wrong.
- `memory-region` is preferred over `reg`, and a warning is emitted if both exist.
- Reserved-memory mappings use system-memory `iosys_map`, while resource mappings use I/O-memory maps; helpers must handle both.
- The mapped resource size may exceed the visible framebuffer size; invalid stride/height combinations need validation from input helpers.
- Power-domain handling intentionally only manages multiple domains; single domains are left to the driver core.

## Test Signals

Boot tests should cover platform-data and OF simplefb devices, `memory-region` versus `reg`, panel size properties, missing/zero stride fallback, clock/regulator/power-domain retention, native-driver aperture takeover, and framebuffer updates through damage clips.
