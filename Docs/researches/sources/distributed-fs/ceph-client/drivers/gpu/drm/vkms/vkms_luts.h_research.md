# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_luts.h

## Purpose

`vkms_luts.h` is the small public declaration header for VKMS built-in color lookup tables. It defines the shared LUT length and declares the exported linear, sRGB, and inverse-sRGB `vkms_color_lut` descriptors.

## Important APIs, Types, and Functions

- `LUT_SIZE`: fixed table size of 256 entries used by the static tables in `vkms_luts.c`.
- `linear_eotf`, `srgb_eotf`, `srgb_inv_eotf`: extern declarations for immutable `struct vkms_color_lut` descriptors.
- Include guard `_VKMS_LUTS_H_`: prevents duplicate declarations.

## Control Flow

The header has no runtime control flow. It provides compile-time constants and extern declarations for color code that samples LUTs.

## State and Persistence Behavior

The declarations refer to static module-lifetime data defined in `vkms_luts.c`. The header itself owns no storage and performs no initialization.

## Dependencies and Integration Points

- Assumes `struct vkms_color_lut` is visible before or through including VKMS driver headers in consumers.
- Couples `LUT_SIZE` to the generated table definitions and index-ratio math in `vkms_luts.c`.

## Risks and Edge Cases

- Changing `LUT_SIZE` requires regenerating all table initializers and revisiting index conversion logic.
- Because this header only forward-declares objects, consumers must include the right VKMS type definitions to avoid incomplete-type failures.

## Test Signals

- Compile coverage for all VKMS color consumers catches missing type declarations and symbol signature drift.
- Static assertions or table-size tests are useful if `LUT_SIZE` is ever changed.
