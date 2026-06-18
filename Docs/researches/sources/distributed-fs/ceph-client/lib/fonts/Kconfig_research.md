# sources/distributed-fs/ceph-client/lib/fonts/Kconfig

## Purpose
Defines Kconfig options for kernel compiled-in console/display fonts under `FONT_SUPPORT`. It lets framebuffer, STI, DRM panic, and DRM client log users select specific bitmap fonts and auto-selects a safe default when none is chosen.

## Important APIs, Types, and Functions
This is configuration data rather than C code. Key symbols are `FONT_SUPPORT`, `FONTS`, individual font booleans such as `FONT_8x8`, `FONT_8x16`, `FONT_10x18`, Terminus and Sun font options, and `FONT_AUTOSELECT`, which selects `FONT_8x16` when no explicit font option is enabled.

## Control Flow
Kconfig visibility and defaults depend on console/display symbols and architecture predicates. `FONTS` gates most user-visible choices. Several fonts have architecture/platform defaults when `FONTS` is not selected. `FONT_AUTOSELECT` is a derived bool that depends negatively on every explicit font choice and selects `FONT_8x16`.

## State and Persistence
The state is build-time `.config` symbol selection. It persists in kernel configuration and controls which font objects are compiled.

## Dependencies and Integration Points
Integrates with `lib/fonts/Makefile`, framebuffer console, STI console, DRM panic/log paths, SPARC, ARM/Acorn, Amiga/Mac defaults, BOOTX text, and early framebuffer support. Selected symbols determine available `font_desc` objects for `font.c`.

## Risks
Dependency expressions must match driver capabilities; selecting an unsupported font can waste space or fail display expectations. `FONT_AUTOSELECT` must be kept in sync with every individual font option. Some options are hidden unless `FONTS` is enabled, so defaults are important for noninteractive configs.

## Test Signals
Run Kconfig builds for framebuffer, DRM panic, SPARC, ARM Acorn, Mac, and minimal configurations. Verify `FONT_AUTOSELECT` selects `FONT_8x16` only when no other font is selected and that Makefile object inclusion matches selected symbols.
