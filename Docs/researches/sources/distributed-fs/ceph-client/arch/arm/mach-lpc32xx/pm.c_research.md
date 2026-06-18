# sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/pm.c

Purpose: LPC32xx suspend implementation that copies a low-level suspend routine into IRAM so DRAM can enter self-refresh while clocks stop.

Important APIs/types/functions: Defines `lpc32xx_pm_enter()`, `lpc32xx_pm_ops`, and `lpc32xx_pm_init()` arch initcall.

Control flow: PM init sets the EMC SDRAM self-refresh clock behavior and installs suspend ops. Enter allocates a backup of the IRAM target area, copies `lpc32xx_sys_suspend` into IRAM, flushes I-cache/cache, calls the IRAM routine, restores the original IRAM contents, and frees the backup.

State and persistence: State includes a temporary heap backup of the IRAM code area and global suspend ops. Hardware state includes EMC self-refresh mode bit and whatever `suspend.S` changes during halt.

Dependencies and integration points: Depends on `suspend.S` symbols, `lpc32xx.h` static mappings, Linux suspend core, cache maintenance, and kmemdup allocation.

Risks: If allocation fails suspend returns `-ENOMEM`. Copying over IRAM assumes no other critical IRAM user needs that range during suspend. Only mem suspend is advertised despite comments mentioning standby.

Test signals: Run suspend-to-mem, verify IRAM contents restore, DRAM retention, wake events, and behavior under memory pressure.
