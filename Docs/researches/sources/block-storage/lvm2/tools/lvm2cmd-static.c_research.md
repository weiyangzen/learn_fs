# File Research: sources/block-storage/lvm2/tools/lvm2cmd-static.c

## Purpose
Provides `liblvm2cmd` initialization entry points for static builds.

## Main Behavior
- `lvm2_init()` calls `cmdlib_lvm2_init(1, 0)`.
- `lvm2_init_threaded()` calls `cmdlib_lvm2_init(1, 1)`.

## Important Details
- The first argument marks the library as statically compiled.
- Threaded and non-threaded initialization are separated but share the same underlying initializer.
- This file is intentionally tiny and delegates all real setup to `lvmcmdlib.c`.

## Dependencies
- `lvm2cmdline.h` for `cmdlib_lvm2_init`.
- `tools/lvm2cmd.h` for the public API declarations.
