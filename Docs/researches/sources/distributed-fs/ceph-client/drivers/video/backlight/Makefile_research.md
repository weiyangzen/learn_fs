# sources/distributed-fs/ceph-client/drivers/video/backlight/Makefile

## Purpose
This Makefile maps LCD and backlight Kconfig symbols to their corresponding driver objects in `drivers/video/backlight`.

## Important APIs, types, and functions
It uses kbuild `obj-$(CONFIG_SYMBOL) += object.o` lines. Relevant mappings include `CONFIG_LCD_AMS369FG06 -> ams369fg06.o`, `CONFIG_BACKLIGHT_88PM860X -> 88pm860x_bl.o`, `CONFIG_BACKLIGHT_AAT2870 -> aat2870_bl.o`, `CONFIG_BACKLIGHT_ADP5520 -> adp5520_bl.o`, `CONFIG_BACKLIGHT_ADP8860 -> adp8860_bl.o`, `CONFIG_BACKLIGHT_ADP8870 -> adp8870_bl.o`, `CONFIG_BACKLIGHT_APPLE -> apple_bl.o`, `CONFIG_BACKLIGHT_APPLE_DWI -> apple_dwi_bl.o`, `CONFIG_BACKLIGHT_ARCXCNN -> arcxcnn_bl.o`, `CONFIG_BACKLIGHT_AS3711 -> as3711_bl.o`, `CONFIG_BACKLIGHT_AW99706 -> aw99706.o`, `CONFIG_BACKLIGHT_CLASS_DEVICE -> backlight.o`, and `CONFIG_BACKLIGHT_BD6107 -> bd6107.o`.

## Control flow
Kbuild includes objects as built-in or modules according to each symbol value. The generic `backlight.o` class core is only built when `BACKLIGHT_CLASS_DEVICE` is enabled.

## State and persistence
Only build graph state exists. Runtime behavior is controlled by the resulting objects and their module metadata.

## Dependencies and integration points
The Makefile is the bridge from `backlight/Kconfig` symbols to C sources. It must remain synchronized with config names, module aliases, and file renames.

## Risks and test signals
Risks include missing object mappings, typos in symbol names, and building a driver without its framework object. Test signals include enabling each listed config as `m` and `y`, `make modules`, and comparing Kconfig entries against Makefile coverage.
