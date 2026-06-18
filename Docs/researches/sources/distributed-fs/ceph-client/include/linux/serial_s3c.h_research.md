# sources/distributed-fs/ceph-client/include/linux/serial_s3c.h

## Purpose

`serial_s3c.h` defines register offsets, bit masks, default register values, and machine configuration data for Samsung S3C/S5P/Apple S5L style UART controllers. It is an SoC-specific companion to `serial_core.h`, allowing platform setup and the Samsung UART driver to agree on register layout and per-port defaults.

## Important APIs, Types, And Functions

The file exports register offsets such as `S3C2410_ULCON`, `S3C2410_UCON`, `S3C2410_UFCON`, `S3C2410_UTRSTAT`, `S3C2410_UERSTAT`, `S3C2410_UFSTAT`, `S3C2410_UMSTAT`, `S3C2410_UTXH`, `S3C2410_URXH`, `S3C2410_UBRDIV`, and S3C64XX interrupt registers. It defines line-control masks for character size, parity, stop bits, and IR mode; control bits for clock selection, break, IRQ mode, FIFO timeout, loopback, DMA burst/mode, and error interrupts; FIFO trigger/reset/full/count masks for multiple chip families; modem control/status bits; divisor slot register offset; and Apple S5L-specific interrupt/status masks.

The only C type is `struct s3c2410_uartcfg`, available outside assembly. It captures hardware port number, default serial flags, clock selection, fractional divisor support, and default values for `ucon`, `ulcon`, and `ufcon`.

## Control Flow

There is no executable control flow. Driver code uses these macros while probing or configuring a port: choose the SoC-specific clock source and FIFO layout, build line-control values from termios, set or clear break and loopback, enable CPU or DMA modes, reset FIFOs, decode status/error bits during interrupt service, and program default UCON/UFCON values from `struct s3c2410_uartcfg`.

## State And Persistence

State is held by hardware registers and by per-machine `s3c2410_uartcfg` instances, not by this header. Default values such as `S3C2410_UCON_DEFAULT`, `S5PV210_UCON_DEFAULT`, and `APPLE_S5L_UCON_DEFAULT` influence initial persistent UART state until runtime termios or driver operations change it.

## Dependencies And Integration Points

The header depends on `linux/serial_core.h` for `upf_t` and UART core types when not included from assembly. It integrates with ARM Samsung platform initialization, the Samsung serial driver, clock selection logic, FIFO/interrupt handling, DMA-capable UART paths, and SoC-specific device descriptions.

## Risks And Test Signals

Risks are register-bit drift between SoC variants, mismatched FIFO count masks or trigger shifts, using a default UCON/UFCON value on the wrong controller family, and confusing similarly named AFC/RTS macros. Test signals include boot console on each supported SoC, termios parity/size/stop-bit changes, FIFO interrupt thresholds, RX error reporting, break generation, DMA mode TX/RX, and regression tests for Apple S5L timeout and threshold flags.
