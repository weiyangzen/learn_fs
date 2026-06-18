# Group Research: group_8_9front_sources_os_plan9_9front_sys_src_9_omap_archomap_c_sources_os_pl_d2fb715b33bc

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/archomap.c -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/archomap.c

OMAP3530/Cortex-A8 board support for the 9front `omap` kernel, aimed at BeagleBoard and IGEPv2-style boards. It defines memory-mapped register layouts and board setup for clocks, GPIO, pin muxing, USB host/TLL/OTG, display clocks, cache identification, VFP enablement, reboot, Ethernet defaults, and flash reset.

Key behavior:
- `archconfinit` chooses the CPU frequency, defaulting to 500 MHz unless `*cpumhz` is configured.
- `configclks` sequences MPU, USB, PLL, wakeup, peripheral, and core clocks, including DPLL setup and GPTIMER clock selection.
- `configgpio` programs GPIO6 pin 176 as the SMSC9221 Ethernet interrupt input.
- `configscreengpio` and `screenclockson` enable GPIO1/DSS pieces needed by the LCD/display path.
- `setpadmodes` writes SCM pad configuration for USB, UART3, IGEP Ethernet IRQ, and GPMC/flash pins.
- `resetusb` resets OTG, UHH, and USB TLL blocks and sets host/TLL operating modes.
- `fpon` enables ARM VFP/NEON coprocessor access and prints VFP identity/capability information.
- `archreset` performs early SoC initialization: cache report, software boot config cleanup, pin muxing, clocks, GPIO, memory config, USB reset, and FPU enablement.
- `archreboot` requests global software reset through PRM reset control and spins if reset does not happen.
- `archether` declares a board Ethernet controller of type `9221` on IRQ 34.
- `cacheinfo` reads CP15 cache size/type registers for the two Cortex-A8 cache levels.

Notable dependencies:
- OMAP physical addresses from `mem.h`.
- ARM CP15 and VFP definitions from `arm.h`.
- USB EHCI structures from `usbehci.h`.
- Network and flash interfaces from the port layer.

Research notes:
- The file contains many hard-coded board register values and comments documenting U-Boot-derived pad settings.
- L3 protection-region dumping exists for diagnostics; modification code is left disabled under `if(0)`.
- USB setup is explicit about OMAP3 quirks, including port/TLL/ULPI mode constraints.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/archomap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/arm.h -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/arm.h

Cortex-A8/ARMv7 definitions shared by C and assembly code in the OMAP port.

Key contents:
- ARM PSR mode, interrupt disable, and condition flag constants.
- Coprocessor numbers and CP15 register/opcode names for system control, cache, TLB, vectors, performance counters, and lockdown registers.
- Main control and auxiliary control bit definitions for MMU, caches, branch prediction, high vectors, access flags, and L2 behavior.
- ARM MMU descriptor constants for section/page entries, access permissions, domains, cacheability, and high vectors.
- Instruction classification macros for FPA/VFP coprocessor instruction decoding.

Research notes:
- This header is foundational for `l.s`, `cache.v7.s`, `lexception.s`, `coproc.c`, `trap.c`, `mmu.c`, and FPU emulation.
- The MMU constants are ARMv7-specific in places, with comments noting deprecated ARM access-permission encodings.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/arm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/arm.s -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/arm.s

Assembler macro include for the OMAP Cortex-A8 port.

Key contents:
- Kernel/physical address conversion and L1 page-table index macros.
- Section PTE templates for cached DRAM and uncached I/O.
- Delay and UART “wave” debug-output macros.
- Encodings for ARMv7 instructions not natively named by the assembler: SMC, WFI, DMB, DSB, ISB, CLZ, CPSIE/CPSID, VFP register moves.
- Cache/TLB barrier macros and page-table fill/zero helpers used by boot and reboot assembly.

Research notes:
- This file is macro infrastructure, not standalone executable code.
- It is included by `l.s`, `lexception.s`, and `rebootcode.s`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/arm.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/cache.v7.s -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/cache.v7.s

ARMv7/Cortex-A8 cache-maintenance routines.

Key behavior:
- Exports instruction-cache invalidate, data-cache clean, invalidate, and clean+invalidate operations.
- Provides single set/way CP15 cache operators plus whole L1/L2 cache traversal.
- `cacheuwbinv` disables interrupts, cleans/invalidates data cache, and invalidates I-cache.
- L2 wrappers select level 2 and reuse the shared whole-cache loop.
- `wholecache` reads cache geometry from CP15, computes way/set encodings, and iterates all sets and ways.

Research notes:
- Whole-cache traversal remaps function pointers into the current PC segment so it can run during MMU transition windows.
- The set/way shifts are hard-coded for Cortex-A8 cache geometry.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/cache.v7.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/clock.c -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/clock.c

OMAP3530 timer, watchdog, delay, and fast-tick implementation.

Key behavior:
- Uses GPTIMER1 as a free-running 32 kHz base timer and GPTIMER2 as the interrupting kernel clock.
- `clockshutdown` resets timers and disables WDT2/WDT3.
- `clockinit` enables the ARM performance cycle counter, starts timer hardware, installs the clock interrupt, sanity-checks ticking, and calibrates delay loops.
- `clockintr` calls the generic `timerintr` and acknowledges timer overflow.
- `watchdoginit` enables periodic watchdog assurance through clock links.
- `timerset` programs the next timer interrupt within min/max bounds.
- `fastticks` returns a widened monotonically maintained value from the 32-bit cycle counter.
- `microdelay` and `delay` spin using `m->delayloop`.

Research notes:
- Comments explain OMAP timer clock source constraints and the choice to use 32 kHz GPTIMERs.
- Watchdog control uses the OMAP magic start/stop sequences.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/coproc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/coproc.c

Runtime helpers for ARM coprocessor and VFP register access.

Key behavior:
- `cpwr` and `cprd` synthesize small instruction sequences containing MCR/MRC and a return instruction, flush caches, then execute them.
- `cpwrsc` and `cprdsc` specialize access to CP15 system-control registers.
- `fprd` and `fpwr` synthesize VMRS/VMSR sequences for VFP system register access.
- `MAP2PCSPACE` maps generated stack instructions into the caller PC segment before execution.

Research notes:
- The generated-code approach avoids needing static assembly wrappers for every CP15/VFP register tuple.
- Correctness depends on cleaning data cache and invalidating instruction cache before calling generated code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/coproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/dat.h

Core machine data declarations for the OMAP kernel.

Key contents:
- Time constants, `HZ`, and timer conversion macros.
- Forward declarations and typedefs for core kernel types.
- `Label`, `FPsave`, `PFPU`, `Confmem`, `Conf`, `MMMU`, `PMMU`, and `Mach` definitions.
- Per-process MMU state and per-machine stack/register/cache/timing state.
- Global CPU/proc register bindings: `m` in R10 and `up` in R9.
- ISA-style config structure used by generic drivers.
- `Memcache` cache-description structure populated by `cacheinfo`.
- DMA mode constants: post-increment, constant, indexed, and double-indexed.

Research notes:
- The OMAP port is uniprocessor here: `MAXMACH` is 1 in `mem.h`, and structures reflect that.
- FPU save state is soft/emulated-oriented and stores control/status plus register space.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/devarch.c -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/devarch.c

Implementation of the OMAP `#P` architecture device.

Key behavior:
- Provides dynamic architecture files via `addarchfile`.
- Implements Plan 9 device methods for attach, walk, stat, open, close, read, and write.
- Built-in files include `cputype`, `tb`, and `ns`.
- `cputyperead` reports the CPU name, clock, and architecture label.
- `tbread` exposes timebase information from `fastticks`.
- `nsread` reports nanosecond timing information.

Research notes:
- This is a small hardware-info and extension device, not a filesystem implementation.
- `archinit` installs the default arch files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/devarch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/devdss.c -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/devdss.c

Device interface for OMAP Display Subsystem settings.

Key behavior:
- Defines a device with files for display control/settings.
- Uses the `OScreen` state from `screen.h`.
- `settingswrite` parses display configuration text such as geometry/depth/channel/orientation values.
- `screenread` returns current display configuration state.
- `screenwrite` updates settings and validates channel strings through `strtochan`.
- Access is serialized by `dsslck`.

Research notes:
- The device is the control-plane counterpart to `screen.c` display initialization and console drawing.
- It uses Plan 9 device plumbing rather than a generic sysfs-like model.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/devdss.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/dma.c -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/dma.c

OMAP system DMA support.

Key behavior:
- Defines SDMA controller and channel register layouts.
- `dmainit` resets the DMA controller, clears interrupts, disables channels, and installs interrupt handlers.
- `dmastart` allocates a DMA channel/IRQ slot, configures source/destination addressing modes, rounded transfer length, block-complete interrupt, and starts the channel.
- `dmaintr` acknowledges DMA completion, marks the caller’s `done` flag, wakes the caller rendezvous, and disables the channel/IRQ.
- `isdmadone` reports completion state for a DMA IRQ slot.
- `dmatest` allocates scratch memory and runs a simple fill/copy validation using DMA.

Research notes:
- The implementation maps DMA channels one-to-one with IRQ slots and panics if all slots are in use.
- Cache coherency is caller-sensitive; the test path explicitly invalidates cache after DMA.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/dma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/ether9221.c -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/ether9221.c

SMSC LAN9221 Ethernet driver for IGEPv2-style OMAP boards.

Key behavior:
- Defines LAN9221 register layout, FIFO command/status bits, interrupt bits, MAC/PHY indirect register access, EEPROM state, and multicast table storage.
- `smcreset` checks chip ID, resets hardware, waits for power readiness, configures FIFOs/MAC, loads or synthesizes Ethernet address, and initializes interrupt masks.
- `smcattach`, `smctransmit`, and `smcreceive` implement Plan 9 `Ether` driver operations using TX/RX FIFOs.
- `macrd`/`macwr` access MAC registers through the LAN9221 CSR synchronizer.
- `smcpromiscuous` toggles promiscuous receive mode.
- `smcmulticast` is present but effectively a stub.
- `smcinterrupt` acknowledges LAN9221 interrupts, handles RX/TX status, wakes receive/transmit paths, and clears GPIO IRQ state through `gpioirqclr`.
- Optional `USE_KPROCS` paths define RX/TX kernel processes but are disabled because comments report slower boot.
- `smcpnp` probes the board controller and installs driver hooks.
- `ether9221link` registers the driver as Ethernet type `9221`.

Research notes:
- The file documents board-specific assumptions: chip-select 5, base `0x2c000000`, GPIO pin 176/IRQ 34.
- The driver is FIFO-based rather than descriptor-ring based; comments note this is slow and DMA does not help much.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/ether9221.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/fns.h

Function prototypes and port macros for the OMAP kernel.

Key contents:
- Prototypes for architecture reset, clock, cache, MMU, DMA, trap, IRQ, UART, screen, coprocessor, FPU, and reboot helpers.
- Generic interrupt macros mapping `intrenable`/`intrdisable` to `irqenable`/`irqdisable`.
- Atomic-operation macros mapping Plan 9 CAS/TAS names to 32-bit ARM implementations.
- Address conversion macros `KADDR` and `PADDR`.
- `MASK(v)` bit-mask helper used heavily across the OMAP port.
- Stub macros for unsupported or trivial page-color/kmap behavior.

Research notes:
- This header is the main cross-file contract for the OMAP kernel subtree.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/fpi.c -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/fpi.c

Software floating-point internal arithmetic routines.

Key behavior:
- Operates on `Internal` extended representations from `fpi.h`.
- Provides rounding, exponent matching, normalization, renormalization, add, subtract, multiply, divide, and compare.
- Handles zero, infinity, and NaN cases through `fpi.h` macros.
- Multiplication splits significands into chunks for portable integer arithmetic.
- Division implements a bit-building quotient loop over the internal fraction width.

Research notes:
- Arithmetic is used by ARM FPA/VFP emulation in `fpiarm.c`.
- The implementation targets kernel portability and avoids relying on hardware floating point.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/fpi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/fpi.h -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/fpi.h

Header for the software floating-point internal format.

Key contents:
- Defines `Word`, `Single`, and `Double`.
- Defines fraction and exponent geometry: hidden bit, guard bit, carry bit, exponent bias, infinity exponent, and fraction width.
- Defines `Internal` as sign, exponent, low fraction, and high fraction fields.
- Macros identify and set weird values, infinity, NaN, and zero.

Research notes:
- The internal format supports the arithmetic core in `fpi.c`, memory conversions in `fpimem.c`, and instruction emulation in `fpiarm.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/fpi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/fpiarm.c -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/fpiarm.c

ARM floating-point and selected atomic instruction emulator.

Key behavior:
- Decodes and emulates old ARM 7500 FPA instructions and VFP single/double operations when they trap as undefined instructions.
- Uses `fpi.c` and `fpimem.c` for arithmetic and conversion.
- Implements binary operations, unary operations, comparison/condition-code updates, loads/stores, and conversions to integer.
- `condok` applies ARM condition-code predicates from CPSR.
- `fpaemu` handles legacy FPA-style instruction encodings.
- `vfpemu` handles VFP register-transfer, arithmetic, load/store, and compare cases.
- `ldrex` and `strex` emulate exclusive access instructions using global `ldrexvalid` state.
- `casemu` emulates compare-and-swap style instruction patterns.
- `fpiarm` is the public trap-side entry point; it fetches the faulting instruction, dispatches emulation, and advances PC when handled.

Research notes:
- Header comments state it does not fully model ARM floating-point status/properties beyond what the Inferno-derived environment needs.
- All arithmetic is effectively done through the internal double-precision representation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/fpiarm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/fpimem.c -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/fpimem.c

Conversions between memory floating-point encodings and `Internal` soft-FP values.

Key behavior:
- `fpis2i` converts 32-bit single to `Internal`.
- `fpid2i` converts 64-bit double to `Internal`.
- `fpiw2i` converts integer word to `Internal`.
- `fpii2s` converts `Internal` to single.
- `fpii2d` converts `Internal` to double.
- `fpii2w` converts `Internal` to integer word.
- Handles sign, exponent bias adjustments, denormal-like low exponent cases, infinity, NaN, and zero.

Research notes:
- These routines are memory-format glue for `fpiarm.c` instruction emulation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/fpimem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/init9.s -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/init9.s

Tiny assembly `main` for boot startup.

Key behavior:
- Sets the static base register R12.
- Passes `boot` and an argv pointer to `startboot`.
- Loops forever if `startboot` returns.

Research notes:
- The comment explains this is assembly to avoid dragging in extra C runtime routines before SB is initialized.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/init9.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/io.h -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/io.h

OMAP I/O register definitions for GPMC and related low-level hardware.

Key contents:
- Timing and chip-select constants for the OMAP GPMC.
- `Gpmccs` chip-select register layout.
- `Gpmc` controller register layout, including config, IRQ, timeout, error, and per-chip-select register blocks.

Research notes:
- Used by architecture/flash-adjacent code that needs GPMC register-level access.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/l.s -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/l.s

Primary OMAP ARM kernel assembly startup and low-level CPU primitives.

Key behavior:
- `_start` builds early section mappings, sets up kernel stack and SB, enables MMU/caches, clears BSS, initializes `Mach`, and calls kernel `main`.
- `_reset` provides a reset entry path.
- `_r15warp` adjusts execution across address segments during MMU transitions.
- Exports range cache operations: `cachedwbse`, `cachedwbinvse`, and `cachedinvse`.
- Exports MMU helpers: enable, disable, invalidate all, invalidate address.
- Exports CP15 accessors for CPU ID, cache type, control, TTB, DAC, FSR/IFSR/FAR, PID, SCR, and PSR.
- Implements interrupt priority helpers `splhi`, `spllo`, `splx`, `islo`.
- Implements TAS, CLZ, labels, caller-PC fetch, `idlehands`, and `coherence`.
- Includes `cache.v7.s` for full cache operations.

Research notes:
- Startup emits serial “wave” characters for very early diagnostics.
- The loader uses R11 as scratch, and comments/macros account for that.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/lexception.s -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/lexception.s

ARM exception vector and trap-entry assembly.

Key behavior:
- Defines the vector stubs and vector table copied to high vectors by `trapinit`.
- `_vsvc` handles SWI/system-call entry, saves user registers into `Ureg`, calls `syscall`, restores state, and returns with `RFE`.
- Undefined, prefetch-abort, data-abort, IRQ, and FIQ vector paths switch to SVC mode and call `trap`.
- Handles separate save/restore paths for traps originating in kernel versus user mode.
- `setr13` installs per-mode stack pointers for IRQ/FIQ/abort/undefined/system modes.

Research notes:
- The file carefully avoids ambiguous writeback forms of MOVM/LDM/STM, with comments referencing known assembler/architecture pitfalls.
- FIQ currently returns without dedicated handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/lexception.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/lproc.s -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/lproc.s

Process-transition assembly helpers.

Key behavior:
- `touser` performs the first transition to user mode by installing the user stack pointer, setting SPSR to user mode, stacking the user PC (`UTZERO+0x20`), and returning from exception.
- `forkret` restores a saved `Ureg` frame for a newly forked process and returns through `RFE`.

Research notes:
- Comments explain Plan 9 assembler `RFE` semantics as a pre-v6 return-from-exception simulation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/lproc.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/main.c -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/main.c

Main OMAP kernel bootstrap and machine configuration.

Key behavior:
- Maintains parsed configuration entries from `plan9.ini` via `getconf`, `addconf`, `writeconf`, and `plan9iniinit`.
- `main` sequences early initialization: machine setup, UART, architecture reset, trap/MMU/process subsystems, devices, links, environment, clock, screen, and first user process.
- `machinit` initializes the single `Mach` structure and per-mode stacks.
- `reboot` copies reboot trampoline code to `REBOOTADDR`, shuts down devices/clocks/interrupts, and calls the trampoline.
- `init0` completes first-process setup and enters user space.
- `confinit` detects available DRAM by probing possible memory sizes, builds `Conf.mem`, computes page/proc/swap/image allocation sizes, and sets uniprocessor config.
- `isaconfig` parses ISA-style config strings.
- `cmpswap` maps to ARM CAS.
- `setupwatchpts` reports unsupported watchpoints.

Research notes:
- Memory probing relies on `trapinit`/`probeaddr` being ready.
- The port assumes one CPU and uses an OMAP-specific base DRAM map.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/mem.h -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/mem.h

OMAP memory-layout and physical-address constants.

Key contents:
- Size, bit-field, alignment, page, stack, and cache-line macros.
- Kernel/user virtual layout: `KZERO`, `L1`, `CONFADDR`, `KTZERO`, `UZERO`, `UTZERO`, `USTKTOP`, and `REBOOTADDR`.
- ARM PTE public flag mappings used by generic kernel code.
- OMAP physical addresses for SCM, clock modules, DSS/DISPC, SDMA, USB TLL/UHH/OHCI/EHCI/OTG, UARTs, MMC, interrupt controller, PRM, watchdogs, timers, GPIO, L3/GPMC/SMS/DRC, and DRAM.
- `VIRTIO` and NAND/flash mapping constants.

Research notes:
- `MAXMACH` is 1 and `MACHSIZE` is one page.
- I/O space is treated as directly mapped in the kernel address plan.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/mmu.c -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/mmu.c

ARMv7 MMU and page-table management for the OMAP kernel.

Key behavior:
- `mmuinit` initializes kernel L1 mappings for DRAM, I/O, vectors, and device mappings, then enables the MMU domain setup.
- `mmumap` installs section mappings; `mmuidmap` identity-maps physical memory windows.
- `mmuswitch` changes the current process address space and repopulates user L1 entries.
- `flushmmu` and `mmurelease` clear stale process mappings.
- `putmmu` allocates L2 page tables as needed, installs user page mappings, handles cacheability/write bits, and invalidates relevant TLB/cache state.
- `mmuuncache` converts a virtual range to uncached mappings.
- `mmukmap`/`mmukunmap` map and unmap physical ranges in a fixed segment map area.
- `cankaddr`, `vmap`, and `vunmap` provide physical-to-kernel mapping helpers.

Research notes:
- The implementation uses Plan 9 `Page` objects to back L2 page tables and keeps per-process `mmul2` lists.
- Cache/TLB maintenance is explicit around page-table updates.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/rebootcode.s -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/rebootcode.s

OMAP reboot trampoline copied to low memory during kernel reboot.

Key behavior:
- Disables interrupts, adjusts Cortex-A8 auxiliary control to reduce speculation/cache-maintenance risk, and turns caches off.
- Reworks double mappings so physical DRAM and kernel virtual addresses remain reachable during MMU shutdown.
- Switches execution, stack, and SB into physical DRAM space.
- Disables MMU and caches, copies the new kernel image from source to destination with `memmove`, flushes caches, and branches to the physical entry.
- Provides `cachesoff`, `_r15warp`, and stub `panic`/`pczeroseg`.
- Includes `cache.v7.s`.

Research notes:
- Comments state the code must fit under 11 KB to avoid stepping on PTEs.
- Serial wave characters trace reboot progress.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/rebootcode.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/screen.c -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/screen.c

OMAP DSS/DISPC framebuffer and text-console implementation.

Key behavior:
- Defines DSS and DISPC register layouts and graphics-plane configuration constants.
- Maintains screen settings, framebuffer `Memimage`, console colors, default font, cursor position, virtual screen buffer, and display window.
- `lcdinit` and `configdispc` program display timings, pixel clock divisors, framebuffer base, graphics attributes, FIFO thresholds, and LCD output.
- `screeninit` allocates framebuffer memory, initializes the display, sets up draw/screen globals, and installs console output.
- `flushmemscreen` writes back framebuffer cache lines for changed rectangles.
- `attachscreen`, `getcolor`, `setcolor`, and `blankscreen` implement generic screen hooks.
- `screenputc`, `scroll`, and `screenwin` implement the kernel text console on the framebuffer.
- `mousectl`, cursor functions, and power hooks are present but minimal/stub-like.

Research notes:
- The file is tightly coupled to OMAP DSS registers and the `OScreen` settings structure.
- Landscape orientation is tracked but much of the console logic assumes fixed framebuffer geometry.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/screen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/screen.h -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/screen.h

Display, cursor, and framebuffer interface header for the OMAP screen code.

Key contents:
- Forward declarations for `Cursor`, `OScreen`, `Omap3fb`, and `Settings`.
- External hooks for mouse tracking, screen attach/flush, cursor control, screen size/aperture, blanking, draw image reset, and software cursor routines.
- `Settings` holds width, height, depth, channel, pixel clock, margins, sync widths, and orientation.
- `OScreen` stores current display settings.
- `Omap3fb` describes the active-color framebuffer.

Research notes:
- Shared by `screen.c` and `devdss.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/screen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/softfpu.c -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/softfpu.c

Process-level soft-FPU integration hooks.

Key behavior:
- Provides placeholder/proc hooks for FPU save/restore/fork/setup/notify/noted behavior.
- `notefpsave` returns the process FP save area.
- `fpuinit` is effectively empty.
- `fpuemu` calls `fpiarm` to emulate faulting floating-point instructions.
- `fpudevprocio` currently returns 0, so `/proc` FP I/O is not implemented here.

Research notes:
- The real instruction emulation lives in `fpiarm.c`; this file connects it to process and trap plumbing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/softfpu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/syscall.c -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/syscall.c

OMAP syscall and user-notification register handling.

Key behavior:
- `syscall` is entered from SWI exception assembly, adjusts PC, validates user mode, dispatches through `systab`, stores return values, handles errors/notes/procctl, and exits through `kexit`.
- `notify` builds a user notification frame and redirects execution to the user notify handler.
- `noted` validates and restores notification frames according to Plan 9 note action.
- `execregs` initializes registers for a new exec image.
- `forkchild` copies the parent `Ureg`, sets child return value to 0, and arranges `forkret`.

Research notes:
- This file is architecture-specific glue around generic Plan 9 syscall and note semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/trap.c -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/trap.c

OMAP interrupt controller, exception, fault, and trap handling.

Key behavior:
- Defines OMAP MPU INTC register layout and 96 IRQ vectors.
- `trapinit` copies high-vector stubs, installs banked stacks, masks all interrupts, sets priorities, and marks IRQ setup ready.
- `irqenable`/`irqdisable` manage per-IRQ handler lists and mask/unmask INTC lines.
- `irq` reads active IRQ, dispatches all handlers on that vector, masks unexpected interrupts, accounts interrupt timing, and acknowledges INTC.
- `faultarm` routes user/kernel memory faults into Plan 9 fault handling or panics on unrecoverable kernel faults.
- `trap` handles IRQ, prefetch abort, data abort, and undefined-instruction exceptions, including breakpoint notes, memory fault decoding, external abort panics, and soft-FPU emulation.
- `probeaddr` safely probes a physical/virtual address by using trap recovery.
- Dump helpers print stack, GPRs, and CP15 system-control registers.

Research notes:
- Data-fault status decoding uses ARMv7 extended FSR bits and distinguishes translation, permission, alignment, domain, external abort, and parity cases.
- Undefined user instructions are offered to `fpiarm`; unhandled cases become debug notes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/uarti8250.c -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/uarti8250.c

OMAP 8250-like UART driver, using OMAP UART3 as Plan 9 console COM3.

Key behavior:
- Defines standard 8250 register offsets and bits plus OMAP mode register handling.
- Registers one UART at `PHYSCONS`, IRQ 74, as the console.
- Maintains sticky write state for registers whose bits must be preserved.
- Implements Plan 9 `PhysUart` operations for enable/disable, FIFO, kick, break, baud, bits, stop, parity, modem control, DTR/RTS, status, getc, and putc.
- `i8250enable` sets UART mode, detects FIFO, optionally enables IRQ, and initializes DTR/RTS.
- `i8250interrupt` handles modem status, transmitter empty, receive-data, line-status, and timeout interrupts.
- `uartconsinit` selects this UART as `consuart` and configures `115200 8N1`.

Research notes:
- Baud-rate programming is disabled under `#ifdef notdef`; the configured baud is recorded but hardware speed is not changed there.
- Comments say UART0/UART1 exist but are not believed to be externally connected.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/uarti8250.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/usbehci.h -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/usbehci.h

EHCI host-controller structures and constants used by OMAP USB code.

Key contents:
- Debug-print macros controlled by `ehcidebug`.
- Forward declarations and incomplete pragmas for EHCI controller structures.
- EHCI capability, command, status, interrupt, config, port, and debug-port bit constants.
- `Poll`, `Ctlr`, `Eopio`, and `Ecapio` structure definitions for generic EHCI controller state and MMIO registers.
- OMAP UHH register layout and hostconfig bit definitions.
- Declarations for generic EHCI linkage/memory/run helpers.
- `dmaflush` macro is empty for this port.

Research notes:
- This header bridges OMAP-specific controller setup in `usbehciomap.c` with generic EHCI logic elsewhere in the 9front tree.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/usbehci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/usbehciomap.c -->
# File Research: sources/os/plan9/9front/sys/src/9/omap/usbehciomap.c

OMAP3-specific EHCI USB host-controller attachment.

Key behavior:
- `ehcireset` stops the controller, clears upper 64-bit address segment if needed, resets hardware, chooses frame-list size, and sets interrupt threshold to one interrupt per millisecond.
- `shutdown` resets/stops EHCI and clears frame-list base.
- `wrulpi` writes ULPI PHY registers through OMAP implementation-specific EHCI register `insn[5]`.
- `reset` probes/configures the OMAP EHCI controller, allocates `Ctlr`, maps capability/operational registers, sets IRQ/port counts, initializes generic EHCI memory, applies OMAP-specific `insn[4]` and ULPI/UTMI setup, links generic EHCI handlers, and enables USB TLL/OTG/EHCI interrupts.
- `usbehcilink` registers the `ehci` HCI type.

Research notes:
- `reset` is single-shot via a static `beenhere`.
- It honors `*nousbehci` and uses `probeaddr(PHYSEHCI)` to skip absent hardware.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/omap/usbehciomap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ahci.h -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/ahci.h

AHCI/SATA register and in-memory structure definitions for the 9front PC port.

Key contents:
- PCI BAR index for AHCI MMIO.
- AHCI host capability, global-control, CAP2, BIOS handoff, enclosure-management, interrupt-status, SATA error, command, control, and status bit definitions.
- `Ahba` host bus adapter register layout.
- `Aport` per-port MMIO register layout, including command list, FIS base, interrupt, task, signature, SATA control/status/error/active, and FBS fields.
- `Afis` received-FIS memory layout pointers.
- Command-list, command-table, PRDT, ATAPI packet, and FIS structure definitions.
- ATA signature and port state constants.

Research notes:
- This header contains data definitions only; AHCI driver behavior is implemented in corresponding C files elsewhere.
- It is PC-port storage substrate code, within subset A’s OS/block-storage-adjacent scope.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ahci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/apbootstrap.s -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/apbootstrap.s

x86 application-processor bootstrap trampoline for the PC port.

Key behavior:
- Starts in real mode from low conventional memory and far-jumps into `_apbootstrap`.
- Loads a small GDT, enables protected mode, sets segment registers, and far-jumps to 32-bit code.
- `_ap32` temporarily double-maps `KZERO` at virtual zero through the supplied page directory, enables PSE paging, and jumps into high virtual execution.
- `_appg` removes the temporary low mapping, sets an AP stack, clears flags, and calls the AP startup vector with APIC information.
- Defines embedded data slots `_apvector`, `_appdb`, and `_apapic`, plus the minimal GDT and descriptor pointer.

Research notes:
- Must be placed on a 4 KB boundary in the first MB, with comments noting an effective first-64 KB restriction.
- This is bootstrap code for SMP AP startup, not storage/filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/apbootstrap.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/apic.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/apic.c

Local APIC and I/O APIC support for the 9front PC kernel.

Key behavior:
- Defines local APIC register offsets, SVR/ICR/ESR/timer bits, divide table, and per-CPU APIC timer calibration state.
- `lapicinit` maps/initializes local APIC state, enables spurious vector, calibrates local APIC timer against `fastticks`, applies Pentium errata handling, masks local vectors, enables APIC error vector, and synchronizes arbitration IDs.
- `lapiconline` reloads the periodic timer and lowers APIC task priority for a CPU.
- `lapicstartap` sends INIT and STARTUP IPIs to boot an application processor.
- `lapicerror` and `lapicspurious` handle local APIC error/spurious interrupts.
- `lapicisr`, `lapiceoi`, and `lapicicrw` expose APIC ISR/EOI/ICR operations.
- `ioapicrdtr`, `ioapicrdtw`, and `ioapicinit` read/write redirection entries and mask all I/O APIC lines.
- `lapictimerset` programs one-shot timer deadlines; `lapicclock` calls MTRR synchronization and generic timer interrupt work.
- `lapicintron`, `lapicintroff`, `lapicnmienable`, and `lapicnmidisable` adjust APIC interrupt/NMI acceptance.

Research notes:
- Timer calibration increases APIC divide value if the measured rate is too high for the counter.
- The code includes compatibility handling for older Intel local APIC quirks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/apic.c -->