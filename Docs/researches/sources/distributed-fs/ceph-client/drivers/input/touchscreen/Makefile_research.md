# sources/distributed-fs/ceph-client/drivers/input/touchscreen/Makefile

## Purpose
This Makefile maps touchscreen Kconfig symbols to their implementation object files and defines a few composite module object lists.

## Important APIs, types, and functions
The file defines composite objects such as `wm97xx-ts-y := wm97xx-core.o`, `goodix_ts-y := goodix.o goodix_fwupload.o`, `tsc2007-y := tsc2007_core.o`, and conditional additions for `tsc2007_iio.o` and WM97xx chip variants. It then maps dozens of `CONFIG_TOUCHSCREEN_*` symbols to `.o` files.

## Control flow
Kbuild evaluates `obj-$(CONFIG_...)` assignments to include built-in or module objects. Composite object variables collect multiple source files into one module target, such as Goodix firmware upload support or WM97xx chip-specific support.

## State and persistence
There is no runtime state. Build outputs depend entirely on `.config` and Kbuild rules.

## Dependencies and integration points
This file is the build counterpart to touchscreen Kconfig. It must align symbol names, source filenames, composite module names, and helper-core selections for all touchscreen drivers.

## Risks
The large list is prone to symbol/object mismatches. Composite module rules can accidentally omit optional pieces if their Kconfig symbol logic changes. Adding, renaming, or splitting a driver requires coordinated Makefile and Kconfig updates.

## Test signals
Run allmodconfig and targeted builds for representative simple, composite, bus-split, and optional-helper drivers: `goodix_ts`, `wm97xx-ts`, `tsc2007`, `ad7879-*`, `goodix_berlin_*`, serial serio touchscreens, and USB composite support.
