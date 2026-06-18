# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_modes_test.c

## Purpose
KUnit tests for DRM analog TV mode constructors. The suite verifies generated NTSC 480i, PAL 576i, and monochrome 576i timings and confirms inline convenience constructors match the generic `drm_analog_tv_mode()` output.

## Important APIs, Types, And Functions
`struct drm_test_modes_priv` holds a mock device and DRM device. `drm_test_modes_init()` builds them with `drm_kunit_helpers`. Test functions call `drm_analog_tv_mode()`, `drm_mode_analog_ntsc_480i()`, `drm_mode_analog_pal_576i()`, `drm_mode_vrefresh()`, and `drm_mode_equal()`. Created modes are registered with `drm_kunit_add_mode_destroy_action()`.

## Control Flow
Each test allocates one or two modes, registers destroy actions, then checks timing fields. NTSC asserts 60 Hz, 720 horizontal display, hsync start 736, htotal 858, vdisplay 480, and vtotal 525. PAL and monochrome assert 50 Hz, hsync start 732, htotal 864, vdisplay 576, and vtotal 625. Inline tests compare full mode equality against generic construction.

## State And Persistence
State is limited to mock DRM device objects and allocated `drm_display_mode` instances that KUnit destroys at test end. No persistent state exists.

## Dependencies And Integration Points
The suite integrates DRM mode generation, KUnit helper devices, and `linux/units.h` for `HZ_PER_KHZ`. It protects analog-TV timing helpers used by probe helpers and connector TV mode enumeration.

## Risks And Maintenance Notes
Expected timings are tied to BT.601 and analog TV assumptions. If DRM changes interlace timing representation, vrefresh rounding, or helper defaults, tests may need updates. Since the suite checks raw timing fields, it can catch both intentional timing policy changes and accidental arithmetic regressions.

## Test Signals
Signals are exact mode fields, vrefresh values, non-null mode allocation, successful destroy action registration, and `drm_mode_equal()` for generic versus convenience constructors.
