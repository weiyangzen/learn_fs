# sources/distributed-fs/ceph-client/drivers/pcmcia/sa11xx_base.h

Purpose: Defines SA11xx MECR bit layout, timing calculation helpers, and public SA11xx PCMCIA base functions.

Important APIs and types: Provides `MECR_*_SET()` and `MECR_*_GET()` macros for BSIO, BSA, BSM, and FAST fields per socket. Inline helpers `sa1100_pcmcia_mecr_bs()` and `sa1100_pcmcia_cmd_time()` convert between command width and MECR wait-state encoding. Declares `sa11xx_drv_pcmcia_add_one()`, `sa11xx_drv_pcmcia_ops()`, and `sa11xx_drv_pcmcia_probe()`.

Control flow: No runtime flow except inline arithmetic/macros used by `sa11xx_base.c`.

State and persistence: Macros operate on MECR values; actual state persists in the hardware MECR register managed by the base driver.

Dependencies and integration points: Consumed by SA1100 and SA1111 board glue plus `sa11xx_base.c`. Requires common `soc_pcmcia_socket` definitions.

Risks: Macro arguments are evaluated in assignment expressions and should be simple lvalues/values. Timing helper arithmetic can underflow for invalidly small cycle requests. Socket selection assumes two MECR halves.

Test signals: Compile coverage and sysfs timing output matching MECR register fields after socket map changes.
