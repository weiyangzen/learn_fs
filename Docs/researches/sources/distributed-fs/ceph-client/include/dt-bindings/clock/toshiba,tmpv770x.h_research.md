# sources/distributed-fs/ceph-client/include/dt-bindings/clock/toshiba,tmpv770x.h

## Purpose
Defines Toshiba TMPV770X PLL, clock, and reset identifiers for DT bindings. It covers many SoC blocks including CPU, memory, video/image processing, networking, PCIe, USB, NAND, UART, I2C, SPI, PWM, and timer domains.

## Important APIs, Types, and Constants
Exports `TMPV770X_PLL_*`, `TMPV770X_CLK_*`, and `TMPV770X_RESET_*` macros. PLL IDs begin at 0, clock IDs extend to values around 129, and reset IDs are a separate namespace ending with video/image reset constants such as `TMPV770X_RESET_VIIFBS1_L1ISP` 39. There are no helper macros or C declarations.

## Control Flow and State
No executable flow. Clock/reset state is handled by the TMPV770X clock and reset controller drivers.

## Dependencies and Integration Points
The header is self-contained. It integrates with DT clock and reset specifiers for TMPV770X platform devices and the matching provider implementation.

## Risks and Test Signals
Because PLL, clock, and reset identifiers share one header but separate semantic namespaces, wrong use in `clocks` versus `resets` is a key integration risk. Test with DTS builds, schema checks, and probe coverage for image/video, networking, storage, and serial peripherals.
