# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_panic.c

## Purpose

`drm_panic.c` implements DRM's panic-screen renderer. Drivers that expose a panic-safe scanout buffer through `drm_plane_helper_funcs.get_scanout_buffer` can register their planes as `kmsg_dumper`s. On kernel panic, this file draws either a user-friendly panic message, recent kmsg text, or a QR code carrying panic logs, then optionally flushes the plane to hardware.

## Important APIs, Types, and Functions

- `struct drm_panic_line` stores text and length for the user message and ASCII logo.
- Blit/fill helpers include `drm_panic_blit()`, `drm_panic_fill()`, page-backed variants, direct-map variants, and `set_pixel` variants.
- Renderers are `draw_panic_screen_user()`, `draw_panic_screen_kmsg()`, and, when enabled, `draw_panic_screen_qr_code()`.
- QR support uses preallocated `qrbuf1`, `qrbuf2`, and a zlib workspace initialized by `drm_panic_qr_init()` and freed by `drm_panic_qr_exit()`.
- `draw_panic_plane()` obtains the scanout buffer, validates format support, sets the panic description, dispatches rendering, calls optional `panic_flush`, and releases the panic lock.
- `drm_panic_register()` and `drm_panic_unregister()` attach/detach per-plane `kmsg_dumper`s.
- `drm_panic_is_enabled()` reports whether a DRM device has any compatible plane.
- Module parameters select panic screen type and QR version.

## Control Flow

At init, `drm_panic_init()` parses `CONFIG_DRM_PANIC_SCREEN`, falls back to user mode on invalid configuration, and preallocates QR resources when configured. Registration walks all planes and registers only those with `helper_private->get_scanout_buffer`.

On a `KMSG_DUMP_PANIC` event, `drm_panic()` resolves the containing plane and calls `draw_panic_plane()`. That function uses `drm_panic_trylock()` to avoid unsafe concurrent drawing, calls the driver's panic buffer callback, rejects unsupported multi-plane or non-convertible formats, and requires one drawing path: `set_pixel`, `pages`, or an `iosys_map`. Drawing converts configured XRGB8888 foreground/background colors to the target format. Page-backed drawing maps pages with `kmap_local_page_try_from_panic()` and handles 24-bit pixels crossing page boundaries.

The user renderer centers the message and draws either a copied mono Linux logo or ASCII logo if it does not overlap. The kmsg renderer fills the screen and writes recent kmsg lines bottom-up with wrapping. The QR renderer gathers kmsg data, optionally zlib-compresses it into a configured URL parameter, calls the Rust QR encoder, scales the QR image to at least 2x, lays it out above the message, and falls back to the user renderer on failure.

## State and Persistence

Persistent runtime state includes the selected `drm_panic_type`, optional copied mono logo, static panic message array with a temporarily substituted description line, and QR buffers/workspace. Per-plane state is stored in each `drm_plane`'s `kmsg_panic` dumper. No panic-time dynamic allocation is intended except debugfs test paths; QR buffers are allocated before panic.

## Dependencies and Integration Points

The file integrates with DRM plane helpers, DRM draw conversion helpers, framebuffer format metadata, kmsg dumpers, fonts, Linux logo, zlib, debugfs, module parameters, and Rust FFI functions from `drm_panic_qr.rs`. Driver integration requires `get_scanout_buffer`, optional `panic_flush`, and a linear or panic-addressable scanout buffer.

## Risks and Edge Cases

- Panic context cannot sleep, allocate, take regular locks, or rely on IRQ/task progress. Driver callbacks must honor that contract.
- Only single-plane formats convertible from XRGB8888 are supported.
- Page-backed 24-bit drawing has special cross-page handling; invalid page arrays can still prevent pixels from being written.
- QR mode depends on preallocated buffers and zlib workspace; failure falls back to user message.
- `drm_panic_type_get()` indexes `drm_panic_type_map`; init must set a valid type before user reads.
- Debugfs trigger is explicitly marked unsafe and only for testing.
- Multiple registered planes may all draw during panic; each uses the device panic lock.

## Test Signals

KUnit coverage is included through `tests/drm_panic_test.c` when enabled. Additional test signals include supported and unsupported formats, `set_pixel` versus mapped versus page-backed buffers, QR buffer allocation failure, QR too-large fallback, kmsg wrapping, panic description trimming, panic flush callback invocation, registration/unregistration counts, and debugfs trigger behavior outside real panic context.
