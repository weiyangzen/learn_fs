# sources/distributed-fs/ceph-client/lib/fonts/Makefile

## Purpose
Build rules for the kernel font library. It composes the font support object from common font handling code, optional rotation support, and selected built-in bitmap font objects.

## Important APIs, Types, and Functions
This is kbuild data. `font-y` starts with `fonts.o`, conditionally adds `font_rotate.o` for `CONFIG_FRAMEBUFFER_CONSOLE_ROTATION`, conditionally adds `font_*.o` objects for each `CONFIG_FONT_*`, and finally adds `font.o` to `obj-*` when `CONFIG_FONT_SUPPORT` is enabled.

## Control Flow
Kbuild expands `font-y` based on configuration and links the selected objects into the composite `font.o`. The top-level `obj-$(CONFIG_FONT_SUPPORT)` controls whether the composite is built at all.

## State and Persistence
No runtime state exists. Build outputs are determined by `.config`.

## Dependencies and Integration Points
Depends on symbols defined in `lib/fonts/Kconfig` and source files in the same directory. It integrates with kernel kbuild composite-object semantics and the console font selection code that expects selected `font_desc` objects to be linked.

## Risks
Kconfig/Makefile drift can produce selectable fonts that are never linked, or linked objects that cannot be selected. Object order is documented as sorted by family-size, which should remain stable if consumers depend on predictable built-in ordering.

## Test Signals
Build with each `CONFIG_FONT_*` symbol enabled individually and in combinations, check that expected objects appear in build logs, and verify rotation object inclusion with `CONFIG_FRAMEBUFFER_CONSOLE_ROTATION`.
