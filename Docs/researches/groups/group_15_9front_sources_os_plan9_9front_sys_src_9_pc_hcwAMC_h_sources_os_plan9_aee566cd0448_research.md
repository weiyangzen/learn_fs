# Group Research: group_15_9front_sources_os_plan9_9front_sys_src_9_pc_hcwAMC_h_sources_os_plan9_aee566cd0448

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/hcwAMC.h -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/hcwAMC.h

## Purpose
Defines a single static byte-array payload, `hcwAMC[]`, used as embedded firmware/microcode data by the PC TV driver path.

## Key Elements
The file is a large `static uchar hcwAMC[] = { ... };` initializer containing 2027 lines of hexadecimal byte data and no functions, macros, comments, or type declarations. A repository reference search shows `devtv.c` includes this header and passes `hcwAMC` plus `sizeof hcwAMC` to `kfirloadu(...)`, so the payload is loaded into the TV/KFir-related device path at runtime.

## Dependencies
Depends on the includer already defining `uchar`; it is meant to be included from C source rather than compiled independently.

## Behavior/Risks
This is opaque device data, not executable C logic. Review risk is mostly provenance and correctness of the blob: corruption, truncation, or unsigned-byte type changes would affect device initialization. Because it is `static`, each includer would get a private copy, but current use appears to be a direct include by `devtv.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/hcwAMC.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/hpet.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/hpet.c

## Purpose
Implements HPET probing, CPU-frequency calibration, and monotonic fast-clock reads for the 9front PC kernel.

## Key Elements
`hpetprobe()` maps the HPET physical address, validates the period register, computes `hpet.freq` from femtoseconds-per-tick, and prints the discovered rate. `hpetinit()` starts HPET counting and uses `hpetcpufreq()` to calibrate `m->cpuhz`, `m->cpumhz`, `m->cyclefreq`, `m->delaylcycles`, and `m->loopconst`; secondary CPUs copy CPU timing values from CPU 0. `hpetread()` returns extended ticks by accumulating the 32-bit low counter into `hpet.last`.

## Dependencies
Uses kernel MMIO mapping (`vmap`), low-level cycle reading (`cycles`), delay calibration (`delayloop`), per-Mach CPU state, locks, and constants from `mem.h`/`io.h`.

## Behavior/Risks
The HPET is used for timing measurement, not interrupt generation; LAPIC/PIT paths provide interrupts elsewhere. Counter extension assumes calls occur often enough and under lock to interpret 32-bit wrap correctly. Invalid HPET periods return failure from probe.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/hpet.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/i8253.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/i8253.c

## Purpose
Implements the legacy Intel 8253/8254 PIT clock source and fallback CPU-frequency calibration.

## Key Elements
Defines PIT I/O ports, mode commands, channel-2 speaker-control bits, frequency constants, and timing bounds. `i8253reset()` programs channel 0 for scheduler interrupts and channel 2 as a free-running clock source. `i8253cpufreq()` measures delay-loop and optional TSC frequency against channel 2. `i8253init()` allocates I/O ports, initializes the PIT, and sets CPU timing fields. `i8253timerset()` adjusts channel-0 period with min/max bounds. `i8253enable()` registers the clock interrupt, and `i8253read()` exposes a shifted cumulative counter-2 tick value.

## Dependencies
Uses port I/O helpers (`inb`, `outb`), interrupt registration (`intrenable`), `timerintr`, `cycles`, `delayloop`, `Mach` timing fields, and `IrqCLOCK`.

## Behavior/Risks
The code handles VMware-like zero deltas by forcing a nonzero divisor. `i8253read()` detects unexpectedly large counter jumps and reloads channel 2, so extreme latency or emulation quirks can perturb fast-clock continuity.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/i8253.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/i8259.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/i8259.c

## Purpose
Initializes and manages the legacy dual 8259 PIC interrupt controllers.

## Key Elements
`i8259init()` allocates PIC ports, programs master/slave ICWs, unmasks the slave cascade, configures ISR reads, and probes ELCR level-trigger state. `i8259isr()` reads ISR state and sends EOIs. `i8259assign()` validates IRQs, rejects unsafe shared edge-triggered lines, attaches enable/disable callbacks, and maps IRQs to `VectorPIC + irq`. `i8259irqno()` normalizes unusable PCI IRQs and remaps IRQ2 to IRQ9. `i8259on()` and `i8259off()` restore or mask PIC interrupt delivery.

## Dependencies
Uses `Vctl` from `io.h`, port I/O, `VectorPIC`, `MaxIrqPIC`, `BUSUNKNOWN`, and architecture interrupt dispatch hooks.

## Behavior/Risks
Shared handlers are accepted only for level-triggered ELCR lines; sharing an edge-triggered PIC IRQ is explicitly rejected. ELCR detection is chipset-dependent and guarded by conservative tests.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/i8259.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/init9.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/init9.c

## Purpose
Provides a tiny C entry wrapper that adapts the first argument to Plan 9 boot startup.

## Key Elements
Declares `startboot(char*, char**)` and defines `_main(char *argv0)`, which calls `startboot(argv0, &argv0)`.

## Dependencies
Depends on the boot environment supplying `startboot`.

## Behavior/Risks
There is no defensive logic here; it exists solely to shape the initial argument vector expected by the boot code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/init9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/io.h -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/io.h

## Purpose
Defines PC interrupt vector constants, interrupt-control structures, bus address macros, and PCMCIA data structures.

## Key Elements
The first enum assigns exception vectors, PIC IRQ vectors, LAPIC offsets, syscall vector `64`, and APIC external vector range. `Vctl` describes one registered interrupt/trap handler, including handler function, argument, ISR/EOI hooks, enable/disable callbacks, IRQ/vector/CPU metadata, and driver name. The file also defines `BUSUNKNOWN`, ISA/PCI address translation macros, EISA constants, and PCMCIA slot/configuration/map structures.

## Dependencies
Uses kernel types such as `Ureg`, `Lock`, `ulong`, `ushort`, `uchar`, and `KNAMELEN`.

## Behavior/Risks
This header is central ABI for interrupt registration. Constants must stay aligned with trap setup, PIC/APIC code, and assembly vector-table assumptions; changing vector numbers or `Vctl` layout would affect multiple low-level subsystems.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/irq.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/irq.c

## Purpose
Implements architecture-neutral interrupt/trap handler registration and dispatch for the PC kernel.

## Key Elements
Maintains `vctl[256]` handler chains, `vclock` for the clock handler, and interrupt service-time histograms. `irqhandled()` dispatches traps and interrupts, performs ISR/EOI callbacks, updates per-Mach interrupt accounting, calls registered handlers, handles clock preemption, and logs or probes spurious interrupts. `trapenable()` registers CPU exception handlers below `VectorPIC`. `intrenable()` maps IRQs through architecture hooks, chains compatible handlers, enables hardware delivery, and records the clock handler. `intrdisable()` removes matching handlers and disables hardware delivery when appropriate. `irqinit()` exposes an `irqalloc` arch file listing vector, IRQ, and handler name.

## Dependencies
Depends on `Vctl`, `arch->intrirqno`, `arch->intrassign`, `arch->intrvecno`, optional `arch->intrspurious`, memory allocation, locks, `trap`, `preempted`, and arch-file registration.

## Behavior/Risks
Shared interrupt chains require compatible ISR/EOI semantics. On multiprocessor systems, removed `Vctl` objects may be delayed through a small ring before free to reduce races with in-flight dispatch.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/irq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/l.s -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/l.s

## Purpose
Provides 32-bit x86 bootstrap assembly, low-level CPU/port primitives, trap/syscall entry stubs, FPU/SSE helpers, synchronization helpers, VMX instruction wrappers, and the interrupt vector table.

## Key Elements
Bootstrap labels `_startKADDR`, `_multibootheader`, `_multibootentry`, `_startPADDR`, `mode32bit`, and `_startpg` handle multiboot metadata, early GDT setup, page-table construction, KZERO mapping, BSS clearing, Mach pointer setup, stack setup, and transfer to `main`. The file implements port I/O (`inb`, `outb`, string I/O), descriptor/control-register access (`lgdt`, `lidt`, `getcr*`, `putcr*`), TSC/MSR helpers, `cpuid`, `delayloop`, FPU/SSE save/restore, SPL interrupt priority functions, atomic/synchronization primitives, label save/restore, halt/mwait, RDRAND, debug-register helpers, VMX helpers, `touser`, common trap entry, syscall entry, `forkret`, and `vectortable`.

## Dependencies
Includes `mem.h` and shares constants with trap setup, segment descriptors, `Mach` layout assumptions, `main`, `trap`, `syscall`, and memory initialization (`MemMin` is written here and consumed by `memory.c`).

## Behavior/Risks
This file encodes hardware contracts directly: vector-table entry size is known by `trapinit()`, the first bootstrap page layout must match `mem.h`, and many instructions are emitted with raw bytes. Small layout or selector changes can break boot, trap return, user entry, or virtualization support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/main.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/main.c

## Purpose
Defines the main PC kernel startup sequence, initial process entry, machine initialization, configuration sizing, process machine-state hooks, shutdown, and reboot path.

## Key Elements
`main()` performs ordered kernel initialization: Mach/boot args, traps, I/O, console/screen, CPU/memory/architecture setup, clock setup, RAM disk, configuration, allocators, PCI, MMU, interrupts, timers, process/channel/page/user initialization, and scheduler entry. `mach0init()` and `machinit()` initialize CPU 0 state. `init0()` initializes devices, sets environment variables, starts alarm kproc, builds the initial user stack, and calls `touser()`. `confinit()` sizes process/image/swap/kernel/user memory budgets. `procsetup()`, `procfork()`, `procrestore()`, and `procsave()` manage per-process GDT/LDT, debug registers, VMX, FPU, and TLB state. `exit()` and `reboot()` quiesce CPUs/devices, clear secrets, and jump through reboot trampoline code.

## Dependencies
Depends on nearly every early PC kernel subsystem: boot args, traps, I/O, console, CPU identify, memory, arch hooks, PCI, MMU, timers, process scheduler, channels, page allocator, FPU, VMX, pools, and reboot trampoline data.

## Behavior/Risks
Initialization order is critical. Reboot deliberately runs on CPU 0, disables devices, clears sensitive pages, resets secret pools, and remaps low memory before jumping to physical reboot code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/mem.h -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/mem.h

## Purpose
Defines fundamental 32-bit x86 memory, virtual-address, segment, selector, and page-table constants for C and assembly.

## Key Elements
Declares page/word sizes, alignment macros, `MAXMACH`, `KSTACK`, clock constants, kernel/user virtual layout (`KZERO`, `KTZERO`, `VPT`, `KMAP`, `VMAP`, `USTKTOP`), fixed bootstrap physical/virtual addresses (`CONFADDR`, `CPU0PDB`, `CPU0PTE*`, `CPU0GDT`, `MACHADDR`, `CPU0MACH`), boot argument locations, GDT segment indexes/selectors, segment descriptor flags, virtual MMU sizing, PTE flags, page-directory/table index macros, and PAT write-combining index.

## Dependencies
Included by both C and assembly sources; values are consumed directly by `l.s`, MMU code, memory discovery, trap setup, and process/user entry code.

## Behavior/Risks
The comments note tight coupling: `ramscan` knows `CPU0END`, and `_startPADDR` assumes `CPU0PDB` is the first reserved page and that there are six reserved bootstrap pages. Changing these constants requires synchronized updates across boot assembly and memory management.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/memory.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/memory.c

## Purpose
Builds and finalizes the PC physical memory map, reserves BIOS/kernel regions, discovers RAM, maps low memory, and exposes allocation helpers for UPA/UMB device address spaces.

## Key Elements
Defines memory classes for unbacked physical address space, upper memory blocks, RAM, ACPI, and reserved ranges. `rampage()` allocates early page-table pages from `conf.mem` or directly from the memory map. `mapkzero()` maps RAM/UMB ranges into KZERO with correct caching flags. Low-memory helpers locate EBDA, conventional memory size, BIOS tables, VGA/ROM reservations, and UMB device ROMs. `checksum`, `sigscan`, `sigsearch`, and `rsdsearch()` find BIOS/ACPI signatures including RSDP. `upaalloc`, `upaallocwin`, `upafree`, `umballoc`, and `umbfree` allocate device address ranges. `umbexclude()` parses boot exclusions. `mtrrexclude()` removes ranges with unexpected cache attributes. `e820scan()` parses bootloader E820 data and maps usable RAM; `ramscan()` probes RAM when E820 is unavailable. `meminit0()` seeds default maps, reserves kernel/bootstrap areas, discovers memory, and applies MTRR filtering. `memreserve()` reserves page-rounded ranges before finalization. `meminit()` maps UMBs and transfers usable RAM into `conf.mem[]`.

## Dependencies
Uses `MemMin` set by `l.s`, memory-map APIs (`memmapadd`, `memmapalloc`, `memmapfree`, `memmapnext`, `memmapsize`), mapping APIs (`pmap`, `vmap`, `vunmap`, `punmap`), MTRR attributes, boot config, and `conf.mem`.

## Behavior/Risks
The bootloader E820 map is preferred; otherwise the kernel probes memory in 4 MB chunks and stops after high missing memory to avoid mistaking device/video regions for RAM. BIOS/UEFI maps may be unreliable, so `memreserve()` is intended for architecture code to protect discovered tables before final allocation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/memory.c -->