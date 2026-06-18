# File Research: sources/block-storage/lvm2/tools/lvm2cmd.c

## Purpose
Provides `liblvm2cmd` initialization entry points for normal dynamic/non-static builds and a stub shell implementation for library contexts.

## Main Behavior
- `lvm2_init()` calls `cmdlib_lvm2_init(0, 0)`.
- `lvm2_init_threaded()` calls `cmdlib_lvm2_init(0, 1)`.
- Defines `lvm_shell()` as a no-op returning `0`.

## Important Details
- The static flag is `0`, unlike `lvm2cmd-static.c`.
- The no-op `lvm_shell()` satisfies linkage for builds that expose command-library APIs but do not provide the interactive executable shell implementation from `lvm.c`.

## Dependencies
- `lvm2cmdline.h`.
- `tools/lvm2cmd.h`.
