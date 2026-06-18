# sources/distributed-fs/ceph-client/drivers/media/platform/atmel/Kconfig

## Purpose
This Kconfig file declares the Atmel media platform driver menu entry and the `VIDEO_ATMEL_ISI` option for the Atmel Image Sensor Interface capture driver.

## Important APIs, Types, and Functions
The primary symbol is `VIDEO_ATMEL_ISI`, a tristate option. It depends on `V4L_PLATFORM_DRIVERS`, `VIDEO_DEV`, `OF`, and either `ARCH_AT91` or `COMPILE_TEST`. It selects `VIDEOBUF2_DMA_CONTIG` and `V4L2_FWNODE`.

## Control Flow
When enabled, Kbuild includes `atmel-isi.o` through the sibling Makefile. The dependencies restrict visibility to V4L2 platform-driver builds with device-tree support and either AT91 hardware or compile-test coverage.

## State and Persistence
The only persistent state is the selected kernel configuration. Runtime capture state lives in `atmel-isi.c`.

## Dependencies and Integration Points
The option wires the driver to the V4L2 core, OF graph/fwnode endpoint parsing, and DMA-contiguous vb2 allocation used by the ISI DMA engine.

## Risks and Edge Cases
Missing `V4L2_FWNODE` or vb2 DMA selection would break the driver at build time. Overly narrow architecture dependencies would reduce compile coverage; overly broad dependencies could expose an unsupported platform driver.

## Test Signals
Use `ARCH_AT91` builds and `COMPILE_TEST` allmodconfig coverage. Confirm `CONFIG_VIDEO_ATMEL_ISI=m` produces `atmel-isi.ko`.
