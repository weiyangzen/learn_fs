# sources/distributed-fs/ceph-client/drivers/tty/serial/atmel_serial.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/atmel_serial.h` defines the Atmel/Microchip USART/UART register offsets, control/status bits, mode fields, FIFO fields, and helper field macros consumed by `atmel_serial.c`. The source was read as a complete 171-line file.

## Important APIs, Types, and Functions

The header is macro-only. It defines control-register commands such as `ATMEL_US_RSTRX`, `RXEN`, `TXEN`, `RSTSTA`, break control, DTR/RTS control, and FIFO enable/clear bits. Mode-register fields cover USART mode selection (`NORMAL`, `RS485`, `HWHS`, `MODEM`, `ISO7816_T0/T1`, `IRDA`), clock source, character length, parity variants, stop bits, channel mode, oversampling, ISO7816 ACK behavior, max iterations, and filters. Interrupt/status definitions cover RX/TX readiness, DMA/PDC completion, break, overrun/frame/parity errors, timeout, TX empty, ISO7816 iteration/NACK, and modem input changes. Additional definitions cover baud generator, timeout, timeguard, FIDI, FIFO mode/level/interrupt registers, IP name, and version.

## Control Flow

There is no executable control flow in the header. `atmel_serial.c` uses these constants to build mode words, issue write-only control commands, mask/unmask interrupts, classify RX errors, configure baud and ISO7816 parameters, and program FIFO thresholds.

## State and Persistence Behavior

The header owns no state. It describes hardware state that persists in MMIO registers until reset, power management, or explicit driver writes. Some registers are command-style write-only controls, while others are latched status or configuration registers.

## Dependencies and Integration Points

The header includes `<linux/bitfield.h>` and uses `BIT()`, `GENMASK()`, `FIELD_PREP()`, and `FIELD_GET()` to keep field definitions explicit. It is tightly integrated with the Atmel serial driver and any other local code that needs the same USART register contract.

## Risks and Edge Cases

Incorrect offsets or masks would corrupt core serial behavior, especially because many control register bits are write commands rather than persistent readable configuration. UART and USART variants reuse offsets differently, for example `ATMEL_US_RTOR`, `ATMEL_UA_RTOR`, and `ATMEL_US_TTGR`. FIFO threshold helpers assume caller-provided values fit field widths. Mode constants built with `FIELD_PREP()` must stay aligned with hardware documentation.

## Test Signals

Build coverage, register readback on supported AT91/SAMA5 variants, termios mode programming, FIFO threshold behavior, ISO7816 configuration, RS485 mode switching, interrupt mask/status handling, and suspend/resume register-cache restoration validate this header contract.
