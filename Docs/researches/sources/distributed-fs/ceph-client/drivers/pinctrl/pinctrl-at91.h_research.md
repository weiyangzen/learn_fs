# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-at91.h

## Purpose
This header is a register-layout contract for Atmel/Microchip AT91 Parallel I/O Controller pinctrl drivers. It contains no executable code; it centralizes PIO register offsets and bit masks used by AT91 pinctrl/GPIO implementations for muxing, GPIO direction/value, interrupt mode, pull configuration, filtering, Schmitt trigger, drive strength, and slew rate.

## Important APIs, Types, and Definitions
The exported API is a set of preprocessor constants. Core PIO offsets include `PIO_PER`, `PIO_PDR`, and `PIO_PSR` for PIO ownership; `PIO_OER`, `PIO_ODR`, and `PIO_OSR` for direction; `PIO_SODR`, `PIO_CODR`, `PIO_ODSR`, and `PIO_PDSR` for output and input data; `PIO_IER`, `PIO_IDR`, `PIO_IMR`, and `PIO_ISR` for interrupts; `PIO_PUER`, `PIO_PUDR`, `PIO_PPDER`, and `PIO_PPDDR` for pulls; `PIO_ASR`/`PIO_BSR` and `PIO_ABCDSR1`/`PIO_ABCDSR2` for peripheral muxing; and late-generation drive/slew offsets such as `SAM9X60_PIO_SLEWR`, `SAMA5D3_PIO_DRIVER1`, and `AT91SAM9X5_PIO_DRIVER1`. The only bit mask is `PIO_SCDR_DIV` for the slow-clock debounce divider.

## Control Flow and State
There is no runtime control flow or persistent C state. State lives in the hardware registers named by the macros. Downstream drivers choose offsets according to SoC generation and then read/write MMIO to apply pinctrl state. Several offsets are aliases because older PIO blocks use A/B selection while newer blocks use ABCD selection at the same addresses.

## Dependencies and Integration Points
The header is guarded by `__PINCTRL_AT91_H` and is intended for inclusion by AT91 pinctrl implementation files in the same driver family. It depends only on the C preprocessor and Linux kernel coding conventions; hardware access helpers are supplied by consumers.

## Risks
Incorrect offset use can corrupt mux, GPIO, or interrupt setup across an entire PIO bank. The aliasing of `PIO_ASR` with `PIO_ABCDSR1` and `PIO_BSR` with `PIO_ABCDSR2` makes SoC-specific selection logic important. Register names do not encode which silicon generation supports them, so consumers must gate late-generation drive and slew registers correctly.

## Test Signals
Useful validation comes from building AT91 pinctrl drivers that include this header, booting boards with GPIO, mux, pull, debounce, and interrupt DT states, and checking debugfs pinctrl state against expected PIO register values. Regression signals include broken GPIO direction/value operations, failed interrupt trigger configuration, and incorrect peripheral mux selection on SAM9/SAMA5/SAM9X60 variants.
