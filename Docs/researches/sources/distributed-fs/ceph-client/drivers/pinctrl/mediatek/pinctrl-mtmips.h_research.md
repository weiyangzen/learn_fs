# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtmips.h

## Purpose
This header defines the small table-building API for MTMIPS/Ralink pinmux drivers. SoC files use it to declare mux functions, groups, masks, GPIO values, and register shifts, then pass the resulting group array to `mtmips_pinctrl_init()`.

## Important APIs And Types
`FUNC(name, value, pin_first, pin_count)` initializes `struct mtmips_pmx_func` with a mux value and contiguous pin range. `GRP(name, func, mask, shift)` initializes a group whose GPIO value equals its mask. `GRP_G(name, func, mask, gpio, shift)` allows a group-specific GPIO value separate from the field mask. `struct mtmips_pmx_func` stores function name, field value, contiguous pin range, generated pin array, owning groups, group count, and an `enabled` flag. `struct mtmips_pmx_group` stores group name, enabled flag, sysc field shift/mask/GPIO value, function array, and function count.

## Control Flow And Integration
This header has no runtime flow itself. The SoC-specific drivers include it, build sentinel-terminated `struct mtmips_pmx_group` arrays, and call the shared initializer from their probe functions. The shared implementation mutates `pins`, `groups`, `group_count`, and `enabled` fields at runtime, so these tables are not strictly const.

## State And Persistence
The structs include mutable fields populated or changed by `pinctrl-mtmips.c`. Generated pin arrays and group backpointers are devm-managed by the initializer. Hardware persistence is not described here; the implementation writes sysc GPIO mode registers.

## Dependencies
The header assumes Linux kernel types such as `u32`, `ARRAY_SIZE`, and `struct platform_device` are available from including C files. It also assumes contiguous pin ranges are sufficient to describe every SoC function.

## Risks
Because function/group tables are mutable, declaring them `const` in a SoC file would be invalid with the current implementation. The `char` type for mux values, masks, and GPIO values is narrow; larger fields would need schema changes. Incorrect `pin_first`/`pin_count` values directly affect generated pin descriptors and GPIO eligibility.

## Test Signals
Compile all RT2880/RT305x/RT3883 users after macro changes. Runtime tests should verify group counts, function names, generated pin names, and sysc field writes match each SoC table.
