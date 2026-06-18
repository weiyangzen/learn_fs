# Group Research: group_1489_plan9_sources_os_plan9_plan9_sys_src_9_ppc_l_s_sources_os_plan9_pla_b2eaa2e527be

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/l.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/l.s

PowerPC assembly support for early boot, BAT/MMU enablement, trap entry/return, TLB miss fast paths, atomic operations, cache maintenance, FPU state, and SPR accessors.

Key responsibilities:
- `start` disables interrupts, sets `SB`, enters `mmuinit0`, builds `Mach`, zeroes `up`, and calls C `main`.
- `mmuinit0` clears TLBs, programs BAT mappings for kernel DRAM, FPGA/IO, and direct internal-memory access, then enables instruction/data translation via `RFI`.
- Implements interrupt priority primitives: `splhi`, `splx`, `spllo`, `islo`.
- Provides process transition helpers: `touser`, `setlabel`, `gotolabel`, `forkret`.
- Implements exception vector save/restore: `tlbvec`, `trapvec`, `saveureg`, and `restoreureg`.
- Implements 603e-style instruction/data TLB miss handlers `imiss` and `dmiss` that search hash PTE groups before falling back to normal trap handling.
- Provides TLB/cache primitives: `tlbflushall`, `tlbflush`, `dczap`, `dcflush`, `icflush`, cache enable/disable helpers, and `mmudisable`.
- Provides atomic helpers: `tas`, `_xinc`, `_xdec`, `cmpswap`.
- Saves/restores all 32 FPU registers plus FPSCR and initializes Plan 9 FP constants.
- Exposes many SPR accessors for MSR, BAT, HID, SDR1, segment registers, hash registers, miss registers, DEC, DAR, DSISR, and related PowerPC state.
- Includes `ucuconf`-specific PPC 755/L2 cache/BAT helpers and `mul64fract`.

Important behavior:
- Uses `SPRG0..3` to preserve R0/R1/LR/vector across low-level exception entry.
- Trap entry detects user versus kernel mode and switches user traps onto the current process kernel stack.
- `saveureg` re-enables MMU translation before returning to C trap handlers.
- TLB miss fast paths count `m->tlbfault`, `m->imiss`, and `m->dmiss`.
- Atomic operations use load-reserve/store-conditional and include `DCBF` workarounds for 603x issues.
- `mmudisable` also disables I/D caches before returning to a physical caller.

Dependencies:
- Must match `mem.h` constants, `Ureg` layout, `Mach` field offsets, PowerPC assembler conventions, and C trap/syscall/MMU code.
- Calls C symbols such as `main`, `trap`, and cache/MMU helpers.

Notable risks:
- Any mismatch between `Ureg` offsets here and C trap structures breaks all exception return.
- BAT constants are board-configuration-sensitive and differ under `ucuconf`.
- TLB miss code assumes hash table layout and PTE group format used by `mmu.c`.
- The file mixes generic PPC, MPC8260, and UCU/Saturn-specific paths behind preprocessor conditionals.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/lblast.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/lblast.h

Assembly fragment defining a Blast-board `mmuinit0` routine for PowerPC BAT startup mapping.

Key responsibilities:
- Clears 64 TLB entries with `TLBIE`.
- Maps `KZERO` to physical 0 with BAT0 and BAT1, covering 512 MiB in two 256 MiB regions.
- Maps `FPGABASE` uncached through DBAT2.
- Maps `INTMEM` direct/uncached through DBAT3.
- Leaves IBAT2 and IBAT3 unused.
- Enables IR/DR/RI/FP in MSR and returns through `RFI` into virtual mode.

Dependencies:
- Uses constants and macros from `mem.h` and the PPC assembler environment.
- Duplicates the non-`ucuconf` path now present directly in `l.s`.

Notable risks:
- Appears to be a legacy or include-style startup fragment; if included with `l.s`, duplicate `mmuinit0` definitions would conflict.
- Hard-coded BAT layout assumes Blast/MPC8260 board memory map.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/lblast.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/lucu.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/lucu.h

Assembly fragment defining a UCU-specific `mmuinit0` for PPC 755/Saturn-style startup.

Key responsibilities:
- Clears 64 TLB entries.
- Maps `KZERO` to physical 0 using BAT2 only, for a 256 MiB kernel DRAM window.
- Enables instruction/data MMU, recoverable exceptions, and FP through SRR0/SRR1 plus `RFI`.

Dependencies:
- Uses `mem.h` PowerPC/BAT constants and assembler macros.
- Mirrors the `ucuconf` `mmuinit0` branch embedded in `l.s`.

Notable risks:
- Legacy/include-style duplicate of code now present in `l.s`.
- BAT2-only setup is board-specific and relies on later `ucuconf` code copying BAT2 into other BAT slots.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/lucu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/m8260.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/m8260.c

MPC8260/PowerQUICC II board support for Plan 9 PPC systems, especially EST SBC8260/Blast-style boards.

Key responsibilities:
- Defines the 64-entry interrupt vector to SIMR/SIPNR mask mapping.
- Initializes `Mach`, clock rates, caches, FPU, bank-register fixes, Ethernet disable state, FPGA access width, and default `plan9.ini`.
- Provides hardware interrupt setup, vector enable/disable, interrupt acknowledge, and vector fetch.
- Implements CPM timer-based `fastticks`, `timerinit`, `timerset`, and timer interrupt handoff to `timerintr`.
- Creates configured shared physical segments for `fpgaN` and `dspN`.
- Provides CPM command execution via `cpmop` and shared I/O lock wrappers.
- Allocates CPM buffer descriptors and initializes FCC-style RX/TX descriptor rings with main-memory descriptors.
- Installs trap vectors, including special imiss/dmiss vectors for assembler miss handling.
- Implements a watchdog-like reboot attempt via `sypcr`.

Important behavior:
- Computes bus, CPM, BRG, VCO, CPU, and cycle frequencies from reset clock registers.
- Disables FCC Ethernet early because firmware may have left DMA buffers in arbitrary memory.
- Uses a default Plan 9 configuration string when flash `plan9.ini` is absent or uninitialized.
- Allocates FCC buffer descriptors in normal memory rather than dual-ported RAM to avoid 8260 A.1 cache/DMA hangs.
- `timerset` clamps too-near and too-far deadlines.

Dependencies:
- Depends on `m8260.h` hardware maps, `mem.h` board constants, PPC assembly helpers, and Plan 9 port initialization.
- Exports globals such as `iomem` and `etheraddr`.

Notable risks:
- Many register writes are board errata or hardware-layout assumptions.
- Timer and interrupt code assumes specific MPC8260 vector numbering.
- `bdalloc` boundary check is loose because it tests after assigning `p`.
- Reboot path is minimal and writes to a hard-coded address after enabling watchdog behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/m8260.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/m8260.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/m8260.h

Hardware register, descriptor, and CPM structure definitions for MPC8260/PowerQUICC II support.

Key contents:
- Buffer descriptor `BD` and ring `Ring` definitions plus descriptor status bits.
- Parameter RAM layouts for MCC, IOC, SCC, FCC, SMC UART, and related CPM peripherals.
- MMIO register structs for SCC, FCC, SMC, SPI, memory banks, ports, IDMA, SI, IMM, and the full `Imap` including dual-port RAM and internal registers.
- CPM command field masks, sub-block/page codes, channel IDs, operation codes, and clock routing constants.
- Function prototypes for ring/BD allocation, CPM operations, I/O locking, and reboot.

Role:
- Provides the C representation of MPC8260 hardware state used by UART, Ethernet, timer, interrupt, and CPM code.
- Encodes manual-derived register offsets with comments that act as the ABI between C code and memory-mapped device blocks.

Notable risks:
- Struct layout must match the exact hardware memory map; padding or compiler differences would be fatal.
- Several fields use broad reserved arrays and comments from the manual; maintenance requires hardware documentation.
- The header is tightly coupled to board memory constants from `mem.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/m8260.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/main.c

PPC Plan 9 kernel mainline, configuration parsing, initial process creation, and machine-independent boot sequencing glue.

Key responsibilities:
- Clears BSS and runs early initialization: `machinit`, `confinit`, allocator, traps, MMU, `plan9.ini`, interrupts, clock/timer, console, printing, process and device initialization, paging, swap, shared segments, FP baseline, first user process, and scheduler.
- Parses `plan9inistr` into a fixed `plan9ini` table and exposes `getconf`.
- Builds initial environment entries in `init0`.
- Creates the first user process with stack segment, text segment, copied `initcode`, and scheduler entry.
- Implements shutdown `exit`, process FP setup/save/restore hooks, memory sizing in `confinit`, ISA-style config parsing, and case-insensitive string helpers.

Important behavior:
- Supports only one `Mach`.
- Memory sizing uses board constants `MEM1SIZE`, `MEM2SIZE`, and the end of kernel image.
- User/kernel page split depends on `*kernelpercent` and CPU-server mode.
- `init0` creates root/dot, initializes devices, starts `alarm` and `mmusweep`, then enters user mode through `touser`.
- `procsave` lazily saves FPU state only when active.

Dependencies:
- Relies on board-specific `machinit`, `trapinit`, `mmuinit`, `hwintrinit`, `timerinit`, `sharedseginit`, and UART console code.
- Depends on Plan 9 port layer process, segment, page, channel, and environment APIs.

Notable risks:
- `MAXCONF` is both the number of config entries and the temporary line buffer length, so long config lines are not supported.
- Boot ordering is strict: traps/MMU/memory/device setup are interdependent.
- `confinit` is Blast-board-specific despite living in generic PPC directory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/mcc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/mcc.c

MPC8260 MCC2/TDM A:2 driver fragment intended for a T1-framer interface, but it is not integrated as normal Plan 9 kernel code.

Key responsibilities visible in the file:
- Declares MCC2 ioctl/read/write/open/release-style entry points.
- Provides `ioctl_parm` to configure SI mode register loopback/echo/normal operation.
- Handles ioctl cases for MCC mode, HPI read/write, FPGA read/write, memory read/write relative to the MPC8260 internal map, and SI RAM control reads.
- Contains Linux-style character device initialization using `register_chrdev`, `struct file`, `struct inode`, `copy_to_user`, `copy_from_user`, `MOD_INC_USE_COUNT`, and `printk`.

Important behavior:
- Accesses hard-coded HPI/FPGA physical regions and the internal memory map.
- Uses a global `mcc_iorw_t` command structure type from `mcc2.h`.
- The file ends at `#else` after `#ifndef MODULE`, indicating it is either incomplete or intentionally truncated.

Dependencies:
- Includes Plan 9 headers but then references Linux kernel APIs and types not provided by the surrounding Plan 9 tree.
- Depends on `mcc2.h`, many MCC/SI/CPM types, and external routines not defined in this file.

Notable risks:
- This file is almost certainly non-buildable in the Plan 9 kernel as-is.
- Direct user-controlled physical address read/write paths would be high-risk if active.
- The incomplete preprocessor/module tail suggests source import residue rather than maintained driver code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/mcc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/mem.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/mem.h

Shared PPC memory, register, MMU, trap, and address-layout constants for C and assembly.

Key contents:
- Selects `ucu.h` or `blast.h` depending on `ucuconf`.
- Defines byte/page/cache sizes, PTE/PTEG sizes, `MAXMACH`, `MACHSIZE`, `KSTACK`, and clock tick rate.
- Defines PowerPC SPR numbers, BAT register macros, MSR bit encodings, SRR1 TLB bits, exception vector codes, and special register assignments for `m` and `up`.
- Defines hashed-page-table and segment-map constants, PTE0/PTE1 encoding helpers, WIMG/PP bits, and HID0 cache bits.
- Defines virtual layout: `KZERO=0x80000000`, `KTZERO=0x80100000`, user text/stack top, `UREGSIZE`, `MACHADDR`, and `MACHPADDR`.
- Defines MPC internal memory and IO base constants plus `getpgcolor`.

Role:
- Forms the low-level ABI shared by `l.s`, trap handling, MMU code, mainline initialization, and hardware drivers.

Notable risks:
- Many assembly offsets and masks depend directly on these constants.
- `isphys(x)` uses the `KZERO` bit convention for this kernel layout.
- The selected board header radically changes memory sizes and PTE policy.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/mmu.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/mmu.c

PowerPC hashed-page-table MMU management for single-processor Plan 9.

Key responsibilities:
- Allocates and installs a per-processor hashed page table using SDR1.
- Uses segment registers and VSIDs to distinguish processes.
- Allocates MMU process IDs with color bits and background sweeping.
- `mmusweep` clears stale process IDs from procs and removes matching PTEs from the hash table.
- `mmuswitch` installs user segment registers or clears them for kernel procs.
- `putmmu` inserts or replaces hashed PTEs, flushes stale TLB entries, and performs text-page I/D cache maintenance.
- `flushmmu`, `mmurelease`, `checkmmu`, `countpagerefs`, and `cankaddr` provide required port interfaces.

Important behavior:
- Hash table size is heuristically based on physical memory.
- Process IDs reserve pid 0 and use top pid bits as sweep colors.
- If no MMU pid is available, `putmmu` loops through `sched()` until one is assigned.
- Kernel mappings are expected to come from BATs; only user segments are installed here.

Dependencies:
- Depends on PPC assembly helpers for SDR1, segment registers, TLB flush, cache flush, and process switching.
- Coupled to `fault.c`/`putmmu` caller expectations and `Page.cachectl`.

Notable risks:
- Comment states the design needs modification for multiprocessor use.
- PTE replacement uses a simple rotating slot within a PTEG.
- Background sweeping and pid exhaustion behavior depend on scheduler progress.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/msaturn.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/msaturn.c

UCU/Saturn PPC board support for interrupt controller setup, machine initialization, trap vectors, and basic reboot hooks.

Key responsibilities:
- Defines Saturn interrupt-controller register addresses and priority mapping.
- Initializes interrupt priority registers and disables all interrupts.
- Enables/disables interrupts by matching requested Plan 9 vector numbers to priority slots.
- Reads interrupt acknowledge/priority register in `intvec` and acknowledges via `intack`.
- Initializes `Mach`, bus/CPU/cycle frequencies, machine-check enable, L2/cache/HID state, FPU baseline, and default `plan9.ini`.
- Installs normal exception vectors through `sethvec`.
- Provides no-op `sharedseginit` and `reboot`.

Important behavior:
- CPU frequency is inferred from PLL register value; bus frequency from Saturn system config.
- Enables L2-related state through `getl2cr`/`putl2cr` and HID0 bits.
- Default configuration selects `ether0=type=saturn` and `sys=ucu`.

Dependencies:
- Depends on `msaturn.h`, `ucu.h`-selected memory constants, PPC assembly cache/SPR helpers, and generic trap code.

Notable risks:
- Interrupt mapping is tiny and board-specific.
- `intvec` logs and acknowledges unknown interrupt priorities.
- Reboot is unimplemented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/msaturn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/msaturn.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/msaturn.h

Small Saturn board interrupt-vector header.

Key contents:
- Defines `Vecuart0`, `Vecuart1`, `Vectimer0`, `Vecether`, and `Vecunused`.

Role:
- Shared by Saturn interrupt, UART, timer, and Ethernet code to agree on logical interrupt vector numbers.

Notable risks:
- Constants are tightly tied to `msaturn.c` priority table.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/msaturn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/mtx.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/mtx.c

Minimal placeholder MTX board-specific source.

Key contents:
- Includes normal kernel and MTX headers.
- Contains only a comment indicating MTX-specific interrupt handling belongs here.

Role:
- Acts as a stub or compilation anchor for an MTX configuration.

Notable risks:
- No functions are implemented; any MTX build expecting board operations from this file must get them elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/mtx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/saturntimer.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/saturntimer.c

Saturn board timer support for Plan 9 PPC.

Key responsibilities:
- Defines Saturn timer register addresses and control bits.
- Implements microsecond conversion via cycle counter and cached multiplier.
- Handles timer interrupts, clearing timer events, acknowledging interrupt controller state, and calling `timerintr`.
- Initializes timer0 as the periodic/kernel event timer and timer1 as the free-running fast tick source.
- Implements `fastticks` using timer1 plus a software seconds counter.
- Implements `timerset` by programming timer0 with clamped offset.

Important behavior:
- Timer1 events increment a `ticks` counter and are also handled opportunistically in `fastticks`.
- `timerset` temporarily leaves only timer1 enabled while computing/reprogramming timer0.
- `timer_ctl` is cached and rewritten with event-clear bits.

Dependencies:
- Depends on `msaturn.h`, `m->bushz`, interrupt enablement, and PPC `cycles`.

Notable risks:
- Direct MMIO access uses raw casts to Saturn addresses.
- `fastticks` asserts timer1 is enabled and mutates timer control state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/saturntimer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/trap.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/trap.c

PowerPC trap, interrupt, syscall, fault, note, and process register handling.

Key responsibilities:
- Manages interrupt handler registration through `intrenable`/`intrdisable`.
- Decodes PPC exception causes and dispatches external interrupts, decrementer clocks, data/instruction faults, TLB misses, syscalls, FP unavailable traps, and program exceptions.
- Implements lazy FP restore/init and FP state gating in trap/syscall return.
- Bridges PPC faults to common `fault()` through `faultpower`.
- Writes exception vectors with `sethvec` and miss vectors with `setmvec`.
- Dispatches interrupt vectors from board-specific `intvec`, calls registered handlers, acknowledges through `intend`, tracks timing/count statistics, and preempts.
- Provides stack/register dump helpers, `callwithureg`, `dumpstack`, and `dumpregs`.
- Sets up kernel process children, validates alignment, handles `execregs`, `forkchild`, `userpc`, `setregisters`, `setkernur`, and `dbgpc`.
- Implements full syscall dispatch and Plan 9 note delivery/return (`notify`, `noted`).

Important behavior:
- User trap entry records kernel-entry cycles and saves `up->dbgreg`.
- Syscalls take syscall number from `r3`; arguments are copied from user stack `Sargs`.
- `NOTED` is handled specially before normal notify.
- `notify` saves `Ureg` on the user stack and disables active FP state.
- Interrupt dispatch loops up to 64 vectors per external interrupt.

Dependencies:
- Must match `l.s` `Ureg` layout and exception frame conventions.
- Depends on board-specific `vectorenable`, `vectordisable`, `intvec`, `intend`.
- Uses port `systab`, notes, process, fault, and tracing infrastructure.

Notable risks:
- Contains diagnostic FP state checks that can print/dump/panic on inconsistencies.
- Vector patching emits raw instruction words and must stay ISA-encoding-correct.
- `if(vno > nelem(vctl))` should conceptually be `>=`; vector 256 would index out of range.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/uartsaturn.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/uartsaturn.c

Saturn dual-UART driver implementing Plan 9 `PhysUart` operations and console/debug output.

Key responsibilities:
- Defines Saturn UART register layout, bit encodings, two UART instances, and default UART configs.
- Provides PNP list, init/enable/disable, status, parity/stop/bits/baud changes, interrupt handling, polled getc/putc, and transmitter kick.
- Handles RX full, TX empty, and RX error interrupts.
- Selects console UART from `console=` config.
- Provides low-level `dbgputc`, `dbgputs`, and `dbgputx` on UART A.

Important behavior:
- Baud divisor uses `14745600/16`.
- `sukick` sends staged output when TX interrupt reports empty.
- `sugetc` uses a static buffered polled read path.
- `suinterrupt` explicitly calls `intack`.

Dependencies:
- Depends on `msaturn.h`, generic UART layer functions, and Saturn interrupt controller.

Notable risks:
- `sustatus` uses a stack buffer but calls `free(p)`, which is erroneous.
- `suenable` range check permits `nr == Nuart`, which is out of bounds.
- Busy-wait get/put paths can spin forever if hardware is unresponsive.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/uartsaturn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/uartsmc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/uartsmc.c

MPC8260 SMC UART driver implementing Plan 9 `PhysUart` for SMC1.

Key responsibilities:
- Defines SMC mode/event bits, BD error bits, and 32-byte RX/TX buffer sizing.
- Creates `SMC1` UART config and PNP list.
- `smcsetup` configures SMC parameter RAM, Port D pins, BRG, clock mux, and CPM init command.
- `smcinit` allocates receive/transmit BDs and buffers, initializes parameter RAM, clears events, and programs UART mode.
- Provides enable/disable, status, FIFO/no-op modem control, parity/stop/bits/baud changes, break stub, TX kick, interrupt RX/TX handling, polled getc/putc, and console selection.

Important behavior:
- SMC BDs must be allocated from dual-port RAM via `bdalloc`.
- RX interrupt invalidates data cache before copying received bytes.
- TX flushes cache before handing the descriptor to CPM.
- Only SMC1 is configured; SMC2 config is commented out.

Dependencies:
- Depends on MPC8260 `imm.h`/`m8260.h`, CPM command helpers, I/O locking, UART framework, and board interrupt vector constants.

Notable risks:
- `smcstatus` repeats the Saturn stack-buffer/free bug.
- Some mode setters disable RX/TX but do not explicitly restore enable bits in all cases.
- Polled getc/putc paths spin on descriptor ownership.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/uartsmc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/uartsmc.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/uartsmc.h

Shared data declaration for MPC8260 SMC UART state.

Key contents:
- Defines `UartData` fields for SMC number, SMC registers, SMC parameter RAM, RX/TX buffers, RX/TX BDs, and init/enable state.
- Declares `uartdata[Nuart]`, `baudgen`, and `smcsetup`.

Role:
- Lets board-specific and UART code share SMC UART state and setup entry points.

Notable risks:
- The header defines storage, not just extern declarations, so including it in multiple C translation units would duplicate `uartdata`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/uartsmc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/ucu.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/ppc/ucu.h

UCU/Saturn board memory and PTE policy constants.

Key contents:
- Defines flash and memory sizing: 32 MiB main memory, no second memory bank, no flash `plan9.ini`.
- Defines Saturn MMIO base and 128 TLB entries.
- Defines PPC PTE policy bits for valid/write/read-only/uncached mappings.

Role:
- Selected by `mem.h` under `ucuconf` to specialize PPC memory layout and MMU policy.

Notable risks:
- Uses `FLASHMEM` and `PLAN9INI` as `~0`, intentionally signaling no usable flash config.
- The `PTEVALID` definition encodes write-through global cache policy.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ppc/ucu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/c_fcr0.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/c_fcr0.s

Tiny MIPS assembly stub for reporting floating-point implementation identity.

Key responsibilities:
- `C_fcr0` returns `0x500`, claiming an R4000-style implementation with LL/SC support.

Role:
- Supports MIPS user/runtime code that probes FCR0 to choose locking/floating-point behavior.

Notable risks:
- It reports a synthetic FP implementation rather than real hardware FP state, matching this port’s FP emulation strategy.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/c_fcr0.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/clock.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/clock.c

Atheros AR7161/RouterBOARD RB450G MIPS clock, watchdog, delay, and fast-tick support.

Key responsibilities:
- Controls watchdog timer: silence, reset-on-timeout, immediate reset, stop, and shutdown.
- Implements millisecond and microsecond delays using CP0 count.
- Handles clock interrupts by programming CP0 compare, petting watchdog, and calling `timerintr`.
- Calibrates approximate MIPS rate with an instruction loop.
- Initializes per-Mach timing fields, compare interrupt period, and enables clock interrupt level.
- Implements `timerset`, `fastticks`, `µs`, `perfticks`, `lcycles`, `cycles`, and `syncclock`.

Important behavior:
- Assumes RB450G base tick frequency of 680 MHz divided by MIPS 24K count divisor 2.
- `microdelay` resets CP0 count if target wraps or is too close to `~0`.
- `fastticks` rewrites compare if the next interrupt is too far away to avoid lost interrupts.
- Multiprocessor sync support exists but `conf.nmach` is effectively one for this board.

Dependencies:
- Depends on CP0 assembly helpers, AR7161 reset/watchdog registers from `io.h`, and Plan 9 timer infrastructure.

Notable risks:
- Frequency is hard-coded for RB450G.
- Delay and fasttick code mutate CP0 count/compare under `splhi`, which affects timing assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/dat.h

RouterBOARD/MIPS machine data definitions shared with the Plan 9 port layer.

Key contents:
- Type forwards for kernel machine objects and `Tval`.
- MIPS boot magic definitions.
- Machine-specific `Lock`, `Label`, `Confmem`, and `Conf` structures.
- Emulated FP state definitions and `FPsave` structure, including raw 32-bit FP registers, FCR31, branch-delay emulation state, and stuck-fault tracking.
- Per-process PMMU state.
- `Mach` layout, with first fields explicitly fixed for `l.s`.
- `KMap` and software TLB entry structures.
- Active-machine global and external register variables `m` and `up`.

Role:
- Defines the ABI between MIPS assembly, MMU/fault code, process code, FP emulator, and the generic Plan 9 port layer.

Notable risks:
- `Mach` first-member ordering is hard-coded in assembly.
- FP emulation state is exposed through `/dev/proc` expectations by keeping registers first.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/devarch.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/devarch.c

RouterBOARD architecture device `#P`, exposing CPU/timer/MMU/FP-emulation status and controls.

Key responsibilities:
- Implements dynamic arch-file registration through `addarchfile`.
- Provides Plan 9 device methods for attach, walk, stat, open, read, write, and close.
- Exposes `cputype`, `timebase`, and `archctl`.
- `archctlread` reports CPU MHz, software-TLB hash collisions, kernel/user TLB misses, FP emulator debug status, and optional fault stats.
- `archctlwrite` controls `fpemudebug` when compiled with `FPEMUDEBUG`.

Dependencies:
- Uses Plan 9 dev/net utility functions, command parsing, MIPS timing helpers, and `faultsprint`/`fpemuprint`.

Notable risks:
- `Qmax` is fixed at 16 and files cannot be deleted once added.
- `nsread` is present but not registered.
- Debug command name is replaced with `dummy` unless `FPEMUDEBUG` is enabled.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/devarch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/devether.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/devether.c

Atheros AR71xx Ethernet driver and Plan 9 `#l` Ethernet device for RouterBOARD RB450G.

Key responsibilities:
- Defines ARGE MAC/DMA register layout, descriptor format, controller state, and two fixed interface descriptors.
- Manages generic Ethernet netif plumbing: probing, attach, walk/open/read/write/stat, loopback, output queue, and shutdown.
- Initializes RX/TX DMA descriptor rings and a shared receive-block pool.
- Handles RX/TX interrupts by waking receive/transmit kprocs.
- RX kproc drains descriptors, strips CRC, and passes packets through `etheriq`.
- TX kproc reclaims descriptors, copies queued blocks to hardware descriptors, kicks DMA, and handles underruns.
- Provides MII/switch scaffolding, though AR8316 switch support is under `NOTYET` and normal `athmii` is stubbed.
- Implements multicast/promiscuous stubs and interface statistics.

Important behavior:
- Leaves much of ARGE0 as RouterBOOT initialized; copies or configures only key registers.
- Only all-relevant DMA interrupts are enabled; TX interrupts are mostly used for ring pressure/underrun.
- Uses uncached `KSEG1` descriptor memory and explicit `dcflush`/`coherence` around DMA buffers.
- Computes input/output queue sizes from link Mbps with sanity caps.
- Uses global `arge0mac`/`arge1mac` from RouterBOARD config.

Dependencies:
- Depends on Plan 9 `netif`, AR7161 interrupt levels, MII helper headers, block allocator, cache helpers, and `io.h`.

Notable risks:
- File TODO notes promiscuous mode and ether1/switch/MII initialization are incomplete.
- MII initialization is stubbed, so link setup relies on firmware or fixed config.
- Shared RX block pool is global across controllers.
- Direct DMA descriptor ownership requires strict cache coherency discipline.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/devether.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/etherif.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/etherif.h

RouterBOARD Ethernet interface declarations.

Key contents:
- Defines `MaxEther=2` and `Ntypes=8`.
- Defines `Ether` controller structure with hardware fields, queue, MAC address, optional driver callbacks, and embedded `Netif`.
- Declares `etheriq`, `addethercard`, `ethercrc`, and `parseether`.
- Provides ring index helper macros `NEXT` and `PREV`.

Role:
- Shared contract between Ethernet device code and any controller-specific drivers.

Notable risks:
- Callback fields are guarded by `MULTIETHERTYPES`; this port’s `devether.c` mostly provides a single built-in controller path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/etherif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/ethermii.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/ethermii.c

Generic MII/PHY helper implementation for Ethernet drivers.

Key responsibilities:
- Probes PHY addresses in a mask, reads PHY IDs, allocates `MiiPhy`, and selects a current PHY.
- Provides current-PHY register read/write wrappers.
- Resets a PHY through BMCR reset.
- Programs auto-negotiation advertisement for 10/100, pause, and optional 1000BASE-T modes.
- Determines link status, speed, duplex, and flow-control from BMSR, ANLPAR, MSCR/MSSR, and advertised capabilities.

Important behavior:
- Reads BMSR twice in `miistatus` because link status is sticky.
- Stores user/driver advertisement preferences in `MiiPhy`.
- Handles 1000BASE-T before falling back to 10/100 negotiation.

Dependencies:
- Requires driver-supplied `mir` and `miw` MDIO operations.

Notable risks:
- Returns `-1` for incomplete autonegotiation or link down; callers must tolerate transient failures.
- No freeing path for allocated `MiiPhy` objects.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/ethermii.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/ethermii.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/ethermii.h

MII/PHY register and structure definitions.

Key contents:
- Defines standard MII register numbers: BMCR, BMSR, PHY IDs, autonegotiation, gigabit control/status, and extended status.
- Defines bit masks for BMCR, BMSR, ANAR/ANLPAR, MSCR, MSSR, and ESR.
- Defines `Mii` with PHY table, current PHY, controller pointer, and MDIO callbacks.
- Defines `MiiPhy` with OUI, address, advertisement state, link/speed/duplex, and flow-control flags.
- Declares MII helper functions.

Role:
- Shared API for Ethernet drivers that need generic PHY probing and autonegotiation.

Notable risks:
- Covers common standard registers only; vendor-specific PHY setup must live elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/ethermii.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/faultmips.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/faultmips.c

MIPS page-fault decoding, validation, diagnostics, and alignment checking.

Key responsibilities:
- `tstbadvaddr` inspects the faulting instruction and checks whether CP0 BadVAddr matches the effective address implied by load/store opcode and base register.
- Tracks repeated identical faults to detect stuck fault handling.
- `faultsprint` optionally reports max repeated fault info.
- `faultmips` aligns fault address to page, determines read/write, calls common `fault()`, posts user notes on failure, and panics for kernel faults.
- Implements MIPS `validalign`.

Important behavior:
- Handles branch-delay faults by testing the delay-slot instruction.
- Treats TLB modification/store exceptions as writes, most others as reads.
- Ignores apparent spurious BadVAddr mismatches after logging.

Dependencies:
- Depends on `reg()` from FP/MIPS support, `seg`, `fault`, `postnote`, `tlbvirt`, and trap exception names.

Notable risks:
- Instruction decoder covers many but not every possible memory-reference opcode.
- Stuck-fault diagnostics are mostly disabled unless `Debug` is changed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/faultmips.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/fns.h

RouterBOARD/MIPS function prototype and low-level macro header.

Key contents:
- Imports port-level prototypes.
- Declares board, clock, cache, TLB, MMU, trap, FP, PCI, I/O, UART, interrupt, syscall, watchdog, and architecture helper functions.
- Defines `procsetup` as FP initialization.
- Declares register helpers such as CP0 config/status/count/compare, TLB accessors, cache flushes, and assembly process-transition routines.
- Defines `waserror`, `KADDR`, `PADDR`, and `KSEG1ADDR`.

Role:
- Central compile-time contract among MIPS assembly, C platform code, device drivers, and the generic Plan 9 kernel.

Notable risks:
- Prototype mismatches here can hide ABI issues with assembly routines.
- Some declared functions are platform stubs or provided outside this batch.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/fpimips.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/fpimips.c

MIPS COP1 floating-point emulator for a MIPS32r2/24K Plan 9 port without usable hardware FP.

Key responsibilities:
- Keeps raw 32-bit FP register words in `FPsave` and converts to/from Plan 9 internal FP only when needed.
- Decodes COP1 instructions, FP loads/stores, CPU/FP register moves, control-register moves, arithmetic, conversion, comparison, and FP branches.
- Emulates single/double/word/vlong conversions and basic arithmetic using common `fpi` routines.
- Handles MIPS FP register-pair endian ordering for double/vlong transfers.
- Implements FP branch delay-slot behavior, including emulating FP delay slots or executing non-FP delay slots in user mode with watchpoint-assisted return.
- Provides `fpwatch` to complete delayed branch execution after a watchpoint trap.
- Implements branch classification and branch target calculation for integer and FP branches.
- Initializes emulated FP state and Plan 9 constants F24=0.0, F26=0.5, F28=1.0, F30=2.0.
- Exposes `reg()` for fault code and optional debug output through `fpemuprint`.

Important behavior:
- Fakes `MOVW FCR0,R1` as `0x500` to advertise R4000-style LL/SC capability.
- Can emulate runs of consecutive FP instructions in one trap.
- Rejects floating point in note handlers via `FPillegal`.
- Does not attempt to fully update MIPS FP exception status; arithmetic is done in double precision.

Dependencies:
- Depends on Plan 9 `fpi` internal FP library, `Ureg` register layout, MIPS watch registers, cache flush helpers, `Tos.kscr`, and trap handling.

Notable risks:
- Several operations are explicitly unimplemented: sqrt and many newer conditional/reciprocal forms.
- 64-bit DMTC1/DMFC1 paths print warnings that word order may be wrong.
- Watchpoint-assisted delay-slot execution is intricate and globally serialized by `watchlock`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/fpimips.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/init9.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/init9.s

Tiny MIPS userland bootstrap assembly for Plan 9.

Key responsibilities:
- `_main` sets static base register `R30`.
- Places `boot(SB)` and a pointer to arguments onto the stack frame.
- Calls `startboot(SB)`.

Role:
- Entry shim for the initial user boot program.

Notable risks:
- Assumes exact Plan 9 MIPS calling convention and initial stack layout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/init9.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/initreboot.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/initreboot.s

Minimal MIPS assembly helper for reboot/runtime entry on RouterBOARD.

Key responsibilities:
- `_main` sets `R30` and jumps directly to C `main`.
- Defines `ret` target used by barrier macros.
- Provides `setsp`, `coherence`, and full I/D cache clean/invalidate helper `cleancache`.

Role:
- Small standalone low-level support for reboot or reduced initialization contexts.

Dependencies:
- Includes `mem.h` and `mips.s`; uses MIPS cache/barrier macros.

Notable risks:
- Cache flush operates by index over fixed cache-size constants.
- Interrupt state is changed during cache cleaning and restored afterward.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/initreboot.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/io.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/io.h

RouterBOARD AR7161/MIPS board IO, interrupt, reset, PCI, and SMBus definitions.

Key contents:
- Defines `Mhz`, DUART frequency, CPU interrupt levels, and interrupt-level assignments for PCI, USB, Ethernet, UART/APB, and clock.
- Defines AR7161 reset/watchdog/APB/PCI interrupt/reset register addresses and bit masks.
- Defines `Vctl` interrupt handler descriptor.
- Provides PCI bus encoding helpers, PCI config register offsets/classes, `Pcisiz`, and `Pcidev`.
- Defines PCI vendor IDs used elsewhere.
- Defines PCI/ISA window address helpers.
- Defines SMBus transaction types and `SMBus` structure.

Role:
- Hardware contract for clock/watchdog, interrupt routing, PCI support, Ethernet, USB, UART, and any future SMBus users.

Notable risks:
- Register addresses are hard-coded for this SoC/board.
- `PCIWINDOW` and `ISAWINDOW` are zero, so DMA address translation is assumed identity-like.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/l.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/rb/l.s

MIPS 24K RouterBOARD low-level assembly for boot, traps, software TLB, cache, atomics, and CP0 access.

Key responsibilities:
- `start` initializes `R30`, disables interrupts, validates data-segment alignment, clears compare/status/cause, disables watchdog action, cleans cache, configures KSEG0 caching, initializes `Mach`, clears BSS, and calls `main`.
- `touser` enters user mode at `UTZERO+32`.
- Implements interrupt priority helpers: `intron`, `introff`, `idle`, `wait`, `splhi`, `splx`, `spllo`, `islo`.
- Provides context helpers `setlabel`/`gotolabel`.
- Implements TLB operations: `puttlb`, `puttlbx`, `gettlbx`, `gettlbp`, `gettlbvirt`, wired/page-mask/random helpers.
- Implements software-TLB hash lookup in the UTLB miss vector, filling hardware TLB directly on cache hits or falling back to full exception handling.
- Provides exception vectors and `exception` entry handling for user/kernel traps and syscalls.
- Saves/restores `Ureg` frames, implements `forkret`, and handles kernel `wait` PC advancement.
- Implements atomics `tas`, `_xinc`, `_xdec`, `cmpswap`.
- Implements `icflush`, `dcflush`, `cleancache`.
- Exposes CP0 status/count/compare/config/cause/watch/perf helpers and fake `C_fcr0`.

Important behavior:
- Software TLB hash macro must match C `mmu.c` calculations.
- Exception entry uses separate user and kernel stack paths.
- Syscall path calls C `syscall` and returns via `sysrestore`.
- Cache operations switch between cached/uncached execution with barrier macros.
- `C_fcr0` reports `0x500`, consistent with FP emulator/runtime expectations.

Dependencies:
- Must match `mem.h`, `mips.s`, `dat.h` `Mach` and `Ureg` offsets, and C trap/MMU/fault code.

Notable risks:
- Register save/restore order is a hard ABI with C.
- UTLB fast path correctness depends on software TLB hashing and ASID handling.
- Boot has a hard sanity check for data-segment alignment and returns to ROM if invalid.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/rb/l.s -->