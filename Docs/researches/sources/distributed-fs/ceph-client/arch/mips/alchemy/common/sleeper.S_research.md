# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/sleeper.S

## Purpose
`sleeper.S` contains the low-level MIPS assembly sleep and wake routines for Alchemy SoCs. It saves CPU register context, flushes caches, programs scratch registers for ROM wake return, places SDRAM/DDR into self-refresh or sleep mode, triggers processor sleep, and restores CPU context at the wake trampoline.

## Important APIs, Types, And Functions
Exported leaf routines are `alchemy_sleep_au1000`, `alchemy_sleep_au1550`, `alchemy_sleep_au1300`, and `alchemy_sleep_wakeup`. Macros `SETUP_SLEEP` and `DO_SLEEP` implement common context-save and sleep-trigger logic. The code references `__flush_cache_all` and calls `au1x00_fixup_config_od` on wake. It uses CP0 registers `STATUS`, `CONTEXT`, `PAGEMASK`, and `CONFIG`, stackframe offsets such as `PT_R*`, and fixed KSEG1 system/memory controller addresses.

## Control Flow
Each sleep routine begins with `SETUP_SLEEP`: reserve stackframe space, save selected GPRs and CP0 registers, flush caches, and write the saved stack pointer plus `alchemy_sleep_wakeup` address into system scratch registers. The CPU-specific body then caches the instructions that must execute while memory is being placed into low-power mode and sequences memory-controller commands. Au1000/Au1100/Au1500 issue precharge, auto-refresh, and sleep commands; Au1550/Au1200 issue precharge/self-refresh, wait for status, then disable SDRAM clocks; Au1300 disables DDR ports/ODT, precharges, auto-refreshes, blocks access, enters self-refresh, waits for status, and disables SDRAM clocks. `DO_SLEEP` writes `SYS_SLPPWR` and `SYS_SLEEP` to enter sleep.

On wake, firmware/ROM returns to `alchemy_sleep_wakeup` using scratch registers. The wake path restores CP0 state, calls `au1x00_fixup_config_od`, restores saved GPRs, and returns to the C caller in `power.c`.

## State And Persistence
The assembly routine persists CPU context on the current kernel stack and temporary wake metadata in system scratch registers. It mutates memory-controller state, SDRAM clocking, CP0 registers, and sleep-control registers. Higher-level `power.c` handles broader SoC register save/restore around this low-level transition.

## Dependencies And Integration Points
It depends on MIPS assembly conventions, stackframe layout from `asm/stackframe.h`, register definitions, cache flush symbol availability, Alchemy ROM wake behavior using `sys_scratch0/1`, and memory-controller register layouts for the three CPU families. `power.c` dispatches to these routines from `au_sleep()`.

## Risks
This code is extremely hardware- and timing-sensitive. Any stackframe layout mismatch, missing saved register, wrong fixed address, or incorrect memory-controller command can hang the system with RAM asleep. The code caches instructions before disabling memory access; changes that enlarge or move the critical region must preserve that behavior. `alchemy_sleep_wakeup` assumes the stack pointer saved in scratch registers is intact and that ROM jumps to the saved RA. CP0 restoration and Config[OD] fixup are required for early errata handling.

## Test Signals
Suspend/resume on each CPU-family path is the primary test: Au1000/Au1100/Au1500, Au1550/Au1200, and Au1300. Validation should include repeated sleep cycles, memory integrity checks after wake, IRQ wake sources, cache coherency checks, static bus device access, and clock restoration. Instrumented builds can confirm scratch registers are programmed and wake returns through `alchemy_sleep_wakeup`; hardware debug is often required for failures because bad sequencing may stop all logging.
