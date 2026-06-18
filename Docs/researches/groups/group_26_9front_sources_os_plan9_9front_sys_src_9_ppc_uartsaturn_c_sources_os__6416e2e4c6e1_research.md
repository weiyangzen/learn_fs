# Group Research: group_26_9front_sources_os_plan9_9front_sys_src_9_ppc_uartsaturn_c_sources_os__6416e2e4c6e1

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ppc/uartsaturn.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ppc/uartsaturn.c

Implements a Plan 9 `PhysUart` driver for two memory-mapped Saturn UARTs on PPC. It defines register layout, baud/parity/stop/bits programming, interrupt handling, console selection from `console`, and debug output helpers (`dbgputc`, `dbgputs`, `dbgputx`).

The driver exposes `saturnphysuart` with standard UART callbacks. Receive interrupts drain `rxb` while `Lsr_rxavail` is set; transmit interrupts disable `Ier_txempty` until `uartkick` stages more bytes. FIFO, modem control, RTS, DTR, and break are stubs.

Notable details: UART A/B base addresses are derived from `Saturn`; `subaud` only programs divisor registers when `uart->enabled`; `sukick` loops up to `Txsize` but breaks after writing one byte, effectively single-byte kick despite the size constant.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ppc/uartsaturn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ppc/uartsmc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ppc/uartsmc.c

Implements a PPC 8260 SMC UART driver using CPM-style buffer descriptors. It configures SMC UART mode, allocates RX/TX descriptors and cacheline-aligned buffers, programs baud generators, and exposes `smcphysuart`.

Key paths: `smcinit` performs hardware setup via `smcsetup`, configures descriptors, events, and `smcmr`; `smcenable` enables SMC interrupts; `smcinterrupt` handles break, busy/error, receive buffer, and transmit buffer events. `smckick` writes staged output into the TX buffer descriptor and flushes cache before marking it `BDReady`.

Dependencies include PPC CPM structures from `imm.h` and `uartsmc.h`, `bdalloc`, `dcflush`, `dczap`, `sync`, and `intrenable`. Only SMC1 is active; SMC2 is present but commented out.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ppc/uartsmc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ppc/ucu.h -->
# File Research: sources/os/plan9/9front/sys/src/9/ppc/ucu.h

Small PPC platform memory/MMU header for a Saturn-based target. It defines flash/DRAM/plan9.ini locations, the `Saturn` MMIO base, `TLBENTRIES`, and PTE policy bits used by fault/MMU code.

The file sets `MEM1SIZE` to 32 MiB, disables a second memory bank, and defines cache/write policy defaults: `PTEVALID` as write-through/memory-coherent bits, writable and read-only encodings, and cached/uncached selectors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ppc/ucu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/clock.c -->
# File Research: sources/os/plan9/9front/sys/src/9/sgi/clock.c

Provides SGI/MIPS clock initialization and timekeeping using the MIPS count/compare registers. `clockinit` estimates CPU speed with a calibrated instruction loop, sets delay-loop calibration, initializes `m->cyclefreq`, min/max timer periods, and enables interrupt level 7.

`clock` schedules the next compare interrupt and calls `timerintr`. `fastticks` accumulates monotonic ticks from `rdcount` under `splhi` to avoid recursive trap/interrupt reentry. `µs`, `microdelay`, `delay`, `perfticks`, and `timerset` provide the machine-dependent timing API.

The code assumes a 150 MHz Indy-style base and a count register that advances at half clock rate.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/9/sgi/dat.h

Defines SGI/MIPS machine-dependent data structures consumed by the portable Plan 9 kernel and assembler. It includes `Conf`, `Confmem`, `Label`, `ISAConf`, floating-point save state, process MMU state, `Mach`, `KMap`, and software TLB entries.

Important ABI constraint: the leading fields of `Mach` are fixed for `l.s` and cannot move. The file defines per-Mach TLB PID ownership, active kmaps, timer accounting, delay calibration, and soft-TLB collision stats.

Also defines global `active`, register globals `m` and `up`, and MIPS-specific `KMap`/`Softtlb` structures used by `mmu.c` and the assembly TLB miss path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/devkbd.c -->
# File Research: sources/os/plan9/9front/sys/src/9/sgi/devkbd.c

Implements the SGI keyboard/mouse controller device as Plan 9 device `#b`. It exposes `scancode` for raw keyboard scancodes and `leds` for lock LED control.

The controller is i8042-like but accessed through SGI HPC3 keyboard/mouse MMIO. `kbdinit` maps the controller, initializes a nonblocking queue, drains pending bytes, reads/modifies the controller command byte, enables keyboard interrupts/scancode set 1, and adds a clock poll hook. `i8042intr` routes aux-port bytes to `sgimouseputc` and keyboard bytes to the scancode queue.

Open of `scancode` is eve-only and exclusive via a ref count. LED writes parse a small integer and send the 0xed keyboard LED command.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/devkbd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/etherseeq.c -->
# File Research: sources/os/plan9/9front/sys/src/9/sgi/etherseeq.c

Implements a SEEQ 8003 Ethernet driver attached through SGI HPC3 DMA. It registers an `ether` card type named `seeq`.

The driver models HPC3 Ethernet registers with `Hio`, uses descriptor rings for RX/TX, and runs separate receive and transmit kernel processes. RX descriptors are replenished with page-sized buffers, packets are copied to allocated Blocks and queued with `etheriq`; TX descriptors are filled from `edev->oq` and kicked through HPC3 DMA state.

`startup` initializes DMA fixes, rings, station address, receive mode, and status registers. `shutdown` resets the channel. Interrupts clear overflow/completion and wake the RX/TX paths. Promiscuous and multicast are no-ops because the driver always receives promiscuously.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/etherseeq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/faultmips.c -->
# File Research: sources/os/plan9/9front/sys/src/9/sgi/faultmips.c

Handles MIPS page/address faults and alignment validation. `faultmips` converts MIPS TLB exception causes into Plan 9’s common `fault` call, posts user notes on unrecoverable user faults, and panics with register dumps on kernel faults.

`tstbadvaddr` decodes the faulting MIPS load/store instruction to check whether `badvaddr` matches the computed effective address, including branch-delay handling. Debug-only stuck-fault tracking records repeated faults at the same VA/PC/pid/cause.

`validalign` relaxes 64-bit alignment to 32-bit alignment for this 32-bit OS/compiler environment, then posts `"sys: odd address"` on invalid alignment.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/faultmips.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/9/sgi/fns.h

Machine-dependent function declarations and address macros for the SGI/MIPS port. It includes ARCS console calls, clock, cache, MMU/TLB, FP, trap, interrupt, process, screen, and utility prototypes.

Defines `KADDR`, `PADDR`, and `KSEG1ADDR` conversions, plus `userureg`. The file is the declaration bridge between C files and low-level assembly routines in `l.s`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/fptrap.c -->
# File Research: sources/os/plan9/9front/sys/src/9/sgi/fptrap.c

Handles selected MIPS floating-point traps, especially unimplemented operations that are likely underflows. `fptrap` inspects FCR31, fetches the trapping instruction, attempts `fpunimp`, advances PC, and clears the unimplemented bit when handled.

`fpunimp` decodes COP1 operations and formats, estimates exponents/signs, handles ABS/NEG directly, and zeroes destination registers for guessed underflow cases while setting underflow exception/sticky bits. It does not implement full FP emulation.

`branch` decodes integer and FP branch/jump instructions to compute the correct resume PC when the FP trap occurred in a branch delay slot.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/fptrap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/init9.s -->
# File Research: sources/os/plan9/9front/sys/src/9/sgi/init9.s

Tiny MIPS assembly entry wrapper for boot startup. `_main` sets the static base register, stores the `boot` function and an argument-frame pointer on the stack, and jumps to `startboot`.

This is a boot-loader-side handoff helper rather than the main kernel entry path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/init9.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/io.h -->
# File Research: sources/os/plan9/9front/sys/src/9/sgi/io.h

Defines SGI I/O constants: `Mhz`, uncached MMIO mapping macro `IO(t,x)`, SGI IRQ numbers, INT2 local interrupt register addresses, and key device bases for HPC3 Ethernet, keyboard/mouse, Newport graphics, and memory configuration registers.

`INT2_BASE` is fixed to the IP24/Indy address. The file is included by SGI device, interrupt, and memory discovery code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/l.s -->
# File Research: sources/os/plan9/9front/sys/src/9/sgi/l.s

Main SGI/MIPS assembly support file. It contains boot entry `start`, ARCS firmware call trampoline, user-mode entry, interrupt priority routines, label save/restore, TLB register access, soft-TLB hash/miss fast path, general exception vector save/restore, FP save/restore, atomics, cache flushes, block output, and CP0 count/compare accessors.

The UTLB miss path hashes `TLBVIRT`, checks `m->stb`, installs even/odd TLB entries, and falls back to the general exception path on miss/collision. `saveregs`/`restregs` define the `Ureg` stack frame consumed by `trap.c`.

This file is ABI-critical with `dat.h`, `mem.h`, and `ureg.h`: register globals, `Mach` offsets, UREG offsets, and cache/TLB constants must remain aligned.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/main.c -->
# File Research: sources/os/plan9/9front/sys/src/9/sgi/main.c

SGI kernel bootstrap and machine setup. `main` initializes ARCS console, memory, `conf`, `Mach`, kmap, timers, formats, optional graphics, TLB, pages, processes, devices, first user process, and scheduler.

Memory discovery reads SGI memory config registers and filters out kernel and ARCS-reserved regions. `machinit` installs ARCS-dispatched exception hooks for UTLB miss and general exceptions, clears FP interrupts, and initializes the clock. `init0` sets environment variables and starts `boot`.

Also handles process FP state setup/fork/save, reboot through ARCS, kernel config sizing, and basic stubs for watchpoints/ISA config.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/mem.h -->
# File Research: sources/os/plan9/9front/sys/src/9/sgi/mem.h

SGI/MIPS memory, MMU, exception, and address-space constants shared by C and assembly. It defines page size selection, stack/Mach sizing, CP0 registers, status/cause bits, exception codes, MIPS segments, kernel/user virtual layout, PTE bits, TLB PID counts, soft-TLB sizing, and kmap layout.

Default pages are 4 KiB; optional 16 KiB pages are noted as poor. KSEG0/KSEG1 direct maps, KSEG3 kmap, `MACHADDR`, `SPBADDR`, and cache coloring macros are central to `l.s`, `mmu.c`, and `main.c`.

The PTE defaults use noncoherent write-back caching, with comments noting MIPS 24K cache behavior and errata tradeoffs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/mmu.c -->
# File Research: sources/os/plan9/9front/sys/src/9/sgi/mmu.c

Implements SGI/MIPS TLB and kmap management. It invalidates hardware TLB entries, manages a fixed `KMap` pool, maintains per-Mach active kmaps, assigns TLB PIDs to processes, populates a software TLB cache, and handles kmap faults.

`kmap` maps physical pages into KSEG3 while preserving cache-color bits to avoid virtual coherence exceptions. `putstlb` updates the hashed soft-TLB entry used by the assembly fast miss path; `putmmu` updates both soft and hardware TLB, including text-cache flush when needed.

`purgetlb` invalidates stale process ASIDs, clears dead soft-TLB entries, and invalidates hardware entries whose PID no longer maps to a live process. `mmuswitch` uses TLB entry 0 to establish current PID.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/screen.c -->
# File Research: sources/os/plan9/9front/sys/src/9/sgi/screen.c

Implements SGI Newport graphics support and SGI mouse decoding. It defines Newport, VC2, XMAP9, DCB, drawing-mode, and color-map register constants, maps Newport registers, allocates a 1280x1024 RGBX32 software framebuffer, and flushes dirty rectangles to hardware.

`flushmemscreen` lazily switches the graphics mode, disables ARCS console if needed, initializes software cursor mode, then writes rectangle spans through host register writes. Hardware cursor support exists but is disabled via `SWCURSOR`.

`attachscreen` exposes the `Memdata` to `devdraw`; color and blanking hooks are stubs. `sgimouseputc` decodes the 3-byte SGI mouse protocol and calls `mousetrack`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/screen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/screen.h -->
# File Research: sources/os/plan9/9front/sys/src/9/sgi/screen.h

Declares mouse/screen/devdraw interfaces shared by SGI screen, mouse, and draw code. It provides prototypes for cursor control, `flushmemscreen`, `attachscreen`, mouse tracking, mouse protocol helpers, and draw locking.

Defines `ishwimage(i)` as `0`, meaning hardware image acceleration is not advertised to `../port/devdraw.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/screen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/trap.c -->
# File Research: sources/os/plan9/9front/sys/src/9/sgi/trap.c

Implements SGI/MIPS trap, interrupt, syscall, note, and register-dump handling. `trap` dispatches external interrupts, FP exceptions, TLB faults, VCEs, watchpoints, coprocessor-unusable traps, and default exceptions.

The interrupt subsystem chains handlers per MIPS interrupt level. `hpc3irqlevel` maps SGI HPC3 IRQs to MIPS interrupt levels and unmasks INT2 bits. FP handling lazily enables/restores FPU state, posts FP notes, and uses `fptrap` for selected cases.

The file also implements user notify/noted stack frames, syscall dispatch from assembly, fork/kproc child register setup, exec register setup, user PC/debug PC helpers, protected register writes for `/proc`, and diagnostic stack/register dumps.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/uartarcs.c -->
# File Research: sources/os/plan9/9front/sys/src/9/sgi/uartarcs.c

Provides a Plan 9 UART abstraction over SGI ARCS firmware console calls. It creates a single `arcsuart`, uses ARCS service calls for polling input and output, and sets it as `consuart` during early console init.

`arcsproc` periodically polls firmware input and feeds characters into the UART layer. `kick` writes queued UART output through ARCS while holding `arcslock`. Most hardware-control callbacks are no-ops or validate only trivial settings: baud positive, bits 7/8, one stop bit, no parity.

This is an early/firmware console bridge, later disabled by graphics setup if Newport screen takes over.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/sgi/uartarcs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/arch.c -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/arch.c

Generic ARM/Tegra architecture glue for process and register handling. It supplies `setkernur`, `evenaddr`, `userpc`, `setregisters`, `kprocchild`, `dbgpc`, `procsetup`, `procsave`, `procfork`, `procrestore`, and `userureg`.

Most FP work delegates to VFP helpers. `procsave` writes back cache around the `Proc`, and `procrestore` wakes WFI and writes back L1 cache for stability. `setregisters` preserves PSR mode/interrupt bits when userland writes register state through `/proc`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/arch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/archtegra.c -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/archtegra.c

Tegra 2 SoC support file. It defines MMIO register layouts for clock/reset, power, SCU, flow controller, diagnostics, and the global `soc` address table for core devices.

Responsibilities include CPU clock defaults and errata setup, Ethernet device declaration (`rtl8169` on PCIe), SCU enablement, available CPU count, clock/reset enablement, stopping/starting secondary CPUs, SMP/cache-coherency diagnostics, secure-mode checks, Cortex-A9 auxiliary control setup, secondary CPU entry (`cpustart`), SGI interrupt handling, board reset/reboot, device accessibility checks, and flash stubs.

Important coupling: secondary CPUs wait on `l1ptstable`, which the RTL8169 attach path sets after PCI/Ethernet init stabilizes the L1 page table.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/archtegra.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/arm.h -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/arm.h

ARMv7/Cortex-A8/A9 shared constants for C and assembler. It defines PSR mode/status bits, coprocessor numbers and CP15 register selectors, system control bits, auxiliary-control bits, cache/TLB operation selectors, vector-base selectors, PL310-related control bits, ARMv7 L1/L2 PTE formats, access permissions, domains, cacheability/sharability attributes, and high-vector address.

The PTE comments emphasize that lock-containing memory must be cached, buffered, sharable, and write-allocate for LDREX/STREX to work in SMP mode.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/arm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/arm.s -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/arm.s

Assembler macro/header file for Tegra 2 ARM code. It defines address conversion macros, L1 PTE construction helpers, early delay and UART byte-output macros, raw instruction encodings for ARMv7/TrustZone/barrier/FP operations, cache/TLB barrier sequences, PTE fill/zero macros, zero-segment static-base setup, ARMv7 RFE encodings, and CPU-ID extraction.

This file is included by low-level assembly such as startup, exception, cache, and reboot code. It encodes assumptions about R9/R10 register globals and avoids R11 due to loader use.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/arm.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/cache-l2-pl310.c -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/cache-l2-pl310.c

Implements Tegra 2’s external PL310 L2 cache as a `Cacheimpl`. It configures ways/sets, enables PL310 with required auxiliary bits, and provides whole-cache and range operations for invalidate, writeback, and writeback+invalidate.

The code documents two critical hardware issues: shared-attribute override must be set for correctness, and clean+invalidate needs an erratum 588369 workaround by temporarily forcing write-through/no-line-fill in the debug register.

Range invalidation cleans unaligned boundary lines first. Whole-cache operations use way masks and a `bg_op_running` flag with lock coordination, optionally releasing the lock while polling on SMP.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/cache-l2-pl310.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/cache.v7.s -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/cache.v7.s

ARMv7 cache maintenance assembly. It implements I-cache invalidate, set/way data-cache operations, cache-level selection, whole L1/L2 writeback/invalidate wrappers, unified L1 writeback+invalidate, and the shared `wholecache` set/way iterator.

`wholecache` reads cache geometry via CP15, uses precomputed set/way shifts from `CACHECONF`, disables interrupts, runs barriers, iterates all ways and sets, and calls the selected operation stub. It includes early panic paths if cache shift parameters are invalid.

The file is intended for inclusion/use by both normal kernel code and early/reboot code where MMU mapping may be unusual.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/cache.v7.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/caches-v7.c -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/caches-v7.c

Discovers and reports ARMv7 cache geometry. `cacheinfo` fills `Memcache` for a given level, using CP15 cache-size registers for internal caches and `allcache->info` for external L2. `allcacheinfo` walks cache-level ID fields. `prcachecfg` prints cache level, type, ways, sets, line size, write capabilities, and L1 I-cache indexing policy.

This file supplies metadata used by low-level cache assembly and diagnostics; it does not perform maintenance operations itself.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/caches-v7.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/caches.c -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/caches.c

Defines cache-operation composition layers. `allcaches` combines L1 architectural operations with external L2 operations in the correct order for invalidate, writeback, and writeback+invalidate, both whole-cache and range-based. `nullcaches` is a no-op implementation, and `l1caches` wraps only L1 operations.

`allcacheson` initializes PL310 and sets global `allcache`, `nocache`, and `l1cache` pointers. DMA-sensitive paths rely on this wrapper so data reaches RAM before device reads and stale CPU cachelines are invalidated after device writes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/caches.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/clock-tegra.c -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/clock-tegra.c

Handles Tegra 2 SoC timers outside the Cortex private timers. It models four shared 29-bit countdown timers and the 32-bit 1 MHz microsecond counter.

`tegclock0init` arms the shared Tegra watchdog timer and registers `tegwdogintr`; `tegclockshutdown` disables it on CPU0. `tegclockinit` verifies the freerunning microsecond counter configuration and movement. `perfticks` returns the microsecond counter, keeping zero from being returned.

The shared watchdog requires clearing interrupt state and reading trigger to satisfy hardware/documentation quirks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/clock-tegra.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/clock.c -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/clock.c

Cortex-A private timer and Plan 9 clock implementation for Tegra 2. It uses the Tegra 1 MHz counter as `fastticks` and Cortex local timers for periodic scheduling interrupts. It also contains optional local-watchdog code and multi-CPU clock sanity checks.

`clockinit` shuts down old timers, enables ARM cycle counters, validates the microsecond counter and local timer, installs the local timer IRQ, calibrates delay loops on CPU0, starts watchdogs, desynchronizes per-CPU timers, and arms periodic ticks. `clockintr` clears local timer interrupt state, calls `timerintr`, appeases the Tegra watchdog, and checks secondary CPU clock progress.

`fastticks` extends the 32-bit microsecond counter to a per-Mach 64-bit value under `splhi`. `timerset` converts fasttick targets to local-timer cycles with min/max clamping.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/coproc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/coproc.c

Runtime coprocessor access helpers for ARM. Because ARM encodes coprocessor/register fields directly in instructions, this file builds two-instruction stubs in memory, flushes data cache, invalidates I-cache, and calls them to read/write CP15 and VFP control/register state.

`cprd`/`cpwr` generate MRC/MCR operations; `cprdsc`/`cpwrsc` specialize CP15. `fprd`/`fpwr` generate VMRS/VMSR for FP control registers. `fpsavereg`/`fprestreg` generate VSTR/VLDR for double FP registers.

All operations run at `splhi` and use cache maintenance to make generated instructions executable and coherent.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/coproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/dat.h

Tegra/ARM machine-dependent data definitions. It defines time constants, core typedefs, FP/VFP save structures, `Conf`, ARM MMU state in `Mach` and `Proc`, the `Mach` structure, fake kmap macros, global `active`, cache metadata, cache implementation interface, DMA mode enum, IRQ numbers, and the `Soc` address table structure.

`Mach` contains MMU fields known to assembly, fastclock state, probe/trap state, CPU frequency, VFP state, exception save areas, and stack. `PMMU` tracks L2 page-table pages. `Cacheimpl` provides the cache operation vtable used by drivers and MMU code.

The file also declares global cache pointers and platform globals such as `navailcpus`, `kseg0`, `memsize`, `l1ptstable`, and `machaddr`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/devarch.c -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/devarch.c

Implements Plan 9 architecture device `#P` for Tegra/ARM. It supports dynamically adding read/write files via `addarchfile`, backed by `Dirtab` entries and function tables.

The default exported files are `cputype`, which reports ARM CPU name and MHz, and `timebase`, which reports `cycles()` as a fixed-width hex value. An `nsec` file exists but is commented out.

The device follows normal Plan 9 devtab operations: attach, walk, stat, open, read directory or handler, and write handler dispatch.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/devarch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/ether8169.c -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/ether8169.c

RTL8110/8168/8169 Gigabit Ethernet driver for Tegra/ARM, registered as `rtl8169`. It defines Realtek register maps, descriptor formats, MAC variants, PHY access, multicast hashing, statistics, RX/TX rings, PCI probing, interrupt handling, reset/restart, attach, and Plan 9 `Ether` callbacks.

DMA/cache correctness is central: TX packet data is written back before ownership is given to hardware; RX packet data is invalidated before handing to the network stack; descriptor/ring updates use `coherence`; descriptor/stat buffers are aligned. RX/TX processing is split into kernel processes awakened by interrupt-masked status bits.

Initialization resets the device, allocates 1024 TX and RX descriptors, fills RX buffers from a block pool, configures variant-specific magic registers and burst settings, sets descriptor base addresses, enables interrupts, and starts link handling. Error paths restart the controller on FIFO overrun, receive descriptor unavailable, receive errors, or stalled state. PCI probing matches Realtek IDs, detects PCIe, maps BAR2 directly on TrimSlice, validates hardware MAC version, initializes MII, and enables bus mastering.

Notable coupling: `rtl8169attach` sets `l1ptstable.word` and writes it back so secondary Tegra CPUs can proceed after page-table state is stable.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/ether8169.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/fns.h

Function declarations and macros for the Tegra/ARM port. It imports portable Plan 9 declarations, declares ARM/Tegra cache, clock, interrupt, MMU, FPU, PCI, UART, screen, CPU, coprocessor, timer, and architecture hooks, and maps legacy `intrenable`/`intrdisable` to GIC `irqenable`/`irqdisable`.

Defines `cycles`, `KADDR`, `PADDR`, `getpgcolor`, no-op `kmapinval`, and `MASK`. It is the central declaration bridge between C files, assembly routines, and portable kernel code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/io.h -->
# File Research: sources/os/plan9/9front/sys/src/9/teg2/io.h

Minimal Tegra I/O header. It defines `BUSUNKNOWN`, a zero `PCIWINDOW`, and `PCIWADDR(va)` as `PADDR(va)+PCIWINDOW`.

The RTL8169 driver uses `PCIWADDR` to convert CPU virtual packet/descriptor addresses into PCI-visible DMA addresses.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/teg2/io.h -->