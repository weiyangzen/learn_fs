# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/sleep.S

Purpose: low-level PXA25x/PXA27x/PXA3xx suspend entry routines that finish CPU sleep after C code has prepared the system.

Important APIs/types/functions: assembly entry points are `pxa3xx_finish_suspend`, `pxa27x_finish_suspend`, and `pxa25x_finish_suspend`. They use SMEMC and clock register constants such as `MDREFR`, `CCCR`, `CLKCFG`, and `UNCACHED_PHYS_0`.

Control flow: PXA3xx writes sleep mode to coprocessor p14 and spins. PXA27x/PXA25x prepare the requested PWRMODE, physical-zero pointer, SDRAM self-refresh bits, and reduced clock settings, then branch into common CPU suspend code that executes from safe memory while clocks and SDRAM behavior change.

State and persistence: mutates CPU power mode, clock configuration, and SDRAM refresh/self-refresh state. No durable persistence, but correctness preserves DRAM contents across suspend.

Dependencies and integration points: called by PXA PM code; depends on `smemc.h`, PXA register definitions, ARM assembler macros, and board suspend paths such as SharpSL.

Risks: wrong register values can hang resume or corrupt memory. Errata workarounds are timing/order sensitive and SoC-family conditional assembly must match the selected kernel.

Test signals: suspend/resume smoke tests on each PXA family, resume PC validation, DRAM stress after resume, and clock-rate validation around sleep.
