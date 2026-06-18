# sources/distributed-fs/ceph-client/arch/xtensa/platforms/xt2000/include/platform/serial.h

Purpose: Defines XT2000 DUART addresses, IRQs, crystal frequency, and base baud.

Important APIs, types, and functions: `DUART16552_1_INTNUM`, `DUART16552_2_INTNUM`, `DUART16552_1_ADDR`, `DUART16552_2_ADDR`, `DUART16552_XTAL_FREQ`, and `BASE_BAUD`.

Control flow: Header-only constants used by 8250 platform device setup and generic serial code.

State and persistence: No runtime state.

Dependencies and integration: `asm/core.h`, `asm/io.h`, XT2000 setup's `plat_serial8250_port` table, and 8250 serial driver.

Risks: Endian-specific address adjustment happens in setup, so these base addresses must remain raw channel bases; wrong crystal frequency produces incorrect baud.

Test signals: 8250 serial probe, console baud correctness, and interrupts from both DUART channels.
