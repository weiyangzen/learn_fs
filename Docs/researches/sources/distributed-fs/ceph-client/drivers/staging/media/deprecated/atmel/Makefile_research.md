# sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/Makefile

## Purpose
This Makefile maps the deprecated Atmel ISC Kconfig symbols to the built objects.

## Important Build Rules
`atmel-isc-objs` contains `atmel-sama5d2-isc.o`, `atmel-xisc-objs` contains `atmel-sama7g5-isc.o`, and `atmel-isc-common-objs` contains `atmel-isc-base.o atmel-isc-clk.o`. The final object rules build `atmel-isc-common.o` for `CONFIG_VIDEO_ATMEL_ISC_BASE`, `atmel-isc.o` for `CONFIG_VIDEO_ATMEL_ISC`, and `atmel-xisc.o` for `CONFIG_VIDEO_ATMEL_XISC`.

## Control Flow and State
The Makefile has no runtime state. It ensures both SoC-specific drivers link against a shared common module/object when selected by Kconfig.

## Dependencies and Integration Points
It depends on the Kbuild object-composition convention and Kconfig symbols in the adjacent Kconfig file. Link-time integration requires exported symbols from `atmel-isc-base.o` and `atmel-isc-clk.o` to be available to the SoC-specific object modules.

## Risks and Test Signals
Risks are stale object names after file moves or symbol changes and incorrect base selection causing unresolved exports. Test signals are module and built-in builds for each Kconfig combination and verifying `modinfo`/link output includes the intended object composition.
