# Group Research: group_6_9front_sources_os_plan9_9front_sys_src_9_kw_ether1116_c_sources_os_pla_383c50e6bf0d

Scope: `Docs/research_subset_a.md` includes `sources/os/plan9/9front`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/ether1116.c -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/ether1116.c

Kirkwood Marvell gigabit Ethernet driver for 88e1116/88e1121-class PHY setups used by SheevaPlug, OpenRD, and GuruPlug boards. It defines the MAC register map, RX/TX DMA descriptor formats, interrupt causes, MIB counters, PHY pages, and controller state.

The driver uses uncached, aligned RX and TX descriptor rings, a private receive block pool, explicit L1/L2 cache maintenance around DMA buffers, and a receive kproc (`rcvproc`) woken by interrupts to avoid doing all packet input at interrupt level. TX queuing is ring based, with `txreplenish`, `transmit`, and queue restart logic through `txkick`; RX uses `rxreplenish`, `receive`, and `rxkick`.

MII/PHY support is substantial. `miird`/`miiwr` drive the Marvell SMI register, `mymii` handles a board-specific dual-port PHY hack, and `kirkwoodmii` performs reset/autonegotiation/status handling. `miiphyinit` switches PHY pages to configure LEDs, RGMII power, timing delay, MDIX, and power/energy-detect behavior.

Initialization resets/quiesces the controller, programs DRAM access windows, assigns MAC/filter tables, configures SDMA burst/coalescing, enables selected interrupts, starts the RX queue, and installs the Plan 9 `Ether` entry points. Statistics are accumulated from clear-on-read MIB counters and exposed through `ifstat`.

Notable risks: several comments document hardware errata and "magic" delays/register values; jumbo mode is deliberately disabled because the input queue cannot handle it; MAC fallback for second controllers mutates controller 0's address; interrupt handling has special cases for GuruPlug RX errors and spurious TX-buffer interrupts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/ether1116.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/flashkw.c -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/flashkw.c

SheevaPlug/Kirkwood NAND flash driver for the glueless NAND interface, focused on Hynix/Samsung large-page NAND chips. It maps the command/address/data registers through address bit aliases and implements the Plan 9 flash interface.

The driver probes NAND by resetting the chip, polling status, reading ID bytes, matching vendor/device IDs, and deriving page, erase-block, and spare sizes from the ID fields. It supports block erase, page read, page write, and unaligned read/write by read-modify-write of whole pages.

ECC is software based using `nandecc` and `nandecccorrect`, computed per 256-byte chunk and stored in the last 24 spare bytes for a 2 KiB page. Reads validate and correct one-bit data/ECC errors; uncorrectable ECC errors fail the read. A single-page cache avoids repeated NAND reads and supports partial-page rewrites.

Hardware access is serialized with `nandclaim`/`nandunclaim`, which toggles the NAND chip-enable control bit. `ctlrwait` polls status and resets the flash if it appears stuck.

Notable risks: comments say this should eventually merge with the generic NAND code; erase invalidates the whole single-page cache; write support is page-granular internally and assumes spare area is large enough for the ECC layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/flashkw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/fns.h

Kirkwood ARM platform function declarations and low-level helper macros. It combines imported port-layer prototypes with machine-specific assembly/C routines used across boot, MMU, traps, cache management, interrupts, process setup, UART, FPU emulation, and memory allocation.

Key exported areas include cache and L2-cache maintenance, CP15 register accessors, TLB operations, process save/restore hooks, interrupt registration, vector setup, MMU mapping helpers, uncached allocation, and early UART output. `coherence` is defined as `barriers`.

The file also defines `KADDR`, `PADDR`, `MASK`, PCI bus encoding helpers, and a `wave(c)` macro for emergency pre-console UART output through `PHYSCONS`.

Notable risks: comments explicitly say `KADDR`/`PADDR` are "not good enough"; the header is a broad platform contract and depends heavily on matching assembly symbol names.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/io.h -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/io.h

Kirkwood I/O and SoC register definition header. It defines bus types, PCI BDF helpers, internal register base addresses, SoC revision constants, interrupt vector numbers, interrupt controller register structures, CPU control/status registers, DRAM/window target attributes, and PCIe register layout.

Important hardware mappings include eFuse, PCI/PCIe config space, MPP, SDIO, interrupt banks, bridge interrupts, CPU reset/clock/L2 registers, and the Marvell PCIe capability/configuration block. It also defines DRAM target/attribute constants used by Ethernet and USB bridge address windows.

This file is consumed by platform drivers such as Ethernet, EHCI, UART, trap/interrupt code, and architecture reset/setup code.

Notable risks: several declarations are partial hardware maps with comments saying "some day" or "if we actually use these"; register offsets must match the Marvell 88F6281/Kirkwood manuals.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/l.s -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/l.s

Kirkwood ARMv5/ARM926EJ-S boot and low-level assembly. `_start` is entered from U-Boot with the MMU disabled, switches to SVC mode, disables MMU/caches, flushes L1/L2, creates initial section mappings, enables the MMU/caches, warps execution into the virtual kernel mapping, clears the low identity map, sets the Mach stack, and calls `main`.

The file also contains an unused `_reset` path, emergency UART output helper, cache enable/disable and L1 cache maintenance routines, Marvell L2 cache control/flush/invalidate routines, MMU enable/disable/TLB invalidation, CP15 register accessors, interrupt priority routines (`spl*`), atomic/tas helpers, label save/restore, idle wait-for-interrupt, and barrier wrapper.

The initial page tables map low DRAM temporarily, map 512 MiB at `KZERO`, and map MMIO. Later C code refines vector and I/O mappings.

Notable risks: the code contains hardware-specific cache-flush loops and SheevaPlug L2 sequences; comments call out ARM/assembler ambiguities and deprecated `SWPW` use for tas.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/lexception.s -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/lexception.s

Kirkwood ARM exception-vector assembly. It defines the vector stubs copied by `trapinit`, the vector table, syscall/SWI entry, undefined instruction, prefetch abort, data abort, IRQ, FIQ, mode switching to SVC, and trap-frame save/restore paths.

`_vsvc` handles syscalls from SVC mode and calls `syscall`. `_vswitch` transitions from exception modes into SVC mode and distinguishes user vs kernel-origin traps based on SPSR. Both paths build a Plan 9 `Ureg`, reload kernel static base and extern-register state, call `trap`, then restore registers and return with `RFE`.

The file also provides `setr13` for installing per-mode stacks.

Notable risks: several comments address Plan 9 assembler `MOVM` ambiguity; correctness depends on exact `Ureg` layout and banked ARM register behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/lexception.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/lproc.s -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/lproc.s

Small Kirkwood ARM process-transition assembly file. `touser` creates the first transition to user mode by installing the user stack pointer, setting SPSR to user mode, pushing the user entry PC (`UTZERO+0x20`), and returning through the simulated `RFE`.

`forkret` restores a saved trap frame for a newly forked process and returns to the interrupted context through `RFE`.

Notable risks: comments document that Plan 9 assembler `RFE` is not the ARMv6 instruction but a pre-v6 load-multiple-with-SPSR behavior; this is tightly coupled to trap-frame layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/lproc.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/main.c -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/main.c

Kirkwood kernel C entry and platform bring-up. It parses early `plan9.ini` from `CONFADDR`, manages configuration variables, initializes Mach state, memory configuration, devices, processes, and the first user process.

`main` is called after assembly has enabled the MMU. It handles possible data-segment realignment, zeros BSS, initializes console UART, machine state, architecture reset, MMU, traps, clock, printing, memory, devices, user process, and scheduler.

Reboot support serializes the current configuration back into boot args, shuts down devices/clocks, clears secret memory, copies `rebootcode` to `REBOOTADDR`, flushes caches, and jumps into the trampoline with physical entry/code/size.

`confinit` hard-codes Sheeva memory as 512 MiB minus an 8 KiB reservation, excludes kernel pages, and sizes process, swap, image, interrupt, and memory pools.

Notable risks: memory sizing is static for the platform; comments warn data segment misalignment can fail late; `writeconf` must fit in the fixed boot-args area.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/mem.h -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/mem.h

Kirkwood memory-layout and page-table constants shared by C and assembly. It defines page size, stack sizes, kernel/user address ranges, boot-args location, page-table/Mach placement, reboot-code address, clock constants, cache line size, software PTE flags, and physical SoC regions.

The layout maps physical DRAM at `KZERO` (`0x60000000`), starts kernel text at `KZERO+0x800000`, stores early config at `KZERO+4 KiB`, reserves page tables/Mach near `KZERO+64 KiB`, and uses `VIRTIO == PHYSIO` for MMIO.

It also defines physical addresses for DRAM, internal registers, UART, NAND variants, boot ROM, and CESA SRAM.

Notable risks: comments document fragile early memory placement around U-Boot, vectors, Mach, and L1/L2 PTE storage.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/mmu.c -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/mmu.c

Kirkwood ARM MMU management. It builds/refines vector and MMIO mappings, manages process L1/L2 page-table state, switches address spaces, installs user PTEs, and exposes simple kernel mapping helpers.

`mmuinit` maps high vectors and virtual zero through L2 tables to physical DRAM, replaces the broad MMIO section with small-page mappings, optionally exposes crypto sandbox pages, and stores the L1 pointer in `m->mmul1`.

Per-process mappings use coarse L1 entries pointing to small-page L2 tables stored in `Proc.mmul2`. `mmuswitch`, `flushmmu`, `mmurelease`, and `putmmu` maintain L1 entries, write back caches, invalidate TLBs, and flush I-cache for text changes.

`mmuuncache`, `mmukmap`, `mmukunmap`, `cankaddr`, `vmap`, and `vunmap` provide limited section-based helpers for uncached memory and physical mapping.

Notable risks: comments identify wasteful 4 KiB allocation for 1 KiB L2 tables, a disabled buggy optimization in `mmul1empty`, and temporary/crocked `vmap` behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/rebootcode.s -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/rebootcode.s

Kirkwood reboot trampoline assembly copied to `REBOOTADDR` before reboot. It disables caches/MMU safely, remaps low physical memory, copies the already-loaded new kernel image to its physical destination, flushes caches, and jumps to the new kernel entry.

`main` receives physical entry, source, and byte count. `cachesoff` flushes caches, disables cache bits, recreates identity mappings, invalidates TLBs, and reverts addressing state so the MMU can be disabled. Local implementations of `_r15warp`, `mmudisable`, `mmuinvalidate`, and `cacheuwbinv` make the trampoline self-contained.

Notable risks: code must run safely while transitioning away from the normal kernel mapping; it avoids loader-reserved registers and uses a tiny stack near the destination.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/rebootcode.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/trap.c -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/trap.c

Kirkwood ARM trap, fault, and interrupt handling. It defines handler tables for low, high, and bridge interrupt banks, installs vectors/stacks, dispatches interrupts, handles ARM fault status codes, and provides debug register/stack dump helpers.

`trapinit` maps vector code into `HVECTORS`, initializes banked stacks, disables/clears interrupt sources, registers high/bridge summary handlers, and enables watchdog/access-error bridge interrupts. `intrenable`/`intrdisable` attach one handler per interrupt bit and update masks.

`trap` handles IRQs, prefetch aborts, data aborts, and undefined instructions. Data aborts inspect FSR/FAR and decide between VM fault handling, user notes, or kernel panic. Undefined user instructions are passed to ARM floating-point emulation before posting a debug note.

The file also supports interrupt timing histograms, probing fault-prone addresses, stack traces, and register dumps.

Notable risks: interrupt registration silently ignores duplicate handlers; fault probing uses global state and a lock; trap behavior depends on exact PC correction for abort types.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/uartkw.c -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/uartkw.c

Kirkwood UART driver for the Marvell 16550-like console UART. It defines UART register layout and status/control bits, one controller, one console UART, interrupt-driven RX/TX, and polling getc/putc support.

`kw_enable` enables FIFO and RX/TX interrupts through the high interrupt bank. `kw_intr` services THR-empty and RX-data causes, dispatching to `uartkick` and `kw_read`. `kw_kick` pushes up to 16 bytes to the transmitter. Console setup binds `consuart` and applies `b115200 l8 pn s1 i1`.

Most line-control methods (`baud`, bits, stop, parity, modem, RTS/DTR/FIFO) are stubs returning success or doing nothing, so the port relies on existing firmware/default UART setup.

Notable risks: frequency is set to zero, baud programming is not implemented, and several paths lazily initialize `regs` because early print paths can run before normal PNP.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/uartkw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/usbehci.h -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/usbehci.h

Kirkwood-specific EHCI header overriding generic USB debug macros and defining EHCI capability, operational, debug-port, polling, and controller structures. It contains register bits for EHCI command/status/interrupt/config/port/debug fields plus the Kirkwood/Freescale-flavored operational register layout.

`Ctlr` is the platform-private state used by generic EHCI code: capability/operational register pointers, DMA allocators, frame list, async/periodic queue heads, isochronous state, interrupt counters, and polling rendezvous state.

The `Eopio` layout includes standard EHCI registers, Kirkwood OTG/device endpoint registers, and Freescale-style snoop/priority/system interface registers.

Notable risks: comments say some Kirkwood registers are undocumented publicly and may now be standard; this header is tightly coupled to the generic EHCI implementation's expected private structures.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/usbehci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/usbehcikw.c -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/usbehcikw.c

Kirkwood USB EHCI host-controller glue. It discovers a fixed EHCI controller at `soc.ehci`, configures bridge address windows and PHY registers, invokes generic EHCI memory/linkage, and registers the host-controller type.

`ehcireset` resets the controller, clears high address segment, chooses frame-list size, programs USB bridge windows for two 256 MiB DRAM chip-selects, powers/calibrates the PHY, applies Marvell errata and guideline magic values, and leaves the controller stopped for generic setup.

`reset` allocates/claims one controller, sets HCI port/IRQ/nports, assigns uncached DMA allocation hooks, calls `ehcireset`, `ehcimeminit`, and `ehcilinkage`, and enables the USB interrupt.

Notable risks: many PHY and mode settings are magic values from errata/Linux; `findehcis` assumes fixed Sheeva/Kirkwood addresses and only one controller instance.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/usbehcikw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/archlx2k.c -->
# File Research: sources/os/plan9/9front/sys/src/9/lx2k/archlx2k.c

Minimal LX2K architecture hook. It disables the ARM SBSA watchdog by writing zero to the watchdog control/status register at `VIRTIO+0x13a0000`.

`archlx2klink` performs this watchdog shutdown during platform link/setup.

Notable risks: the watchdog address is hard-coded and there is no validation or status readback.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/archlx2k.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/clock.c -->
# File Research: sources/os/plan9/9front/sys/src/9/lx2k/clock.c

LX2K ARM64 clock and delay implementation using the ARM generic timer and performance counter. It enables PMCCNTR, user access to counters, CNTP timer operation, computes CPU frequency by measuring PM cycles over a generic-timer interval, and registers the physical non-secure timer interrupt.

`fastticks` reads `CNTPCT_EL0` and reports `CNTFRQ_EL0`; `timerset` programs `CNTP_TVAL_EL0`; `microdelay` and `delay` spin on computed microseconds. `synccycles` provides a barrier-style multi-CPU synchronization helper, though this platform header sets `MAXMACH` to one.

Notable risks: `clockshutdown` is empty; CPU frequency measurement assumes a stable counter and PMCCNTR setup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/9/lx2k/dat.h

LX2K ARM64 machine data definitions. It defines `Conf`, `Confmem`, FPU save state, process and machine MMU state, `Mach`, `ISAConf`, device config structures, hardware register types, and extern-register bindings for `m` and `up`.

The platform uses ARM64 FP/SIMD state (`FPalloc` with 32 128-bit registers), a `PFPU` state model, and a page-table based `MMMU`/`PMMU` design with ASIDs. `Mach` includes MMU top-level pointer, FPU state, CPU type/frequency fields, and Plan 9 per-machine data.

Notable risks: `MAXSYSARG`, AOUT magic, FPU state constants, and MMU fields must match shared port code and assembly trap-frame conventions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/9/lx2k/fns.h

LX2K ARM64 platform function declarations. It exposes low-level assembly routines for exceptions, atomics, interrupt priority, user entry, FPU control, SMC calls, TTBR/TLB maintenance, cache maintenance, MMU helpers, clock, trap/IRQ, UART, DMA flushing, PCI config/interrupts, and platform configuration.

The header defines `PADDR`/`KADDR` through platform functions rather than simple masks, and declares Plan 9 linkage points such as `trapinit`, `intrinit`, `mmu1init`, `putasid`, `meminit`, and `uartconsinit`.

Notable risks: declarations include broader SoC APIs (`ccm`, `gpc`, `iomux`, `gpio`, `lcd`) that are not implemented in this group, implying shared ARM64 platform expectations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/gic.c -->
# File Research: sources/os/plan9/9front/sys/src/9/lx2k/gic.c

LX2K GICv3 interrupt controller driver. It defines GIC distributor and redistributor register offsets, locates the redistributor for each CPU, initializes interrupt groups/priorities/targets, enables the CPU interface, dispatches IRQ/FIQ interrupts, and maps PCI interrupts through the PCI layer.

`intrinit` disables/clears the distributor on CPU 0, resets SPI configuration, initializes SGI/PPI redistributor state for the current CPU, then enables ICC group 1 handling. `irq` reads `ICC_IAR1_EL1`, ignores spurious IDs, dispatches matching `Vctl` handlers, marks clock interrupts, and EOIs through `ICC_EOIR1_EL1`.

`intrenable` supports normal IRQs, a special FIQ path, PPI/SPI enablement, priority programming, CPU target selection, and PCI delegation when the TBDF is a PCI bus value. `intrdisable` only delegates PCI disable and otherwise does not remove normal GIC handlers.

Notable risks: handler chains are bucketed by `intid % 32`; non-PCI `intrdisable` is effectively unimplemented; SPI targeting assumes CPU 0.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/gic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/io.h -->
# File Research: sources/os/plan9/9front/sys/src/9/lx2k/io.h

LX2K I/O constants. It defines interrupt numbering for GIC PPIs/SPIs used by timer, UART, USB, and PCIe, along with `BUSUNKNOWN`, `PCIWINDOW`, and `PCIWADDR`.

The values feed clock setup, PL011 UART, xHCI, PCIe root complex setup, and generic interrupt registration.

Notable risks: all device IRQs are hard-coded to LX2K wiring.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/l.s -->
# File Research: sources/os/plan9/9front/sys/src/9/lx2k/l.s

LX2K ARM64 boot, MMU, trap, syscall, interrupt, atomic, cache/TLB, FPU, and SMC assembly. `_start` enters with physical addressing, switches from EL2 to EL1 if needed, disables MMU/caches, clears page tables/BSS on CPU 0, calls `mmuidmap`/`mmu0init`, enables the MMU, moves into the kernel virtual address range, and calls `main`.

`mmuenable` programs MAIR, TCR, TTBR0/TTBR1, enables I/D caches and MMU, and returns to virtual addresses. The file includes DAIF-based `spl*`, WFI idle, virtual/performance cycle counters, labels, atomics via LDXR/STXR, TTBR writes, local/broadcast TLB invalidations, FP/SIMD save/restore, user entry, syscall return, note/fork return, EL0/EL1 trap frame setup, vector stubs patched by C code, fault-proof `peek`, and PSCI/SMC call support.

Notable risks: the vector stubs contain self-branches intended to be patched; trap-frame offsets and `TRAPFRAMESIZE` must exactly match `Ureg`; EL2 setup assumes a specific boot environment.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/main.c -->
# File Research: sources/os/plan9/9front/sys/src/9/lx2k/main.c

LX2K ARM64 kernel entry and platform bring-up. It parses boot arguments from `BOOTARGS`, initializes configuration environment state, starts the first user process, sizes memory and kernel/user pools, starts secondary CPUs through PSCI `CPU_ON`, handles reboot/reset through PSCI and a reboot trampoline, and provides DMA cache flushing.

`main` has separate paths for secondary and boot CPUs. The boot CPU initializes config, memory, console, traps, FPU, GIC, timer, pages, processes, segments, devices, users, MP, MMU ASID/page-table state, and scheduler. `mpinit` maps MPIDR values to Plan 9 CPU indexes and calls `smccall`.

`reboot` migrates to CPU 0, shuts down devices/clock/interrupts, clears secrets, restores identity TTBR, copies `rebootcode`, flushes I/D caches, and jumps.

Notable risks: `MAXMACH` is one in `mem.h`, so MP scaffolding exists but normally does not start additional CPUs; boot-arg parsing mutates `BOOTARGS` in place.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/mem.c -->
# File Research: sources/os/plan9/9front/sys/src/9/lx2k/mem.c

LX2K early memory and initial page-table setup. `mmuidmap` creates a temporary TTBR0 identity map for virtual DRAM during early boot. `mmu0init` creates the shared kernel TTBR1 mappings for initial DRAM and `VIRTIO`, including page-level mappings for unaligned MMIO tails and higher-level table links when needed.

`meminit` records available DRAM from the end of the kernel up to 4 GiB, maps it with `kmapram`, and optionally adds a second high-memory region using the `*maxmem` configuration variable.

Notable risks: memory layout is hard-coded for GPP DRAM region 1 and optional region 2; comments note the initial shared table is later completed by `meminit`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/mem.h -->
# File Research: sources/os/plan9/9front/sys/src/9/lx2k/mem.h

LX2K ARM64 memory and MMU constants. It defines 4 KiB pages, effective 34-bit virtual addressing, multi-level page-table index macros, kernel/user virtual layout, TTBR0/TTBR1 page-table placement, Mach placement, boot args, reboot address, memory attributes, ARM64 PTE bits, and physical I/O/DRAM bases.

The layout maps DRAM through high virtual aliases (`VDRAM`, `KZERO`, `KSEG0`, `KMAP`, `VMAP`) and maps MMIO through `VIRTIO`. It defines ARM64 memory attribute indexes for write-back/write-through/uncached/device memory and access/shareability/execute-never flags.

Notable risks: `MAXMACH` is one despite MP scaffolding elsewhere; page-table macros are nontrivial and shared with assembly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/pcilx2k.c -->
# File Research: sources/os/plan9/9front/sys/src/9/lx2k/pcilx2k.c

LX2K PCIe root-complex driver for two DesignWare PCIe controllers. It defines controller address windows, DBI/config/I/O/memory bases, IRQ ranges, iATU register programming, config-space accessors, interrupt fanout, and root bridge initialization.

`rootinit` disables iATUs, maps config space, enables DBI read-only writes, programs bridge bus numbers/class/command/BARs, scans PCI buses, initializes INTx interrupt handlers, configures outbound I/O and memory iATUs, maps bus resources, and prints inventory.

Config reads/writes use DBI before parent device discovery and iATU CFG0/CFG1 windows after. PCI interrupts are collected into fixed vector slots and invoked by shared controller IRQ handlers; MSI is disabled for devices before installing handlers.

Notable risks: interrupt dispatch calls every registered vector on each PCI interrupt without device-specific status filtering; `pciintrenable` removes prior slots by device pointer; controller address ranges are hard-coded.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/pcilx2k.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/uartlx2k.c -->
# File Research: sources/os/plan9/9front/sys/src/9/lx2k/uartlx2k.c

LX2K PL011 UART driver adapted from BCM2835 code. It defines PL011 register offsets and bits, a single console UART at `VIRTIO+0x11c0000`, and full basic UART methods for enable/disable, interrupt RX/TX, baud, bits, stop, parity, break, getc, and putc.

`enable` disables the UART, registers the GIC interrupt when requested, enables TX/RX interrupts, then turns the UART on. `interrupt` drains RX FIFO, kicks TX, and clears interrupt causes. `baud` programs integer/fractional divisors from a 24 MHz clock.

`uartconsinit` sets `consuart`, marks it as console, applies line settings, and flushes buffered kernel messages.

Notable risks: modem/DTR/RTS/FIFO controls are no-ops; divisor math is simple and tied to the configured 24 MHz clock.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/uartlx2k.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/usbxhcilx2k.c -->
# File Research: sources/os/plan9/9front/sys/src/9/lx2k/usbxhcilx2k.c

LX2K xHCI/DWC3 host-controller glue. It allocates up to two xHCI controllers at fixed MMIO bases, links them to the generic xHCI HCI layer, sets the IRQ, and applies DWC3 core initialization.

`coreinit` programs GCTL, GUCTL, and GFLADJ fields for host mode, power-down scaling, auto-retry, and 30 MHz frame-length adjustment. `reset` allocates the first unused controller and returns it as an `"xhci"` HCI type.

Notable risks: controller discovery is fixed-address and append-only; no shutdown or platform power sequencing appears here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/lx2k/usbxhcilx2k.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/arch.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/arch.c

MT7688 MIPS architecture glue for port-layer expectations. It implements idle, address alignment checks, process setup/fork/save/restore stubs, user PC/debug PC helpers, protected register writes for `/proc`, kernel `Ureg` construction for sleeping processes, and kproc child scheduling setup.

`procsetup` initializes floating-point state and copies initial FP status into the process save area. `setregisters` preserves status and `r27` while allowing register updates from devproc.

Notable risks: process save/restore/fork are mostly stubs; comments note some routines may need architecture-specific completion.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/arch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/bootargs.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/bootargs.c

MT7688 boot-argument and `plan9.ini` parser. It stores up to 64 key/value pairs copied from `CONFADDR`, provides `getconf`, exports values into `#e`/`#ec` through `setconfenv`, and can serialize current kernel environment back to the boot-args buffer with `writeconf`.

`plan9iniinit` parses ASCII lines in place, skipping blank/comment/malformed lines and splitting on `=`.

Notable risks: `writeconf` is static and not used in this file; parsing mutates the boot buffer; fixed `MAXCONFLINE` truncates stored values through `strecpy`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/bootargs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/clock.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/clock.c

MT7688 MIPS clock implementation using CP0 count/compare. It calibrates CPU speed by timing an instruction loop against the count register, sets delay-loop calibration, initializes machine frequency fields, programs timer periods, and enables timer interrupt `INTR7`.

`fastticks` maintains a 64-bit-ish accumulated tick count across 32-bit count wrap and ensures compare is not too far in the future. `clock` dismisses timer interrupts by writing compare and calls `timerintr`. `timerset` clamps requested periods to min/max bounds.

Notable risks: `Basetickfreq` is hard-coded as `580 MHz / 2`; calibration assumes the loop instruction count and CP0 counter behavior match the SoC.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/dat.h

MT7688 MIPS machine data definitions. It defines Plan 9 configuration structures, MIPS FP emulator save state, process FPU state, process MMU PID state, Mach fields, KMap, software TLB entries, active CPU state, and hardware device config structures.

`FPsave` includes emulated FP register bits, control/status, delay-slot execution tracking, and stuck-fault detection fields. `Mach` includes soft-TLB state, process pointer, interrupt PC, TLB fault counters, PID ownership, kmap tracking, timer counters, CPU speed/delay fields, and stack.

Notable risks: comments mark legacy MIPS AOUT/boot magic handling; the FP and TLB structures are tightly coupled to MIPS trap/MMU code outside this group.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/devarch.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/devarch.c

MT7688 `#P/arch` device implementation. It provides an extensible arch directory with `addarchfile`, standard device attach/walk/stat/open/read/write operations, and two built-in read-only files: `cputype` and `sysctl`.

`cputyperead` reads MIPS PRID/config registers and reports endian mode, CPU family, revision, I/D cache sizes, coherency/write type, TLB entries, FPU presence, and COP2 presence. `sysctlread` reads system-control chip ID, clock gating, and reset registers, then formats per-device clock/reset state using a static gate table.

Notable risks: `chipid` is treated as a string without explicit null termination; the arch directory has a hard maximum of 16 entries.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/devarch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/ether7688.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/ether7688.c

MT7688 MediaTek Ethernet/PDMA driver with integrated switch/PHY setup. It defines RX/TX descriptor formats, PDMA global config, interrupt masks, switch MII access, controller state, and Plan 9 `Ether` callbacks.

The driver reads/writes system, Ethernet, and switch registers through fixed MMIO macros. MII access goes through switch PCTL registers. `doreset` and `ethreset` apply switch and PHY reset/init sequences with many hard-coded register values. `getmacaddr` reads GDMA1 MAC registers.

`attach` initializes switch/PHY/MII, allocates uncached descriptor rings in KSEG1, allocates RX blocks, initializes TX descriptors, programs PDMA ring pointers/counts/indexes, enables RX/TX interrupts and DMA, sets VLAN ethertype, marks link up, and starts `rxproc`/`txproc`.

`rxproc` waits for RX descriptors marked done, flushes cache, passes blocks to `etheriq`, replenishes buffers, and advances CPU index. `txproc` reads outbound queue blocks, waits for free TX descriptors, pads short frames, flushes cache, and advances TX index. `etherinterrupt` wakes RX/TX processes and records DMA/spurious stats.

Notable risks: many switch/PHY constants are magic; TX/RX cache flushing and descriptor ownership are delicate; promiscuous/multicast/shutdown are stubs; link is forced up.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/ether7688.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/faultmips.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/faultmips.c

MT7688/MIPS fault handling glue. It classifies MIPS TLB/load/store faults, calls the common Plan 9 `fault` handler, posts user fault notes, and panics with register dumps on unhandled kernel faults.

`tstbadvaddr` decodes the instruction at EPC, including branch-delay handling, to check whether the computed effective address matches `badvaddr`. `ckfaultstuck` tracks repeated faults at the same VA/PC/PID/cause to diagnose faults that are not being fixed.

`validalign` enforces user pointer alignment, relaxing 64-bit alignment to 32-bit alignment for a 32-bit OS.

Notable risks: detailed fault debugging is gated by `Debug`; instruction decoding is partial and conservative.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/faultmips.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/fns.h

MT7688 MIPS platform function declarations and address macros. It exports clock, trap, MMU/TLB, kmap, interrupt, cache, FPU, bootargs, UART, low-level CP0/config, and architecture helper routines.

The header defines `KADDR`, `PADDR`, `KSEG1ADDR`, `FMASK`, user-reg detection, pointer/integer conversion helpers, and UART/serial console entry points. It also exposes MIPS-specific register accessors such as `rdcount`, `wrcompare`, `getcause`, `getstatus`, config reads, and watch register access.

Notable risks: several prototypes point to code outside this group; simple address macros assume the configured MIPS segment layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/fpi.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/fpi.c

Architecture-independent floating-point interpreter arithmetic core used by the MT7688 MIPS FP emulator path. It operates on the internal extended format defined in `fpi.h`.

It implements rounding, exponent matching, normalization/renormalization, add, subtract, multiply, divide, compare, and helper normalization. It handles zero, infinity, and NaN cases explicitly. The file notes that internal arguments to subtract/divide are reversed from naive expectation: `fpisub` computes `y - x`, and `fpidiv` computes `y / x`.

Multiplication uses chunked fixed-point partial products; division uses iterative subtract/shift quotient construction. Rounding uses guard bits and ties-to-even behavior.

Notable risks: arithmetic mutates `Internal` operands in places such as exponent matching and normalization, so callers need disposable copies where required.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/fpi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/fpi.h -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/fpi.h

Header for the MT7688 floating-point interpreter. It defines machine-independent FP word types, maps Plan 9 `FPdbleword` as `Double`, defines internal fraction/exponent constants, and declares the `Internal` representation.

`Internal` stores sign, exponent, low fraction with guard bits, and high fraction with hidden bit. Macros classify and set zero, infinity, and quiet NaN. The header declares arithmetic routines from `fpi.c` and conversion routines from `fpimem.c`.

Notable risks: comments state field order matters; conversion code depends on this representation and on Plan 9 double-word layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/fpi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/fpimem.c -->
# File Research: sources/os/plan9/9front/sys/src/9/mt7688/fpimem.c

Memory-format conversion routines for the MT7688 floating-point interpreter. It converts between IEEE single/double/integer memory values and the internal `Internal` FP format.

Input conversions include single-to-internal, double-to-internal, 32-bit word-to-internal, and 64-bit integer-to-internal. Output conversions round the internal value and produce single, double, 32-bit integer, or 64-bit integer results, including underflow-to-zero and saturation-style max integer handling.

Notable risks: output conversions intentionally mutate the supplied `Internal`, so callers must pass disposable copies; integer negation of minimum negative values relies on C two's-complement behavior assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/mt7688/fpimem.c -->