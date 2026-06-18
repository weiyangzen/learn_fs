# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/hw/Kconfig

## Purpose
Defines MMP display hardware controller and optional LCD-controller SPI-port configuration.

## Important APIs, Types, and Functions
- `config MMP_DISP_CONTROLLER` is a bool depending on clocks, I/O memory, and MMP/PXA910/compile-test platform support.
- `config MMP_DISP_SPI` is a bool depending on `MMP_DISP_CONTROLLER && SPI_MASTER` and defaults to `y`.

## Control Flow
Kconfig exposes the hardware controller option and, when available, the SPI master option used for panel initialization.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Controls compilation of `mmp_ctrl.o` and `mmp_spi.o` from the hw Makefile.

## Risks
Default SPI support depends on `SPI_MASTER`; missing it prevents SPI panels from initializing through the LCD controller.

## Test Signals
Build matrix should cover controller only, controller plus SPI, and compile-test builds.
