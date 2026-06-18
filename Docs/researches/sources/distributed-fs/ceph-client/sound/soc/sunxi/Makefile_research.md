# sources/distributed-fs/ceph-client/sound/soc/sunxi/Makefile

## Purpose
`sound/soc/sunxi/Makefile` maps Allwinner ASoC Kconfig symbols to the driver objects built for this directory.

## Important APIs, Types, And Functions
The build rules include `sun4i-codec.o`, `sun4i-i2s.o`, `sun4i-spdif.o`, `sun8i-codec-analog.o`, `sun50i-codec-analog.o`, `sun8i-codec.o`, `sun8i-adda-pr-regmap.o`, and `sun50i-dmic.o` under their corresponding `CONFIG_SND_*` symbols.

## Control Flow
There is no runtime control flow. Kbuild expands `obj-$(CONFIG_...)` entries according to whether each symbol is `y`, `m`, or unset.

## State And Persistence
Persistent state is the generated build graph. A built-in symbol links the object into the kernel image; a module symbol builds a loadable module.

## Dependencies And Integration Points
The file integrates directly with `Kconfig` symbols in the same directory and with the top-level ALSA SoC build. It is the final step that turns selected Sunxi audio support into compiled object files.

## Risks And Edge Cases
Any mismatch between Kconfig symbols and object names causes selected drivers to disappear from builds. The helper `sun8i-adda-pr-regmap.o` is hidden behind a selected symbol and must remain available to analog drivers.

## Test Signals
Build all Sunxi audio symbols as modules and built-ins, inspect `modules.order` for expected object modules, and run targeted incremental builds after changing Kconfig names or adding/removing driver files.
