# File Research: sources/block-storage/parted/libparted/labels/pt-common.h

## Purpose

`pt-common.h` factors repeated disk-label backend boilerplate into macros used by multiple libparted partition table implementations.

## Main Responsibilities

- Defines `NULL_IF_DISCOVER_ONLY()` so write callbacks disappear in discover-only builds.
- Defines `PT_define_limit_functions(PT_type)` to generate:
  - `PT_type_partition_check()`,
  - `PT_type_partition_max_start_sector()`,
  - `PT_type_partition_max_length()`.
- Defines `PT_op_function_initializers(PT_type)` to populate the common `PedDiskOps` function pointers for a backend.

## Dependencies and Interactions

The generated limit functions call `ptt_partition_max_start_len()`, `ptt_partition_max_start_sector()`, and `ptt_partition_max_length()` from `pt-tools.c`. Backends include this header near the end of their file after defining the required `PT_type_*` functions.

## Notable Details

The macros encode libparted’s expected naming convention for disk-label backends. A backend using `PT_op_function_initializers(foo)` must provide functions such as `foo_probe`, `foo_read`, `foo_partition_new`, `foo_partition_align`, and related partition methods.
