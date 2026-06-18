# sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/common.h

Purpose: Private LPC32xx architecture declarations shared by platform files.

Important APIs/types/functions: Declares `lpc32xx_map_io()`, `lpc32xx_serial_init()`, `lpc32xx_get_uid()`, `lpc32xx_sys_suspend()`, and `lpc32xx_sys_suspend_sz`.

Control flow: No runtime flow; it provides prototypes for C and assembly integration.

State and persistence: No state, but it exposes the suspend assembly size symbol and UID access contract.

Dependencies and integration points: Used by `common.c`, `phy3250.c`, `pm.c`, and `suspend.S` integration.

Risks: Prototype/signature drift with the assembly symbol or PM caller breaks suspend copying. The suspend size is declared as `int` even though emitted as a word symbol.

Test signals: Compile all LPC32xx objects with warnings enabled; suspend path validates assembly symbol linkage.
