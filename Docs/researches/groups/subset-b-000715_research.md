# Research: subset-b-000715

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/floppy.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/floppy.h

## Purpose
`floppy.h` adapts the generic Linux floppy driver to m68k machines, mainly Q40 and Sun3x. It supplies controller discovery, IRQ registration, pseudo-DMA setup, DMA memory allocation, and the Q40 hard interrupt path expected by the shared floppy core.

## Important APIs, Types, and Functions
The header defines `FDC1`, `N_FDC`, `N_DRIVE`, `FLOPPY0_TYPE`, virtual-DMA wrappers such as `fd_request_dma()`, `fd_get_dma_residue()`, `fd_dma_setup()`, and `fd_dma_mem_alloc()`, and I/O helpers `fd_inb()`/`fd_outb()`. `m68k_floppy_init()` selects a Q40 ISA base or Sun3x setup. `floppy_hardint()` is the IRQ entry for Q40 programmed I/O transfers.

## Control Flow, State, and Persistence
State is static per translation unit: `virtual_dma_count`, `virtual_dma_residue`, `virtual_dma_addr`, `virtual_dma_mode`, and `doing_pdma`. Setup marks `use_virtual_dma` and `can_use_virtual_dma`, while interrupts copy bytes between `virtual_dma_addr` and the FDC data port until the status bits stop indicating DMA-ready.

## Dependencies and Integration Points
It depends on `<asm/io.h>`, `sun3xflop.h`, vmalloc/vfree, `dma_spin_lock`, and the generic floppy core symbols `floppy_interrupt`, `virtual_dma_port`, status/data register constants, and IRQ APIs. Q40 uses ISA `inb/outb`; Sun3x delegates I/O and IRQ setup to Sun3x helpers.

## Risks
Only Q40 and Sun3x are implemented; other m68k machines return no controller. Static inline state in a header is unusual but mirrors old floppy-driver include patterns. Pseudo-DMA depends on exact status-bit timing and can silently report residue if the FDC stops requesting data early. DMA memory uses `vmalloc`, so callers must not assume physical contiguity.

## Test Signals
Useful signals are Q40 and Sun3x boot/probe logs, floppy read/write interrupt completion, DMA residue accounting on short transfers, and regression builds for configurations without Q40/Sun3x support. There is no local unit-test surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/floppy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/fpu.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/fpu.h

## Purpose
`fpu.h` provides the architecture constant for the maximum saved floating-point state size used by task switching, signal frames, and the m68k FPU emulator.

## Important APIs, Types, and Functions
The only API is `FPSTATESIZE`. It is selected by CPU/FPU configuration: 216 bytes for 68020/68030, 96 for 68040, 28 for the emulator, 16 for ColdFire MMU, 12 for 68060, and zero when no supported FPU state exists.

## Control Flow, State, and Persistence
There is no runtime control flow or state. The preprocessor computes the ABI-visible constant at build time.

## Dependencies and Integration Points
The header integrates with thread state layout and the math emulator. `math-emu.h` explicitly warns that changes to the C FPU data layout must stay in sync with the size defined here.

## Risks
Wrong values break context-save sizing and can corrupt adjacent task state. The configuration order matters: emulator and ColdFire choices are mutually exclusive with classic FPU CPU choices in normal builds.

## Test Signals
Compile coverage across 020/030, 040, 060, ColdFire MMU, and emulator configs is the key signal. Runtime signals include stable FPU context switching, signal delivery, and emulator tests under `CONFIG_M68KFPU_EMU`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/ftrace.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/ftrace.h

## Purpose
`ftrace.h` is an intentionally empty m68k architecture hook header. It satisfies generic include paths without declaring m68k-specific ftrace support.

## Important APIs, Types, and Functions
It exposes no macros, types, or functions.

## Control Flow, State, and Persistence
There is no control flow or state.

## Dependencies and Integration Points
The file integrates only by existing at the architecture include path expected by generic tracing code.

## Risks
The main risk is false assumption: consumers must not infer dynamic ftrace support from this header. Any future implementation would need careful ABI and instruction-patching support.

## Test Signals
The relevant signal is that m68k builds including generic tracing headers continue to compile. There is no direct runtime behavior to test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/hash.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/hash.h

## Purpose
`hash.h` provides an m68k-optimized `__hash_32()` for original 68000/010-class CPUs that lack a long multiply instruction, preserving the generic `hash_32()` behavior without using unavailable `MULU.L`.

## Important APIs, Types, and Functions
It defines `HAVE_ARCH__HASH_32` and `static inline u32 __hash_32(u32 x)`. The function multiplies by the Linux golden ratio constant using a hand-written addition/shift chain plus a 16-bit `mulu.w` on the high factor.

## Control Flow, State, and Persistence
The function is pure and has no state. Inline assembly computes partial products into data registers and returns the combined 32-bit hash.

## Dependencies and Integration Points
It depends on `u32`/`u16` types from the including context and integrates with generic hash helpers that prefer architecture-provided `__hash_32()` when `HAVE_ARCH__HASH_32` is set.

## Risks
Inline assembly constraints are performance- and correctness-critical. Toolchain changes can affect register allocation, and the implementation assumes m68k instruction timing and semantics. The result must remain equivalent to multiplying by `GOLDEN_RATIO_32`.

## Test Signals
Compare `__hash_32()` against the generic multiplication implementation over representative and randomized values, especially on 68000-targeted compiler output. Build tests should cover constraints with GCC versions used by the tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/hp300hw.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/hp300hw.h

## Purpose
`hp300hw.h` exposes minimal HP 300 platform hardware identity for m68k code.

## Important APIs, Types, and Functions
The header includes `bootinfo-hp300.h` and declares `extern unsigned long hp300_model`.

## Control Flow, State, and Persistence
There is no local control flow. `hp300_model` is persistent boot-time global state populated by HP300 setup code and then read by platform drivers or diagnostics.

## Dependencies and Integration Points
It depends on HP300 bootinfo definitions and integrates with model-detection code under the HP300 m68k machine port.

## Risks
Consumers rely on initialization ordering: `hp300_model` must be valid before hardware-specific probes branch on it. The file intentionally does not validate model values.

## Test Signals
Build HP300 configs and inspect boot model reporting. Platform-specific driver probes should select the expected path for each supported HP300 model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/hp300hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/hwtest.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/hwtest.h

## Purpose
`hwtest.h` declares tiny hardware-presence probes for m68k memory-mapped registers.

## Important APIs, Types, and Functions
`hwreg_present(volatile void *regp)` tests whether a register can be safely read. `hwreg_write(volatile void *regp, unsigned short val)` tests whether a register accepts a write. Implementations live in `arch/m68k/mm/hwtest.c`.

## Control Flow, State, and Persistence
The header has no state. The implementation is expected to trap or recover from bus errors while probing volatile addresses.

## Dependencies and Integration Points
It is used by board/platform detection and optional hardware drivers that need to avoid touching absent registers directly.

## Risks
Hardware probing can have side effects on real devices. Callers must pass correctly aligned register addresses and choose harmless values for write tests. The declarations are deliberately available to modules.

## Test Signals
Signals are successful boot probes on machines with and without optional devices, plus fault-path testing on unmapped addresses where practical. Compile coverage for modular users is also relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/hwtest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/idprom.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/idprom.h

## Purpose
`idprom.h` defines the Sun IDPROM data layout used by m68k Sun3/Sun3x code to identify machine type, Ethernet address, manufacture date, serial number, and checksum.

## Important APIs, Types, and Functions
`struct idprom` models the PROM bytes, including `id_format`, `id_machtype`, `id_ethaddr[6]`, `id_date`, a 24-bit serial field, checksum, and reserved bytes. It declares global `struct idprom *idprom`, `idprom_init()`, and `SUN3_IDPROM_BASE`.

## Control Flow, State, and Persistence
The PROM contents are read once by `idprom_init()` and then persisted through the global pointer for machine setup and network address users.

## Dependencies and Integration Points
It depends on Linux integer types and Sun machine definitions. Ethernet drivers and Sun3 platform setup use the parsed identity data.

## Risks
The bitfield serial representation is compiler-layout-sensitive, although the surrounding m68k ABI is fixed. Checksum validation is outside this header. Consumers must not dereference `idprom` before initialization.

## Test Signals
Boot logs should report correct Sun3/Sun3x model and MAC address. Tests or instrumentation should verify checksum handling and that `id_machtype` maps correctly through `machines.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/idprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/intersil.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/intersil.h

## Purpose
`intersil.h` describes the Intersil 7170 clock chip used by Sun3 systems.

## Important APIs, Types, and Functions
It defines command bits for oscillator frequency, 12/24-hour mode, run/stop, interrupt enable, normal/test mode, and the 100 Hz mask. `struct intersil_dt` models counter/alarm date-time fields, and `struct intersil_7170` groups counter, alarm, interrupt register, and command register. `intersil_clock` casts `clock_va` to the mapped device, and `intersil_clear()` reads the interrupt register.

## Control Flow, State, and Persistence
There is no function control flow. Hardware state persists in the RTC registers addressed through `clock_va`.

## Dependencies and Integration Points
Sun3 timekeeping, clock interrupt, and RTC code map `clock_va`, program `cmd_reg`, read `counter`, and clear interrupt state through this header.

## Risks
The structs assume exact hardware register ordering and byte-sized accesses. `intersil_clear()` has side effects by acknowledging interrupts. Incorrect mode bits can stop the clock or enter test mode.

## Test Signals
Boot time should be read correctly, periodic clock interrupts should clear, and 24-hour mode should avoid ambiguous hour values. Suspend/reset behavior should preserve expected RTC state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/intersil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/io.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/io.h

## Purpose
`io.h` is the top-level m68k I/O access selector. It chooses MMU or non-MMU I/O definitions and then layers generic Linux I/O helpers on top.

## Important APIs, Types, and Functions
For `__uClinux__` or `CONFIG_COLDFIRE`, it includes `io_no.h`; otherwise it includes `io_mm.h`. It aliases `gf_ioread32` and `gf_iowrite32` to big-endian `ioread32be`/`iowrite32be`.

## Control Flow, State, and Persistence
There is no runtime state. Configuration controls which accessor implementation is compiled.

## Dependencies and Integration Points
It integrates all m68k drivers using standard `readb`, `writeb`, `inb`, `outb`, `ioremap`, and generic I/O APIs. The `gf_*` aliases support drivers that expect Open Firmware-style big-endian cell access.

## Risks
Wrong configuration selection changes endian behavior and address translation. Since generic `asm-generic/io.h` is included after arch-specific definitions, arch macros must be defined before the generic fallback is parsed.

## Test Signals
Build both MMU and non-MMU/ColdFire configs. Runtime tests should verify endian-correct MMIO on internal peripherals, PCI, ISA bridges, and big-endian firmware-style register accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/io_mm.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/io_mm.h

## Purpose
`io_mm.h` implements m68k MMU-enabled I/O accessors, especially ISA-style port and memory access for Q40, Amiga PCMCIA, and Atari ROM ISA bridges.

## Important APIs, Types, and Functions
The header defines bridge address translations such as `Q40_ISA_IO_B`, `AG_ISA_IO_B`, and `ENEC_ISA_IO_B`, runtime or compile-time `ISA_TYPE`/`ISA_SEX`, inline translators `isa_itb()`, `isa_itw()`, `isa_mtb()`, and access macros `isa_inb/outb`, `isa_readb/writeb`, string I/O, ROM-ISA variants, delay variants, relaxed accessors, and `IO_SPACE_LIMIT`.

## Control Flow, State, and Persistence
Accessors are inline and branch on `ISA_TYPE` only when multiple ISA bridges are compiled. No persistent state is kept here, but multi-ISA builds depend on external globals `isa_type` and `isa_sex`.

## Dependencies and Integration Points
It depends on `raw_io.h`, `virtconvert.h`, `kmap.h`, and platform headers such as `amigayle.h`. Drivers that use legacy PC `inX/outX` macros on m68k route through this file.

## Risks
Endian selection through `ISA_SEX` is subtle. Atari ROM ISA splits port ranges below 1024 from regular accesses, so callers using unusual ports can hit the wrong path. The file cautions that non-ISA drivers should not use `inX/outX`.

## Test Signals
Build Q40, Amiga PCMCIA, Atari ROM ISA, and multi-ISA configs. Runtime signals are correct register reads/writes, string I/O transfers, and byte order on 16/32-bit port accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/io_mm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/io_no.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/io_no.h

## Purpose
`io_no.h` implements I/O access for non-MMU m68k and ColdFire systems, where physical and I/O virtual addresses are usually identity-mapped.

## Important APIs, Types, and Functions
It defines `iomem(a)`, raw volatile `__raw_readb/w/l` and `__raw_writeb/w/l`, default `readb/w/l` and `writeb/w/l`, ColdFire internal-I/O detection helpers `__cf_internalio()` and `cf_internalio()`, and PCI window constants when `CONFIG_PCI` is enabled.

## Control Flow, State, and Persistence
For ColdFire systems with `IOMEMBASE`, `readw/readl/writew/writel` branch at runtime: internal peripherals use native big-endian order, while bus ranges such as PCI are byte-swapped to little-endian. There is no persistent software state.

## Dependencies and Integration Points
It integrates with ColdFire platform register definitions from `coldfire.h` and `mcfsim.h`, byte-swap helpers, generic I/O, kmap, and virtual-address conversion code. PCI users consume `PCI_IOBASE` and address masks.

## Risks
The internal-I/O range check is central; wrong `IOMEMBASE` or `IOMEMSIZE` corrupts endian handling. Direct volatile dereferences require correctly mapped addresses and do not impose higher-level locking.

## Test Signals
Signals include correct access to native-endian ColdFire peripherals, byte-swapped PCI device configuration/MMIO, non-MMU boot probes, and compile coverage with and without `IOMEMBASE` and `CONFIG_PCI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/io_no.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/irq.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/irq.h

## Purpose
`irq.h` defines m68k IRQ namespace sizing and the common IRQ-controller entry points used by machine ports.

## Important APIs, Types, and Functions
`NR_IRQS` is selected per platform family, from 8 on small classic systems to 256 on ColdFire. Classic CPU configs define `IRQ_SPURIOUS`, `IRQ_AUTO_1` through `IRQ_AUTO_7`, and `IRQ_USER`. The file declares `m68k_irq_startup()`, `m68k_irq_shutdown()`, auto/user interrupt setup, `m68k_setup_irq_controller()`, `irq_canonicalize()`, `do_IRQ()`, and `irq_err_count`.

## Control Flow, State, and Persistence
There is no local runtime flow. The declarations connect machine initialization to generic IRQ descriptor management. `irq_err_count` persists interrupt error accounting.

## Dependencies and Integration Points
It depends on atomic/linkage headers and generic irq data/chip/desc types. Machine-specific interrupt code for Atari, Mac, Q40, VME, Sun, ColdFire, and virtual machines consumes these definitions.

## Risks
Undersized `NR_IRQS` breaks platforms with high interrupt numbers, while oversizing wastes descriptor memory. `irq_canonicalize()` only exists as a real function on classic MMU CPUs.

## Test Signals
Build each major machine config and verify high-numbered IRQ registration, autovector delivery, spurious IRQ counting, and canonicalization on platforms with cascaded interrupt controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/irqflags.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/irqflags.h

## Purpose
`irqflags.h` implements m68k local interrupt flag primitives used by spinlocks, preemption, and generic IRQ code.

## Important APIs, Types, and Functions
It defines `arch_local_save_flags()`, `arch_local_irq_disable()`, `arch_local_irq_enable()`, `arch_local_irq_save()`, `arch_local_irq_restore()`, `arch_irqs_disabled_flags()`, and `arch_irqs_disabled()`. The implementations manipulate the status register interrupt priority level.

## Control Flow, State, and Persistence
The functions directly read or write the CPU status register. ColdFire uses `move`/`ori.l`/`andi.l`; classic m68k uses word operations. MMU builds special-case Q40 or non-hardirq contexts when enabling interrupts.

## Dependencies and Integration Points
It depends on `thread_info.h`, `entry.h`, `preempt.h`, and machine macros such as `MACH_IS_ATARI` and `MACH_IS_Q40`. Generic lock and IRQ code call these primitives throughout the kernel.

## Risks
Incorrect masks can enable interrupts in hardirq context or fail to restore IPL. Atari treats HSYNC at IPL 2 specially, so generic disabled-state checks differ from other systems.

## Test Signals
Signals include lockdep/preemption correctness, nested save/restore behavior, Atari HSYNC handling, Q40 interrupt-enable behavior, and compile/run coverage for ColdFire and classic m68k.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/kexec.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/kexec.h

## Purpose
`kexec.h` defines minimal m68k architecture limits and identifiers for the generic kexec core.

## Important APIs, Types, and Functions
When `CONFIG_KEXEC_CORE` is enabled it defines unrestricted source, destination, and control memory limits as `-1UL`, `KEXEC_CONTROL_PAGE_SIZE` as 4096, `KEXEC_ARCH` as `KEXEC_ARCH_68K`, and a stub `crash_setup_regs()`.

## Control Flow, State, and Persistence
There is no real control flow in the stub; crash register capture is not implemented in this header.

## Dependencies and Integration Points
Generic kexec code includes these constants to validate image placement and architecture matching.

## Risks
The unrestricted memory limits are broad and rely on higher-level validation. The dummy crash register setup means crash dump register fidelity is missing or incomplete.

## Test Signals
Build with `CONFIG_KEXEC_CORE`, load a kexec image, and verify reboot into the new kernel. Crash-kexec users need explicit validation that register state expectations are either absent or acceptable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/kexec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/kmap.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/kmap.h

## Purpose
`kmap.h` exposes m68k I/O remapping and port mapping helpers, primarily for MMU-enabled systems.

## Important APIs, Types, and Functions
It defines cache modes `IOMAP_FULL_CACHING`, `IOMAP_NOCACHE_SER`, `IOMAP_NOCACHE_NONSER`, and `IOMAP_WRITETHROUGH`. MMU builds declare `__ioremap()` and `iounmap()`, and provide `ioremap()`, `ioremap_wt()`, `memset_io()`, `memcpy_fromio()`, and `memcpy_toio()`. `ioport_map()` returns a direct cast and `ioport_unmap()` is a no-op.

## Control Flow, State, and Persistence
Mapping state is owned by `arch/m68k/mm/kmap.c`; inline helpers only choose cache flags or perform direct copies through forced pointers.

## Dependencies and Integration Points
MMIO drivers use these helpers to map physical device ranges and copy to/from I/O memory. `io_mm.h` and `io_no.h` include this header for generic I/O compatibility.

## Risks
Wrong cache flags can break device coherency. `memcpy_*io` uses compiler builtins, so callers must ensure the target region is safe for normal-width accesses. `ioport_map()` does not allocate a special mapping.

## Test Signals
Driver probe and MMIO access on MMU systems, cache-mode validation for framebuffers and device registers, and build coverage for non-MMU configs where the MMU-only block is omitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/kmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/libgcc.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/libgcc.h

## Purpose
`libgcc.h` supplies an architecture-specific 32x32 to 64-bit multiply primitive for common libgcc-style helpers on m68k CPUs that support long multiply.

## Important APIs, Types, and Functions
Unless `CONFIG_CPU_HAS_NO_MULDIV64` is set, it defines `umul_ppmm(w1, w0, u, v)` using `mulu%.l %3,%1:%0` inline assembly to produce high and low product words.

## Control Flow, State, and Persistence
The macro has no persistent state. It emits one multiply sequence and assigns results to caller-provided lvalues.

## Dependencies and Integration Points
`lib/muldi3.c` and other arithmetic helpers can use `umul_ppmm()` for faster 64-bit multiplication. CPUs without the instruction fall back to C implementations.

## Risks
The macro depends on exact compiler constraints and CPU instruction availability. Enabling it on 68000 or ColdFire variants without long multiply would fail at build or runtime.

## Test Signals
Build with and without `CONFIG_CPU_HAS_NO_MULDIV64`, inspect generated assembly, and run 64-bit multiply/divide helper tests over edge values such as zero, max words, and carries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/libgcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/linkage.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/linkage.h

## Purpose
`linkage.h` provides m68k assembly alignment and syscall/linkage protection macros.

## Important APIs, Types, and Functions
It sets `__ALIGN` and `__ALIGN_STR` to `.align 4`. `asmlinkage_protect(n, ret, args...)` expands to arity-specific empty inline assembly constraints that keep stack-passed syscall arguments live until function exit.

## Control Flow, State, and Persistence
There is no runtime state. The macros alter compiler optimization behavior by adding artificial uses of return values and arguments.

## Dependencies and Integration Points
Architecture syscall wrappers and low-level assembly/C boundaries use these definitions through generic linkage headers.

## Risks
The arity-specific macros only cover up to six arguments. Removing or weakening the constraints can let GCC reuse caller-owned stack argument slots or tail-call in ways that break syscall ABI assumptions.

## Test Signals
Compile syscall-heavy code with optimization and inspect that argument stack slots are not clobbered prematurely. Runtime syscall ABI tests are the practical signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/linkage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m5206sim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m5206sim.h

## Purpose
`m5206sim.h` maps the ColdFire 5206/5206e System Integration Module for board and driver code.

## Important APIs, Types, and Functions
It defines CPU metadata, `MCF_BUSCLK`, includes `m52xxacr.h`, and names SIM registers for interrupt control, masks/pending bits, watchdog, DRAM, chip selects, timers, DMA, UARTs, GPIO, pin assignment, and I2C. It also defines platform IRQ numbers for I2C, timers, profiler, and UARTs.

## Control Flow, State, and Persistence
There is no executable flow. The macros are stable MMIO addresses and constants used to program persistent SoC hardware registers.

## Dependencies and Integration Points
It depends on `MCF_MBAR`, `MCF_CLK`, and configuration symbols such as `CONFIG_M5206e` and `CONFIG_NETtel`. Timer, UART, DMA, GPIO, I2C, and interrupt-controller code consume the addresses.

## Risks
UART base ordering changes for NETtel boards. 5206e-only registers must not be used on base 5206. Misprogramming SIM registers affects memory timing, chip-select decode, or interrupt routing.

## Test Signals
Build 5206 and 5206e variants, boot board configs, verify UART console order, timer IRQs, and I2C base probing. Hardware register smoke tests should confirm expected MBAR offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m5206sim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m520xsim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m520xsim.h

## Purpose
`m520xsim.h` defines register maps and interrupt constants for ColdFire 5207/5208 SoCs.

## Important APIs, Types, and Functions
It defines one interrupt controller at `MCFICM_INTC0`, mask/force/ICR offsets, vector base 64, IRQ derivations for UART, FEC, QSPI, PIT, and I2C, SDRAM controller addresses, EPORT/GPIO registers, pin-assignment bits, PIT bases, UART bases, FEC base/size, QSPI chip selects, reset and power-management registers, and I2C base.

## Control Flow, State, and Persistence
The file is declarative. Hardware state persists in MMIO registers programmed by platform initialization and device drivers.

## Dependencies and Integration Points
It depends on `m52xxacr.h` and constants such as `MCF_CLK`. Generic ColdFire interrupt, GPIO, serial, FEC Ethernet, QSPI, PIT, reset, PM, and I2C code all depend on these names.

## Risks
The SoC uses absolute `0xFC...` addresses rather than MBAR-relative expressions, so memory-map assumptions must match boot setup. GPIO generic aliases start at the chip-select bank, which callers must interpret with the pin numbering model.

## Test Signals
Signals include boot console on all three UARTs, FEC interrupt delivery, PIT tick, GPIO numbering, QSPI chip-select mapping, and software reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m520xsim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m523xsim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m523xsim.h

## Purpose
`m523xsim.h` maps ColdFire 523x system integration registers and peripheral interrupt assignments.

## Important APIs, Types, and Functions
The header defines CPU/bus clock constants, dual interrupt controller bases under `MCF_IPSBAR`, interrupt offsets, vector base 64, UART/FEC/QSPI/PIT/I2C IRQs, SDRAM control registers, reset controller bits, UART/FEC/QSPI bases, QSPI chip-select GPIOs, large GPIO data/direction/set/clear banks, generic GPIO aliases, pin assignment registers, PIT bases, EPORT registers, and I2C base.

## Control Flow, State, and Persistence
No runtime code exists here. Register state is controlled by SoC setup and drivers through these address constants.

## Dependencies and Integration Points
It depends on `MCF_IPSBAR`, `MCF_CLK`, and `m52xxacr.h`. It feeds the common ColdFire interrupt controller, serial, Ethernet, SPI, GPIO, timer, reset, and I2C subsystems.

## Risks
The file provides many adjacent GPIO registers where off-by-one offsets can change unrelated pins. The interrupt controller numbering must match vector-base assumptions in common interrupt code.

## Test Signals
Boot a 523x config and verify UART, FEC, QSPI chip-selects, PIT interrupts, GPIO set/clear operations, and reset controller writes against hardware manuals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m523xsim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m525xsim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m525xsim.h

## Purpose
`m525xsim.h` defines ColdFire 525x SIM, peripheral, GPIO, and interrupt mappings.

## Important APIs, Types, and Functions
It supplies CPU name and bus clock, includes `m52xxacr.h`, and defines interrupt controller registers, vector base and peripheral IRQs, SDRAM/DRAM controls, DMA, UARTs, FEC, QSPI, GPIO banks, pin-assignment masks, PIT/EPORT/reset/I2C registers, and generic GPIO limits.

## Control Flow, State, and Persistence
The file has no code; it is consumed as compile-time MMIO metadata. Persistent state resides in hardware registers addressed by the macros.

## Dependencies and Integration Points
ColdFire common drivers use the UART, FEC, timer, GPIO, QSPI, reset, and interrupt constants. Conditional blocks adapt the map to selected 525x variants.

## Risks
Peripheral base addresses and chip-select GPIO numbers vary between closely related parts; using the wrong config can route drivers to the wrong hardware. Pin-mux masks need read/modify/write care in callers.

## Test Signals
Expected signals are serial console, Ethernet, QSPI chip selects, PIT tick, GPIO bank access, and IRQ delivery on a 525x board. Build coverage should include all variant conditionals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m525xsim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m5272sim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m5272sim.h

## Purpose
`m5272sim.h` maps ColdFire 5272 SIM registers and peripheral resources.

## Important APIs, Types, and Functions
It defines CPU metadata, bus clock, cache include, SIM interrupt registers, reset/watchdog, DRAM/chip-select controls, timers, DMA, UART bases, FEC base/size, GPIO limits, interrupt aliases for timer, profiler, UARTs, FEC, and I2C, plus I2C base/size.

## Control Flow, State, and Persistence
The header is declarative. Persistent SoC state is stored in the hardware registers and updated by platform/device code.

## Dependencies and Integration Points
It depends on `MCF_MBAR`, `MCF_CLK`, and `m52xxacr.h`. It supports common ColdFire serial, FEC Ethernet, timer, DMA, I2C, GPIO, and interrupt setup.

## Risks
The 5272 has older SIM-style interrupt mappings rather than the newer INTC map, so mixing with other ColdFire headers would break IRQ values. DRAM/chip-select definitions are boot-critical.

## Test Signals
Board boot, UART console, FEC network IRQs, timer ticks, I2C probe, and memory-controller setup are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m5272sim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m527xsim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m527xsim.h

## Purpose
`m527xsim.h` supports ColdFire 5271 and 5275 variants with shared and variant-specific SIM definitions.

## Important APIs, Types, and Functions
It defines CPU/bus clock, interrupt controllers, vector base, UART/FEC/QSPI/PIT/I2C IRQs, SDRAM and DMA registers, UART/FEC/QSPI bases, QSPI chip selects, variant-specific GPIO PODR/PDDR/PPDSDR/PCLRR banks, generic GPIO aliases and pin limits, pin-assignment registers, PIT/EPORT/reset/I2C registers, and UART enable masks.

## Control Flow, State, and Persistence
No executable flow is present. Conditional preprocessing selects the correct 5271 or 5275 register map.

## Dependencies and Integration Points
It depends on `MCF_IPSBAR`, `MCF_CLK`, and `m52xxacr.h`. Common ColdFire drivers and board setup code use the map for serial, Ethernet, SPI, GPIO, timer, and interrupts.

## Risks
5271 and 5275 differ substantially in GPIO layout, FEC count, QSPI chip selects, and pin masks. Incorrect Kconfig selection can cause writes to unrelated registers. Generic GPIO bases differ by variant.

## Test Signals
Build both 5271 and 5275 configs. Runtime signals include UART enable masks, one or two FEC devices as configured, QSPI chip-select GPIOs, PIT interrupts, and GPIO numbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m527xsim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m528xsim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m528xsim.h

## Purpose
`m528xsim.h` maps ColdFire 5280/5282 integration registers, interrupts, and GPIO/pin multiplexing.

## Important APIs, Types, and Functions
It defines CPU metadata, dual interrupt controllers, vector base and peripheral IRQs, SDRAM/DMA/UART/FEC/QSPI bases, QSPI chip-select pins, extensive GPIO data/direction/set/clear registers, pin assignment registers, PIT and EPORT bases, QADC and GPT GPIO helper registers, generic GPIO aliases, reset bits, and I2C base.

## Control Flow, State, and Persistence
The header has no runtime control flow. Drivers persist configuration by programming the mapped hardware registers.

## Dependencies and Integration Points
It depends on `MCF_IPSBAR`, `MCF_CLK`, and `m52xxacr.h`, and feeds common ColdFire serial, FEC, QSPI, GPIO, PIT, EPORT, QADC/GPT, reset, and I2C code.

## Risks
The GPIO map spans many named ports and up to 180 pins; generic GPIO users rely on the alias base matching the pin-numbering convention. Timer and QSPI IRQ numbers must match interrupt-controller setup.

## Test Signals
Signals include serial console, FEC transmit/receive interrupts, QSPI chip select operation, PIT tick, GPIO set/clear across multiple ports, and I2C probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m528xsim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m52xxacr.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m52xxacr.h

## Purpose
`m52xxacr.h` defines cache control and access-control register settings for ColdFire version 2 cores.

## Important APIs, Types, and Functions
It defines CACR bits for enabling, invalidating, freezing, and selecting instruction/data caches; ACR base/mask/access/cache bits; `CACHE_TYPE`, `CACHE_INIT`, `CACHE_MODE`, `CACHE_INVALIDATE`, optional instruction/data invalidate modes, and `ACR0_MODE`/`ACR1_MODE`.

## Control Flow, State, and Persistence
There is no executable code. Kconfig selections such as `CONFIG_CACHE_I`, `CONFIG_CACHE_D`, and `CONFIG_CACHE_BOTH` choose the constants used by low-level cache setup.

## Dependencies and Integration Points
ColdFire v2 SIM headers include this file. Cache initialization, TLB/cacheflush code, and early boot setup program CACR/ACR registers from these macros.

## Risks
Cache mode mistakes can corrupt DMA or instruction fetch coherency. Older instruction-cache-only devices share this file with split-cache parts, so Kconfig assumptions matter. `ACR0_MODE` maps RAM based on `CONFIG_RAMBASE`.

## Test Signals
Boot with instruction-only, data-only, and split-cache configs where supported. Validate cache flush/invalidate behavior, DMA coherency, and performance counters or memory tests under copy/write buffer settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m52xxacr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m5307sim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m5307sim.h

## Purpose
`m5307sim.h` maps the ColdFire 5307 SIM for early boot and peripheral drivers.

## Important APIs, Types, and Functions
It defines CPU/bus clock metadata, includes `m53xxacr.h`, names reset/watchdog, pin, PLL, bus, interrupt, chip-select, DRAM, timer, parallel port, DMA, UART, GPIO, IRQPAR, system IRQ, and I2C registers. It also accounts for `CONFIG_OLDMASK` and board-specific UART ordering.

## Control Flow, State, and Persistence
No code executes here. Conditional preprocessing selects register layouts and board-specific UART base order.

## Dependencies and Integration Points
It depends on `MCF_MBAR`, `MCF_CLK`, and ColdFire v3 cache definitions. Common serial, timer, DMA, I2C, GPIO, interrupt, and memory setup consume these constants.

## Risks
`CONFIG_OLDMASK` changes chip-select register naming and offsets. UART base order differs on NETtel/SecureEdgeMP3. Incorrect IRQPAR or chip-select programming can disable external devices.

## Test Signals
Build old-mask and regular configs. Runtime signals include console UART selection, timer/profile IRQs, I2C, DMA, and external chip-select device access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m5307sim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m53xxacr.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m53xxacr.h

## Purpose
`m53xxacr.h` defines cache and ACR configuration for ColdFire version 3 cores such as 5307 and 53xx.

## Important APIs, Types, and Functions
It defines CACR bits, ACR mode bits, cache sizes for `CONFIG_M5307` and `CONFIG_M53xx`, line size, ways, `CACHE_TYPE`, optional `CACHE_PUSH`, `CACHE_MODE`, `CACHE_INIT`, `CACHE_INVALIDATE`, `CACHE_INVALIDATED`, and RAM ACR modes.

## Control Flow, State, and Persistence
There is no runtime flow. Preprocessor choices select write-through or copy-back behavior and whether separate user A7 is enabled.

## Dependencies and Integration Points
Included by 5307 and 53xx SIM headers. Low-level cache setup and flush routines use these constants to program CACR/ACR registers.

## Risks
Copy-back cache requires correct push behavior for DMA and memory coherency. Cache size and line-size constants must match silicon. `CONFIG_COLDFIRE_SW_A7` changes user-stack behavior via `CACR_EUSP`.

## Test Signals
Run cache coherency and DMA tests under write-through and copy-back configs. Build coverage should include 5307 and 53xx cache sizes and validate flush loops use the defined line/way geometry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m53xxacr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m53xxsim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m53xxsim.h

## Purpose
`m53xxsim.h` is the large ColdFire 532x/53xx SoC register map, covering interrupt routing, clocks, boot setup, FlexBus, GPIO, PLL, system control, SDRAM, EPORT, and I2C.

## Important APIs, Types, and Functions
It defines CPU metadata, interrupt vectors and peripheral IRQs, interrupt controller registers, timer/profile IRQs, UART/FEC/QSPI/timer/reset/power-management bases, a board-specific assembler `m5329EVB_setup` macro and `PLATFORM_SETUP`, chip configuration module bits, FlexBus chip-select registers and masks, exhaustive GPIO data/direction/set/clear/pin-mux/drive-strength bits, generic GPIO aliases, PLL fields, SCM registers, SDRAM controller fields, EPORT registers, and I2C base/size.

## Control Flow, State, and Persistence
Most content is declarative. The assembler setup macro is early-boot control flow: it disables the watchdog, configures core SRAM via `RAMBAR1`, moves the stack into SRAM, and calls `sysinit`.

## Dependencies and Integration Points
It depends on `m53xxacr.h`, `MCF_CLK`, and assembler context for the EVB setup macro. Common ColdFire drivers use the UART, FEC, QSPI, timer, GPIO, SDRAM, FlexBus, and I2C constants.

## Risks
The header contains many absolute addresses; wrong SoC selection causes destructive MMIO writes. The EVB setup macro changes stack location before C code. GPIO and pin-mux bitfields are dense and easy to miscombine.

## Test Signals
Signals include M5329EVB early boot without dBUG initialization, UART console, FEC networking, QSPI, timer/profile IRQs, GPIO and pin-mux behavior, SDRAM sizing, FlexBus external device access, and I2C probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m53xxsim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m5407sim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m5407sim.h

## Purpose
`m5407sim.h` maps the ColdFire 5407 SIM and peripheral resources.

## Important APIs, Types, and Functions
It defines CPU name, bus clock, includes `m54xxacr.h`, and provides reset/watchdog, pin/IRQ assignment, PLL, bus master, interrupt, chip-select, DRAM, timer, UART, parallel port, DMA, GPIO, ICR alias, pin assignment, IRQ level/vector, and I2C constants.

## Control Flow, State, and Persistence
The file is macro-only. Hardware state is owned by SIM registers programmed by setup and drivers.

## Dependencies and Integration Points
It depends on `MCF_MBAR`, `MCF_CLK`, and v4 cache definitions. It supports common m68k/ColdFire serial, timer, DMA, GPIO, I2C, memory, and interrupt setup.

## Risks
The 5407 uses older SIM-style interrupt controls with fixed IRQ levels. Misconfigured chip-select or DRAM registers can break external memory/peripherals. GPIO support is limited to 16 pins.

## Test Signals
Signals include serial console, timer/profiler IRQs, DMA channel access, I2C, GPIO, and board memory/chip-select validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m5407sim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m5441xsim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m5441xsim.h

## Purpose
`m5441xsim.h` maps ColdFire 5441x SoC resources, including multi-controller interrupts and a broad modern peripheral set.

## Important APIs, Types, and Functions
It defines CPU metadata, `MACHINE`, `FPUTYPE`, `IOMEMBASE`, `IOMEMSIZE`, includes `m54xxacr.h`, and maps three interrupt controllers, UARTs, I2C, DSPI, FEC, GPIO/EPORT, DMA/eDMA interrupts, eSDHC, FlexCAN, timers, reset, and pin/peripheral registers.

## Control Flow, State, and Persistence
There is no executable code. Constants are consumed by setup and drivers to program persistent MMIO device state.

## Dependencies and Integration Points
It integrates with ColdFire v4 cache handling, `io_no.h` internal-I/O detection through `IOMEMBASE`, and common serial, Ethernet, SPI, I2C, GPIO, DMA, SDHCI, CAN, and interrupt-controller code.

## Risks
Multiple interrupt controllers and vector bases increase the chance of IRQ misrouting. `IOMEMBASE/IOMEMSIZE` directly affect endian handling in non-MMU I/O. Peripheral register overlap assumptions must match the 5441x manual.

## Test Signals
Build and boot 5441x configs, verify UART/FEC/I2C/DSPI/eSDHC/FlexCAN IRQs, GPIO/EPORT behavior, DMA error interrupts, and correct endian access for internal registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m5441xsim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxacr.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxacr.h

## Purpose
`m54xxacr.h` defines cache and ACR policy for ColdFire version 4 cores.

## Important APIs, Types, and Functions
It defines data/instruction/branch cache CACR bits, ACR base/mask/cache modes, `ACR_BA()` and `ACR_ADMSK()`, cache sizes for M5407/M54xx/M5441x, line size, ways, set masks, `CACHE_MODE`, `CACHE_INIT`, invalidate modes, optional `CACHE_PUSH`, and ACR modes for MMU and non-MMU configurations.

## Control Flow, State, and Persistence
There is no executable flow. Build-time configuration selects cache geometry and copy-back/write-through behavior.

## Dependencies and Integration Points
M5407, M54xx, and M5441x SIM headers include this file. Cache initialization, cacheflush code, and I/O mapping rely on its ACR definitions, especially `IOMEMBASE/IOMEMSIZE` under MMU.

## Risks
Version 4 has separate instruction/data caches and branch cache; incomplete invalidation can leave stale instructions or data. Copy-back mode requires dirty-line pushes before device DMA. ACR masks must match RAM and MMIO size.

## Test Signals
Signals include cache flush tests after code patching, DMA coherency tests, MMU and non-MMU boot, copy-back versus write-through configurations, and performance/branch-cache sanity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxacr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxgpt.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxgpt.h

## Purpose
`m54xxgpt.h` defines MCF54xx general purpose timer register addresses and bitfields.

## Important APIs, Types, and Functions
It maps four GPT channels through `MCF_GPT_GMS*`, `GCIR*`, `GPWM*`, `GSR*`, plus indexed macros `MCF_GPT_GMS(x)` and siblings. It defines mode, GPIO, interrupt, watchdog, input/output capture, PWM, counter, prescaler, status, overflow, and capture-field macros.

## Control Flow, State, and Persistence
The file is macro-only. Timer state persists in GPT registers controlled by timer, PWM, or GPIO drivers.

## Dependencies and Integration Points
It depends on `MCF_MBAR`. M54xx timer/PWM/GPIO watchdog users program the GPT through these constants.

## Risks
Indexed macros assume four channels at 0x10 spacing. Bitfield macros do not validate width, so callers must pass values already in range. Clearing status bits may be write-one-to-clear depending on hardware behavior outside this header.

## Test Signals
Use all four channels in timer, capture, PWM, and GPIO modes. Verify prescaler/counter programming, interrupt status handling, and watchdog enable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxgpt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxpci.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxpci.h

## Purpose
`m54xxpci.h` maps ColdFire 547x/548x PCI controller registers and helper bitfields.

## Important APIs, Types, and Functions
It defines PCI configuration, global status/control, target/initiator window, configuration address, TX/RX FIFO/packet registers, arbiter registers, `PCIGSCR_*`, `PCICAR_*`, `WXBTAR(hostaddr,pciaddr,size)`, initiator window flags, target enable bits, arbiter flags, and `PCICR1_CL()`/`PCICR1_LT()`.

## Control Flow, State, and Persistence
There is no local control flow. PCI bridge state persists in MBAR-mapped controller registers programmed during PCI host setup and transaction handling.

## Dependencies and Integration Points
It depends on `CONFIG_MBAR` and integrates with m54xx PCI host-controller setup, config-space access, address-window programming, and arbiter control.

## Risks
Window macros operate on high address bits and size masks; wrong values expose incorrect host memory or PCI ranges. Reset, parity, and system-error bits have controller-wide effects. FIFO register programming is hardware-specific.

## Test Signals
Signals include PCI bus enumeration, config reads/writes through `PCICAR`, memory and I/O BAR access through initiator windows, interrupt/error reporting, and arbiter behavior with multiple masters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxpci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxsim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxsim.h

## Purpose
`m54xxsim.h` maps ColdFire 547x/548x System Integration Unit resources.

## Important APIs, Types, and Functions
It defines CPU and machine metadata, `FPUTYPE`, `IOMEMBASE/IOMEMSIZE`, interrupt controller offsets, UART bases, system IRQ assignments, slice timer bases, GPIO data/direction/set/clear registers, EPORT registers, pin assignment registers and masks, and I2C base/size.

## Control Flow, State, and Persistence
The header is declarative. Persistent state lives in SIU MMIO registers programmed by platform code and drivers.

## Dependencies and Integration Points
It includes `m54xxacr.h` and feeds `io_no.h` internal-I/O checks, m54xx serial, timer, GPIO, EPORT, I2C, FEC/PSC-related pinmux users, and interrupt setup.

## Risks
`IOMEMBASE` controls endian behavior for ColdFire I/O accessors. Pin assignment registers multiplex many functions, so callers must coordinate read/modify/write updates. IRQ numbers are vector-base-relative.

## Test Signals
Boot M54xx configs, verify UARTs, slice timer tick/profiler, I2C, GPIO/EPORT interrupts, power/reset behavior, and correct internal peripheral endian access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/m54xxsim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_asc.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_asc.h

## Purpose
`mac_asc.h` defines offsets and control bits for the Apple Sound Chip used on classic Macintosh systems.

## Important APIs, Types, and Functions
It maps the ASC sample buffer (`ASC_BUF_BASE`, `ASC_BUF_SIZE`), control, enable, mode, volume, channel register, and per-channel frequency byte offset through `ASC_FREQ(chan, byte)`.

## Control Flow, State, and Persistence
There is no code. State persists in the ASC MMIO buffer and registers.

## Dependencies and Integration Points
Mac sound drivers and platform audio initialization use these constants when programming sample playback, volume, and frequency.

## Risks
The header exposes raw offsets only; users must know the mapped ASC base and required access widths. The `ASC_CHAN` comment marks uncertainty, so callers should avoid relying on undocumented semantics.

## Test Signals
Signals include ASC sample playback, volume control, frequency programming per channel, and no buffer overrun beyond the 0x800-byte buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_asc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_baboon.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_baboon.h

## Purpose
`mac_baboon.h` describes the Baboon custom IC on the PowerBook 190, particularly media-bay control and interrupts.

## Important APIs, Types, and Functions
It defines `BABOON_BASE`, `struct baboon` with media-bay control, status, and interrupt flag registers, `baboon_present`, and interrupt helpers `baboon_register_interrupts()`, `baboon_irq_enable()`, and `baboon_irq_disable()`.

## Control Flow, State, and Persistence
The header has no code. Runtime state includes hardware media-bay register bits and the global `baboon_present` flag.

## Dependencies and Integration Points
Mac interrupt code cascades Baboon interrupts from NuBus slot C, and IDE/media-bay code interprets status bits for device presence and IDE interrupt state.

## Risks
Several status/control bits are undocumented. The base address overlaps the IDE controller area, so careless struct access can affect IDE registers. Presence detection must guard all Baboon accesses.

## Test Signals
Signals include PowerBook 190 media-bay insertion/removal interrupts, IDE interrupt delivery through Baboon, slot power control behavior, and no Baboon access on non-Baboon Macs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_baboon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_iop.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_iop.h

## Purpose
`mac_iop.h` defines Apple Macintosh I/O Processor register layout, message protocol constants, and kernel message structures for SCC and ISM IOPs.

## Important APIs, Types, and Functions
It defines IOP base addresses for IIfx and Quadra, status/control bits, IOP counts, channel/message sizes, channel states, message statuses, shared-memory offsets, `struct mac_iop`, `struct iop_msg`, presence globals, and APIs for listening, sending, completing, uploading/downloading/comparing code, polling ISM IRQs, and registering interrupts.

## Control Flow, State, and Persistence
Message state persists in `struct iop_msg` queues and in IOP shared RAM. The control model sends messages by channel, waits for reply/complete states, and handles unsolicited messages through registered handlers.

## Dependencies and Integration Points
Mac serial, ADB/floppy/storage-management paths can use SCC and ISM IOPs. Interrupt registration integrates with Mac IRQ routing.

## Risks
The hardware has bypass and firmware-mediated modes; using the wrong register union can corrupt devices. Message queues require correct completion handling to avoid stuck channels. Shared-memory offsets are protocol ABI.

## Test Signals
Signals include SCC serial through IOP, ISM polling, message send/reply completion, unsolicited handler delivery, firmware upload/download comparison, and interrupt registration on IIfx/Quadra models.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_iop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_oss.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_oss.h

## Purpose
`mac_oss.h` describes the OSS interrupt and ROM-control chip used in place of VIA2 on Macintosh IIfx systems.

## Important APIs, Types, and Functions
It defines `OSS_BASE`, interrupt source indexes and pending bits for NuBus slots, IOPs, sound, SCSI, 60 Hz, VIA1, parity, and unused lines, `OSS_POWEROFF`, `struct mac_oss`, globals `oss` and `oss_present`, plus interrupt registration/enable/disable APIs.

## Control Flow, State, and Persistence
The header is declarative. Runtime state is the OSS register block, including interrupt level assignments, pending bits, poweroff control, and 60 Hz acknowledgement.

## Dependencies and Integration Points
Mac IRQ setup uses OSS for IIfx interrupt routing. Poweroff and timer acknowledgment code use `rom_ctrl` and `ack_60hz`.

## Risks
OSS is not VIA-compatible beyond selected behavior. Interrupt pending bits are 16-bit fields and require correct endian/access width. Poweroff is a ROM-control bit with machine-wide effect.

## Test Signals
IIfx boot should detect `oss_present`, route NuBus/SCSI/IOP/sound interrupts, acknowledge 60 Hz ticks, and power off through `OSS_POWEROFF`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_oss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_psc.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_psc.h

## Purpose
`mac_psc.h` defines the Apple Peripheral System Controller used on AV Macs for DMA, sound, SCC, Ethernet, SCSI, FDC, and interrupt control.

## Important APIs, Types, and Functions
It defines `PSC_BASE`, IFR/IER offsets, one-shot DMA control/address/length/command offsets for SCSI, Ethernet, FDC, SCC receive/transmit channels, sound DMA/control/source/status registers, global `psc`, interrupt registration/enable/disable APIs, and inline byte/word/long accessors.

## Control Flow, State, and Persistence
The inline accessors directly read/write the mapped PSC register space. PSC DMA state persists in hardware channel registers; sound DMA may run continuously.

## Dependencies and Integration Points
Mac AV Ethernet, SCSI, serial, floppy, sound, and interrupt code use these offsets. PSC interrupts occupy several level groups in `macints.h`.

## Risks
Some fields are explicitly inferred or unknown. Sound DMA can overwrite memory if not disabled early. DMA channels use paired one-shot buffers, so driver sequencing must flip channels correctly.

## Test Signals
Signals include PSC interrupt enable/disable per level, MACE Ethernet DMA, SCSI/FDC/SCC DMA transfers, sound DMA shutdown at boot, and correct byte/word/long register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_psc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_via.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_via.h

## Purpose
`mac_via.h` maps the Macintosh VIA/RBV register interface and bit definitions for ADB, RTC, SCC, sound, NuBus, video, cache, power, and interrupt routing.

## Important APIs, Types, and Functions
It defines VIA/RBV base addresses, VIA1/VIA2/RBV port bits, 6522 register offsets, RBV-specific registers, monitor and interrupt-enable helper macros, globals `via1`, `via2`, `rbv_present`, `via_alt_mapping`, and APIs for L2 flush, interrupt registration/enabling/disabling, NuBus IRQ startup/shutdown, VIA1 IRQ handling, head select, and SCSI DRQ checks.

## Control Flow, State, and Persistence
The header has no implementation, but callers manipulate persistent VIA/RBV MMIO state. `IER_SET_BIT`/`IER_CLR_BIT` encode the 6522 interrupt-enable convention.

## Dependencies and Integration Points
Mac ADB, RTC, SCSI, NuBus, poweroff, video, cache flush, and IRQ code all depend on these definitions. `macints.h` maps IRQ numbers for VIA sources.

## Risks
Many bits differ by model, and comments document incomplete or conflicting sources. VIA2 may be an RBV or OSS replacement, so callers must check presence flags. Some bits control power or cache.

## Test Signals
Signals include ADB/RTC operation, VIA timer interrupts, NuBus interrupt cascade, RBV monitor detection, cache flush behavior, poweroff, and correct handling of machines without real VIA2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_via.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/machdep.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/machdep.h

## Purpose
`machdep.h` declares the m68k machine-dependent callback table used by generic architecture code to call platform implementations.

## Important APIs, Types, and Functions
It declares function-pointer globals for scheduler, IRQ initialization, model/hardware reporting, RTC clock and PLL access, reset/halt, IDE init/setup, heartbeat, L2 flush, and beep. It also declares `hw_timer_init()`, optional `timer_heartbeat()`, and `config_BSP()`.

## Control Flow, State, and Persistence
The function pointers are global platform state initialized during machine setup. Generic code branches indirectly through them for operations that vary by machine.

## Dependencies and Integration Points
It depends on seq_file, interrupt, time, RTC, and buffer-head type declarations. All m68k machine ports provide or assign these hooks.

## Risks
Null or incorrectly assigned hooks cause boot-time or runtime failures. Callback signatures are ABI between machine code and generic m68k code. The heartbeat stub hides absence when `CONFIG_HEARTBEAT` is disabled.

## Test Signals
Boot each machine family and verify model reporting, IRQ init, RTC read/write, reset/halt, optional IDE setup, heartbeat, L2 flush, and beep behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/machdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/machines.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/machines.h

## Purpose
`machines.h` defines Sun machine-type decoding constants used with IDPROM machine identifiers.

## Important APIs, Types, and Functions
It defines `struct Sun_Machine_Models`, `NUM_SUN_MACHINES`, architecture masks and values (`SM_SUN3`, `SM_SUN3X`, etc.), type masks, and model IDs for Sun3, Sun3x, and legacy Sun4/Sun4c/Sun4m classes.

## Control Flow, State, and Persistence
There is no runtime code. Constants decode the `id_machtype` byte read from IDPROM.

## Dependencies and Integration Points
Sun3 IDPROM code and model reporting use these constants. The header is adapted from broader SPARC definitions but reduced for the m68k Sun3 port.

## Risks
The include guard still uses `_SPARC_MACHINES_H`, which is historically odd but functional. The model count must remain aligned with the model table in `arch/m68k/sun3/idprom.c`.

## Test Signals
Signals include correct decoding of Sun3/160, 3/50, 3/260, 3/110, 3/60, 3/E, 3/460, and 3/80 IDPROM values and matching model-table bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/machines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/machw.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/machw.h

## Purpose
`machw.h` defines Macintosh video memory mapping constants.

## Important APIs, Types, and Functions
It defines `VIDEOMEMBASE` as `0xf0000000`, `VIDEOMEMSIZE` as 4 MiB, and `VIDEOMEMMASK` as the negative 4 MiB mask.

## Control Flow, State, and Persistence
There is no code. The constants describe the virtual video-memory mapping installed by early assembly.

## Dependencies and Integration Points
Mac framebuffer and early console code use these constants to address mapped video RAM.

## Risks
The constants assume `head.S` installed the mapping. Incorrect size or mask assumptions can wrap or alias framebuffer access.

## Test Signals
Signals include working early framebuffer access and no video memory access beyond the mapped 4 MiB range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/machw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/macintosh.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/macintosh.h

## Purpose
`macintosh.h` defines core Macintosh platform APIs, model descriptors, hardware-type enums, and bootloader-provided data.

## Important APIs, Types, and Functions
It declares reset/poweroff/IRQ functions, IRQ enable/disable hooks, PRAM read/write/size APIs, `struct mac_model`, hardware type constants for ADB, VIA, SCSI, IDE, SCC, Ethernet, expansion, and floppy, `macintosh_config`, `struct mac_booter_data`, and `mac_bi_data`.

## Control Flow, State, and Persistence
Machine setup fills `macintosh_config` and `mac_bi_data` from bootinfo. PRAM functions persist small values in battery-backed storage. IRQ functions control runtime interrupt state.

## Dependencies and Integration Points
It includes Mac bootinfo plus Linux seq/interrupt/irq headers. Mac drivers branch on the model descriptor to choose ADB, SCSI, IDE, serial, Ethernet, expansion, and floppy implementations.

## Risks
Hardware type enums are compact char fields; unsupported or mismatched values send drivers down wrong paths. PRAM writes have persistent side effects. Bootloader data must be trusted but validated by setup code where possible.

## Test Signals
Signals include correct model identification, PRAM access, reset/poweroff, IRQ enable/disable, and driver selection for representative Mac II, Quadra, PowerBook, LC, and AV systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/macintosh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/macints.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/macints.h

## Purpose
`macints.h` defines the Macintosh m68k IRQ numbering scheme and named interrupt aliases.

## Important APIs, Types, and Functions
It defines source base offsets for VIA1, VIA2, PSC levels 3-6, NuBus, and Baboon, `NUM_MAC_SOURCES`, helpers `IRQ_SRC()` and `IRQ_IDX()`, aliases for ADB, VBlank, timers, SCSI, MACE, SCC, NuBus slots, Baboon lines, and `SLOT2IRQ()`/`IRQ2SLOT()`.

## Control Flow, State, and Persistence
There is no control flow. The macros encode a stable IRQ namespace where each source block has eight indexes.

## Dependencies and Integration Points
It includes `asm/irq.h` and is consumed by Mac VIA/PSC/OSS/Baboon/NuBus interrupt-controller code and device drivers.

## Risks
Aliases overlap where different machines route similar functions through PSC or OSS. The slot conversion assumes NuBus slot numbering offset by 47.

## Test Signals
Signals include registration and delivery for VIA timers/ADB, SCSI/SCSIDRQ, PSC MACE/SCC, OSS SCC, NuBus slots 9-F, and Baboon media-bay interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/macints.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/math-emu.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/math-emu.h

## Purpose
`math-emu.h` defines the internal ABI for the m68k software FPU emulator, including FPSR/FPCR bit fields, C data structures, debug helpers, and assembler macros.

## Important APIs, Types, and Functions
It defines FPSR accrued/exception/condition-code bits, FPCR rounding and precision constants, debug masks, `union fp_mant64`, `union fp_mant128`, `struct fp_ext`, `struct fp_data`, `FPDATA`, `dprint()`, `uprint()`, assembler offsets, PC access macros, instruction fetch helpers, user-memory access macros with exception-table fixups, and debug printing macros.

## Control Flow, State, and Persistence
For C, emulator state lives in `current->thread.fp` as `struct fp_data`. For assembly, macros advance saved PC, fetch instruction words/longs from user space, and recover faults through fixup sections.

## Dependencies and Integration Points
It depends on `setup.h`, `linkage.h`, scheduler/current task state, printk, pt_regs offsets, and thread FP register offsets. FPU emulator C and assembly files share this layout.

## Risks
The header explicitly requires synchronization with `asm/fpu.h` and assembler offsets. User access macros are fault-sensitive. Big-endian quotient extraction is assumed. Debug printing can perturb emulator timing.

## Test Signals
Signals include FPU emulator instruction suites, rounding/precision tests, exception bit behavior, user fault recovery during instruction operand access, signal/context-switch preservation, and assembler offset validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/math-emu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mc146818rtc.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mc146818rtc.h

## Purpose
`mc146818rtc.h` provides machine-dependent CMOS RTC access macros for m68k, currently for Atari systems.

## Important APIs, Types, and Functions
Under `CONFIG_ATARI`, it includes `atarihw.h`, defines `ATARI_RTC_PORT(x)`, `RTC_ALWAYS_BCD`, `CMOS_READ(addr)`, and `CMOS_WRITE(val, addr)`. Reads and writes select an RTC register through port 0 and transfer data through port 1.

## Control Flow, State, and Persistence
The macros perform two I/O operations per RTC access. RTC state persists in hardware CMOS registers.

## Dependencies and Integration Points
Generic MC146818 RTC code uses `CMOS_READ` and `CMOS_WRITE`. Atari I/O helpers provide the port access functions.

## Risks
Only Atari is implemented here. The macros are statement expressions and evaluate arguments in the access sequence. Incorrect port spacing breaks all RTC access. `RTC_ALWAYS_BCD` indicates callers must not force BCD assumptions.

## Test Signals
Atari builds should read and set system time through the RTC, handle binary/BCD mode correctly, and avoid RTC regressions on non-Atari configs where these macros are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mc146818rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcf8390.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcf8390.h

## Purpose
`mcf8390.h` supplies board-specific NE2000/NS8390 Ethernet resource definitions for ColdFire evaluation and embedded boards.

## Important APIs, Types, and Functions
It defines byte/word swap helpers `BSWAP` and `RSWAP`, and conditional resource macros such as `NE2000_ADDR`, optional `NE2000_ADDR0/1`, `NE2000_ODDOFFSET`, `NE2000_ADDRSIZE`, IRQ vector/priority/level values, and `NE2000_BYTE` access type for boards including ARN5206, M5206eC3, NETtel, M5307C3, SecureEdgeMP3, ARN5307, and M5407C3.

## Control Flow, State, and Persistence
There is no code. Kconfig selects one resource map at compile time, and driver state persists in the NE2000 device and interrupt controller.

## Dependencies and Integration Points
ColdFire 8390-compatible Ethernet drivers include this header to locate the device, handle odd-register addressing, byte swapping, and IRQ setup.

## Risks
Board conditionals overlap for some CPU families and must be selected precisely. Swap behavior differs between boards; wrong `BSWAP/RSWAP` corrupts packet/register data. Some NETtel 5307 configs define two NE2000 devices.

## Test Signals
Signals include successful NE2000 probe, correct MAC register access, packet transmit/receive, IRQ delivery, and odd-offset addressing on each supported board configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcf8390.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcf_pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcf_pgalloc.h

## Purpose
`mcf_pgalloc.h` implements ColdFire page-table allocation helpers for the m68k MMU memory-management code.

## Important APIs, Types, and Functions
It defines `pte_free_kernel()`, `pte_alloc_one_kernel()`, `pmd_alloc_kernel()`, `pmd_populate()`, `pmd_populate_kernel`, `__pte_free_tlb()`, `pte_alloc_one()`, `pte_free()`, `pmd_free()`, `pgd_free()`, and `pgd_alloc()`. It uses `ptdesc` helpers and copies `swapper_pg_dir` into new PGDs.

## Control Flow, State, and Persistence
Allocation functions request DMA-capable zeroed page-table memory, run page-table constructors, and free on constructor failure. `pgd_alloc()` initializes a new PGD from the kernel swapper directory and clears user entries below `PAGE_OFFSET`.

## Dependencies and Integration Points
It depends on TLB headers, page-table descriptor helpers, `swapper_pg_dir`, and m68k page-table constants. The MM subsystem calls these functions during address-space creation, teardown, and TLB gather.

## Risks
Page tables are allocated with `GFP_DMA`, constraining memory sources. `pmd_free()` is `BUG()` because PMDs are embedded in PGDs; any generic MM path that tries to free one is fatal. Constructor/destructor pairing must stay exact.

## Test Signals
Signals include process creation/exit under memory pressure, mmap/munmap churn, fork/exec, TLB teardown, page-table leak checks, and validation that no generic path calls `pmd_free()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcf_pgalloc.h -->
