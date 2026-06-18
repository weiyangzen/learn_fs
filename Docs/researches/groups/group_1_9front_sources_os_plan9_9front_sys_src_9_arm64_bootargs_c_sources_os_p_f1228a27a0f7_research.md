# Group Research: group_1_9front_sources_os_plan9_9front_sys_src_9_arm64_bootargs_c_sources_os_p_f1228a27a0f7

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/bootargs.c -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/bootargs.c

Implements ARM64 boot configuration parsing for 9front’s QEMU-style ARM64 kernel.

Key behavior:
- Maintains a small case-insensitive `name=value` configuration table with override semantics.
- Parses existing `BOOTARGS` as newline-separated `plan9.ini` content.
- Parses flattened device tree data at `DTBADDR`, including `/memory` `reg`, `/cpus/cpu*` `reg`, and `/chosen` `bootargs`.
- Derives `*maxmem` from the memory node when absent.
- Counts CPU nodes and installs `*ncpu` unless the user provided one.
- Exposes `getconf`, `setconfenv`, and `writeconf` for kernel configuration and reboot persistence.

Dependencies:
- Uses Plan 9 string/token helpers, `KADDR`, `cankaddr`, `BOOTARGS`, and kernel environment helpers.

Research notes:
- Device-tree parsing is intentionally narrow and only extracts early boot configuration needed by the port.
- `writeconf` serializes the live kernel environment back into `BOOTARGS` for reboot.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/bootargs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/cache.v8.s -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/cache.v8.s

ARMv8 cache-maintenance assembly for instruction/data cache ranges and whole-cache operations.

Key behavior:
- Provides instruction cache invalidation by range and all-cache invalidation.
- Provides data cache clean, clean-to-PoU, invalidate, and clean+invalidate by virtual address range.
- Provides whole L1 and L2 set/way cache operations.
- Computes line size, set count, and way count from `CCSIDR_EL1` after selecting cache level with `CSSELR_EL1`.
- Masks interrupts around cache-size selection and maintenance loops, then restores `DAIF`.

Dependencies:
- Uses ARM64 system register encodings from `sysreg.h`.
- Called by MMU, reboot, DMA, and text-flush paths.

Research notes:
- Range operations align start/end addresses to discovered cache line size.
- Whole-cache operations use set/way iteration and barriers to make state globally visible.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/cache.v8.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/clock.c -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/clock.c

ARM64 virtual timer and timebase support.

Key behavior:
- Enables the performance counter and user-readable virtual counter access.
- Uses `CNTVCT_EL0` as `fastticks` and virtual timer interrupts as scheduler clock interrupts.
- Reads `CNTFRQ_EL0` on CPU 0 and stores it as `m->cyclefreq`.
- Programs `CNTV_TVAL_EL0` in `timerset`.
- Implements microsecond and millisecond busy waits.
- Provides `synccycles` rendezvous for multi-CPU startup synchronization.

Dependencies:
- Uses `sysrd/syswr`, timer interrupt registration, `timerintr`, and machine state.

Research notes:
- User-visible timing is based on the virtual counter rather than the PMU cycle counter.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/dat.h

ARM64 machine data definitions shared by kernel C code.

Key definitions:
- Time constants, GPIO mode values, and common typedefs.
- `Label`, FPU save/allocation structures, and per-process FPU state.
- `Conf` and `Confmem` memory/process configuration structures.
- Per-machine MMU state with top-level user page table pointer.
- Per-process MMU state with page-table freelists and ASID/TPIDR tracking.
- ARM64 `Mach` layout, including the assembly-known prefix fields.
- `ISAConf`, debug macros, and device resource descriptors.

Dependencies:
- Includes `../port/portdat.h` after architecture-specific type definitions.

Research notes:
- `Mach` register bindings declare `m` in `R27` and `up` in `R26`.
- `PMMU` encodes ASID and user TLS state needed by `trap.c` and `mmu.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/devrtc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/devrtc.c

Minimal PL031 RTC device driver exposed as `#r/rtc`.

Key behavior:
- Maps RTC registers at `VIRTIO + 0x01010000`.
- Exposes a directory with one `rtc` file.
- Reads the current time directly from the first RTC register.
- Allows read access to all users and denies writes except that non-eve write opens are rejected earlier.

Dependencies:
- Uses Plan 9 device table helpers, `readnum`, and standard error handling.

Research notes:
- The write method always returns `Eperm`; this is a read-only RTC interface in practice.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/devrtc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/fns.h

ARM64 architecture function declaration header.

Key declarations:
- Assembly helpers for interrupts, atomics, labels, user entry, FPU register save/restore, TLB operations, and hypercalls.
- Cache maintenance APIs from `cache.v8.s`.
- MMU mapping and process-ASID APIs.
- Boot, clock, FPU, trap, IRQ, PCI, UART, DMA, and configuration entry points.
- Stub-style prototypes for subsystems not present in this target but expected by shared code.

Dependencies:
- Extends `../port/portfns.h`.

Research notes:
- This header is the main contract between ARM64 C code and assembly support files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/fpu.c -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/fpu.c

ARM64 floating-point/SIMD lazy context management.

Key behavior:
- Saves and restores FP control/status and 32 vector registers through assembly helpers.
- Keeps separate user FP and nested kernel FP save stacks.
- Disables FP access by default and enables/restores state lazily on FP traps.
- Handles kernel FP use during syscalls, traps, and interrupts with `fpukenter`/`fpukexit`.
- Handles fork, save, restore, notify, and noted paths.
- Posts a floating-point error note for repeated user FP traps while already active.

Dependencies:
- Uses `getfcr/setfcr/getfsr/setfsr`, `fpon/fpoff`, `fpsaveregs/fploadregs`, process state, and note machinery.

Research notes:
- Kernel FP state can nest through linked `FPalloc` records.
- User state is protected during kernel entry so kernel vector use does not corrupt user registers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/fpu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/gic.c -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/gic.c

ARM64 Generic Interrupt Controller support for QEMU virt-style GIC.

Key behavior:
- Defines distributor and redistributor register offsets.
- Finds per-CPU redistributor by matching `GICR_TYPER`.
- Initializes the distributor on CPU 0, clears/enables groups, priorities, targets, and configurations.
- Initializes per-CPU SGI/PPI redistributor state.
- Enables the CPU interface through ICC system registers.
- Dispatches IRQs and FIQs through registered `Vctl` handlers.
- Routes PCI interrupt registration to `pciqemu.c`.

Dependencies:
- Uses `VIRTIO`, interrupt constants from `io.h`, ICC system registers, and PCI helpers.

Research notes:
- SPI interrupts are targeted at CPU 0; SGI/PPI interrupts stay per-CPU.
- `intrdisable` only delegates PCI removal and does not remove non-PCI `Vctl` entries.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/gic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/init9.s -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/init9.s

Tiny Plan 9 user init entry stub.

Key behavior:
- Loads static base into `R28`.
- Passes the kernel `boot` function address in `R0`.
- Branches to `startboot`.

Dependencies:
- Relies on Plan 9 ARM64 ABI conventions and boot support elsewhere.

Research notes:
- This file is only the assembly bridge into the userland boot startup path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/init9.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/io.h -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/io.h

ARM64 QEMU interrupt and bus constants.

Key definitions:
- Defines PPI/SPI bases and interrupt numbers for FIQ, virtual counter, UART, and PCI lines.
- Defines `BUSUNKNOWN`, `PCIWINDOW`, and `PCIWADDR`.

Dependencies:
- Used by interrupt, PCI, clock, and UART code.

Research notes:
- The constants match a narrow QEMU/virt platform target rather than a generic ARM64 board description.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/l.s -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/l.s

Core ARM64 assembly for boot, MMU transition, traps, syscall return, atomics, TLB, FP register movement, and hypercalls.

Key behavior:
- `_start` enters EL1 from EL1/EL2, disables MMU/caches, clears BSS and page tables on CPU 0, builds initial mappings, and enables virtual addressing.
- Establishes per-CPU `Mach`, stack, `TPIDR_EL1`, and static base.
- Provides interrupt priority helpers, atomics, labels, idle wait, cycle reads, and TLB maintenance.
- Provides `touser`, syscall path `vsys0`, trap paths for EL0/EL1, and return paths `forkret`/`noteret`.
- Saves and restores complete trap frames in vector stubs.
- Provides FPU enable/disable and vector register save/load instructions.
- Provides fault-proof `peek` and an `HVC` wrapper.

Dependencies:
- Uses constants from `mem.h` and `sysreg.h`; called by startup, trap, MMU, FPU, and main code.

Research notes:
- Vector stubs are template code patched by `trap.c` to branch to EL0 or EL1 handlers.
- Boot supports both primary and secondary CPU entry.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/main.c -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/main.c

ARM64 kernel mainline, CPU startup, reboot, exit, and DMA cache flush handling.

Key behavior:
- `init0` initializes devices/environment, starts alarm process, builds initial user stack, and enters user mode.
- `confinit` computes CPU count, process counts, page pools, swap/image sizing, and kernel memory pool limits.
- `main` initializes console, boot arguments, memory, traps, FPU, interrupts, clock, pages, processes, devices, and scheduler.
- Secondary CPUs initialize traps/FPU/interrupts/clock/MMU and enter scheduler.
- `mpinit` starts other CPUs through PSCI `CPU_ON` hypercalls.
- `exit` uses PSCI CPU off or system reset.
- `reboot` serializes config, shuts down devices/clock/interrupts, clears secrets, and jumps through reboot trampoline.
- `dmaflush` performs clean/invalidate with block alignment.

Dependencies:
- Uses broad kernel port APIs, PSCI `hvccall`, `rebootcode`, cache operations, and memory/pool subsystems.

Research notes:
- The port assumes QEMU-like CPU identification and reset behavior.
- Reboot explicitly returns to an identity-mapped trampoline.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/mem.c -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/mem.c

Initial ARM64 kernel memory map creation and RAM discovery.

Key behavior:
- Builds a temporary TTBR0 identity map for DRAM below `-KZERO`.
- Builds the initial shared TTBR1 kernel page table for early DRAM and VIRTIO I/O.
- Handles misaligned VIRTIO mappings by falling back to page mappings.
- Seeds higher-level kernel table pointers when more page-table levels are required.
- `meminit` derives memory limit from `*maxmem` or a default, maps RAM into the kernel map, and populates `conf.mem[0]`.

Dependencies:
- Uses page table constants from `mem.h`, `kmapram`, and boot config.

Research notes:
- Early page tables cover just enough for kernel startup and device I/O; `meminit` fills RAM mappings later.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/mem.h -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/mem.h

ARM64 memory layout, page-table, and PTE constant definitions.

Key definitions:
- Page size, effective virtual address width, page-table level math, and index macros.
- Kernel virtual layout for `VDRAM`, `KTZERO`, `KZERO`, `VMAP`, `KMAP`, `KSEG0`, and Mach areas.
- Boot argument, DTB, reboot trampoline, user text, stack, and user segment limits.
- Cache/memory attribute encodings, shareability, MAIR slots, and PTE bits.
- Physical DRAM base and utility macros.

Dependencies:
- Used by C and assembly across boot, MMU, traps, and devices.

Research notes:
- The effective VA width is 36 bits, with a high-half kernel layout.
- `KZERO` provides direct mapping for the first 1 GB of physical RAM.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/mmu.c -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/mmu.c

ARM64 runtime MMU mapping and per-process address-space switching.

Key behavior:
- Allocates per-CPU user top-level tables in `mmu1init`.
- Converts between direct-mapped physical and virtual addresses.
- Provides `kmapram`, `mmukmap`, `vmap`, and no-op `vunmap`.
- Builds kernel mappings with block pages when possible and page mappings otherwise.
- Walks/allocates process page tables from `up->mmufree`.
- Allocates ASIDs from a 256-entry table and invalidates stale ASID mappings.
- Installs user PTEs in `putmmu`, including text-cache synchronization.
- Switches TTBR0 with ASID tagging and releases process page tables.

Dependencies:
- Uses cache/TLB helpers, page allocator, process MMU fields, and constants from `mem.h`.

Research notes:
- `putasid` proactively switches away from a sleeping process’s page tables on SMP to avoid stale table pages on another CPU.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/pciqemu.c -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/pciqemu.c

QEMU ARM64 PCI ECAM configuration and simple interrupt fanout.

Key behavior:
- Maps PCI ECAM space at `0x3F000000`.
- Implements 8/16/32-bit PCI config reads and writes by ECAM address calculation.
- Registers handlers in a fixed 32-entry vector table.
- Enables four PCI interrupt lines and fans every interrupt to all registered handlers.
- Scans bus 0, maps BARs with `pcibusmap`, and optionally prints inventory.

Dependencies:
- Uses Plan 9 PCI helpers and ARM64 interrupt registration.

Research notes:
- Interrupt dispatch does not demultiplex by device interrupt status; registered handlers must tolerate shared interrupt calls.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/pciqemu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/rebootcode.s -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/rebootcode.s

ARM64 reboot trampoline copied to a physical/identity-mapped address.

Key behavior:
- Copies replacement kernel code to the requested entry address.
- Cleans and invalidates caches.
- Disables MMU, data cache, and instruction cache in `SCTLR_EL1`.
- Invalidates local TLB and caches again.
- Clears argument registers and returns to the copied entry address through `LR`.

Dependencies:
- Included into `main.c` as `rebootcode.i` and copied to `REBOOTADDR`.

Research notes:
- Designed to execute outside normal high-half kernel mappings during reboot.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/rebootcode.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/sysreg.c -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/sysreg.c

Dynamic ARM64 system register read/write thunk generator.

Key behavior:
- Builds small executable instruction stubs for arbitrary encoded system registers.
- Caches generated `MRS`/`MSR` stubs in a static buffer.
- Flushes data/instruction caches after emitting new code.
- Provides `sysrd` and `syswr` callable from `KZERO`.

Dependencies:
- Uses cache maintenance, per-CPU `m->machno`, and locking.

Research notes:
- Avoids needing one assembly function per system register while working around immediate register encodings.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/sysreg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/sysreg.h -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/sysreg.h

ARM64 system register and barrier operand encoding definitions.

Key definitions:
- Encodes many EL1/EL2/EL0 system registers with `SYSREG`.
- Covers CPU ID, MMU, exception, timer, cache, TPIDR, PMU, and GIC ICC registers.
- Defines final `SYSREG` macro for C-side numeric encodings.
- Defines barrier domain/type constants like `ISH`, `NSH`, and `SY`.

Dependencies:
- Assembly files temporarily redefine `SYSREG` to Plan 9 assembler `SPR(...)` form.

Research notes:
- This header is shared by C and assembly but intentionally has assembler-specific redefine patterns.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/sysreg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/trap.c -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/trap.c

ARM64 trap, syscall, fault, notify, process-register, and dump support.

Key behavior:
- Allocates and patches the ARM64 vector table with the template stubs from `l.s`.
- Classifies ESR exception classes and handles aborts, FP traps, IRQs, FIQs, SError, and unhandled traps.
- Enters/exits kernel accounting and FPU protection around traps and syscalls.
- Implements syscall dispatch through `dosyscall`.
- Builds user notification frames and validates `noted` resume modes.
- Handles translation/access/permission faults via generic `fault`.
- Saves/restores TPIDR_EL0 and FPU state across process switches.
- Sets up kernel and fork child scheduler contexts.
- Dumps registers and kernel stack PCs for diagnostics.

Dependencies:
- Uses `syswr`, `irq/fiq`, FPU helpers, process/note/fault machinery, and assembly symbols.

Research notes:
- Kernel faults inside `peek` are specially recovered by redirecting PC to link.
- User-modifiable PSR bits are masked in `setregisters`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/uartqemu.c -->
# File Research: sources/os/plan9/9front/sys/src/9/arm64/uartqemu.c

QEMU PL011 UART driver for ARM64 console and serial I/O.

Key behavior:
- Defines PL011 register offsets and bit fields.
- Instantiates one UART at `VIRTIO + 0x1000000`, 24 MHz, 115200 baud.
- Handles RX/TX interrupts, FIFO fill/drain, interrupt clearing, and UART enable/disable.
- Implements line control for baud, data bits, stop bits, parity, and break.
- Provides polled `getc`/`putc`.
- Initializes the console UART with `l8 pn s1`.

Dependencies:
- Uses shared UART infrastructure and interrupt registration.

Research notes:
- Derived from the BCM PL011 driver but hardwired to the QEMU ARM64 mapping.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/arm64/uartqemu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/arch.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/arch.c

Shared ARM/BCM architecture glue for process state and user register handling.

Key behavior:
- Fills kernel `Ureg` context for sleeping process stack traces.
- Enforces word-aligned user addresses.
- Returns debug/user PC from `up->dbgreg`.
- Masks protected PSR bits when writing registers through proc interfaces.
- Sets kernel process scheduler stack/PC.
- Hooks FPU process setup/fork/save/restore.
- Switches away from user page tables on SMP during process save.
- Implements `userureg` and a spl-protected `cas32`.

Dependencies:
- Uses ARM PSR constants, FPU helpers, MMU switch, and process state.

Research notes:
- This is architectural glue rather than board-specific code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/arch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/archbcm.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/archbcm.c

BCM2835/Raspberry Pi 1 board support.

Key behavior:
- Defines global `Soc` parameters for 512 MB DRAM, bus/physical/virtual I/O ranges, and cache attributes.
- Implements watchdog reset, watchdog feed, and watchdog disable.
- Enables FPU in `archreset`.
- Reports CPU as ARM1176JZF-S.
- Restricts CPU count/startup to one CPU.
- Installs watchdog feed as a clock callback.
- Implements `cmpswap` via `cas32`.

Dependencies:
- Uses power management registers at `VIRTIO + 0x100000`.

Research notes:
- This file targets the original single-core Raspberry Pi SoC.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/archbcm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/archbcm2.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/archbcm2.c

BCM2836/Raspberry Pi 2 and related multicore board support.

Key behavior:
- Defines `Soc` parameters for BCM2836-style I/O, ARM local registers, and SMP cache attributes.
- Implements watchdog reset/feed/disable and CPU identification for Cortex-A7/A53.
- Derives CPU count from hardware limit and optional `*ncpu`.
- Starts secondary CPUs using ARM local mailbox `startcpu` fields and `sev`.
- Provides mailbox clear/wake helpers.
- Coordinates secondary startup with per-CPU locks.
- `cpustart` performs per-secondary trap, clock, MMU, timer, FPU, active-mach, and scheduler setup.

Dependencies:
- Uses ARM local mailbox registers, `cpureset`, `machinit`, trap/clock/MMU/timer setup, and watchdog clock link.

Research notes:
- The SoC DRAM size is capped below physical I/O overlap.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/archbcm2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/arm.h -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/arm.h

ARMv6/v7 status register, coprocessor, cache, MMU, and page-table definitions.

Key definitions:
- CPSR mode/interrupt/status bit masks.
- FPA/VFP coprocessor identifiers and instruction classification macros.
- CP15 register, CRm, op1/op2 constants for ID, control, timers, fault, cache, TLB, vectors, and performance monitor access.
- Main/auxiliary control register bits for ARMv6/v7.
- Cache and TLB operation encodings.
- Translation table cacheability bits.
- L1/L2 PTE type, cache, shareability, AP, DAC, and no-exec bits.
- High vector base constant.

Dependencies:
- Used by ARM assembly, MMU, trap, clock, coprocessor, and FPU code.

Research notes:
- Central compatibility header for both ARM1176 and Cortex-A7 style ports.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/arm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/arm.s -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/arm.s

Shared ARMv6/v7 assembly macro definitions.

Key behavior:
- Defines physical address and L1 index macros.
- Provides assembler macro forms for barriers, `MCRR`, `MRRC`, `MSR`, CPS interrupt enable/disable, debug GPIO pulse, and CPU ID detection.
- Supplies default ARMv6-style barrier implementations overridden by ARMv7 assembly.

Dependencies:
- Included by `armv6.s` and `armv7.s`.

Research notes:
- This file is macro infrastructure, not standalone executable code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/arm.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/armv6.s -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/armv6.s

ARM1176/ARMv6 boot and low-level machine support for BCM2835.

Key behavior:
- Starts in SVC mode with IRQ/FIQ disabled.
- Disables MMU/caches, invalidates caches/TLB, clears Mach/page-table space, initializes page tables, enables MMU/caches/high vectors, and jumps to virtual `main`.
- Enables the ARM1176 cycle counter.
- Provides CP15 fault/status/id accessors, cycle counter read, spl helpers, test-and-set via SWP, labels, idle wait, barriers, TLB invalidation, and cache maintenance.
- Provides range and whole-cache operations using ARMv6 cache maintenance instructions.

Dependencies:
- Includes `arm.s`, `mem.h`, and `arm.h`.
- Calls `mmuinit` and `main`.

Research notes:
- L2 cache operations are stubs because this target does not enable L2 cache.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/armv6.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/armv7.s -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/armv7.s

Cortex-A7/ARMv7 boot, SMP startup, atomics, and low-level machine support.

Key behavior:
- CPU 0 performs primary boot: enters SVC from possible HYP mode, disables caches/MMU, clears tables, initializes MMU, enables SMP/coherency, caches, MMU, and high vectors.
- Secondary CPUs enter through `cpureset`, locate their `Mach`, install per-CPU page table base, enable MMU/caches, and call `cpustart`.
- Handles HYP-to-SVC transition with `ERET`.
- Provides CP15 accessors, cycle read, spl helpers, LDREX/STREX `cmpswap` and `tas`, labels, idle WFI, barriers, SEV, and TLB invalidation.
- Provides cache line range operations and includes `cache.v7.s` for whole-cache operations.

Dependencies:
- Includes `arm.s` and `cache.v7.s`.
- Calls `mmuinit`, `mmuinvalidate`, `main`, and `cpustart`.

Research notes:
- Explicitly toggles SMP bit in auxiliary control before and after early cache/MMU setup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/armv7.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/bootargs.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/bootargs.c

BCM boot configuration parser for device tree, ATAGs, and reboot-saved config.

Key behavior:
- Maintains a 64-entry config table with case-insensitive keys.
- Parses newline `plan9.ini` content and command-line tokens.
- Parses flattened device tree nodes for memory, `/chosen/bootargs`, `emmc2bus` DMA ranges, and PCI host bridge memory/DMA windows.
- Parses legacy ARM ATAG memory and command-line records.
- `bootargsinit` first uses the firmware-provided DTB/ATAG physical pointer, then falls back to `CONFADDR`.
- Exposes `getconf`, `setconfenv`, and `writeconf`.

Dependencies:
- Uses kernel address conversion, firmware boot pointer, and environment helpers.

Research notes:
- More capable than the ARM64 bootargs parser because Raspberry Pi firmware may provide either DTB or ATAGs and board-specific bus windows.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/bootargs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/cache.v7.s -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/cache.v7.s

Cortex/ARMv7 cache-maintenance implementation shared by normal and reboot assembly.

Key behavior:
- Invalidates all instruction cache and branch predictor, or an instruction-cache range.
- Provides set/way data cache operators for clean, invalidate, and clean+invalidate.
- Provides whole L1 and L2 cache operations using selected cache level and CCSIDR-style set/way counts.
- Wraps unified clean+invalidate with interrupt masking.
- Computes set/way register contents in a hand-translated loop.

Dependencies:
- Included by `armv7.s` and reused by reboot code.
- Uses ARM CP15 cache-size select/register operations.

Research notes:
- Whole-cache functions can execute before MMU is on by remapping function pointers into the current PC segment.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/cache.v7.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/clock.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/clock.c

BCM283x timer support for system timer, ARM timer, cycle counter, and ARM generic timer.

Key behavior:
- Uses system timer 3 at 1 MHz for CPU 0 hzclock and `fastticks`.
- Uses local generic timer for secondary CPU clock interrupts when supported.
- Uses ARM timer for `perfticks` and immediate interrupt forcing.
- Calibrates CPU cycle frequency against the 1 MHz system timer.
- Programs next clock interrupt with min/max period bounds.
- Provides microsecond/millisecond delay functions.

Dependencies:
- Uses CP15 timer feature probing, interrupt registration, ARM local timer registers, and `timerintr`.

Research notes:
- CPU 0 must receive system timer interrupts; secondary CPUs must receive local generic timer interrupts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/coproc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/coproc.c

Dynamic ARM coprocessor and VFP register access thunk generator.

Key behavior:
- Emits small executable instruction pairs for arbitrary MRC/MCR and VFP control/register operations.
- Caches generated instruction stubs per CPU.
- Provides generic `cprd/cpwr`, CP15 convenience wrappers, VFP control `fprd/fpwr`, and VFP data register save/restore helpers.
- Flushes data/instruction caches after emitting new instructions.

Dependencies:
- Uses cache maintenance, locking, ARM coprocessor constants, and per-CPU `m`.

Research notes:
- Mirrors ARM64 `sysreg.c` for the ARMv6/v7 coprocessor encoding model.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/coproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/dat.h

BCM/ARM kernel data structure definitions.

Key definitions:
- Time constants and architecture typedefs.
- FPU save/allocation structures supporting hardware VFP and software emulation.
- `Conf`/`Confmem`, Mach MMU state, and process MMU state.
- `Mach` layout with assembly-known fields, CPU timing, FPU state, and exception-mode scratch save areas.
- Fake `KMap` macros for direct mapping.
- Global active CPU state, register-bound `m`/`up`, and `machaddr`.
- `ISAConf`, debug macros, device descriptors, SoC descriptor, and GPIO function constants.

Dependencies:
- Includes `../port/portdat.h`.

Research notes:
- `m` is register `R10` and `up` is `R9` on this port.
- The `Soc` structure drives bus/physical/virtual address translation across DMA and device code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/devarch.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/devarch.c

BCM `#P` architecture device and console UART setup.

Key behavior:
- Provides dynamic registration for architecture files with read/write callbacks.
- Exposes `cputype` and `cputemp` files.
- Implements the Plan 9 device methods for `#P`.
- Selects console UART from `console` config, enables it if needed, applies line settings, and replays buffered kernel messages.
- Controls the activity LED through firmware virtual GPIO or a configured GPIO pin.

Dependencies:
- Uses `addarchfile`, UART physical device table, GPIO helpers, firmware temperature, and config access.

Research notes:
- `okay` honors Raspberry Pi firmware config keys for LED GPIO and active-low polarity.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/devarch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/devgpio.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/devgpio.c

Plan 9 GPIO device `#G` for Raspberry Pi pins.

Key behavior:
- Encodes file, parent, naming scheme, and pin number in Qid paths.
- Supports BCM, board, WiringPi, and generic naming schemes with revision-dependent pin tables.
- Exposes `gpio` directory, pin data files, `ctl`, and `event`.
- Data files read/write pin level as `0` or `1`.
- `ctl` supports scheme selection, pin function, pull control, and edge event configuration.
- Registers a GPIO interrupt handler that records edge events into a 32-bit event mask and wakes readers.
- Allows only one event reader at a time.

Dependencies:
- Uses low-level GPIO operations from `gpio.c` and Plan 9 command parsing/device helpers.

Research notes:
- Event reads return raw bytes from the 32-bit event mask and clear on wrapped offsets.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/devgpio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/dma.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/dma.c

BCM2835 DMA controller support for channels 0-6.

Key behavior:
- Defines DMA register and control block formats.
- Converts CPU virtual addresses to peripheral bus addresses with `soc.busdram`.
- Converts VIRTIO device addresses to bus I/O addresses with `soc.busio`.
- Lazily initializes DMA channels, allocates aligned control blocks, enables channel registers, and registers interrupts.
- Starts device-to-memory, memory-to-device, and memory-to-memory transfers.
- Uses cache clean/invalidate around source, destination, and control blocks.
- Waits for interrupt completion with timeout, reports errors, and resets failed channels.

Dependencies:
- Uses interrupt registration, cache maintenance, SoC address mapping, and Plan 9 sleep/rendezvous.

Research notes:
- Comments note only a subset of channels work reliably for MMC.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/dma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/dwcotg.h -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/dwcotg.h

Register map and bit definitions for the Synopsys DesignWare USB 2.0 OTG host controller.

Key contents:
- Defines `Dwcregs` covering global, host, port, host-channel, FIFO, and power/clock registers.
- Defines host channel structure and `Maxchans`.
- Defines masks and symbolic values for OTG, AHB, USB config, reset, interrupts, RX status, FIFO sizing, hardware config, LPM, host config, port status, channel characteristics, split transactions, transfer sizing, and power gating.

Dependencies:
- Consumed by the BCM USB host driver.

Research notes:
- This header is declarative hardware interface data; it contains no executable functions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/dwcotg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/emmc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/emmc.c

BCM Arasan eMMC/SD host controller driver implementing Plan 9 `SDio`.

Key behavior:
- Defines controller registers and command/status/interrupt bits.
- Initializes/reset host controller and determines external clock rate from firmware clock API or default.
- Sets SD bus width and clock speed.
- Enables interrupts and handles card/data completion wakeups.
- Sends SD commands with response decoding and error recovery for command/data inhibit states.
- Uses DMA channel `DmaChanEmmc` for data transfers to/from the FIFO register.
- Integrates LED activity with `okay`.
- Registers itself with `addmmcio`.

Dependencies:
- Uses `getclkrate`, GPIO/interrupt helpers, DMA, cache flush via DMA, and generic SD layer.

Research notes:
- Transfer path is interrupt-assisted after DMA completion, then waits for `Datadone`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/emmc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/ether4330.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/ether4330.c

Broadcom BCM4330-family SDIO Wi-Fi Ethernet driver.

Key behavior:
- Takes over the eMMC SDIO bus, reconfigures GPIO routing to Wi-Fi pins, negotiates SDIO functions, high speed, 4-bit bus, and block sizes.
- Implements SDIO direct and extended I/O, backplane windowing, chip memory/register access, packet I/O, and abort/reset paths.
- Scans Silicon Backplane cores, detects supported chip IDs/revisions, resets ARM/D11/SOCRAM cores, sizes RAM, and configures clocks/pulls/drive strength.
- Selects firmware/config/regulatory files by chip ID/revision, uploads firmware/config into chip RAM, verifies uploads, and releases the on-chip ARM core.
- Implements SDPCM framing for command, event, and data channels.
- Runs reader and timer kernel processes for packet/event reception and periodic scanning.
- Implements firmware command interface, variables, WEP/WPA/WPA2 keys, join, scan, event handling, link state, multicast/promiscuous mode, and ifstat output.
- Registers an Ethernet card named `4330`.

Dependencies:
- Uses SDIO, Ether, netif, GPIO, firmware files in `/boot` or `/lib/firmware`, block queues, and Plan 9 command parsing.

Research notes:
- The driver supports multiple related Broadcom chips, including 4330, 43362, 43430, and 4345 variants.
- The control interface is tailored for `aux/wpa` expectations, including status strings and key commands.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/ether4330.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/fns.h

BCM architecture function declaration header.

Key declarations:
- Architecture device registration, reset/reboot/watchdog, boot args, cache operations, MMU operations, clock, coprocessor, DMA, GPIO, firmware, framebuffer, interrupt, UART, and process/trap helpers.
- Floating-point hardware/emulation entry points.
- Port-called helpers for delay, interrupt level, alignment checks, idle, and kernel register setup.
- Address conversion macros `KADDR` and `PADDR`.

Dependencies:
- Extends `../port/portfns.h`.

Research notes:
- This is the principal cross-file API surface for the BCM port.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/fpiarm.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/fpiarm.c

ARM floating-point instruction emulator for FPA and VFP opcodes.

Key behavior:
- Uses Inferno internal FP routines for arithmetic, conversion, comparison, and rounding.
- Emulates ARM 7500 FPA load/store, transfer, compare, unary, and binary operations.
- Emulates selected VFP load/store, core/extension register transfer, data processing, compare, immediate, and conversion operations.
- Maintains emulated FP state in `FPalloc`, initializes constants/status, and handles notify duplication.
- Checks ARM condition codes before executing an FP instruction.
- Advances PC by 4 for each emulated FP instruction and stops at the first non-FP opcode.
- Raises errors for unimplemented FP instructions.

Dependencies:
- Uses `ureg.h`, `arm.h`, `../omap/fpi.h`, process FPU save state, and user address validation.

Research notes:
- Arithmetic is done in double precision and does not fully model ARM FP trap status.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/fpiarm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/gpio.c -->
# File Research: sources/os/plan9/9front/sys/src/9/bcm/gpio.c

Low-level Raspberry Pi GPIO register operations.

Key behavior:
- Maps GPIO registers at `VIRTIO + 0x200000`.
- Sets pin function select fields.
- Configures pull-up/down/off using legacy BCM2835-2837 handshake or BCM2711 pull registers.
- Sets, clears, and reads pin levels.
- Enables/disables rising or falling edge detection and reads/clears event status.
- Registers the GPIO MMIO page as a physical device segment.

Dependencies:
- Uses SoC physical/virtual mapping, `addphysseg`, and delay helpers.

Research notes:
- `gpiomeminit` exposes GPIO as a device physical segment named `gpio`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/bcm/gpio.c -->