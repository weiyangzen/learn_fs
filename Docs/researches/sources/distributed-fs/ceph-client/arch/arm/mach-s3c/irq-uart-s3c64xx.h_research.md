# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/irq-uart-s3c64xx.h

Purpose: UART interrupt definitions for S3C64xx.

Important APIs/types/functions: declares or defines per-UART interrupt mapping helpers/macros used by Samsung serial IRQ setup.

Control flow: no local flow; included by UART IRQ/device setup code.

State and persistence: constants map UART subinterrupts to generic IRQ numbers.

Dependencies and integration points: integrates S3C64xx IRQ definitions with the Samsung serial driver and platform devices.

Risks: wrong UART IRQ mapping breaks console RX/TX/error handling.

Test signals: serial console interrupts, RX/TX under load, and all configured UART ports.
