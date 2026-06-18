# sources/distributed-fs/ceph-client/drivers/media/rc/keymaps/Makefile

## Purpose

`drivers/media/rc/keymaps/Makefile` is the Kbuild manifest for the rc-core remote-controller keymap modules. It lists the individual `rc-*.o` objects that are built when `CONFIG_RC_MAP` is enabled and asks maintainers to keep the list alphabetically sorted by directory/file name.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_RC_MAP) += ...` attaches the whole keymap object list to the `RC_MAP` Kconfig symbol.
- This snapshot lists 138 keymap objects, including the files covered by this work item such as `rc-adstech-dvb-t-pci.o`, `rc-hauppauge.o`, and `rc-mygica-utv3.o`.
- `rc-cec.o` is intentionally not in this list; it is linked through the parent rc-core Makefile under `CONFIG_MEDIA_CEC_RC`.

## Control Flow

There is no runtime flow. During Kbuild evaluation, enabled objects are compiled either into the kernel or into modules according to `CONFIG_RC_MAP`. Each compiled keymap C file then supplies its own module initialization path that registers a `struct rc_map_list` with rc-core.

## State and Persistence Behavior

The file controls build artifacts only. Omitting an object prevents that keymap from existing as a built-in or module. Adding an object makes the static map available for rc-core registration but does not create runtime state until the object is loaded or linked.

## Dependencies and Integration Points

The Makefile depends on `drivers/media/rc/keymaps/Kconfig`, Kbuild composite-object semantics, and the source filenames in this directory. It integrates with receiver drivers via the `RC_MAP_*` names exported by the compiled objects and with distribution packaging through the module set produced for media keymaps.

## Risks and Edge Cases

The list is hand-maintained and large, so missing a new `rc-*.c`, leaving a deleted object, or breaking alphabetical order are common maintenance risks. Build failures catch stale filenames, but omission of a valid new map may only appear as runtime map lookup failure. Special maps such as CEC must remain in the parent rc-core build path rather than this generic `CONFIG_RC_MAP` list.

## Test Signals

Useful checks include `make M=drivers/media/rc/keymaps`, full media builds with `CONFIG_RC_MAP=y` and `=m`, `LC_ALL=C sort` comparison for list ordering, module packaging checks for expected `rc-*.ko` outputs, and runtime lookup or autoload tests for representative maps from the beginning, middle, and end of the list.
