# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/tests/vkms_color_test.c

## Purpose

`vkms_color_test.c` is a KUnit suite for VKMS color math. It validates LUT indexing/interpolation, sRGB transfer LUT round-trips, and 3x4 color transformation matrices used by the composer and plane color pipeline.

## Important APIs and cases

The suite imports `lerp_u16()`, `get_lut_index()`, `apply_lut_to_channel_value()`, and `apply_3x4_matrix()` from `vkms_composer.c`, plus LUT tables from `vkms_luts.h`. `vkms_color_test_get_lut_index()` checks fixed-point LUT index calculations. `vkms_color_test_lerp()` covers boundary and half-step interpolation rounding. `vkms_color_test_linear()` verifies identity behavior through the linear EOTF table. `vkms_color_srgb_inv_srgb()` checks that sRGB EOTF followed by inverse EOTF returns approximately to the original 8-bit code value. Matrix tests validate a 50% desaturation matrix and a BT.709 encoding matrix.

## Control flow and state

The file is pure test code. It uses static reference LUT data, static parameter arrays, and KUnit expectations. No persistent kernel driver state is modified beyond loading the test module.

## Dependencies and integration

It depends on DRM fixed-point helpers, KUnit, VKMS composer exports, and the `EXPORTED_FOR_KUNIT_TESTING` namespace. These tests directly protect compositor color correctness because the same helpers are used during scanline blending.

## Risks and test signals

The strongest coverage is for rounding edges and standard transfer/matrix behavior. It does not exercise full plane atomic state, writeback output, or live DRM colorop property transitions. Passing `vkms-color` is a signal that color helper arithmetic and LUT table ratios remain compatible with expected 16-bit ARGB behavior.
