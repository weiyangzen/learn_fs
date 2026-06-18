# Group Research: group_1490_plan9_sources_os_plan9_plan9_sys_src_9_rb_main_c_sources_os_plan9_p_185eae6c95a7

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/main.c

RouterBoard MIPS kernel mainline for Plan 9. It performs early board bring-up, fixed boot argument setup, process/user initialization, reboot, shutdown, and memory sizing.

Key responsibilities:
- Initializes RouterBoard boot arguments as `/boot/boot boot`, fixed memory configuration, FP save area, Mach state, kmap, traps, TLB, pages, processes, channels, swap, and the first user process.
- Installs MIPS exception vectors into KSEG0 vector slots and clears bootstrap exception-vector mode.
- Reports MIPS 24K CPU identity, endian mode, FPU presence, TLB entries, and L1 cache geometry.
- Builds the initial user stack and init text segment, then enters user mode through `touser(sp)`.
- Seeds early `/env` settings in `init0`, including `cputype`, `terminal`, `service`, `nobootprompt`, and `nvram`.
- Implements Plan 9 reboot by copying `rebootcode` to `REBOOTADDR`, shutting down devices/interrupts/clocks, and jumping to the trampoline with loaded-kernel physical addresses.
- Implements `exit` by disabling the watchdog, waiting for other CPUs/console output, enabling bootstrap vectors, arming a short watchdog reset, then falling back to ROM.

Important interfaces:
- `main`, `machinit`, `vecinit`, `init0`, `userinit`, `confinit`.
- `parsemipsboothdr` for MIPS boot executable header parsing during `rebootcmd`.
- `reboot`, `exit`, `idlehands`, `procsave`, `procrestore`.

Dependencies and assumptions:
- Assumes a single CPU (`MAXMACH` and `conf.nmach` are 1) and fixed RouterBoard memory size from `MEMSIZE`.
- Relies on MIPS assembly helpers for CP0 access, vectors, cache flushes, status changes, user entry, and watchdog control.
- `getconf` is a stub returning nil; this port hard-codes the boot environment instead of reading a full configuration file from RouterBOOT.

Notable risks:
- Initialization order is strict; traps, kmap, TLB, pages, and channel devices are sequenced explicitly.
- `confinit` computes kernel/user memory before setting several process/image/swap counts, so the exact ordering is part of the port contract.
- Reboot and exit paths run with devices and interrupts being torn down and are sensitive to cache/vector correctness.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/mem.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/mem.h

RouterBoard MIPS memory, CPU, exception, TLB, and address-layout constants shared by C and assembly.

Key contents:
- Defines page sizes, stack sizes, cache sizes, cache-line size, alignment macros, and fixed single-CPU limits.
- Defines MIPS CP0 register numbers, status bits, config bits, cause bits, cache ECC bits, exception codes, and trap-vector addresses.
- Defines `Ureg` offsets and `UREGSIZE` for assembly trap-frame layout.
- Defines MIPS address segments (`KUSEG`, `KSEG0`, `KSEG1`, `KSEG2`, `KSEG3`), RouterBoard layout (`MACHADDR`, `KTZERO`, `REBOOTADDR`, `PHYSCONS`, `ROM`), and fixed `MEMSIZE`.
- Defines TLB page-size encodings, PTE bits, cacheability modes, soft-TLB sizing, ASID count, wired/random TLB boundaries, and user stack/text layout.

Role:
- This header is the ABI between low-level MIPS assembly, trap handling, MMU code, kmap, reboot code, and early console output.
- It encodes the MIPS 24K cache aliasing policy: 4 KiB pages use 8 colors, while larger pages collapse `NCOLOR` to 1.

Notable constraints:
- `PTECACHABILITY` is write-through (`PTENONCOHERWT`) because the comments cite MIPS 24K erratum 48 disallowing write-back.
- `NWTLB` is zero, so the wired large I/O TLB mechanism is compiled but unused.
- `MEMSIZE` is fixed at 256 MiB and `PCIMEM` is hard-coded for the rb450g platform.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/mips.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/mips.s

MIPS 24K assembly macro include for the RouterBoard port. It defines instruction encodings and helper macros used by startup, exception, cache, TLB, and reboot assembly.

Key responsibilities:
- Defines symbolic register aliases (`SP`, `MACH`, `USER`) and basic instruction macros such as `NOP`, `CONST`, and `RETURN`.
- Encodes MIPS32R2 operations not directly named by the assembler: `DI`, `EI`, `EHB`, `JALRHB`, `JRHB`, `MFC0`, `MTC0`, `RDHWR`, `SYNC`, and `WAIT`.
- Wraps `ERET` with hazard barriers and a post-ERET NOP for MIPS 24K behavior.
- Provides barrier macros that jump through a hazard-barrier return sequence, including a KSEG1 variant.
- Provides a direct serial `PUTC` macro using `PHYSCONS`.
- Defines cache operation encodings for primary data/instruction and secondary/tertiary cache operations.

Role:
- This file is not a standalone implementation; it is an assembly support header included by other MIPS assembly files.
- It centralizes CPU-specific erratum/hazard handling so trap and MMU assembly can use consistent barriers.

Notable constraints:
- Several operations are raw `WORD` encodings, so correctness depends on MIPS32R2 instruction layout and the Plan 9 assembler's expectations.
- The comments explicitly tie some sequences to MIPS 24K errata and experience with required hazard barriers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/mips.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/mmu.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/mmu.c

RouterBoard MIPS MMU management for hardware TLB invalidation, color-aware temporary kernel mappings, software TLB entries, ASID allocation, user mapping insertion, and TLB purge.

Key responsibilities:
- Initializes all hardware TLB entries as invalid in `tlbinit`.
- Manages the fixed `KMap` pool used by `kmap`/`kunmap`, including per-Mach active mappings and TLB entries.
- Chooses kmap virtual addresses that preserve cache index/color bits to avoid MIPS virtual coherence exceptions.
- Handles kernel kmap faults from KSEG3 through `kfault`.
- Allocates per-process TLB PIDs/ASIDs with `newtlbpid`, switches ASIDs in TLB entry 0 in `mmuswitch`, and purges dead ASIDs in `purgetlb`.
- Inserts user mappings in both the software TLB hash and hardware TLB through `putmmu`, applying the port cacheability policy and page cache-flush state.
- Provides stubs or simple implementations for `checkmmu`, `countpagerefs`, and `cankaddr`.

Important behavior:
- During startup, kmap entries use a small wired TLB range; after `up` becomes non-nil, the code shares all but one TLB entry between kernel and user mappings.
- `putstlb` hashes even/odd page pairs by virtual address plus ASID and tracks hash collisions.
- `purgetlb` invalidates software and hardware entries for ASIDs no longer owned by live processes.

Dependencies and assumptions:
- Depends on MIPS CP0/TLB helpers (`puttlb`, `puttlbx`, `gettlbp`, `gettlbvirt`, `tlbvirt`, `setwired`) and on the `Softtlb` layout used by assembly TLB-miss code.
- Assumes direct KSEG0/KSEG1 mappings for normal physical memory and fixed `MEMSIZE`.

Notable risks:
- `NWTLB` is zero, so `wiredpte` will panic if used.
- KMap pool exhaustion spins through `kmapinval` and retries, printing diagnostic timing if starved.
- Software-TLB hash collisions overwrite prior entries and rely on refault/reload behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/rebootcode.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/rebootcode.c

Small MIPS reboot trampoline copied to `REBOOTADDR` by `reboot()` before jumping into a newly loaded kernel.

Key responsibilities:
- Prints `Boot` through the raw i8250-compatible console registers.
- Saves incoming entry/code/size arguments in static variables before moving the stack near the new kernel entry.
- Copies the loaded kernel image from `code` to `entry`, cleans caches, enforces coherence, and jumps to the new entry point.
- Provides local `putc` polling on the UART line-status register.
- Supplies stub `syscall` and `trap` definitions so the tiny trampoline can link.

Dependencies and assumptions:
- Runs in KSEG0/direct-mapped space with TLBs ignored.
- Assumes the serial console is at `PHYSCONS` and register spacing matches the port's 32-bit CSR access style.
- Assumes `setsp`, `memmove`, `cleancache`, and `coherence` are safe in the reboot context.

Notable risks:
- The stack is deliberately moved to `entry - 0x20 - 4`; overlap with the target image layout would be fatal.
- If the new kernel returns, the code only prints `?!` and loops forever.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/rebootcode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/trap.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/trap.c

RouterBoard MIPS trap, interrupt, syscall, register dump, and note-delivery implementation.

Key responsibilities:
- Dispatches MIPS exception codes to interrupt handling, VM faults, kmap faults, VCE diagnostics, watchpoints, FPU emulation, user notes, or kernel panic/exit.
- Maintains interrupt handler chains per interrupt level, enables RouterBoard APB UART subinterrupts, masks jabbering interrupts, and periodically resets interrupt counts.
- Handles clock interrupts, device interrupt polling, preemption, and delayed scheduling at trap exit.
- Implements Plan 9 user notification (`notify`, `noted`, `validstatus`) and the MIPS user-stack frame used for note handlers.
- Implements system call entry directly from assembly, including syscall tracing, argument validation, error-stack handling, `NOTED` special handling, note delivery, and return-value placement.
- Provides process fork/kproc register setup (`forkchild`, `kprocchild`), exec register setup (`execregs`), user PC helpers, and kernel stack/register dump helpers.

Important behavior:
- Kernel KSEG3 TLB faults are routed to `kfault`; user TLB faults are passed to `faultmips`.
- Floating-point coprocessor unusable traps from user mode are handled by software FP emulation because the port has no usable FPU path here.
- `#define setstatus(v)` makes the status updates in this file no-ops as an experiment noted in the source.
- Interrupt `pollall` treats `ILduart0` specially through APB subinterrupt status.

Dependencies and assumptions:
- Trap-frame offsets must match `mem.h`, `ureg.h`, and assembly vector code.
- Depends on `faultmips`, `fpuemu`, `fpwatch`, scheduler, note, syscall, and Plan 9 port-layer process APIs.

Notable risks:
- Note return validation preserves interrupt mask and forbids privileged/user-hostile status bits, but any trap-frame ABI mismatch would corrupt user return.
- Jabber suppression disables interrupt sources after 25,000 handler invocations within a reset interval.
- Kernel exceptions generally dump registers/stack and call `exit(1)` rather than trying to recover.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/uarti8250.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/uarti8250.c

Single-console 8250-like UART driver for the RouterBoard port, using memory-mapped 32-bit CSR slots at `PHYSCONS`.

Key responsibilities:
- Defines one `Ctlr` and one console `Uart` named `cons`, wired to `ILduart0`.
- Implements the `PhysUart` interface: enable/disable, kick, break, baud/bits/stop/parity, modem control, RTS/DTR, FIFO, status, getc, and putc.
- Provides early output fallback when `normalprint` is false by polling raw `PHYSCONS` registers directly.
- Handles UART interrupts for modem status, transmit-empty, receive-ready, line-status, and character-timeout conditions.
- Stages output through Plan 9 UART queues and re-enables transmit-empty interrupts while data remains.
- Provides `i8250console()` to bind the UART queues to `kbdq`, `serialoq`, `consuart`, and console input conversion.
- Exposes `_uartputs`, `_uartprint`, `serialputc`, `serialputs`, and `serialkick` for low-level console users.

Important behavior:
- Baud-rate programming is disabled under `#ifdef notdef`; `i8250baud` records the requested baud but does not change hardware speed.
- `i8250enable` probes FIFO support once before enabling interrupts and clears pending events by calling the interrupt handler immediately.
- A periodic clock callback can poll the interrupt handler to recover stuck output.

Dependencies and assumptions:
- Depends on the generic `devuart.c` framework, `intrenable`, APB interrupt routing in `trap.c`, and Plan 9 queues.
- Assumes only the first UART is the console and uses `normalprint` to distinguish early boot from normal queue-backed output.

Notable risks:
- FIFO changes wait for transmitter empty and may drop receive-side data by design.
- Several comments note forced `Ethre` and polling workarounds whose underlying hardware cause is not fully known.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/uarti8250.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/arch.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/arch.c

ARM/Tegra process and trap-glue routines that connect the generic Plan 9 kernel to Cortex-A9 register, timing, and process-state conventions.

Key responsibilities:
- Builds minimal kernel `Ureg` context for sleeping processes in `setkernur`.
- Implements architecture alignment checks for syscall/file/proc paths, relaxing 64-bit alignment to 32-bit alignment.
- Updates the user `Tos` structure on kernel exit with kernel cycles, process cycles, cycle frequency, and PID, then writes it back from cache.
- Provides user PC, debug PC, kernel process child setup, process setup/save/restore, and user-ureg detection.
- Delegates floating-point process lifecycle to FPU helpers.

Dependencies and assumptions:
- Depends on ARM `Ureg` layout, `sched`, `cycles`, `l1cache`, and VFP support routines.
- Assumes ARM user mode is identified by `(psr & PsrMask) == PsrMusr`.

Notable risks:
- `setregisters` is a stub, so devproc register writes are effectively ignored for this port.
- `procrestore` performs a full L1 writeback because the comment says the system is more stable with it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/arch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/archtegra.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/archtegra.c

NVIDIA Tegra 2 board and Cortex-A9 MPCore support for Plan 9. It defines SoC register maps, CPU/cache/clock reset setup, SMP bring-up, Ethernet selection, reset/reboot, and device-presence checks.

Key responsibilities:
- Defines typed register layouts for clock/reset, power, SCU, flow controller, and cache-coherency diagnostics.
- Populates global `soc` physical/MMIO addresses for clocks, power, exception-vector handoff, SCU/GIC, UARTs, timers, PCIe, Ethernet, flash, EHCI, IDE, GPIO, SPI, I2C, and MMC.
- Applies Cortex-A9 errata workarounds via CP15 diagnostic-register writes.
- Initializes CPU frequency/delay-loop estimates from defaults or `*cpumhz`.
- Selects the RTL8169 PCIe Ethernet controller for `archether`.
- Enables SCU, SMP/coherency bits, Cortex-A9 cache configuration, clocks, and software-generated interrupt handlers.
- Starts secondary CPUs through Tegra's undocumented exception-vector register, unfreezes flow/reset state, and waits for the secondary CPU to acknowledge.
- Handles secondary CPU startup, including traps/clocks/timers, L1 cache coherence diagnostics, waiting for RTL8169 initialization to stabilize L1 page tables, MMU initialization, FPU enable, and scheduler entry.
- Implements CPU stop, board reboot through clock/reset registers, keyboard stub, flash stubs, and register-access probes for required devices.

Important behavior:
- Secondary CPUs wait on `l1ptstable.word` because the 8169 initialization must finish before copying CPU0's L1 page table.
- `l1diag` is compiled but inactive unless `Debug` is set.
- `clockson` clears all reset bits and enables all clock outputs.

Dependencies and assumptions:
- Assumes a Cortex-A9 in secure mode; `cksecure` panics if running non-secure.
- Depends on CP15 helpers, cache maintenance, SCU/GIC support, MMU code, PCI, RTL8169, and Plan 9 SMP state.

Notable risks:
- CPU startup relies on an undocumented Tegra exception-vector register and comments acknowledge Linux-derived/experimental behavior.
- Flash reset is intentionally unfinished and panics if used.
- `stopcpu` and `startcpu` only cover the flow-controller CPU range available on Tegra 2.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/archtegra.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/arm.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/arm.h

ARMv7/Cortex-A8/Cortex-A9 constants shared by Tegra C and assembly code.

Key contents:
- Defines ARM processor modes, PSR flags, mode masks, and bits that must remain zero.
- Defines coprocessor numbers and CP15 register/opcode names for ID, control, TTB, DAC, fault status/address, cache, TLB, lockdown, vector base, PID, and Cortex diagnostic registers.
- Defines CP15 control-register bits, Cortex-A9 auxiliary-control bits, cache/TLB maintenance operation encodings, performance-counter registers, and PL310 L2 auxiliary bits.
- Defines ARMv7 MMU L1/L2 PTE formats, access permissions, domain encodings, cacheability/shareability attributes, high-vector address, and helper macros for AP/DAC fields.

Role:
- This is the central CP15/MMU/cache ABI for startup assembly, `coproc.c`, MMU code, trap vectors, cache maintenance, and board reset.
- It encodes the port's requirement that memory containing locks be cached, buffered, write-allocate, and shareable so `LDREX`/`STREX` work correctly.

Notable constraints:
- Comments distinguish ARMv7-preferred permission encodings from older forms.
- Many definitions are Cortex-specific, not generic to all ARM versions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/arm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/arm.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/arm.s

Tegra 2 ARM assembly macro include for early startup, exception return, MMU/cache setup, barriers, and low-level CP15 operations.

Key responsibilities:
- Defines physical/virtual conversion macros, L1 index calculations, CPU0 Mach placement, and initial section PTE constants for DRAM and I/O.
- Provides early serial `PUTC`, delay-loop, zero-segment SB setup, and page-table fill/zero macros.
- Encodes ARMv7 instructions and barriers not directly expressed by older Plan 9 assembler syntax: `SMC`, branch-target-cache flushes, `DSB`, `DMB`, `ISB`, `WFI`, `CLZ`, endian/mode/interrupt CPS instructions, `CLREX`, and VFP control moves.
- Defines `BARRIERS` as branch-target flush plus DSB/ISB for PTE/cache/TLB update sequences.
- Defines ARMv7 `RFE` instruction encodings and CPU ID extraction macro.

Role:
- This is included by low-level assembly, not a standalone routine file.
- It bridges Plan 9 assembler conventions with ARMv7/Cortex-A9 hardware requirements.

Notable constraints:
- Comments warn that Plan 9 assembler `RFE` syntax does not mean the ARMv7 architectural `RFE` instruction.
- Several macros depend on code running before or after MMU enable and therefore adjust addresses to match the current segment.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/arm.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/cache-l2-pl310.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/cache-l2-pl310.c

PL310 external L2 cache driver for Tegra 2. It discovers/configures the cache, turns it on/off, and supplies range and whole-cache maintenance operations through `Cacheimpl`.

Key responsibilities:
- Maps the PL310 register layout, including control, auxiliary control, sync, invalidate/clean/clean-invalidate operations, filters, and debug register.
- Honors `*l2off` to disable L2 setup.
- Configures associativity and way size for the Tegra 2 1 MiB PL310 cache.
- Enables required auxiliary bits, especially shared-attribute override, prefetch, parity, and full-line-zero support.
- Implements range invalidate/writeback/writeback-invalidate using physical addresses and cache-line iteration.
- Implements whole-cache operations by way mask, including background-operation coordination and interrupt-level locking.
- Works around PL310 erratum 588369 by temporarily setting debug write-through/no-linefill around clean-invalidate operations.

Important behavior:
- Unaligned invalidation first cleans edge cache lines to avoid dropping dirty bytes outside the requested range.
- The code avoids lock manipulation while PL310 debug write-through mode is active because exclusive operations/locks may not work.
- Whole-cache operations may release `l2lock` while waiting only on multiprocessor systems.

Dependencies and assumptions:
- Depends on `soc.l2cache`, L1 cache helpers, `PADDR`, `CACHELINESZ`, CP15 cache setup, and Plan 9 locks.
- Assumes PL310 ID high byte is ARM when reporting cache info.

Notable risks:
- Source comments say PL310 default settings are guaranteed to work incorrectly unless `Sharovr` is set.
- Busy-wait loops wait directly on hardware operation registers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/cache-l2-pl310.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/cache.v7.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/cache.v7.s

ARMv7 assembly cache-maintenance routines for instruction cache invalidation, L1 data/unified cache operations, optional architectural L2 operations, and set/way traversal.

Key responsibilities:
- Provides `cacheiinv`, `cachedwb`, `cachedwbinv`, `cachedinv`, and `cacheuwbinv`.
- Provides single set/way primitives for clean, clean-invalidate, and invalidate.
- Provides `setcachelvl` and `getwayssets` CP15 cache-size helpers.
- Provides architectural L2 routines `_l2cacheuwb`, `_l2cacheuwbinv`, and `_l2cacheuinv`.
- Implements `wholecache`, which reads selected cache geometry, derives ways/sets, uses shift values from low memory `CACHECONF`, and iterates every set/way.
- Handles early-MMU cases by mapping function and data pointers into the caller's current segment.

Important behavior:
- Whole-cache operations run with interrupts disabled and end with barrier sequences.
- If cache geometry shift values are zero, the code prints a short early-console diagnostic and panics with `bad cache params`.

Dependencies and assumptions:
- Depends on `arm.s`, `arm.h`, low-memory `Lowmemcache` layout, and CP15 cache-size registers.
- Assumes cache line geometry has already been recorded in `CACHECONF` before set/way whole-cache operations are needed.

Notable risks:
- The assembly is tightly coupled to register use by Plan 9's external-register convention (`R9`/`R10`) and to `CACHECONF` offsets.
- Direct set/way operations are sensitive to correct cache-level selection and shift values.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/cache.v7.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/caches-v7.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/caches-v7.c

ARMv7 cache-geometry discovery and diagnostic printing.

Key responsibilities:
- Reads CP15 cache-level and cache-size registers to fill `Memcache` descriptors.
- Supports external L2 reporting by delegating level-2 information to `allcache->info`.
- Computes line length, number of sets, number of ways, set shift, and way shift.
- Prints cache configuration, write policy capabilities, and L1 instruction-cache indexing policy.

Dependencies and assumptions:
- Depends on `cprdsc`, `cpwrsc`, `cpctget`, `log2`, `cachel`, and `allcache`.
- Uses ARMv7 CLIDR/CCSIDR-style fields and Cortex cache-type encodings.

Notable risks:
- `allcacheinfo` currently iterates architectural cache levels and has the external PL310 line commented out, so external L2 reporting depends on other initialization paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/caches-v7.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/caches.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/caches.c

Cache operation composition layer that exposes all-cache, no-cache, and L1-only `Cacheimpl` vtables.

Key responsibilities:
- Initializes `allcache`, `nocache`, and `l1cache` implementations in `allcacheson`.
- Composes whole-system maintenance by ordering L1 and PL310 L2 operations for invalidate, writeback, and writeback-invalidate.
- Provides range operations used by DMA, page-table, and device code.
- Provides null cache operations for uncached/no-op contexts.
- Provides L1-only vtable wrapping the ARMv7 assembly routines.

Important behavior:
- All combined operations run at `splhi`.
- Writeback-invalidate first writes back L1, then L2, then invalidates/writes back L1 to keep DMA-visible memory coherent.

Dependencies and assumptions:
- Depends on `l2pl310init`, PL310 `l2cache`, and assembly L1 cache helpers.
- Assumes instruction caches are handled elsewhere; this file covers data/unified caches.

Notable risks:
- `cachesoff` only calls `l2cache->off`; L1 remains outside this abstraction.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/caches.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/clock-tegra.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/clock-tegra.c

Tegra 2 shared timer and 1 MHz microsecond-counter support, excluding Cortex private timers.

Key responsibilities:
- Defines Tegra shared countdown timer and microsecond counter register layouts.
- Services and clears the Tegra watchdog/shared timer interrupt.
- Starts the Tegra shared watchdog timer on CPU0 with `tegclock0init`.
- Shuts down the shared watchdog/timer from CPU0.
- Verifies the 1 MHz counter is configured by U-Boot as expected and is ticking.
- Provides `perfticks()` from the free-running microsecond counter.

Important behavior:
- `tegclockintr` reads timer trigger to appease the watchdog.
- The watchdog period is halved because the Tegra watchdog fires on the second missed interrupt.
- `perfticks` never returns zero, preventing `m->fastclock` from becoming zero.

Dependencies and assumptions:
- Assumes U-Boot left `soc.microsecond-counter cfg` as `0xb` for a 12 MHz peripheral clock divisor.
- Depends on `soc.tmr`, `soc.µs`, `irqenable`, and clock/watchdog constants.

Notable risks:
- The shared timer/watchdog behavior is tied to sparse documentation, including the required trigger read.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/clock-tegra.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/clock.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/clock.c

Cortex-A9 private timer and Plan 9 timekeeping implementation for the Tegra 2 port.

Key responsibilities:
- Uses Cortex local private timers for periodic clock interrupts and the Tegra 1 MHz counter for fast ticks.
- Defines local timer/watchdog and private global timer register layouts.
- Handles clock interrupts, calls `timerintr`, services Tegra watchdog state, and checks that other CPUs' clocks are still advancing.
- Initializes cycle counters/performance counters for user access.
- Calibrates delay-loop estimates and optional instruction-per-second diagnostics.
- Starts CPU-local watchdog support when enabled by compile-time conditionals.
- Implements `clockshutdown`, `clockinit`, `timerset`, `fastticks`, `lcycles`, `microdelay`, and `delay`.

Important behavior:
- `fastticks` extends the 32-bit 1 MHz counter into `m->fastclock` by detecting low-word wrap under `splhi`.
- `timerset` converts desired fasttick offset into private-timer cycles, clamping between minimum and maximum periods.
- Secondary CPU local timers are unmasked rather than registered through normal IRQ setup.
- `clockprod` can prod a stuck secondary CPU by forcing timer handling and resetting its local timer.

Dependencies and assumptions:
- Assumes the private local timer rate is `250 MHz / 2`, per source comment.
- Depends on Tegra shared clock functions, GIC helpers, CP15 performance counter access, and Plan 9 timer infrastructure.

Notable risks:
- Several watchdog paths are compiled out under `watchdog_not_bloody_useless`.
- Multiprocessor clock sanity can panic if another CPU's tick count diverges by more than one second after startup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/coproc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/coproc.c

Runtime-generated ARM coprocessor access helpers for CP15 and VFP control/register operations.

Key responsibilities:
- Builds tiny instruction buffers containing `MRC`/`MCR`, `VMRS`/`VMSR`, `VSTR`, or `VLDR`, followed by a return instruction.
- Flushes data and instruction caches so generated instruction buffers are executable.
- Provides generic `cprd`/`cpwr` and CP15-specific `cprdsc`/`cpwrsc`.
- Provides VFP control access (`fprd`, `fpwr`) and double-precision register save/restore (`fpsavereg`, `fprestreg`).

Important behavior:
- Operations run with interrupts disabled to keep the generated instruction sequence stable.
- FP reads/saves panic if the CPU's FPU state is marked off, while `fpwr` is allowed because it may enable the FPU.

Dependencies and assumptions:
- Depends on executable stack/local instruction buffers, `cachedwbse`, `cacheiinv`, `coherence`, and ARM instruction encodings.
- Assumes return via `MOV R14, R15` is suitable for these generated snippets.

Notable risks:
- Dynamic instruction generation is sensitive to cache coherency and instruction encoding correctness.
- This approach exists because ARM hard-wires coprocessor register numbers into instructions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/coproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/dat.h

Core Tegra 2 kernel data-structure header: time constants, architecture structs, MMU state, Mach layout, cache abstractions, IRQ numbers, and SoC address table.

Key contents:
- Defines `HZ`, watchdog timeout, CPU frequency conversion macros, and console index.
- Declares architecture types including `Conf`, `FPsave`, `Mach`, `MMMU`, `PMMU`, `Memcache`, `Cacheimpl`, `Soc`, `Uart`, and `Ether`.
- Defines ARM/VFP process FP save state and FP state flags.
- Defines `Conf` and `Confmem` physical-memory accounting.
- Defines per-Mach fields used by assembly first, followed by scheduler, clock, fault, interrupt, profiling, probing, and FPU state.
- Provides fake `kmap`/`kunmap` macros using the direct mapping.
- Defines global `active` CPU state, cache-line-isolated word wrapper, cache capability bits, cache implementation vtable, DMA mode enum, IRQ numbers, and SoC controller address struct.

Role:
- This file is the C-side ABI for most Tegra 2 port files, including assembly-known `Mach` offsets and cache-operation indirection.
- It captures the GIC interrupt numbering scheme: private interrupts 0-31 and Tegra shared-controller banks starting at 32.

Notable constraints:
- `NCOLOR` is 1; this ARM port does not need MIPS-style VCE cache coloring.
- `KMap` is fake because pages are addressed through the direct map.
- `MAXSYSARG` is 5, matching the generic Plan 9 syscall ABI expectation for this port.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/devarch.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/devarch.c

Plan 9 `#P/arch` device for Tegra-specific architecture files.

Key responsibilities:
- Maintains a small dynamic directory of architecture files with per-file read/write callbacks.
- Provides `addarchfile` for other architecture code to register files.
- Implements standard Plan 9 device operations for attach, walk, stat, open, close, read, and write.
- Registers `cputype` and `timebase` in `archinit`.
- Reports CPU type/frequency through `cputyperead`.
- Reports cycle/timebase value through `tbread`; an `nsec` reader exists but is not registered.

Dependencies and assumptions:
- Depends on Plan 9 device helpers, `cputype2name`, `cycles`, and global `m`.
- Directory capacity is fixed at `Qmax` 16 entries.

Notable risks:
- Added files cannot be removed, and duplicate names are rejected.
- `nsread` uses a fixed conversion expression and is commented out from registration.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/devarch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/devcons.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/devcons.c

Plan 9 `#c/cons` device implementation for Tegra, covering console I/O, kernel message log, panic/print paths, keyboard input staging, time files, random, reboot, swap control, and basic identity files.

Key responsibilities:
- Initializes console queues and nonblocking line queue.
- Implements kernel print paths: `print`, `iprint`, `panic`, `pprint`, `putstrn`, kmesg logging, serial/screen/kprint fanout, and panic shutdown.
- Stages interrupt-time keyboard/UART input and flushes it periodically to queues.
- Handles line editing, raw mode, echoing, and `^T` debug commands.
- Implements `#c` files including `cons`, `consctl`, `kmesg`, `kprint`, `cputime`, `drivers`, `hostowner`, `hostdomain`, `pid`, `pgrpid`, `ppid`, `random`, `reboot`, `swap`, `sysname`, `sysstat`, `time`, `bintime`, `user`, `zero`, `null`, `osversion`, and `config`.
- Implements little-endian binary time read/write conversion and time-frequency adjustment commands.
- Implements random helpers `nrand` and `rand`.

Important behavior:
- `iprint` uses a best-effort lock to avoid interleaved MP output without deadlocking when a CPU is already dying.
- `panic` disables `/dev/kprint`, prints through interrupt-safe output, optionally enters `consdebug`, flushes, delays, and exits.
- `Qreboot` accepts `halt`, `reboot`, and `panic`; `halt` calls `reboot(nil, 0, 0)`.
- `Qsysstat` write resets per-Mach counters.

Dependencies and assumptions:
- Depends on Plan 9 queue, device, tod, random, process, pager, reboot, and auth/user helpers.
- Console input is normally supplied by UART code through `kbdcr2nl` or `kbdputc`.

Notable risks:
- `kbd.istage` is a finite interrupt-time ring; overflow drops input.
- `Qkmesg` reads are intentionally unlocked and can see a slurred buffer.
- `/dev/reboot panic` deliberately faults through `*(ulong*)0=0`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/devcons.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/devether.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/devether.c

Generic Plan 9 Ethernet device (`#l`) for Tegra, bridging controller drivers into the `netif` framework.

Key responsibilities:
- Manages an array of discovered `Ether` devices and exposes them through Plan 9 channel operations.
- Delegates walk/stat/open/close/read/write to `netif` helpers.
- Provides receive fanout through `etheriq`, including multicast filtering, promiscuous listeners, bridge suppression, header-only tracing, and copy avoidance for one consumer.
- Provides transmit queueing through `etheroq`, including loopback/broadcast/promiscuous local delivery.
- Registers controller reset functions through `addethercard`.
- Parses Ethernet addresses and computes Ethernet CRC.
- Resets/probes Ethernet controllers by combining `archether`, `isaconfig`, registered card types, address overrides, interrupt hookup, and `netifinit`.
- Calls controller shutdown hooks during device shutdown.

Important behavior:
- Output queue size scales with link speed: larger for gigabit controllers.
- Control writes support `nonblocking` locally before passing unknown commands to controller-specific `ctl`.
- `etherread` lets controller `ifstat` refresh hardware counters for both `ifstats` and normal `stats`.

Dependencies and assumptions:
- Depends on `etherif.h`, `netif.h`, board `archether`, and controller drivers such as RTL8169.
- Expects controller drivers to fill callbacks such as `attach`, `transmit`, `interrupt`, `ifstat`, `promiscuous`, `multicast`, and `shutdown`.

Notable risks:
- Only `MaxEther` controllers can be registered.
- Loopback delivery calls `etheriq` at high interrupt priority.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/devether.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/devuart.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/devuart.c

Generic Plan 9 UART device (`#t`) for Tegra, implementing queue management, file namespace, control parsing, flow control, staging, and console fallbacks over physical UART drivers.

Key responsibilities:
- Discovers UARTs through registered `PhysUart` providers and builds `eiaN`, `eiaNctl`, and `eiaNstatus` directory entries.
- Enables/disables UARTs, opens/closes input/output queues, maintains a list of active UARTs, and starts a periodic service timer.
- Parses UART control commands for baud, bits, stop, parity, FIFO, modem, DTR/RTS, hangup, flush, break, queue limits, nonblocking mode, timer period, and software flow control.
- Stages output from queues into fixed buffers and calls physical `kick`.
- Stages interrupt-time input into rings and periodically moves it to queues.
- Handles XON/XOFF, CTS backoff, hangup, mouse/special UART hooks, and console `uartgetc`/`uartputc`/`uartputs`.

Important behavior:
- `uartenable` returns early if `up` is nil, allowing early boot to retry later.
- Console UARTs bind their input/output queues to `kbdq` and `serialoq` and use `kbdcr2nl`.
- `uartclock` both drains input staging and periodically kicks output to avoid stalls.

Dependencies and assumptions:
- Depends on `PhysUart` implementations, Plan 9 queues, `addclock0link`, and `netif` QID macros.
- The active UART list is protected with interrupt locks because timer callbacks can run during device operations.

Notable risks:
- UART close drains output with sleep and hangup semantics; physical drivers must implement `kick`/status correctly.
- Staging rings can overflow; `uartstageinput` records queue errors and may deassert RTS.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/devuart.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/ether8169.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/ether8169.c

Realtek RTL8110/8168/8169-family gigabit Ethernet driver adapted for Tegra/TrimSlice PCIe, with explicit cache maintenance for DMA.

Key responsibilities:
- Scans PCI Ethernet devices for supported Realtek/Corega IDs, maps BAR2 MMIO directly, wakes devices from PCI power management, validates hardware MAC version, resets the device, initializes MII, and enables bus mastering.
- Registers as `rtl8169` through `ether8169link`.
- Provides Ethernet callbacks for attach, transmit, interrupt, ifstat, promiscuous, multicast, and shutdown.
- Manages 1024-entry TX and RX descriptor rings, a 4096-block private receive pool, and a hardware tally-counter DMA block.
- Initializes receive/transmit configuration, C+ command bits, descriptor base addresses, receive maximum size, multicast hash registers, interrupt mask, and chip-version-specific magic settings.
- Runs receive and transmit kernel processes woken by interrupt status bits.
- Handles link state through `Phystatus` and MII auto-negotiation helpers.
- Maintains hardware/software statistics and exposes PHY register dumps through `ifstat`.
- Handles restart after RX FIFO overflow, descriptor unavailable, receive errors, and selected controller stalls.

Important behavior:
- Uses `allcache->wbse` before TX DMA and `allcache->invse` after RX DMA.
- RX accepts only single-descriptor packets with `Fs|Ls` and no receive error summary; CRC is stripped by subtracting four bytes.
- Multicast hashes are accumulated and never cleared on removal; PCIe variants reverse hash-register byte order.
- Attach sets `l1ptstable.word` after RTL8169 initialization so secondary CPUs can safely copy CPU0's L1 page table.
- `rtl8169interrupt` masks RX/TX causes while waking worker processes, then workers re-enable the masks.

Dependencies and assumptions:
- Depends on Plan 9 PCI helpers, `devether`, `ethermii`, cache vtables, kernel processes, and Tegra PCIe interrupt completion (`pcieintrdone`).
- Assumes 32-bit DMA addresses by writing high descriptor address words as zero.
- Assumes Realtek PHY address 1 and TrimSlice IRQ routing through `Pcieirq`.
- Does not `vmap` the MMIO BAR because the TrimSlice mapping is already usable.

Notable risks:
- Several chip setup paths use undocumented or vendor-driver-derived magic values.
- Restart is a large hammer: it drains rings briefly, resets hardware, frees RX buffers, reinitializes, and wakes workers.
- `rtl8169attach` calls `miistatus(ctlr->mii)` even if MII setup failed, relying on helper nil checks.
- RX fragmentation/oversize behavior drops or panics on unexpected descriptor lengths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/ether8169.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/etherif.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/etherif.h

Ethernet controller interface header for the Tegra Plan 9 port.

Key contents:
- Defines `MaxEther` and number of packet type slots `Ntypes`.
- Defines `struct Ether`, embedding `ISAConf` and `Netif` plus controller callbacks and hardware state.
- Declares generic Ethernet helpers: `etheriq`, `addethercard`, `ethercrc`, and `parseether`.
- Defines circular ring helper macros `NEXT` and `PREV`.

Role:
- This is the contract between `devether.c` and individual Ethernet drivers such as `ether8169.c`.
- It standardizes callback names for attach, detach, transmit, interrupt, stats, control, power, and shutdown.

Notable constraints:
- Only four Ethernet controllers are supported by the fixed `MaxEther`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/etherif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/ethermii.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/ethermii.c

Generic MII/PHY support for Ethernet drivers.

Key responsibilities:
- Probes PHY addresses using driver-supplied `mir`/`miw` operations and records discovered PHYs.
- Provides current-PHY read/write helpers `miimir` and `miimiw`.
- Resets the current PHY through BMCR reset.
- Configures auto-negotiation advertisements for 10/100, pause, and 1000BASE-T capabilities in `miiane`.
- Reads link/autonegotiation status in `miistatus`, deriving speed, duplex, receive flow control, transmit flow control, and link state.

Important behavior:
- Reads `Bmsr` twice because link status is sticky.
- 1000BASE-T status is checked before resolving 10/100 advertised common modes.
- Flow-control resolution follows advertised pause/asymmetric pause combinations only for full duplex.

Dependencies and assumptions:
- Depends on `ethermii.h` register definitions and a controller-populated `Mii` with valid callbacks.
- Allocates `MiiPhy` records dynamically as PHYs are discovered.

Notable risks:
- `miireset` does not wait for reset completion beyond a one-microsecond delay.
- If allocation fails during probe, that PHY is silently skipped.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/ethermii.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/ethermii.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/ethermii.h

MII/PHY register, bit, and data-structure header for Ethernet drivers.

Key contents:
- Defines standard MII register numbers: BMCR, BMSR, PHY IDs, AN advertisement/link partner, expansion, next-page, 1000BASE-T control/status, and extended status.
- Defines BMCR control bits, BMSR capability/status bits, advertisement bits, 1000BASE-T master/slave bits, and extended status bits.
- Defines `Mii` containing discovered PHY table, current PHY, controller pointer, and driver read/write callbacks.
- Defines `MiiPhy` containing OUI, PHY number, advertised capabilities, flow control, 1000BASE-T control, link, speed, duplex, and flow-control results.
- Declares MII helper functions.

Role:
- Shared contract between generic `ethermii.c` and hardware drivers such as RTL8169.

Notable constraints:
- Supports up to 32 PHY addresses and 32 MII registers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/ethermii.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/fns.h

Function prototype and macro header for the Tegra 2 Plan 9 kernel port.

Key contents:
- Includes generic port prototypes and declares architecture-specific cache, clock, MMU, interrupt, PCI, DMA, UART, FPU, CPU/SMP, CP15, screen, probe, reboot, and utility functions.
- Defines `intrenable`/`intrdisable` wrappers over GIC `irqenable`/`irqdisable`.
- Declares functions used by `main`, functions called from the generic port layer, and miscellaneous machine-dependent helpers.
- Defines core convenience macros: `cycles`, `waserror`, `KADDR`, `PADDR`, `MASK`, `PTR2UINT`, `UINT2PTR`, `getpgcolor`, and no-op `kmapinval`.

Role:
- This is the cross-file declaration surface for the Tegra port and the bridge between generic Plan 9 port code and machine-dependent implementations.

Notable constraints:
- `cycles(vlp)` is mapped to `lcycles()` and returns a 32-bit value stored through the pointer.
- `waserror()` directly manipulates `up->nerrlab` and `setlabel`, matching Plan 9 kernel error-stack conventions.
- `KADDR`/`PADDR` assume the port's direct physical/virtual mapping scheme.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/fns.h -->