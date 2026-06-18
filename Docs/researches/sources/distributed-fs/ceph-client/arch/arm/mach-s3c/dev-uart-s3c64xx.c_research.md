# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/dev-uart-s3c64xx.c

Purpose: S3C64xx UART resource definitions for legacy Samsung serial devices.

Important APIs/types/functions: declares per-UART resources for memory and IRQs and provides the resource table consumed by common UART device initialization.

Control flow: common UART init uses these resources when platform code calls `s3c24xx_init_uartdevs()`.

State and persistence: static resource arrays define UART MMIO/IRQ assignment.

Dependencies and integration points: integrates S3C serial driver, `dev-uart.c`, IRQ/map constants, and board-provided UART config.

Risks: incorrect resource order or IRQ mapping breaks console/serial ports.

Test signals: boot console on selected UART, all UART device probes, and low-level UART config match.
