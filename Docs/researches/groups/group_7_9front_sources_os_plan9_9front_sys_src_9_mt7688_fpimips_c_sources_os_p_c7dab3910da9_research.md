# Group Research: group_7_9front_sources_os_plan9_9front_sys_src_9_mt7688_fpimips_c_sources_os_p_c7dab3910da9

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/fpimips.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/fpimips.c

This file implements software MIPS floating-point emulation for the MT7688 port, which targets a MIPS 24K/24KE-class system where hardware FPU may be absent or disabled. It decodes COP1 instructions, emulates floating arithmetic through the common `fpi` internal representation, handles FP loads/stores, FP register/control-register moves, conversions, comparisons, and FP conditional branches.

Important structures are `Instr`, which captures decoded COP1 fields plus converted operands and user state, `FP1`/`FP2` unary/binary operation tables, and `FPcvt` conversion handlers. The emulator preserves MIPS raw FP register semantics: 32 raw 32-bit FP registers, paired even/odd registers for doubles, with explicit attention to word ordering on this little-endian variant.

The central public entry is `fpuemu(Ureg*)`, called from `trap.c` on coprocessor-unusable traps. It validates the faulting PC, handles branch-delay slots, initializes emulated FP state via `fpinit`, repeatedly emulates adjacent FP instructions and NOPs, updates `Ureg.pc`, and posts a note on failure. `fpwatch(Ureg*)` completes the watchpoint-based path used when an FP branch’s delay-slot instruction must run in user mode.

Instruction support includes `LWC1`, `LDC1`, `SWC1`, `SDC1`, `MFC1`, `MTC1`, `CFC1`, `CTC1`, arithmetic add/sub/mul/div, `MOV`, `ABS`, `NEG`, selected rounding/conversion operations, comparisons, and FP branches. Missing operations call `unimp`, generating a user-visible debug note.

The file is not filesystem code, but it is part of the CPU exception substrate that lets user processes execute reliably. That matters to filesystem workloads because page faults, syscalls, and user notes share the same trap/ureg machinery; bad FP emulation can corrupt user register state or trap recovery in filesystem servers.

Notable risks: numeric exception/status behavior is partial, some 64-bit `DMTC1`/`DMFC1` paths print warnings about possible word ordering, and branch-delay-slot execution uses a process FP scratch area plus hardware watchpoints, so correctness depends on the MIPS watch register and ASID behavior matching `mmu.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/fpimips.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/i2c7688.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/i2c7688.c

This is the MT7688 I2C controller driver. It defines register offsets under `I2CBASE`, small command bitfields for the controller state machine, and an `I2Cbus` backend registered by `i2c7688link`.

The controller state is minimal: `Ctlr` stores only the computed clock divider. `init` computes a divider from a 40 MHz base clock and the requested bus speed, then `reset` programs `SM0CTL0` and `SM0CFG2`.

The transaction path is `io(I2Cdev*, uchar*, int olen, int ilen)`. It issues a start condition, writes outgoing bytes in up-to-8-byte chunks through two data registers, checks controller ACK bits, then reads incoming bytes in similar chunks using ACK or NACK commands depending on whether the chunk is final. `i2cbusy`, `i2cstart`, `i2cack`, and `i2cstop` implement timeout, command launch, ACK validation, and bus stop.

The file has no direct filesystem implementation, but it registers a kernel I2C bus that devices may expose through Plan 9 device files or use for board management. Its behavior affects boot-time hardware discovery and embedded peripheral support.

Notable risks: timeout handling returns generic failure and may leave only a stop command as recovery; the clock-divider formula is suspiciously written as `40000000 / (bus->speed - 1)` rather than `(40000000 / bus->speed) - 1`; debug prints use non-ASCII naming in source but runtime behavior is standard C.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/i2c7688.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/init9.s -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/init9.s

This short MIPS assembly file is the user init bootstrap stub. `_main` sets `R30` to `setR30(SB)`, passes the string `boot` and a frame pointer-derived argument pointer on the stack, then jumps to `startboot(SB)`.

It is part of the transition from the kernel-created initial user process to `/boot`. It does not implement filesystem logic, but it is the first user-mode code path that ultimately opens the root and boot namespace.

The file is intentionally tiny and depends on the Plan 9/MIPS calling convention and the `boot` symbol being provided elsewhere in the init code build.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/init9.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/io.h -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/io.h

This header defines MT7688 memory-mapped I/O addresses and hardware register constants. `IO(t,x)` maps physical peripheral addresses through uncached `KSEG1`.

It covers system control, timers, memory counter, GPIO, I2C, I2S, SPI, UARTs, DMA, AES, Ethernet, switch, PCI, Wi-Fi, and USB base addresses. It also defines UART register offsets, system reset register offsets, CPU interrupt numbers, secondary SoC interrupt-controller interrupt IDs, interrupt-controller register offsets, timer/global timer bits, MCNT registers, PDMA Ethernet ring registers, switch DMA counters, and 10/100 switch register offsets.

This header is a hardware map shared by several MT7688 drivers in this group: `irq.c`, `i2c7688.c`, `uarti8250.c`, and likely Ethernet/USB/PCI code elsewhere. It is foundational rather than filesystem-specific, but block/network/filesystem availability on embedded systems depends on these low-level I/O definitions being correct.

Notable risks: comments mark some interrupt IDs as uncertain; `IRQshift` is defined with a trailing semicolon; the header encodes board/SoC assumptions directly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/irq.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/irq.c

This file implements interrupt routing for the MT7688 port. It maps Plan 9 IRQ numbers to MT7688 secondary interrupt-controller lines with `irq2inc` and back with `inc2irq`.

`intrinit` masks all secondary interrupts and registers `incintr` on CPU interrupt `IRQlow`. `intrenable` installs one or more handlers per IRQ, enables CPU interrupt bits directly for CPU-local IRQs, and programs `FIQ_SEL` plus `IRQ_MASK_SET` for SoC-controller IRQs. `intrdisable` masks the reverse path.

`intr(Ureg*)` is called by trap handling for CPU interrupts. It accounts for clock interrupts on `INTR7`, dispatches CPU-level handler chains for `INTR2` through `INTR6`, and reports unhandled pending bits. `incintr` reads `IRQ_STAT` or `FIQ_STAT`, walks secondary interrupt bits, invokes registered handlers, and reports unhandled secondary interrupts. `intrclear` writes `IRQ_EOI`.

Filesystem relevance is indirect: this is the dispatch path for UART, Ethernet, USB, storage, and timer interrupt handlers. A storage or network filesystem workload depends on reliable interrupt masking, acknowledgment, and handler chaining here.

Notable risks: high-priority `IRQhigh` registration is commented out; handler arrays are indexed by assumed IRQ layout; unhandled secondary interrupts are printed and delayed but not otherwise recovered.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/irq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/l.s -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/l.s

This is the main MIPS assembly support file for the MT7688 kernel. It includes MIPS 24K macros and implements boot entry, exception vectors, interrupt priority manipulation, process context helpers, TLB helpers, cache flushing, atomic primitives, CP0 accessors, and the low-level trap save/restore path.

`start` disables interrupts, verifies a sanity word, clears compare/cause state, disables watchdog/reset behavior, configures cache mode, initializes `Mach` and BSS, initializes registers, sets `up` nil, and calls `main`. `touser` sets EPC/status and executes `ERET` into user mode.

The exception path includes `utlbmiss`, a fast software-TLB lookup using the same hash as `mmu.c`, fallback to `gevector`, full `saveregs`, dispatch to `trap` or `syscall`, and `restregs`/`forkret` return. The assembly Ureg layout is explicitly documented in comments and must match `ureg.h`.

TLB functions include `getwired`, `setwired`, `getrandom`, `getpagemask`, `setpagemask`, `puttlbx`, `gettlbx`, `gettlbp`, `gettlbvirt`, `tlbvirt`, and `stlbhash`. Cache functions include `cleancache`, `icflush`, and `dcflush`. Atomic operations are `tas` and `cmpswap` using LL/SC. CP0 accessors include `prid`, count/compare, status/cause/config, watch registers, and debug/config selector reads.

Filesystem relevance is core infrastructure: page faults, copy-on-write, user/kernel transitions, interrupt handling, and cache/TLB consistency all depend on this file. Filesystem servers and page-cache operations rely on correct Ureg save/restore and MMU refill behavior.

Notable risks: several debug or degenerate FPU routines are stubs; early boot and vector copying are highly address-layout sensitive; the fast UTLB refill path must remain exactly consistent with `mmu.c`’s `Softtlb` layout and `stlbhash`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/main.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/main.c

This is the MT7688 kernel bootstrap and machine initialization file. It declares global `Conf`, `machaddr`, initial FP save state, and the per-machine software TLB array.

`main` initializes console UART, formatting, memory configuration, `Mach`, active CPU state, kmap, allocators, timers, plan9.ini, interrupts, CPU identification, page mask, TLB, pages, processes, segments, device links, channel devices, the initial user process, and finally enters the scheduler.

`machinit` sets up `MACHP(0)`, clears `Mach`, initializes CPU speed/hz guesses, binds `m->stb` to the software TLB, installs exception handler pointers at `SPBADDR`, copies vector stubs into `KSEG0` vector addresses, clears BEV, disables CU1/FPU state, and calls `clockinit`.

`init0` initializes channel devices and environment variables, starts the alarm kproc, builds the initial `/boot` user stack, and calls `touser`. `confinit` partitions fixed 128 MB memory between kernel and user pages and sizes process/image/swap pools. `exit` clears secrets on CPU 0 and halts.

Filesystem relevance is high: this file decides memory pool sizing, initializes the page allocator, channels, device table, and first user process that mounts/boots the namespace.

Notable risks: CPU/memory values are hardcoded for the target board; `fmtinit` is unused; some debug checks remain; `confinit` computes kernel pages before setting `conf.nproc`, which mirrors old Plan 9 patterns but is easy to misread.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/mem.h -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/mem.h

This header defines MT7688/MIPS memory layout, CPU register constants, page-table bits, TLB parameters, kernel/user address ranges, cache sizes, and trap cause values.

Key platform constants include `PHYSCONS`, `CONFADDR`, fixed `MEMSIZE` of 128 MB, 4K default pages with optional 16K pages, `KSTACK`, `MACHSIZE`, cache line and cache sizes, MIPS CP0 register numbers, status/cause bits, exception codes, direct-map segments, `MACHADDR`, `KMAPADDR`, and `SPBADDR`.

MMU definitions include MIPS page-mask encodings, `KUSEG/KSEG0/KSEG1/KSEG2/KSEG3`, PTE valid/write/cache/global bits, write-through default caching due to MIPS 24K erratum, ASID/TLB PID macros, hardware TLB size, soft TLB size, kmap size, and user stack/text/kernel text addresses.

Filesystem relevance is foundational: page size, cache policy, user stack limits, kmap layout, and copy-on-write PTE bits affect every filesystem server, page-cache path, and kernel/user copy operation.

Notable risks: the memory map is board-specific; write-back caching is disabled by default for erratum reasons; page size changes have comments warning 16K pages work poorly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/mips24k.s -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/mips24k.s

This assembly include defines MIPS 24K/MIPS32r2 instruction and macro helpers. It supplies register aliases, `NOOP`, `RETURN`, constant construction, `GETMACH`, polled UART `PUTC`, interrupt enable/disable encodings, `EHB`, `SYNC`, `WAIT`, hazard-barrier return macros, LL/SC, CP0 selected register access, RDHWR, and cache operation encodings.

It is included by `l.s` and keeps CPU-specific instruction encodings out of the main assembly body. The macros are important for exception return, cache maintenance, atomic operations, and hazard-safe CP0 updates.

Filesystem relevance is indirect but critical through atomic locking, cache/TLB correctness, and user/kernel exception return stability.

Notable risks: raw `WORD` encodings are architecture-specific and assembler-sensitive; cache op macros rely on Plan 9 assembler syntax tricks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/mips24k.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/mmu.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/mmu.c

This file implements MT7688 MIPS MMU management: hardware TLB initialization, kernel temporary mappings, per-process ASID allocation, software TLB population, TLB purging, and instruction-cache flushing after text mappings.

`tlbinit` invalidates all hardware TLB entries. `kmapinit`, `kmap`, `kunmap`, `kfault`, and `kmapinval` implement the KSEG3-based kmap mechanism for mapping physical pages with cache-color-aware virtual addresses. `putktlb` places kmap entries into hardware TLB entries, initially preserving a small wired range until startup completes.

For user mappings, `mmuswitch` assigns or reuses per-process ASIDs, writes TLB entry 0 to set current PID, and handles `newtlb`. `putmmu` writes a `Softtlb` entry, installs a matching hardware TLB entry, and flushes I-cache for text pages when needed. `purgetlb` invalidates stale ASIDs in process tables, the software TLB, and hardware TLB entries.

Filesystem relevance is direct to page-cache and memory-mapped file behavior. `faultmips`/`fault` ultimately call into this code to install translations for executable text, data, stack, and COW pages; `kmap` is used for kernel access to physical pages during I/O and filesystem operations.

Notable risks: the fast assembly TLB refill path depends on `Softtlb` layout/hash matching this C code; kmap exhaustion retries with diagnostics; cache coloring is manually encoded through `PIDX`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/syscall.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/syscall.c

This file provides MT7688 syscall, note, fork, and exec register handling. `syscall(Ureg*)` is called directly from assembly for system-call traps, enters kernel context, dispatches `dosyscall` using `r1` as syscall number and user stack as arguments, advances PC on success, delivers notifications, handles delayed scheduling, exits kernel context, and restores `EXL` in status.

It also implements FP note-state markers `fpunotify` and `fpunoted`, while `notefpsave` returns nil for this emulated/stubbed FP setup. `notify` builds a user stack frame containing a copied `Ureg` and error string, then redirects PC to the user notify handler. `noted` restores registers and supports `NCONT`, `NRSTR`, and `NSAVE`.

`forkchild` creates a child kernel return frame so the child resumes from `forkret` with return value 0. `execregs` sets initial user stack and PC for `exec`, with PC set to `entry - 4` because the syscall return path advances it.

Filesystem relevance is direct: all filesystem syscalls on this port traverse this file, including open/read/write/mount/stat operations handled by the portable syscall layer.

Notable risks: syscall argument ABI is MIPS/Plan 9 specific; `execregs` relies on the syscall path’s PC advance; note-frame validation is critical for user-controlled register restoration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/trap.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/trap.c

This file implements MT7688 trap, exception, and fault dispatch. It maps MIPS exception codes to names, has register-name metadata for dumps, diagnoses virtual coherence exceptions, and routes interrupts, TLB misses, watchpoints, coprocessor-unusable traps, and fatal kernel faults.

`trap(Ureg*)` enters kernel context, checks TLB shutdown, decodes the exception code, dispatches `CINT` through `intr`, TLB miss/modification through `kfault` or `faultmips`, watch exceptions through `fpwatch`, and COP1 unusable traps through `fpuemu`. User-mode unhandled traps become posted notes; kernel-mode unhandled traps dump registers/stack and exit.

After successful FP emulation it checks emulated FCR31 exception state and posts an FP note if enabled exceptions are pending. On user return it calls `donotify`, adjusts FP/user state comments, and exits kernel context.

Debug helpers include `fpexcname`, `callwithureg`, `dumpstack`, and `dumpregs`.

Filesystem relevance is direct through page faults and syscall-adjacent user exception handling. Any filesystem server faulting on mapped memory, copying buffers, or receiving notes relies on this path.

Notable risks: FP hardware exception path panics because there is no FPU; VCE handling is diagnostic-heavy; kernel faults in KSEG3 are treated as kmap faults and resolved through `kfault`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/uarti8250.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/uarti8250.c

This is the MT7688 8250-like UART driver adapted for memory-mapped 32-bit UART registers. It defines UART register and bit constants, a `Ctlr` with memory-mapped `io`, IRQ, sticky register cache, FIFO state, and one console UART named `uartL`.

The `PhysUart i8250physuart` methods implement status reporting, FIFO control, DTR/RTS/modem control, parity/stop/bits configuration, fixed baud reporting, break, transmit kick, interrupt handling, enable/disable, polling getc/putc, and console init. `uartconsinit` chooses this UART as `consuart` and configures `115200 8N1`.

`i8250interrupt` drains modem, TX-empty, RX-data, line-status, and timeout interrupt causes, updates UART error counters, sends received bytes into the generic UART layer, and restarts transmit output.

Filesystem relevance is indirect but important for console I/O, diagnostics, boot interaction, and serial-backed device files. Console reliability affects debugging filesystem boot and namespace failures.

Notable risks: baud programming is compiled out, so actual hardware speed is assumed preconfigured; only one UART instance is registered; register access uses word indexing through `u32int*` rather than byte I/O.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/uarti8250.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/clock.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mtx/clock.c

This PowerPC MTX file implements the decrementer-based system clock and delay loops. `clockinit` hardcodes CPU and bus frequency, derives decrementer/timebase frequency, calibrates `m->loopconst`, computes `clkreload`, and programs DEC.

`clockintr` handles decrementer interrupts, compensates for late interrupts, updates ticks if needed, reloads DEC, and calls `timerintr`. `delay` and `microdelay` busy-wait using the calibrated loop constant. `fastticks`, `µs`, and `perfticks` expose low-overhead tick values.

Filesystem relevance is indirect: scheduler ticks, timers, sleeps, I/O timeouts, and cache/page daemon timing depend on this code.

Notable risks: CPU/bus frequencies are hardcoded; `timerset` is empty, so high-resolution timer support is absent.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/cycintr.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mtx/cycintr.c

This file is a stub timer interface for MTX. `havetimer` returns 0, and `timeradd`, `timerdel`, and `clockintrsched` are empty.

It signals that this platform does not provide the cyclic timer facility expected by some Plan 9 code paths. Timer functionality instead comes from the basic decrementer clock in `clock.c`.

Filesystem relevance is low, but lack of high-resolution timers can affect timeout granularity for drivers and servers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/cycintr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/9/mtx/dat.h

This is the MTX platform data-structure header. It defines forward declarations, syscall argument count, executable magic, machine-dependent `Label`, `FPsave`, `PFPU`, FP state enum, `Confmem`, `Conf`, per-process `PMMU`, fake `KMap` macros, `Mach`, active-machine state, and `ISAConf`.

`FPsave` must match assembly `fpsave`/`fprestore`. `Mach` has fields known to assembly at the front: `machno`, `splpc`, and current `Proc*`; later fields include page-table base, MMU PID/color state, CPU timing, and kernel stack.

Filesystem relevance is structural: `Conf` sizes process/page/image/swap resources, `PMMU` drives per-process address-space IDs, and fake kmap determines how physical pages are addressed by kernel code.

Notable risks: fake kmap assumes direct mapping via `KZERO`; `Mach` layout is coupled to `l.s`; `NCOLOR` is fixed to 1, simplifying cache-color behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/devarch.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mtx/devarch.c

This file implements the MTX `#P/arch` device. It exposes raw I/O-port access files `iob`, `iow`, and `iol`, supports dynamic arch-file registration through `addarchfile`, initializes I/O allocation tracking, and provides PCMCIA special-hook wrappers.

`archread` and `archwrite` validate I/O port ranges through `checkport`, then perform byte/word/long reads and writes using `inb/ins/inl` and `outb/outs/outl`. Standard VGA ports are allowed; otherwise the port range must be allocated or unused as permitted by the I/O map.

Filesystem relevance is direct as a device file implementation. It adds namespace-visible files that privileged users or drivers can use for low-level hardware access.

Notable risks: raw port access is powerful and permission-sensitive; `archopen` uses the full fixed `archdir` array length rather than `narchdir` in `devopen`, though directory reads use dynamic count.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/devarch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/devrtc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mtx/devrtc.c

This file implements the MTX RTC/NVRAM device for an M48T59/559 Timekeeper. It registers device `#r` with files `rtc` and `nvram`.

The device operations support attach, walk, stat, open, read, and write. `rtc` reads/writes seconds since epoch; writes parse a numeric time and convert to BCD RTC fields. `nvram` reads/writes byte ranges in the Timekeeper NVRAM and calls a placeholder checksum routine. Access is restricted: RTC writes require `eve`, and NVRAM requires `eve` plus `cpuserver`.

Hardware access uses address strobe ports `STB0/STB1` and `Data`, with `nvget`/`nvput`. `rtctime`, `setrtc`, `rtc2sec`, and `sec2rtc` handle BCD and Unix-time conversion. `watchreset` programs the watchdog to reset and spins.

Filesystem relevance is direct: this is a Plan 9 device filesystem node and participates in timekeeping, which affects file timestamps and system logs.

Notable risks: `nvcksum` is empty; RTC years are mapped 70-99 to 1970-1999 and below 70 to 2000-2069; direct NVRAM writes can alter firmware/platform state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/devrtc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/ether2114x.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mtx/ether2114x.c

This is a full PCI Ethernet driver for DEC 2114x/Tulip-family controllers and related PNIC variants. It handles PCI discovery, SROM parsing, MII management, media selection, descriptor-ring setup, transmit, receive, interrupts, statistics, and generic Plan 9 Ethernet registration.

The main state is `Ctlr`, containing PCI/device identity, SROM/media/PHY state, CSR6 mode bits, interrupt mask, receive and transmit descriptor rings, locks, queued setup packet, link speed, and detailed error counters. `Des` models RX/TX descriptors with status/control/DMA address/block pointer.

Driver registration is `ether2114xlink`, adding card names `21140` and `2114x`. `dec2114xpci` scans PCI devices, matches supported IDs, allocates I/O space, resets the device, reads SROM, and links controllers. `reset(Ether*)` binds a controller to an `Ether`, handles MAC/media options, sets DMA bus mastering, initializes rings, installs callbacks, and enables interrupts.

RX/TX operation uses `ctlrinit`, `txstart`, `transmit`, and `interrupt`. The interrupt handler acknowledges CSR5 status, processes receive descriptors into `etheriq`, handles TX completion/errors, raises thresholds on underflow, and tops up TX descriptors.

Filesystem relevance is indirect but important: Plan 9 network stacks and network filesystems depend on this driver for connectivity; the generic `etherif` exports network interfaces as device files.

Notable risks: one line hardcodes `ether->irq = 2` with an explicit complaint comment instead of using PCI interrupt line; media/SROM decoding is partial; some card-specific fake leaves are embedded; DMA coherency depends on `coherence()` and `PCIWADDR`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/ether2114x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/9/mtx/fns.h

This header declares MTX platform functions and macros used across C and assembly-backed code. It includes portable function declarations, MMU/cache helpers, interrupt controller APIs, I/O port functions, PCI config accessors, process FP hooks, Raven/MPIC functions, timer stubs, trap entry, TLB flushes, and address translation macros.

Important macros include `coherence()` as `eieio()`, no-op `cycles`, no-op `idlehands`, no-op `kmapinval`, `userureg`, `KADDR`, and `PADDR`.

Filesystem relevance is dependency-level: most platform source files include this header, and page faults, device files, PCI drivers, and console/network drivers rely on these declarations.

Notable risks: several operations are macros or stubs on this port, so code shared from other architectures may assume stronger behavior than MTX provides.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/i8259.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mtx/i8259.c

This file implements the legacy dual 8259 PIC support used behind the MTX MPIC mixed-mode interrupt path. It initializes master/slave PICs, manages masks, detects level-triggered ELCR support, enables/disables IRQs, acknowledges interrupts, and provides ISR/EOI callbacks for `Vctl`.

`i8259init` allocates controller I/O ports, programs ICW1-4, unmasks the cascade, configures OCW3 status behavior, and probes ELCR. `i8259enable` unmasks an IRQ and sets the handler’s `isr` or `eoi` depending on edge/level triggering. `i8259intack` performs interrupt acknowledge and maps IRQs to `VectorPIC` range.

Filesystem relevance is indirect: serial, ATA, and other legacy device interrupts route through this path, affecting storage and console device files.

Notable risks: shared non-level IRQs are rejected; ELCR detection is chipset-sensitive; this PIC is nested under MPIC vector 0 in `trap.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/i8259.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/inb.s -->
# File Research: sources/os/plan9/9front/sys/src/9/mtx/inb.s

This PowerPC assembly file implements x86-style I/O port accessors over the MTX memory-mapped I/O window at `IOMEM`. It provides byte, short, and long input/output operations plus string/block variants: `inb`, `insb`, `outb`, `outsb`, `ins`, `inss`, `outs`, `outss`, `inl`, `insl`, `outl`, and `outsl`.

The routines OR the port number with `IOMEM`, use `EIEIO` barriers around device accesses, and use byte-reversed load/store instructions for 16/32-bit scalar operations where needed.

Filesystem relevance is through device support: RTC, UART, PIC, PCI config, and raw arch device files all depend on these accessors.

Notable risks: byte ordering differs between scalar and string operations; correctness is tied to Raven/MTX I/O-window mapping.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/inb.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/io.h -->
# File Research: sources/os/plan9/9front/sys/src/9/mtx/io.h

This header defines MTX interrupt numbers, vector ranges, `Vctl`, EISA constants, PCI DMA address mapping, and `BUSUNKNOWN`.

`Vctl` is the per-interrupt handler record used by the trap/interrupt code. It stores next-handler chain, driver name, IRQ, TBDF, optional ISR/EOI callbacks, function pointer, and argument.

`PCIWADDR(va)` maps a kernel virtual address to a PCI-window bus address via `PADDR(va)+PCIWINDOW`, which is used by the Ethernet driver’s DMA descriptors.

Filesystem relevance is mainly device/driver infrastructure: interrupt dispatch and DMA address translation affect block, serial, and network device files.

Notable risks: `PCIWADDR` assumes the Raven PCI window configuration from `raven.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/l.s -->
# File Research: sources/os/plan9/9front/sys/src/9/mtx/l.s

This is the MTX PowerPC low-level assembly file. It implements boot entry, initial BAT/MMU setup, FP initialization, interrupt priority controls, context-label operations, user entry, cache flushes, atomic operations, SPR accessors, TLB flushes, trap vector save/restore, and FP save/restore.

`start` configures MSR, clears interrupt/prefix state, sets early SB, calls `mmuinit0`, receives `memsize` from the ROM/debugger, initializes FP constants, sets up `mach0`, and calls `main`. `mmuinit0` invalidates TLBs, programs BATs for direct kernel mappings and I/O, enables instruction/data MMU, and returns in virtual mode.

The trap path is `trapvec` -> `saveureg` -> C `trap` -> `restoreureg`. It handles user vs kernel stack selection while traps arrive with MMU disabled, saves registers into a `Ureg`, re-enables MMU, and restores state with `RFI`. `forkret` branches into `restoreureg`.

The file also provides `fpsave`/`fprestore`, which must match `FPsave` in `dat.h`, and low-level hardware helpers such as `getdec`, `putdec`, `getdar`, `getdsisr`, `putsdr1`, `putsr`, `gethid0`, `puthid0`, `eieio`, and `sync`.

Filesystem relevance is core OS substrate: user/kernel transitions, page faults, scheduler context, and cache/TLB behavior all affect file servers and memory-mapped I/O.

Notable risks: trap entry depends on precise physical/virtual address transitions; `Mach` and `Ureg` offsets are assembly-coupled; BAT mapping assumptions are platform-specific.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/main.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mtx/main.c

This is MTX PowerPC kernel bootstrap and configuration code. `main` clears BSS, initializes `Mach`, I/O, console, formatting, memory configuration, allocator, Raven bridge, traps, print, CPU ID, MMU, interrupts, clock, processes, segments, timers, links, channel devices, pages, FP initial state, user process, and scheduler.

`machinit` initializes CPU type, a temporary delay constant, enables caches, and marks CPU 0 active. `cpuidprint` identifies the 604e. A small static `plan9ini` provides `console=0` and `ether0=type=2114x`, consumed by `getconf`.

`init0` initializes channel devices, sets environment variables, starts `alarm` and `mmusweep` kprocs, and enters user mode. `confinit` sizes process, page, image, swap, interrupt allocation, and memory pools based on ROM-provided `memsize`, CPU-server status, and optional `*kernelpercent`.

It also implements FP process setup/save hooks, ISA config parsing, and a no-watchpoint implementation.

Filesystem relevance is high: this file initializes the device namespace, page allocator, image cache sizing, COW mode, and initial user process.

Notable risks: configuration is hardcoded rather than parsed from a full plan9.ini source; reboot is unimplemented; exit uses watchdog reset.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/mem.h -->
# File Research: sources/os/plan9/9front/sys/src/9/mtx/mem.h

This header defines MTX PowerPC memory, page, cache, SPR, exception, MMU, and platform address constants.

It sets 4K pages, 16-byte cache lines, 4K kernel stacks, PowerPC SPR numbers, BAT register numbers, 604e-specific SPRs, MSR bit encodings, exception vector codes, magic registers (`MACH` and `USER`), hashed page-table constants, PTE encodings, user/kernel virtual layout, PCI memory windows, I/O memory window, Raven/Falcon/flash addresses, and page-color macros.

Filesystem relevance is foundational: page size, user stack/text addresses, PTE permissions/cache bits, and PCI/I/O address ranges drive memory-mapped file handling, page faults, DMA buffers, and device access.

Notable risks: `isphys` uses `KZERO` direct-map convention; PCI/I/O window constants must match `raven.c`; cache coloring is disabled via `getpgcolor(a) 0`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/mmu.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mtx/mmu.c

This file implements the MTX PowerPC hashed page-table MMU management. It uses one page table per processor and distinguishes processes through VSIDs in segment registers.

`mmuinit` sizes the hash table heuristically from physical memory, allocates it aligned to its size, programs `SDR1`, and initializes MMU PID/color reclamation state. `mmuswitch` assigns or reuses a process MMU PID, writes segment registers for eight user segments, and clears them for kernel processes. `newmmupid` allocates a 21-bit PID with high bits used for a color-based reclamation algorithm.

`mmusweep` is a background kproc that sleeps until allocation reaches a trigger color, clears process PIDs with the sweep color, removes corresponding PTEs from the hash table, flushes all TLBs, and advances colors.

`putmmu` installs a mapping into the hashed page table, choosing a slot in the 8-entry PTE group or round-robin replacement, flushes the relevant TLB entry, and flushes data/instruction caches for executable text pages.

Filesystem relevance is direct: memory faults, COW pages, executable images, and memory-mapped file data depend on this mapping path.

Notable risks: the code is explicitly not multiprocessor-ready; when PID allocation runs out, fault/putmmu loops by scheduling until `mmusweep` catches up; hash replacement is simple and may evict within a PTE group.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/pcimtx.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mtx/pcimtx.c

This file implements PCI configuration-space access and bus scanning setup for MTX. It detects PCI configuration mechanism 1 or 2, sets maximum bus/device limits from configuration if present, scans buses with portable PCI helpers, resets CardBus bridges found on bus 0, computes and applies PCI bus resource mappings, and exposes `pcimtxlink`.

`pcicfgrw8`, `pcicfgrw16`, and `pcicfgrw32` implement read/write access for both PCI config mechanisms using `0xCF8/0xCFC` or mode-2 ports.

Filesystem relevance is indirect through PCI storage, network, and other device drivers. The Ethernet driver in this group depends on PCI discovery and config access here.

Notable risks: PCI mapping starts with fixed `ioa=0x1000` and `mema=0`; mode-2 support is retained despite being deprecated; behavior depends on portable PCI helpers outside this file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/pcimtx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/raven.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mtx/raven.c

This file initializes the Motorola Raven PCI host bridge and MPIC interrupt controller for MTX. It defines a memory layout for Raven registers, configures address maps, swaps MPIC register endianness, and provides MPIC enable/disable/ack/eoi functions.

`raveninit` validates Raven vendor/device IDs, sets up four address windows for PCI memory, compatibility kernel/I/O mappings, and I/O slot 3, finds Raven’s PCI config device, computes the MPIC base, masks and routes 16 MPIC vectors to CPU 0, sets CPU task priority, and enables mixed mode so both 8259 and Raven interrupts are available.

`mpicenable`, `mpicdisable`, `mpicintack`, and `mpiceoi` are used by `trap.c` to route PCI and legacy interrupts.

Filesystem relevance is device infrastructure: PCI network/storage interrupt delivery and DMA windows rely on Raven setup.

Notable risks: address map assumptions must match `mem.h` and `PCIWADDR`; MPIC register access requires byte swapping; only 16 MPIC vectors are initialized.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/raven.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/trap.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mtx/trap.c

This file implements MTX PowerPC trap, interrupt, fault, syscall, note, register, and debug support. It also owns the platform interrupt handler registry and hardware interrupt enabling/disabling logic across MPIC and 8259.

`hwintrinit` initializes the 8259 and routes it through MPIC vector 0. `intrenable` allocates `Vctl`, enables the hardware vector via MPIC or PIC, and chains handlers; `intrdisable` removes matching handlers and disables hardware when no handlers remain. `intr` acknowledges MPIC, handles 8259 cascades, invokes registered handlers, and runs EOI callbacks.

`trap` decodes PowerPC exception vectors. It handles external interrupts, decrementer interrupts, syscalls, floating-point unavailable traps, instruction/data faults, program exceptions, and default user/kernel traps. User faults become notes or call `faultpower`; kernel faults dump registers and panic.

The file also installs exception vectors with `trapinit`/`sethvec`, implements stack/register dumping, process child setup, `evenaddr`, `execregs`, `forkchild`, user PC helpers, register setting, `syscall`, `notify`, and `noted`.

Filesystem relevance is very high: syscalls, page faults, user notes, interrupts, and device completions all pass through this file.

Notable risks: syscall is implemented in C within this trap file rather than a separate assembly entry; FP state checks include debug prints; interrupt vector chaining requires compatible ISR/EOI callbacks for shared vectors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/uarti8250.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mtx/uarti8250.c

This is the MTX 8250-compatible serial driver for COM1/COM2 using I/O-port access. It defines two controllers at `0x3F8` and `0x2F8`, IRQs 4 and 3, and a 1.8432 MHz UART clock.

The `PhysUart` methods implement status, FIFO control, DTR/RTS/modem control, parity/stop/bits, baud divisor programming, break, transmit kick, interrupt service, enable/disable, polling getc/putc, and console selection. `i8250console` reads `console` from config, configures default `9600 8N1`, applies any suffix command, enables polling, and marks the chosen UART as console.

`i8250interrupt` handles modem status, TX empty, RX data, and timeout interrupts. It updates UART error counters and passes received bytes to the generic UART layer.

Filesystem relevance is console and serial device support. Serial devices are exposed through Plan 9 device files and are important for boot/debug access.

Notable risks: FIFO detection logic appears inverted or at least old-style (`if(!(Iir & Ife)) ctlr->fifo = 1`); disable does not unregister interrupt once enabled; console speed defaults to 9600 unless config overrides it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mtx/uarti8250.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/arch.c -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/arch.c

This ARM OMAP architecture helper file contains miscellaneous process/register support routines. It is explicitly described as a temporary dumping ground for architecture-dependent pieces.

It implements `setkernur`, `evenaddr`, `userpc`, `setregisters`, `kprocchild`, `dbgpc`, FP process hooks (`procsetup`, `procfork`, `procsave`, `procrestore`), `userureg`, and a simple `cas32` using `splhi` rather than hardware atomic instructions.

Filesystem relevance is through generic kernel support: `evenaddr` is called from syscall/file code for alignment checks, `setregisters` affects `/proc` register writes, and process setup/save/restore affects filesystem server process scheduling.

Notable risks: `cas32` is only interrupt-safe on the local CPU and not a scalable SMP atomic primitive; a TODO notes VFPv3 state is not saved/restored with newer registers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/arch.c -->