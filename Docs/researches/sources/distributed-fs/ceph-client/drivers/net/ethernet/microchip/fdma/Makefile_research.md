# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/fdma/Makefile

## Purpose
This Makefile builds the Microchip shared FDMA helper object when `CONFIG_FDMA` is enabled.

## Important Rules
`obj-$(CONFIG_FDMA) += fdma.o` creates the composite object, and `fdma-y += fdma_api.o` adds the implementation file. There are no conditional subfeatures.

## Control Flow, State, and Dependencies
The file participates only in kbuild. Its only state is the build-time `CONFIG_FDMA` symbol. It depends on the parent Microchip Ethernet Makefile descending into `fdma/`, which is guarded by the same symbol.

## Risks and Test Signals
The Makefile is intentionally minimal; the main risk is future source additions not being appended to `fdma-y`. Build tests with `CONFIG_FDMA=y` or a driver selecting FDMA should produce `fdma.o` and export the symbols from `fdma_api.c`.
