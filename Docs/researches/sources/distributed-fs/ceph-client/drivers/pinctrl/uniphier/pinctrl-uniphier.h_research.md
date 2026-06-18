# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier.h

## Purpose

This header defines the shared data contract between UniPhier SoC-specific pinctrl data files and the common UniPhier pinctrl driver. It provides packed pin-attribute bit layouts, enums for drive and pull behavior, descriptor structs for groups/functions/SoC data, helper macros for declaring pins and groups, and the common probe/PM entry points.

## Important APIs, Types, And Data

- The packed `drv_data` layout stores input-enable control, drive control register, drive type, pull-up/down control register, and pull direction inside an unsigned long. `BUILD_BUG` logic rejects layouts that exceed `BITS_PER_LONG`.
- `enum uniphier_pin_drv_type` describes supported drive-strength models: 1-bit, 2-bit, 3-bit, fixed 4 mA, fixed 5 mA, fixed 8 mA, and no drive support.
- `enum uniphier_pin_pull_dir` describes pull-up, pull-down, fixed pull states, and no pull register.
- `uniphier_pin_get_*()` inline helpers unpack fields from `pinctrl_pin_desc.drv_data`.
- `struct uniphier_pinctrl_group` holds a group name, pins, pin count, and mux value array.
- `struct uniphier_pinmux_function` maps a function name to group names.
- `struct uniphier_pinctrl_socdata` packages SoC descriptors, function/group counts, GPIO mux callback, and capability flags.
- `UNIPHIER_PINCTRL_PIN`, `UNIPHIER_PINCTRL_GROUP`, `UNIPHIER_PINCTRL_GROUP_GPIO`, and `UNIPHIER_PINMUX_FUNCTION` are the main declaration macros used by SoC files.
- `uniphier_pinctrl_probe()` is the shared probe function implemented outside this header; `uniphier_pinctrl_pm_ops` exposes PM hooks.

## Control Flow

SoC files use the macros in this header to create static descriptor tables. Their platform-driver probe wrappers pass a `struct uniphier_pinctrl_socdata` to `uniphier_pinctrl_probe()`. The common driver later unpacks per-pin `drv_data` with the inline helpers when applying pinconf, pinmux, and GPIO operations.

`UNIPHIER_PINCTRL_GROUP` includes a compile-time guard that requires the `grp##_pins` and `grp##_muxvals` arrays to have the same length. GPIO-only groups can use `UNIPHIER_PINCTRL_GROUP_GPIO`, which sets mux values to `NULL`.

## State And Persistence

The header defines no runtime storage by itself. It shapes immutable SoC descriptor data and the interpretation of packed metadata. Persistent state is limited to hardware state manipulated by the common driver using this data.

## Dependencies And Integration Points

The header includes Linux bit/build/kernel/type helpers and forward-declares `struct platform_device`. It integrates with generic pinctrl through `struct pinctrl_pin_desc` users in the SoC data files, with platform drivers through `uniphier_pinctrl_probe()`, and with PM through `uniphier_pinctrl_pm_ops`.

Capability flags currently include `UNIPHIER_PINCTRL_CAPS_PERPIN_IECTRL` and `UNIPHIER_PINCTRL_CAPS_DBGMUX_SEPARATE`, allowing SoC data to select common-driver behavior without changing probe signatures.

## Risks And Edge Cases

- The packed pointer-sized `drv_data` contract is compact but brittle; field width changes must preserve `BITS_PER_LONG` safety on all supported architectures.
- Casts between packed integers and `void *` rely on storing small bitfields in `drv_data`, not actual pointers.
- The compile-time group length check prevents pin/mux count mismatch but cannot validate mux value semantics.
- Adding new drive or pull types requires synchronized changes in the common driver and all data users.

## Test Signals

Compile-time build coverage is important because macro expansion and `BUILD_BUG_ON_ZERO` checks catch descriptor-shape errors. Runtime validation comes indirectly from probing each UniPhier SoC file and applying pinconf for every drive and pull type used in descriptor data.
