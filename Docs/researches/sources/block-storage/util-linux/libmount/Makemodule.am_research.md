# File Research: sources/block-storage/util-linux/libmount/Makemodule.am

## Scope

Autotools top-level inclusion file for libmount.

## Behavior

- Gates all libmount build content behind `BUILD_LIBMOUNT`.
- Includes source, Python, and samples module makefiles.
- Adds docs subdirectory when GTK-Doc is enabled.
- Installs `libmount/mount.pc`, tracks it as a generated path file, and distributes COPYING.

## Dependencies And Risks

- This file only wires sub-builds; actual source lists live in included makefiles.
- Python bindings are included only if their own nested conditions enable them.
