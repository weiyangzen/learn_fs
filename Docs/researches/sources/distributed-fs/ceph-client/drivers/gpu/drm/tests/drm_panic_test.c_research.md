# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_panic_test.c

## Purpose
KUnit tests for DRM panic screen drawing. The suite verifies panic screen renderers write or address pixels correctly for mapped framebuffers, page-list framebuffers, and callback-driven pixel plotting across several resolutions and formats.

## Important APIs, Types, And Functions
`struct drm_test_mode` describes width, height, DRM fourcc format, draw function, and screen name. `DRM_TEST_MODE_LIST()` expands cases for user, kmsg, and optionally QR-code screens. `drm_test_panic_init()` allocates a `drm_scanout_buffer` and sets a panic description. `drm_test_panic_screen_user_map()` tests contiguous memory through `iosys_map`. `drm_test_panic_screen_user_page()` tests page-backed scanout buffers. `drm_test_panic_screen_user_set_pixel()` installs `drm_test_panic_set_pixel()` to assert bounds.

## Control Flow
For mapped buffers, the test fills vmalloc memory with `0xa5`, sets scanout dimensions/pitch/format, invokes the selected draw function, and checks bytes if panic colors are the configured defaults. For page buffers, it allocates pages, maps and pre-fills each page, draws, validates only bytes within framebuffer size, then frees pages. The set-pixel path never stores pixels; it asserts every callback coordinate is within bounds.

## State And Persistence
State is transient framebuffer memory or allocated pages plus one KUnit-owned `drm_scanout_buffer`. The global panic description is set for the test run. No persistent storage exists.

## Dependencies And Integration Points
The file integrates `drm_panic.h` draw functions, `drm_format_info()`, vmalloc, page allocation, `kmap_local_page()`, and optional `CONFIG_DRM_PANIC_SCREEN_QR_CODE`. Color-byte validation depends on `CONFIG_DRM_PANIC_BACKGROUND_COLOR` and `CONFIG_DRM_PANIC_FOREGROUND_COLOR`.

## Risks And Maintenance Notes
The byte validation is intentionally disabled for non-default panic colors, reducing coverage for custom configurations. Page allocation loops must clean up partially allocated pages correctly. Drawing algorithms that leave padding or untouched pixels could fail map/page tests. Large 1920x1080 allocations may be heavier than most KUnit cases.

## Test Signals
Signals include no allocation failures, all mapped/page framebuffer bytes rewritten to expected default color bytes, no out-of-bounds set-pixel callbacks, and parameter descriptions naming screen, resolution, and format.
