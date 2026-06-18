# Group Research: group_1472_plan9_sources_os_plan9_plan9_sys_src_9_mtx_main_c_sources_os_plan9__77d1d0499171

Scope: `Docs/research_subset_a.md`, specifically `sources/os/plan9/plan9`. I read all 28 listed source files completely. This group covers two Plan 9 kernel platform ports: the PowerPC MTX board support files and a Cortex-A8/OMAP3530 board support set with clocks, console, USB, Ethernet, UART, DMA, floating-point emulation, and low-level ARM helpers.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/main.c

Defines the MTX PowerPC kernel bootstrap, first user process setup, machine-dependent process hooks, and minimal configuration parsing.

Key points:
- `main()` clears BSS, initializes one CPU, early I/O, i8250 serial console, formatting, configuration, Raven bridge, traps, MMU, interrupts, clock, keyboard, process/page/swap systems, FP save area, first user process, then enters the scheduler.
- `machinit()` initializes `Mach`, sets CPU type from PVR, installs a temporary delay loop constant, enables HID0 caches, and marks CPU 0 active.
- `cpuidprint()` identifies only PowerPC 604e explicitly.
- Provides a static fallback `plan9ini[]` with `console=0` and `ether0=type=2114x`; `getconf()` reads from it.
- `init0()` enters low IPL, builds initial `/` and `.` channels, initializes devices, sets kernel environment variables (`terminal`, `cputype`, `service`), starts `alarm` and `mmusweep`, then jumps to user mode.
- `userinit()` creates the first proc, kernel/user stacks, one text page containing `initcode`, and readies it.
- `confinit()` sizes process, image, swap, page, and malloc pools from ROM-provided `memsize`, with different policy for terminals vs CPU servers.
- Provides MTX versions of `reboot()`, `exit()`, `procsetup()`, `procsave()`, `isaconfig()`, `cistrcmp()`, and `cistrncmp()`.

Dependencies and interactions:
- Uses `raveninit()`, `trapinit()`, `mmuinit()`, `hwintrinit()`, `clockinit()`, and Plan 9 port allocators/device setup.
- `isaconfig()` feeds ISA-like configuration to Ethernet/UART style drivers from `getconf()`.
- `mmusweep` is spawned here and implemented in `mmu.c`.
- `initcode` and `touser()` provide the initial user transition.

Research relevance:
- This is the MTX port’s top-level boot and configuration file, linking machine setup to the portable Plan 9 kernel.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/mem.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/mem.h

Defines MTX PowerPC memory layout, page/MMU constants, processor registers, trap codes, and device address windows.

Key points:
- Sets fundamental sizes: 4KB pages, 32-bit words, 8-byte `vlong`, 16-byte cache line, 4KB kernel stack, `MAXMACH` 1.
- Defines PowerPC SPR numbers for DSISR, DAR, DEC, SDR1, SRR0/1, SPRG registers, timebase, PVR, BATs, HID0/1, and 604e performance registers.
- Uses `BIT(i)` for PowerPC’s high-bit-first register numbering.
- Defines MSR bits including external interrupts, privilege, FP, machine check, instruction/data MMU, recoverable interrupt, and endian flags.
- Enumerates PowerPC exception vector codes such as reset, machine check, DSI/ISI, external interrupt, alignment, program, FP unavailable, decrementer, syscall, trace, and 604e-specific vectors.
- Reserves registers `R30` for `m` and `R29` for `up`.
- Defines hash-PTE formats (`PTE0`, WIMG/PP bits in `PTE1_*`) and Plan 9 fault-layer aliases (`PTEWRITE`, `PTERONLY`, `PTEUNCACHED`).
- Defines user/kernel virtual layout: `KZERO=0x80000000`, `KTZERO`, `UTZERO`, `USTKTOP`, user stack size, and register save size.
- Defines MTX physical/device windows: PCI memory ranges, I/O space, Falcon, Raven, flash ranges, and `isphys()`.

Dependencies and interactions:
- Included by C and assembly files.
- `mmu.c` uses PTE and VSID-related constants.
- `raven.c` and `pci.c` rely on PCI/I/O window definitions.
- Trap and syscall code uses exception and MSR constants.

Research relevance:
- This header is the architectural contract for the MTX port’s address map, trap vectors, and MMU encoding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/mmu.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/mmu.c

Implements the MTX PowerPC hash-page-table MMU support and MMU PID aging.

Key points:
- Uses one hash page table per processor; process address spaces are distinguished by VSID fields in segment registers.
- Sizes the page table heuristically from ROM-provided `memsize`, allocates it aligned with `xspanalloc()`, writes SDR1, and initializes MMU PID/color state.
- Defines 21-bit MMU PIDs with two high color bits. PID 0 is reserved.
- `mmusweep()` is a background kernel process that waits for trigger color, clears stale proc `mmupid`s of the sweep color, invalidates matching hash PTEs, flushes all TLBs, and advances sweep/trigger colors.
- `newmmupid()` allocates the next PID, wakes the sweep process near color boundaries, and returns 0 if no safe PID is available.
- `flushmmu()` marks the current proc for a new TLB context and calls `mmuswitch()`.
- `mmuswitch()` sets segment registers for user procs using `VSID(pid, segment)` or clears them for kernel procs.
- `putmmu()` hashes `(vsid, va)` into a PTE group, replaces or inserts a PTE, flushes the specific TLB entry, and handles per-page cache-control states (`PG_NOFLUSH`, `PG_TXTFLUSH`).
- `cankaddr()` reports how much physical memory can be addressed through `KADDR()`.

Dependencies and interactions:
- Spawned by `main.c` as `mmusweep`.
- Called from fault handling to install translations.
- Uses page cache flush states established by text loading and segment code.
- Depends on assembly helpers for segment register, SDR1, TLB, D/I-cache operations.

Research relevance:
- Core virtual-memory implementation for the MTX PowerPC port, including its PID recycling scheme.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/pci.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/pci.c

Implements generic PCI configuration, scanning, bridge discovery, BAR sizing, address assignment, and utility APIs for the MTX port.

Key points:
- Supports PCI configuration mechanisms 1 and 2 via x86-style config I/O ports (`0xCF8`, `0xCFC`, `0xCFA`) exposed through the MTX I/O path.
- Installs `%T` formatting for Plan 9 TBDF bus identifiers.
- `pcibarsize()` probes BAR size by writing all ones and restoring the original BAR.
- `pcibusmap()` recursively sizes and assigns I/O and memory windows, including PCI-PCI bridge windows, with minimum bridge window sizes and sorted allocation tables.
- `pcilscan()` enumerates devices/functions, fills `Pcidev`, reads class/vendor/device/interrupt/BAR information, detects multifunction devices, and recursively scans PCI-PCI bridges.
- `pcicfginit()` detects config mechanism, applies optional `*pcimaxbno` and `*pcimaxdno`, scans buses, resets CardBus bridges, computes top-level window sizes, then writes assigned mappings.
- Provides config read/write APIs for 8/16/32-bit registers: `pcicfgr*()` and `pcicfgw*()`.
- Provides lookup and control helpers: `pcimatch()`, `pcimatchtbdf()`, `pciipin()`, `pcihinv()`, `pcireset()`, `pcisetbme()`, and `pciclrbme()`.
- Keeps a debug ring in `PCICONS` and prints it during PCI inventory.

Dependencies and interactions:
- `raven.c` uses `pcimatch()` to locate Raven PCI registers and derive MPIC base.
- Ethernet and other PCI device drivers use `pcimatch*()` and config accessors.
- `getconf()` from `main.c` controls scan bounds.
- Uses Plan 9 `Pcidev`/`Pcisiz` structures from platform headers.

Research relevance:
- This is the PCI bus substrate for the MTX kernel, including bridge resource allocation rather than relying on firmware.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/pci.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/raven.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/raven.c

Configures the Motorola Raven PCI host bridge and MPIC interrupt controller for MTX.

Key points:
- Defines the memory-mapped Raven register layout, including device/vendor IDs, mapping windows, watchdogs, and MPIC acknowledge/EIO registers.
- `setmap()` programs Raven address windows for PCI memory, kernel/I/O compatibility mappings, and PCI config/I/O space.
- Uses endian-swapped `mpic32r()`/`mpic32w()` helpers because MPIC registers are accessed with swapped byte order.
- `raveninit()` verifies Raven vendor/device ID (`0x1057:0x4801`), establishes four mapping windows, finds Raven’s PCI config entry, computes MPIC base, masks all 16 interrupt sources, routes them to CPU 0, and enables mixed 8259/Raven interrupt mode.
- `mpicenable()` programs vector priority/route, makes vector 0 level-sensitive for 8259 cascade, and installs EOI handling for nonzero vectors.
- `mpicdisable()`, `mpicintack()`, and `mpiceoi()` implement MPIC control.

Dependencies and interactions:
- Called early from `main()` before interrupt initialization.
- `trap.c` uses `mpicenable()`, `mpicdisable()`, `mpicintack()`, and `mpiceoi()`.
- Depends on PCI enumeration and MTX memory constants from `mem.h`.

Research relevance:
- Board-specific bridge and interrupt controller setup for MTX, connecting PCI and the mixed MPIC/8259 interrupt model.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/raven.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/trap.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/trap.c

Implements MTX PowerPC trap dispatch, interrupt registration, syscall entry, FP unavailable handling, user notification, and debug register utilities.

Key points:
- `hwintrinit()` initializes the 8259 and enables MPIC vector 0 as the 8259 cascade.
- `intrenable()`/`intrdisable()` allocate and manage `Vctl` chains per vector, routing PCI IRQs through MPIC and non-PCI IRQs through the 8259 offset vector range.
- `trap()` decodes PowerPC exception code from `ureg->cause`, distinguishes user/kernel mode, dispatches external interrupts, decrementer clock interrupts, syscalls, FP unavailable traps, instruction/data faults, and program exceptions.
- FP unavailable traps lazily restore either the initial FP state or the proc’s saved FP state and set `MSR_FP`.
- `faultpower()` calls portable `fault()` and posts debug notes or panics depending on user/kernel context.
- `sethvec()` writes low exception-vector stubs that branch to handler code, using either direct branch or LR sequence if target is too far; `trapinit()` installs `trapvec` for vectors up to `0x2000`.
- `intr()` acknowledges MPIC, cascades vector 0 through `i8259intack()`, calls all registered handlers, issues EOI, and preempts if a proc is active.
- Provides stack/register diagnostics: `callwithureg()`, `dumpstack()`, `dumpregs()`, `setkernur()`, and `dbgpc()`.
- Defines process entry helpers: `kprocchild()`, `execregs()`, `forkchild()`, `userpc()`, and `setregisters()`.
- `syscall()` reads syscall number from `r3`, copies `Sargs` from user stack, calls `systab`, handles Plan 9 error stacks, returns in `r3`, and performs note delivery.
- `notify()` and `noted()` implement Plan 9 user note delivery/restoration on PowerPC user stacks.

Dependencies and interactions:
- Uses `raven.c` MPIC hooks, i8259 hooks, `clockintr()`, `fault()`, `systab`, `sysctab`, and process/note machinery.
- Assumes PowerPC `Ureg` layout and `mem.h` exception/MSR constants.
- Trap vectors call assembly `trapvec`.

Research relevance:
- Central exception, interrupt, syscall, and user-notification path for the MTX kernel.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/uarti8250.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/mtx/uarti8250.c

Implements the MTX 8250/16550-compatible serial driver and early console binding.

Key points:
- Defines COM1/COM2 base ports, IRQs, UART register offsets, interrupt bits, FIFO bits, line-control bits, modem-control bits, line-status bits, and modem-status bits.
- Provides two `Ctlr` instances and two `Uart` instances chained as COM1 and COM2, using `PhysUart i8250physuart`.
- Maintains sticky register shadows for `Ier`, `Lcr`, and `Mcr` so writes can preserve persistent bits.
- Implements status reporting with baud, hangup flags, DSR/DCD/CTS/RI state, FIFO state, framing and overrun counters.
- Controls FIFO enable/reset, DTR, RTS, modem interrupts, parity, stop bits, word length, baud divisor, break signaling, and TX kicking.
- `i8250interrupt()` handles modem-status, THR-empty, receive-data, timeout, and line-error cases, feeding receive bytes to `uartrecv()` and output via `uartkick()`.
- `i8250enable()` optionally registers interrupts, enables RX/TX interrupts, and asserts DTR/RTS; `i8250disable()` shuts down line controls, interrupts, and FIFOs.
- Provides polled `getc`/`putc` for early console.
- `i8250console()` reads `console` from `getconf()`, configures `b9600 l8 pn s1`, enables without interrupts, and sets `consuart`.

Dependencies and interactions:
- Implements the physical UART backend consumed by generic UART/console layers.
- Uses `intrenable()` from `trap.c`.
- Boot code calls `i8250console()` before normal device setup.

Research relevance:
- Serial console and UART hardware support for MTX, including early polling mode and later interrupt-driven operation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/mtx/uarti8250.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/arch.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/arch.c

Provides OMAP ARM architecture glue for process state, user exit accounting, atomic operations, and kernel process startup.

Key points:
- `setkernur()` fills enough `Ureg` state to show a sleeping proc’s kernel PC/SP and scheduler link register.
- `validalign()` enforces power-of-two address alignment, relaxing 64-bit alignment to 32-bit on this 32-bit ARM environment.
- `kexit()` updates the user-visible `Tos` with kernel cycles, process cycles, cycle frequency, and PID, then writes back/invalidates cache for immediate user visibility.
- `userpc()` returns the last saved user PC from `up->dbgreg`.
- `setregisters()` is a stub that disallows devproc register modification by doing nothing.
- `kprocchild()` initializes kernel process PC/SP and argument state via `linkproc()`.
- `procsetup()`, `procsave()`, and `procrestore()` delegate floating-point state handling and account process cycles.
- `userureg()` identifies user-mode trap frames by PSR mode.
- Provides interrupt-disabled implementations of `_xdec`, `_xinc`, `ainc`, `adec`, and `cas32()`.

Dependencies and interactions:
- Calls FP helpers from `fpiarm.c`/other FP support.
- Uses ARM PSR mode constants from `arm.h`.
- Used by portable proc, devproc, syscall, and scheduler code.

Research relevance:
- Machine-dependent ARM process/accounting glue for the OMAP Plan 9 kernel.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/arch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/archomap.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/archomap.c

Implements OMAP3530/Beagle/IGEP board-specific reset, clocks, GPIO, USB, pad muxing, CPU/cache reporting, Ethernet/flash hooks, and reboot support.

Key points:
- Defines hardware register layouts for USB OTG/TLL, L3 protection regions/agents, clock-management modules, power/reset management, GPIO, SCM pad config, and control ID registers.
- `archconfinit()` sets default CPU speed to 500MHz and allows `*cpumhz` override between 100MHz and 3GHz.
- Provides L3 firewall reporting helpers (`dumpl3pr()`) and cache reporting (`cacheinfo()`, `prcachecfg()`).
- `archether()` declares controller 0 as an SMSC9221-compatible 100Mbps Ethernet device on IRQ 34.
- `configmpu()` adjusts DPLL1/MPU clock multiplier to desired CPU frequency, with max based on SKU.
- `configpll()`, `configper()`, `configwkup()`, `configusb()`, and `configcore()` turn on functional/interface clocks needed for timers, GPIO, USB host/TLL, PLL outputs, and peripherals.
- `configgpio()` configures GPIO6 pin 176 as the SMSC9221 interrupt source and clears outstanding GPIO IRQs; `gpioirqclr()` acknowledges it.
- `configscreengpio()` and `screenclockson()` enable GPIO/DSS clocks and pins for display output.
- `setpadmodes()` programs USB, UART3, Ethernet IRQ, and GPMC/flash pad muxing, largely matching u-boot magic values.
- `fpon()` enables CP10/CP11 access, turns on VFP, reports VFP implementation, and configures FPSCR.
- `resetusb()` resets OTG, UHH, and TLL blocks, chooses ULPI PHY mode, and handles absent TLL.
- `archreset()` is guarded by `beenhere`, initializes temporary CPU timing, clears errata-related boot config memory, configures pads/clocks/GPIO, refreshes config, resets USB, and enables FP.
- `archreboot()` requests global software reset through PRM and loops if reset fails.
- Provides no-op `kbdinit()`, `lastresortprint()`, `cpuidprint()`, `chkmissing()`, `archflashwp()`, and `archflashreset()` for OneNAND on IGEPv2.

Dependencies and interactions:
- Called during early platform boot by `main.c` in the OMAP tree.
- Clock code in `clock.c` assumes timer clock choices made here.
- `ether9221.c` depends on GPIO and pad setup.
- USB host drivers depend on clock/reset setup.
- Display code depends on screen GPIO/DSS clock functions.

Research relevance:
- Primary board-support file for OMAP3530, connecting SoC clocks, muxes, buses, USB, Ethernet, display, flash, and reset behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/archomap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/arm.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/arm.h

Defines Cortex-A8/ARMv7 PSR, coprocessor, CP15, cache/TLB, and MMU page-table constants for C and assembly.

Key points:
- Defines ARM processor modes and interrupt-disable/status bits in CPSR/SPSR.
- Names coprocessors: VFP single/double (`CpFP`, `CpDFP`) and system control (`CpSC`/CP15).
- Defines CP15 primary registers for ID, control, TTB, DAC, fault status/address, cache ops, TLB ops, lockdown, vector base, PID, and Cortex-specific cache/TLB controls.
- Defines opcode fields for TTB0/TTB1/TTB control, DFSR/IFSR, cache-size selection, ID registers, and vector-base registers.
- Defines main control register bits such as MMU enable, alignment fault, D-cache/I-cache, branch prediction, high vectors, access flag, exception endian, and ARMv7 must-be-one/zero masks.
- Defines auxiliary control bits for cache/TLB maintenance behavior, L2 enable, speculative access, NEON/L1 behavior, and issue restrictions.
- Defines CP15 cache maintenance selectors for invalidate, writeback, writeback+invalidate, VA-to-PA, set/way, branch target cache, and barriers.
- Defines TLB invalidate selectors and lockdown selectors.
- Defines L1/L2 page-table encodings: fault, coarse, section, fine, large/small page, cached/buffered, domain, access permissions, and `HVECTORS`.

Dependencies and interactions:
- Included by OMAP C and assembly files including `arm.s`, `cache.v7.s`, `clock.c`, `coproc.c`, and MMU/trap code.
- Supplies bit definitions for dynamic CP15 instruction generation in `coproc.c`.

Research relevance:
- Core ARMv7 architectural definition file for the OMAP port.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/arm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/arm.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/arm.s

Provides shared OMAP ARM assembly macros for address translation, barriers, cache/TLB maintenance, UART debug output, and PTE filling.

Key points:
- Defines `KADDR()`/`PADDR()` assembly forms based on `KZERO`, `PHYSDRAM`, and `KSEGM`.
- Defines `L1X()` for L1 translation-table index calculation.
- Defines `MACHADDR`, section PTE attribute constants for DRAM and I/O, and low-DRAM double-map size.
- Provides `DELAY` busy-loop and `PUTC` macro for direct console register output.
- Defines ARMv7 instruction encodings unavailable as assembler mnemonics: `SMC`, `WFI`, `DMB`, `DSB`, `ISB`, `NOOP`, `CLZ`, `CPSIE`, `CPSID`, `VMRS`, and `VMSR`.
- Provides branch-target cache flush macros (`FLBTC`, `FLBTSE`) using CP15.
- Defines `BARRIERS` as branch-target-cache flush plus DSB/ISB.
- Provides `FILLPTE()` and `ZEROPTE()` macros for boot-time page table population.

Dependencies and interactions:
- Shared by low-level OMAP assembly such as `l.s` and reboot code.
- Uses constants from `mem.h` and `arm.h`.
- Supports early boot before full C runtime and MMU setup are stable.

Research relevance:
- Assembly utility layer for OMAP boot/MMU/cache setup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/arm.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/cache.v7.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/cache.v7.s

Implements ARMv7/Cortex-A8 cache invalidation, writeback, and whole-cache set/way operations.

Key points:
- `cacheiinv()` invalidates the entire instruction cache and issues ISB.
- Provides small set/way primitive functions: `cachedwb_sw()`, `cachedwbinv_sw()`, and `cachedinv_sw()`.
- `setcachelvl()` and `getwayssets()` access Cortex cache-size selection and cache-size ID registers.
- `cachedwb()`, `cachedwbinv()`, and `cachedinv()` apply whole L1 data-cache operations.
- `cacheuwbinv()` atomically writebacks/invalidates data cache and invalidates I-cache with interrupts disabled.
- `l2cacheuwb()`, `l2cacheuwbinv()`, and `l2cacheuinv()` operate on the L2 cache.
- `wholecache()` computes sets/ways from CP15 cache-size registers, chooses shifts for L1 vs L2, disables interrupts, iterates all set/way combinations, calls the selected primitive, restores CPSR, and drains buffers.
- Contains a fallback `buggery` path if code runs in a zero PC segment, printing `?` to console.

Dependencies and interactions:
- Used by C helpers declared in `fns.h`, by boot/reboot code, and by MMU/cache coherency code.
- Assumes Cortex-A8 shift constants for L1 and L2 cache geometry.

Research relevance:
- Low-level cache maintenance implementation required for MMU, DMA, code patching, and reboot reliability.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/cache.v7.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/clock.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/clock.c

Implements OMAP3530 timer, fast tick, delay, and watchdog support.

Key points:
- Uses 32.768kHz timer clocks; GPTIMER1 is the free-running base timer and GPTIMER2 is the periodic interrupt timer.
- Defines OMAP timer/watchdog register layout and reset/start/interrupt bits.
- `clockshutdown()` resets/disables watchdog timers and both used general-purpose timers.
- Watchdog helpers perform OMAP magic start/stop sequences and register a periodic assurance callback.
- `clockintr()` handles timer interrupts, avoids nested timer processing, calls `timerintr()`, and acknowledges overflow.
- `clockinit()` shuts down timers, enables CP15 cycle counter access, initializes `m->fastclock`, starts free-running timer, enables interrupting timer on IRQ 38, verifies interrupts arrive, estimates MIPS loops, sets `delayloop`, and desynchronizes CPUs.
- `timerset()` programs the next timer interrupt within min/max bounds derived from HZ.
- `fastticks()` maintains a 64-bit fast clock from the 32-bit CP15 cycle counter, handling wraparound under a lock.
- `perfticks()`, `lcycles()`, `µs()`, `microdelay()`, and `delay()` expose timing primitives.

Dependencies and interactions:
- Assumes clock-source selections and timer clocks were enabled in `archomap.c`.
- Uses CP15 helpers from `coproc.c`.
- Calls Plan 9 timer, watchdog, and clock-link infrastructure.
- `devcons.c` reads time through `cycles()`/`fastticks()` paths.

Research relevance:
- OMAP platform’s timebase, scheduler tick, watchdog, and delay implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/coproc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/coproc.c

Provides runtime-generated ARM coprocessor and VFP register access helpers.

Key points:
- Dynamically builds small instruction sequences on the stack for `MCR`, `MRC`, `VMRS`, and `VMSR`, followed by a return instruction.
- `MAP2PCSPACE()` maps generated instruction memory into the caller PC’s segment so it can execute correctly under current mappings.
- Flushes written instruction sequences with `cachedwbse()` and invalidates I-cache before execution.
- `cpwr()` writes arbitrary coprocessor register fields; `cpwrsc()` specializes it to CP15/system control.
- `cprd()` reads arbitrary coprocessor register fields; `cprdsc()` specializes it to CP15.
- `fprd()` and `fpwr()` read/write VFP system registers.

Dependencies and interactions:
- Used by `archomap.c`, `clock.c`, cache/MMU code, and FP setup.
- Requires cache maintenance and coherence helpers from assembly.

Research relevance:
- A compact dynamic-instruction mechanism that avoids hand-writing every CP15/VFP accessor.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/coproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/dat.h

Defines OMAP platform data types, kernel machine/proc MMU state, configuration structures, locks, FP save area, cache metadata, and DMA modes.

Key points:
- Defines time constants `HZ`, `MS2HZ`, `TK2SEC`, `Mhz`, and cycle-based `MS2TMR`/`US2TMR`.
- Documents that UART0/1 are ignored and OMAP UART3 is exposed as console 0.
- Declares platform typedefs for `Conf`, `Mach`, `Proc`, `Uart`, `Ureg`, `PTE`, `Tval`, `Memcache`, and more.
- Defines `Lock` with key, saved status register, PC, proc, mach, and ilock flag.
- Defines software-emulated `FPsave` with status/control and 8 internal FP register slots.
- Defines `Confmem`/`Conf` memory and kernel sizing fields.
- Defines `MMMU` and `PMMU` state: L1 table pointer/range, MMU PID, proc L2 page and L2 cache.
- Defines full `Mach` with scheduling, alarm, MMU, timing, interrupt/syscall/fault stats, performance, CPU frequency, exception save areas, and stack.
- Provides fake `kmap()`/`kunmap()` macros mapping pages through `kseg0`.
- Defines global active CPU state, `m` in R10, `up` in R9, `kseg0`, `machaddr`, `memsize`, and `normalprint`.
- Defines `ISAConf`, device-port/device-conf structures, `Memcache`, and DMA addressing modes (`Const`, `Postincr`, `Index`, `Index2`).

Dependencies and interactions:
- Included by most OMAP kernel files.
- Extends portable `portdat.h`.
- `fns.h`, MMU, clock, trap, UART, Ethernet, USB, and DMA code rely on these types.

Research relevance:
- OMAP port’s central machine data model and type contract.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/devarch.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/devarch.c

Implements the OMAP `#P/arch` device and CPU/timebase arch files.

Key points:
- Maintains a small dynamic `archdir` table with per-file read/write function arrays.
- `addarchfile()` adds permanent files under `#P`, rejects duplicates, and assigns qid paths.
- Implements standard Plan 9 device methods for attach, walk, stat, open, close, read, and write.
- `archread()` dispatches per-file reads through the registered function pointer; `archwrite()` dispatches writes similarly.
- `cputype2name()` returns `Cortex-A8`.
- Adds `cputype` and `timebase` in `archinit()`.
- `cputyperead()` reports ARM CPU type and current MHz.
- `tbread()` reports `cycles()` as a hex timebase value.
- `nsread()` exists but is not registered.

Dependencies and interactions:
- `cpuidprint()` in `archomap.c` calls `cputype2name()`.
- Portable dev interfaces use `archdevtab`.
- Other arch code can publish files with `addarchfile()`.

Research relevance:
- Minimal machine introspection filesystem for the OMAP kernel.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/devarch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/devcons.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/devcons.c

Implements the OMAP console device `#c`, kernel printing, console input processing, kmesg/kprint, time files, random, reboot, and system status interfaces.

Key points:
- Defines global console queues: raw keyboard input, processed line input, serial output, and `/dev/kprint` output.
- `printinit()` creates the processed input queue; `consactive()`/`prflush()` observe pending serial output.
- Keeps a rolling `kmesg` buffer for boot/runtime messages.
- `putstrn0()` routes output to `/dev/kprint`, screen, UART, and serial queue, converting newline to CRLF for serial unless raw.
- `print()`, `iprint()`, `panic()`, `sysfatal()`, `_assert()`, and `pprint()` provide kernel/user-visible printing and panic behavior.
- Input path stages interrupt-time characters in `kbd.istage`, flushes them on a clock callback, handles raw/cooked mode, echo, ^U/^D/newline, and ^T debug commands.
- Exposes many files under `#c`: `bintime`, `cons`, `consctl`, `cputime`, `drivers`, `hostdomain`, `hostowner`, `kmesg`, `kprint`, `null`, `osversion`, `pgrpid`, `pid`, `ppid`, `random`, `reboot`, `swap`, `sysname`, `sysstat`, `time`, `user`, and `zero`.
- `consread()` implements each file, including process IDs, CPU time, sysstat, swap stats, driver list, zero/random, and time.
- `conswrite()` handles console output, raw/ctlp toggles, time setting, owner/domain/user writes, reboot commands, sysstat reset, swap setup, and sysname setting.
- Implements endian helpers and binary/text time read/write, including `todset()`, `todsetfreq()`, and `fastticks()` frequency setup.
- `nrand()`/`rand()` provide a simple random fallback seeded from `randomread()`.

Dependencies and interactions:
- Uses UART queues from `devuart.c`, screen output hook, TOD/random subsystems, reboot paths, pager/swap, and process tables.
- Clock callback installed in `consinit()` drains staged keyboard input.
- `panic()` ultimately calls `exit()`.

Research relevance:
- Full console and system-control filesystem for the OMAP kernel, central to boot diagnostics and runtime administration.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/devcons.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/devdss.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/devdss.c

Implements the OMAP DSS screen control device `#v/vgactl`.

Key points:
- Provides a two-entry device tree: root directory and `vgactl`.
- `screenopen()` serializes `vgactl` access with `dsslck` and marks `oscreen.open`.
- `screenclose()` clears `oscreen.open` and unlocks.
- `settingswrite()` parses display mode strings for `800x600`, `1024x768`, and `1280x1024`, then updates `OScreen.settings`.
- `getchans()` selects `RGB16` or `RGB24`, defaulting to `RGB16`; note comments that RGB24 cannot work yet with short pixels.
- `screenread()` reports size/depth/frequency and framebuffer address/size.
- `screenwrite()` rejects nonzero offsets, applies new settings, and calls `screeninit()`.

Dependencies and interactions:
- Uses globals from `screen.c`/`screen.h`: `oscreen`, `settings`, `framebuf`, and `screeninit()`.
- DSS clocks and GPIO are configured in `archomap.c`.

Research relevance:
- Small Plan 9 device interface connecting user-visible display configuration to OMAP screen setup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/devdss.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/devether.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/devether.c

Implements the generic Plan 9 Ethernet `#l` device layer for OMAP hardware drivers.

Key points:
- Maintains up to `MaxEther` registered `Ether` controllers in `etherxx[]`.
- Standard device methods delegate attach/walk/stat/open/close/read/write/bwrite/wstat to `netif` helpers and hardware callbacks.
- `etheriq()` receives packets, filters multicast/broadcast/promiscuous traffic, checks destination/source, handles bridge/headersonly modes, fans packets out to interested `Netfile`s, and can pass the original block without copy.
- `etheroq()` handles transmit accounting, loopback/broadcast/promiscuous local delivery, and queues non-loopback packets to the hardware output queue.
- `etherwrite()` handles netif control writes, `nonblocking` queue control, hardware-specific `ctl`, and packet writes with MTU checks and source MAC insertion.
- `addethercard()` registers hardware reset/probe functions by type.
- `parseether()` parses colon-separated MAC addresses.
- `etherreset()` asks `archether()` for platform devices, applies config/options, matches registered card drivers, installs interrupts, reports device info, initializes netif queues, MAC/broadcast addresses, and controller table.
- `ethershutdown()` calls hardware shutdown callbacks.
- Provides CRC helper `ethercrc()` and debug helpers `dumpoq()`/`dumpnetif()`.

Dependencies and interactions:
- Hardware drivers such as `ether9221.c` register with `addethercard()`.
- `archether()` in `archomap.c` declares available platform Ethernet hardware.
- Uses Plan 9 `netif` framework and `intrenable()`.

Research relevance:
- Hardware-independent Ethernet filesystem and packet multiplexing layer for OMAP network drivers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/devether.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/devuart.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/devuart.c

Implements the generic Plan 9 UART `#t` device layer over physical UART backends.

Key points:
- Discovers `PhysUart` providers through `physuart[]`, builds a linked UART list, allocates `eiaN`, `eiaNctl`, and `eiaNstatus` directory entries.
- `uartenable()` opens/reopens input/output queues, initializes staging buffers, default serial settings, enables hardware, and links the UART into the enabled list.
- `uartdisable()` calls hardware disable and removes from enabled list.
- Supports special mouse UART use through `uartmouse()` and `uartsetmouseputc()`.
- Device methods implement attach/walk/stat/open/close/read/write/wstat/power for `#t`.
- `uartctl()` parses serial control commands: baud, bits, stop, parity, break, DTR/RTS, FIFO, modem control, hangup behavior, queue sizing, nonblocking, timer interval, and XON/XOFF.
- `uartwrite()` writes data to output queues or applies control commands.
- `uartclock()` periodically drains interrupt input staging, handles hangups, applies CTS/XON backoff, and kicks output.
- `uartstageoutput()`, `uartkick()`, `uartrecv()`, and `uartstageinput()` amortize queue operations and manage software/hardware flow control.
- Provides polling console helpers `uartgetc()`, `uartputc()`, and `uartputs()` using `consuart`, with fallback to `lprint`.

Dependencies and interactions:
- Physical UART implementations supply `PhysUart` methods.
- `devcons.c` uses `kbdq`, `serialoq`, and `consuart` set here.
- `clock.c` callback infrastructure drives periodic staging.

Research relevance:
- Portable UART device layer used by the OMAP serial console and serial ports.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/devuart.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/devusb.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/devusb.c

Implements the generic USB `#u` device filesystem and endpoint framework for host-controller drivers.

Key points:
- Provides root `#u`, `#u/usb/ctl`, and per-endpoint directories `epN.M` with `data` and `ctl` files.
- Expects user-level `usbd` to enumerate devices, allocate endpoints, configure devices, and start drivers.
- Registers HCI backend types through `addhcitype()` and probes them in `usbreset()`.
- `usbinit()` initializes each HCI and creates a permanent root-hub control endpoint for each controller.
- Maintains global endpoint table `eps[]`, endpoint refs, maximum used endpoint index, and USB device address generator.
- `newdev()` creates endpoint 0 and a `Udev`; `newdevep()` adds nonzero endpoints under a device.
- `usbgen()` dynamically lists the USB filesystem, including named endpoints exposed directly under `#u`.
- `usbopen()` enforces exclusive data endpoint use, direction permissions, endpoint type configuration, HCI `epopen()`, and transfer-load calculation.
- `usbread()`/`usbwrite()` delegate data transfers to HCI callbacks, with fake root-hub control handling for port enable/reset/status.
- `ctlread()` reports all endpoints or one endpoint; after `newdev`, it returns the new endpoint name via `c->aux`.
- `epctl()` implements endpoint commands: `new`, `newdev`, `hub`, `speed`, `maxpkt`, `ntds`, `pollival`, `samplesz`, `hz`, `info`, `detach`, `address`, `debug`, `clrhalt`, `name`, `timeout`, and `reset`.
- `usbctl()` handles global debug and dump commands.
- `usbshutdown()` calls each HCI shutdown hook.

Dependencies and interactions:
- HCI drivers implement `Hci` callbacks for reset/init/interrupt/endpoint I/O/port operations.
- USB clocks and resets are configured by `archomap.c`.
- Uses Plan 9 device, queue, and ref-counting patterns from the port kernel.

Research relevance:
- Central USB endpoint abstraction and filesystem API used by OMAP USB host-controller support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/devusb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/dma.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/dma.c

Implements basic OMAP3530 system DMA controller initialization, interrupt handling, and memory copy start support.

Key points:
- Defines register layout for the system DMA controller, including IRQ status/enable, reset/status/config, capabilities, global control, and 32 channel register blocks.
- Uses 4 DMA IRQ/channel slots (`Nirq=4`) starting at IRQ 12.
- `isdmadone()` checks a channel’s block-complete bit.
- `dmaintr()` marks the associated transfer done, wakes its rendezvous, verifies/clears block interrupt status, disables its IRQ bit, and releases transfer state.
- `dmainit()` verifies the controller, soft-resets it, clears all channels and interrupt registers, sets global burst size, and installs IRQ handlers for DMA0-DMA3.
- `dmatest()` runs a test DMA copy to scratch DRAM, waits for completion, invalidates cache, and verifies data and overrun behavior.
- `dmastart()` allocates a free DMA IRQ/channel, records completion rendezvous and flag, programs source/destination physical addresses, address modes, element/frame counts, block interrupt, enables the IRQ, and starts the channel.
- Transfers are rounded up to word size and use word-sized elements.

Dependencies and interactions:
- Used by hardware drivers needing DMA, though `ether9221.c` currently avoids DMA.
- Requires cache maintenance on callers for coherent memory.
- Uses `intrenable()` and OMAP physical DMA address constants.

Research relevance:
- Small but important DMA substrate for OMAP peripherals and future block/data movement paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/dma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/ether9221.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/ether9221.c

Implements the SMSC LAN9221 Ethernet driver for IGEPv2-style OMAP boards.

Key points:
- Targets SMSC 9221 at `0x2c000000`, chip select 5, IRQ 34 via GPIO pin 176/module 6.
- Defines full register layout for FIFO ports, status, IRQ, FIFO info, power, MAC CSR, EEPROM, and related control registers.
- Uses FIFO-based RX/TX, with comments noting it is slow and DMA was not beneficial here.
- `macrd()`/`macwr()` perform indirect MAC CSR access through `maccsrcmd`/`maccsrdata`.
- `smcifstat()` reports driver counters and stored EEPROM words.
- `smcpromiscuous()` toggles MAC promiscuous mode; multicast callback accepts all multicast.
- `smctxstart()` checks TX FIFO space, ensures word alignment, writes TX command words and packet data into TX FIFO, and enables TX interrupts.
- `smctransmit()` drains the generic Ethernet output queue into the chip FIFO, putting back a block if FIFO is full.
- `smcattach()` lazily marks the controller initialized, optionally starts kprocs if enabled, installs polling fallback if no IRQ, and announces no DMA.
- `smcreceive()` drains RX status/data FIFOs into Plan 9 blocks, validates lengths/errors, and passes packets to `etheriq()`.
- `smcinterrupt()` clears the GPIO IRQ, reads interrupt status, handles RX/TX interrupt causes, drains TX status FIFO, and either wakes kprocs or directly receives/transmits.
- `smcdetach()` disables interrupts, clears pending status, flushes RX/TX FIFOs, and disables IRQ output.
- `smcreset()` powers up, verifies chip ID and byte test register, writes MAC address registers, enables TX/RX, configures FIFO/IRQ/MAC control, and enables RX/TX interrupts.
- `smcpci()` probes the memory-mapped device and builds a controller list; despite the name, this is platform memory-mapped discovery.
- `smcpnp()` binds a free controller to generic `Ether`, sets IRQ/port/speed, and installs attach/transmit/interrupt/ifstat/promiscuous/multicast/shutdown callbacks.
- `ether9221link()` registers card type `"9221"` with the generic Ethernet layer.

Dependencies and interactions:
- Registered through `addethercard()` in `devether.c`.
- Platform declaration comes from `archether()` in `archomap.c`.
- GPIO interrupt acknowledge is provided by `gpioirqclr()` in `archomap.c`.
- Uses generic `etheriq()` and output queues from `devether.c`.

Research relevance:
- Board-specific Ethernet hardware driver for the OMAP port, bridging SMSC9221 FIFOs to Plan 9 netif.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/ether9221.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/etherif.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/etherif.h

Defines the generic Ethernet controller structure and helper declarations for OMAP Ethernet drivers.

Key points:
- Sets `MaxEther=4` and `Ntypes=8`.
- Defines `Ether` as an `RWlock`, embedded `ISAConf`, controller number, min/max MTU, embedded `Netif`, and hardware callback pointers.
- Hardware callbacks include attach, detach, transmit, interrupt, ifstat, control, power, and shutdown.
- Stores hardware-private `ctlr`, MAC address `ea`, mapped address, IRQ, and output queue.
- Declares shared helper functions: `etheriq()`, `addethercard()`, `ethercrc()`, and `parseether()`.
- Defines ring helper macros `NEXT()` and `PREV()`.

Dependencies and interactions:
- Included by `devether.c`, `ether9221.c`, and platform arch code.
- Extends Plan 9 `netif` structures from `../port/netif.h`.

Research relevance:
- Small contract header between generic Ethernet device code and hardware Ethernet drivers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/etherif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/fns.h

Declares OMAP machine-dependent functions, macros, and compatibility mappings used across the kernel.

Key points:
- Includes portable `portfns.h` and stubs `checkmmu()`/`countpagerefs()`.
- Declares cache, clock, CPU, coprocessor, DMA, MMU, UART, screen, watchdog, and trap/interrupt helpers.
- Maps Plan 9 `cycles(ip)` to `lcycles()`.
- Defines `intrenable()`/`intrdisable()` macros over OMAP `irqenable()`/`irqdisable()`, ignoring bus/TBDF.
- Declares FP emulation and FP process/syscall hooks.
- Declares uncached allocator and MMU map/unmap helpers.
- Provides Plan 9 machine macros: `CAS*`, `TAS`, `PTR2UINT`, `UINT2PTR`, `waserror()`, `KADDR()`, `PADDR()`, `wave()`, and `MASK()`.
- Declares global boot functions called from main: `archconfinit()`, `clockinit()`, `i8250console()`, `links()`, `mmuinit()`, `touser()`, and `trapinit()`.

Dependencies and interactions:
- Included by almost every OMAP C source file.
- Bridges portable kernel calls to OMAP-specific implementations.
- Coordinates assembly-provided routines and C implementations.

Research relevance:
- Central function declaration and macro adapter header for the OMAP port.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/fpiarm.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/fpiarm.c

Implements ARM floating-point instruction emulation and selected atomic/exclusive instruction emulation.

Key points:
- Emulates the older ARM floating-point instruction set using Plan 9 `fpi` internal double-precision arithmetic; does not fully model ARM-visible FP status/traps.
- Defines register offset mapping from `Ureg` to ARM general registers and PC.
- Maintains FP constants for encoded immediate constants 0, 1, 2, 3, 4, 5, 0.5, and 10.
- Implements binary FP operations add, subtract, reverse subtract, multiply, divide, and reverse divide.
- Implements unary FP operations move, negate, absolute value, and round.
- `fcmp()` sets ARM condition flags from FP comparison, returning unordered as V|C.
- `fpemu()` decodes and emulates LDF/STF, CPRT transfers/comparisons, FP status/control moves, integer/FP conversion, and arithmetic instructions; unsupported/deprecated operations call `unimp()`.
- `condok()` evaluates ARM condition codes against `psr`.
- `casemu()` emulates a compare-and-swap style instruction with interrupt exclusion.
- `ldrex()`, `strex()`, and `clrex()` emulate ARM exclusive load/store state with a simple global validity flag.
- `specialopc[]` recognizes LDREX, STREX, CLREX, and CAS-like opcodes before FP decoding.
- `fpiarm()` initializes per-proc FP emulation state on first use, then loops over consecutive emulatable/special instructions, advancing PC until a non-FP instruction is reached.

Dependencies and interactions:
- Uses `../port/fpi.h` arithmetic/conversion helpers.
- Called by trap/undefined-instruction handling through declarations in `fns.h`.
- Stores state in `up->fpsave`.

Research relevance:
- Compatibility layer for ARM FP instructions and atomic primitives where hardware/compiler support is incomplete.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/fpiarm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/init9.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/init9.s

Provides the tiny assembly entry for Plan 9 user boot initialization.

Key points:
- Equivalent to a C `main(char *argv0) { startboot(argv0, &argv0); }`.
- Written in assembly to set static base (`SB`) without pulling in extra C runtime routines.
- Loads `R12` with `setR12(SB)`.
- Passes `boot(SB)` and a pointer to the frame argument area to `startboot(SB)`.
- Loops forever after `startboot()` returns.

Dependencies and interactions:
- Used as initial user/bootstrap code in the OMAP Plan 9 environment.
- Depends on `startboot` and `boot` symbols from the boot/user setup.

Research relevance:
- Minimal startup shim ensuring the Plan 9 boot process enters `startboot()` with SB correctly established.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/init9.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/io.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/omap/io.h

Defines the OMAP General-Purpose Memory Controller register layout and bit fields for flash/non-DRAM memory.

Key points:
- Describes GPMC as working only with flash memory in this port.
- Defines system config bits for idle control and posted NAND writes.
- Defines chip-select config register indices for signal control and address map config.
- Defines chip-select control bits for muxed address/data, NOR/NAND device type, 8/16-bit device size, and sync read/write.
- Defines chip-select map bits for valid mapping and 16MB/128MB size encodings.
- Defines `Gpmc` register layout: sysconfig/status/IRQ, timeout/error/config/status, eight chip-select blocks, prefetch controls, ECC registers, BCH result registers, and BCH software data.
- Each chip-select block includes seven config registers plus NAND command/address/data registers.

Dependencies and interactions:
- Included by OMAP platform files that need GPMC/flash definitions.
- `archomap.c` configures GPMC-related pad modes and flash reset uses `PHYSNAND`.
- Flash drivers can use this structure for OneNAND/NAND access.

Research relevance:
- Hardware register definition header for OMAP flash memory controller support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/omap/io.h -->