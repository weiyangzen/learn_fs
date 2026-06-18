# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_composer.h

## Purpose

`vkms_composer.h` declares KUnit-visible compositor helper APIs and the LUT channel enum used to index `struct drm_color_lut` fields.

## Important APIs and types

`enum lut_channel` maps red, green, blue, and reserved channels to the physical field order of `struct drm_color_lut`; the code relies on this ordering when treating LUT entries as `__u16` arrays. Under `CONFIG_KUNIT`, the header declares `lerp_u16()`, `get_lut_index()`, `apply_lut_to_channel_value()`, and `apply_3x4_matrix()`.

## Integration, state, and risks

The header has no runtime state. It depends on `kunit/visibility.h` and `vkms_drv.h`. Its primary integration point is between `vkms_composer.c` and the KUnit color suite. The risk is ABI/layout sensitivity: the compositor asserts `struct drm_color_lut` has no unexpected padding, and this enum must remain aligned with that struct layout.

## Test signals

The `vkms-color` KUnit suite uses these declarations to validate interpolation, LUT lookup, and matrix transformation behavior. Build failures under `CONFIG_DRM_VKMS_KUNIT_TEST` would flag missing or mismatched declarations.
