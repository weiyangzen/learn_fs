# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/power.c

## Purpose
`power.c` implements high-level Alchemy sleep entry support. It saves SoC core clock, pinmux, and static memory-controller registers, calls the CPU-family-specific assembly sleep routine, and restores the saved registers after wake.

## Important APIs, Types, And Functions
The public entry is `au_sleep()`. Private helpers are `save_core_regs()` and `restore_core_regs()`. Persistent save buffers are `sleep_sys_clocks[5]`, `sleep_sys_pinfunc`, and `sleep_static_memctlr[4][3]`. `au_sleep()` dispatches to assembly functions `alchemy_sleep_au1000()`, `alchemy_sleep_au1550()`, or `alchemy_sleep_au1300()` based on `alchemy_get_cputype()`.

## Control Flow
`au_sleep()` first snapshots frequency-control, clock-source, CPU PLL, AUX PLL, pin-function, and static-memory timing/address/config registers. It then calls the variant-specific low-level sleep code from `sleeper.S`, which handles CPU context, memory self-refresh, and wake handoff. After the assembly routine returns on wake, `restore_core_regs()` rewrites clocks, PLLs, pinmux, and static memory-controller configuration, avoiding CPU PLL restore on write-only early Au1000 parts.

## State And Persistence
The saved arrays persist only across one sleep cycle. Hardware state saved/restored includes clock generator registers, clock source muxes, CPU/AUX PLLs, pinmux, and four static memory banks. The function does not handle peripheral driver state; those are expected to be handled by driver PM or other syscore paths.

## Dependencies And Integration Points
It depends on Alchemy register access helpers, CPU type detection, `au1xxx_cpu_has_pll_wo()`, and the assembly routines in `sleeper.S`. IRQ and DBDMA syscore PM in other files save their own controller state around suspend. Board power-off hooks are separate from this sleep entry.

## Risks
Clock and memory-controller restoration order is hardware-sensitive; incorrect ordering can destabilize wake. The code assumes these register reads produce restorable values, except for write-only CPU PLL variants. Newer peripherals or memory-controller registers not listed here may need separate PM support. `au_sleep()` has no default error path for unknown CPU types; it simply saves and restores without entering a sleep routine.

## Test Signals
Suspend/resume tests on Au1000/Au1500/Au1100, Au1550/Au1200, and Au1300 should verify wake returns, clocks are correct, static bus devices still work, GPIO/pinmux state is preserved, and UART/USB/Ethernet recover through their own PM paths. Instrumentation can compare saved/restored register snapshots. Early Au1000 write-only PLL handling should be tested separately if hardware is available.
