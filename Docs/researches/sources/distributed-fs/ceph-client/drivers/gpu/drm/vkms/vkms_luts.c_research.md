# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_luts.c

## Purpose

`vkms_luts.c` provides built-in VKMS color lookup tables used by the virtual KMS color pipeline. It is data-only: 256-entry DRM LUT arrays encode linear, sRGB EOTF, and inverse sRGB transfer curves, and exported `vkms_color_lut` descriptors give other VKMS color code a uniform way to sample those arrays.

## Important APIs, Types, and Functions

- `linear_array`, `srgb_array`, and `srgb_inv_array`: static `struct drm_color_lut[LUT_SIZE]` tables with identical red/green/blue values and zero reserved fields.
- `linear_eotf`, `srgb_eotf`, and `srgb_inv_eotf`: exported `const struct vkms_color_lut` descriptors containing a table pointer, `lut_length = LUT_SIZE`, and `channel_value2index_ratio = 0xff00ffll`.
- `EXPORT_SYMBOL(...)`: makes the descriptors available to other VKMS compilation units or modules that implement color operations.
- The table-generation comment points to the external LUT generator and notes Skia transfer-function provenance.

## Control Flow

There is no executable control flow beyond module/link-time data initialization. Consumers choose one of the exported descriptors, convert a channel value to an index using the ratio, and read from the associated static array.

## State and Persistence Behavior

All state is static and immutable after load. The backing arrays are private to this translation unit; only descriptor addresses are exported. There is no allocation, locking, refcounting, or persistence outside the kernel image/module lifetime.

## Dependencies and Integration Points

- Depends on DRM `struct drm_color_lut` from `<drm/drm_mode.h>`.
- Depends on `struct vkms_color_lut` from `vkms_drv.h` and `LUT_SIZE` declarations from `vkms_luts.h`.
- Integrates with VKMS color pipeline code that implements EOTF/inverse EOTF transformations and expects 16-bit DRM LUT channel values.

## Risks and Edge Cases

- The descriptor ratio must stay synchronized with `LUT_SIZE` and the 16-bit input range. A mismatched ratio can clamp or skip entries.
- The table values are generated constants, so review should focus on monotonicity, endpoints, and curve identity rather than algorithmic behavior.
- All three channels are equal, making these grayscale transfer curves. Any future per-channel curve must update assumptions in consumers.
- External provenance means regeneration should be reproducible and documented when curves change.

## Test Signals

- Build/link checks should confirm the exported symbols resolve for VKMS color code.
- Unit or KUnit coverage should verify first/last entries are `0x0000`/`0xffff`, each table has exactly `LUT_SIZE` entries, and values are monotonic.
- Color-pipeline tests should compare selected sRGB and inverse-sRGB samples against expected transfer-function tolerances.
