# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_sysfb_modeset_test.c

## Purpose
KUnit tests for `drm_sysfb_build_fourcc_list()`, the helper that derives a DRM format list for system framebuffers while ensuring XRGB8888 fallback support, de-duplicating formats, and replacing alpha variants with equivalent opaque formats.

## Important APIs, Types, And Functions
`struct sysfb_build_fourcc_list_case` describes native fourcc inputs and expected output. Parameter cases cover no native formats, native XRGB8888, duplicate removal, alpha-to-X format conversion, and mixed random formats. `drm_test_sysfb_build_fourcc_list()` allocates a mock DRM device and calls `drm_sysfb_build_fourcc_list()`.

## Control Flow
For each case, the test builds a mock device through `drm_kunit_helpers`, calls the sysfb helper with a fixed output buffer size of 50, then checks returned count and full output buffer memory against the expected array. The expected arrays preserve input order after normalization while ensuring an opaque XRGB8888 fallback appears where needed.

## State And Persistence
State is static parameter data, a stack output array, and transient mock device/DRM device resources. No persistent state exists.

## Dependencies And Integration Points
The test includes `../sysfb/drm_sysfb_helper.h` and uses DRM fourcc definitions plus shared KUnit helpers. It protects sysfb integration used when firmware/system framebuffers are handed to DRM modeset clients.

## Risks And Maintenance Notes
The `remove duplicates` case sets `native_fourccs_size = 11` despite initializing more values, so only the first 11 entries are intentionally passed. Full-buffer `KUNIT_EXPECT_MEMEQ()` means unused output slots are expected to remain zero. Any helper policy change around fallback ordering, duplicate retention, or alpha conversion will require expected arrays to change.

## Test Signals
Signals include exact number of output formats, exact normalized fourcc order, no duplicate retained formats, alpha formats converted to corresponding X formats, and XRGB8888 present for fallback when needed.
