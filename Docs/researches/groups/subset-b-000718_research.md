# subset-b-000718 Research

Grouped research for the listed m68k Ceph-client source mirror files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/udivsi3.S -->
# sources/distributed-fs/ceph-client/arch/m68k/lib/udivsi3.S

## Purpose
Provides the exported `__udivsi3` unsigned 32-bit division helper for m68k configurations that need libgcc-style integer division support inside the kernel, especially CPUs without native full-width multiply/divide helpers.

## APIs, Flow, And State
The single public symbol is `__udivsi3`, exported with `EXPORT_SYMBOL`. Arguments are stack-passed dividend/divisor values and the quotient is returned in `d0`. Classic 680x0 code preserves `d2`, handles small divisors with two `divu` 16-bit operations, and handles large divisors by right-shifting dividend/divisor until the divisor fits in 16 bits, computing a tentative quotient, multiplying back, and correcting an overestimate by one. ColdFire builds use a 32-iteration non-restoring division algorithm over `(p,a)` in `d2:d0`, preserving `d2-d4` through a stack frame.

## Dependencies And Integration
Depends on assembler preprocessor label/register prefix macros and `<linux/export.h>`. It is selected by the m68k lib Makefile for `CONFIG_CPU_HAS_NO_MULDIV64` and is called by compiler-generated unsigned division sequences and by `__umodsi3`.

## Risks And Test Signals
Division-by-zero behavior is not guarded here and follows CPU/compiler ABI expectations. The highest-risk logic is quotient correction for large divisors and ColdFire carry handling. Test signals are m68k kernel builds, arithmetic selftests or boot paths using generated unsigned division, and modulo correctness through `__umodsi3`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/udivsi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/umodsi3.S -->
# sources/distributed-fs/ceph-client/arch/m68k/lib/umodsi3.S

## Purpose
Implements the exported `__umodsi3` unsigned 32-bit modulo helper for m68k kernels that rely on software arithmetic support.

## APIs, Flow, And State
The public symbol is `__umodsi3`, exported with `EXPORT_SYMBOL`. It reads dividend and divisor from the stack, calls `__udivsi3` to compute `a / b`, multiplies that quotient by the divisor, subtracts the product from the original dividend, and returns the remainder in `d0`. On non-ColdFire it calls `__mulsi3`; on ColdFire it uses native `mulsl`.

## Dependencies And Integration
Depends directly on `__udivsi3` and, for classic 680x0 builds, `__mulsi3`. The helper is built alongside the other libgcc arithmetic shims when the m68k CPU configuration lacks sufficient hardware arithmetic support. Compiler-generated unsigned modulo operations and other kernel code can bind to this exported symbol.

## Risks And Test Signals
Correctness inherits all division and multiplication edge cases, especially zero divisors and quotient overflow behavior. Stack offsets differ from `__udivsi3` because this routine pushes arguments for helper calls; regressions tend to show as widespread bad `%` results. Test signals include m68k arithmetic boot smoke tests and paired identities such as `a == (a / b) * b + (a % b)` for nonzero `b`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/lib/umodsi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/mac/Makefile

## Purpose
Defines the core object list for classic Macintosh m68k platform support.

## APIs, Flow, And State
The file contributes `config.o`, `macints.o`, `iop.o`, `via.o`, `oss.o`, `psc.o`, `baboon.o`, `macboing.o`, and `misc.o` to `obj-y`. There is no runtime state; its control flow is Kbuild object selection.

## Dependencies And Integration
This Makefile is consumed by the m68k architecture build. The selected objects collectively provide machine detection, machdep hooks, interrupt controllers, VIA/OSS/PSC/IOP support, Baboon IDE interrupt fan-out, sound, PRAM/RTC, reset, and poweroff services.

## Risks And Test Signals
Because every object is unconditional within the Mac directory, compile-time dependencies must be internally guarded by `CONFIG_*` checks and runtime model detection. Missing an object breaks early boot or device registration. Test signals are Mac m68k defconfig builds and successful boot through `config_mac()`, IRQ setup, timer init, and platform-device registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/baboon.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mac/baboon.c

## Purpose
Manages the Baboon custom IC used on the PowerBook 190 for IDE, PCMCIA, and media-bay interrupt fan-out behind NuBus slot C.

## APIs, Flow, And State
Exports runtime state through `int baboon_present` and keeps the MMIO pointer `static volatile struct baboon *baboon`. `baboon_init()` enables the driver only when `macintosh_config->ident == MAC_MODEL_PB190`; otherwise it clears state. `baboon_register_interrupts()` installs `baboon_irq()` as the chained handler for `IRQ_NUBUS_C`. The handler reads `mb_ifr & 0x07` and calls `generic_handle_irq()` for `IRQ_BABOON_0..2`. `baboon_irq_enable()` and `baboon_irq_disable()` proxy to the parent NuBus C IRQ because individual Baboon masks are undocumented.

## Dependencies And Integration
Depends on `asm/macintosh.h`, `asm/macints.h`, `asm/mac_baboon.h`, and the global `macintosh_config`. It integrates with `macints.c` through IRQ chip dispatch and with `config.c` through model feature selection, especially the Baboon IDE platform IRQ.

## Risks And Test Signals
The code documents an unresolved risk: clearing pending Baboon IRQs and per-source masking are unknown. Enabling/disabling the parent IRQ can affect all Baboon children. Test signals are PowerBook 190 IDE interrupts, `baboon_present` detection logs, and absence of stuck NuBus C interrupt storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/baboon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/config.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mac/config.c

## Purpose
Provides central Macintosh m68k platform configuration: bootinfo parsing, machdep hook wiring, model identification, hardware feature tables, early chip initialization, and platform-device registration.

## APIs, Flow, And State
Important globals are `struct mac_booter_data mac_bi_data`, `struct mac_model *macintosh_config` exported to drivers, and exported SCC platform devices `scc_a_pdev` and `scc_b_pdev`. `mac_parse_bootinfo()` decodes Mac-specific bootinfo tags into `mac_bi_data`. `config_mac()` installs `mach_sched_init`, `mach_init_IRQ`, `mach_get_model`, `mach_hwclk`, reset, halt, and optional beep hooks, then calls `mac_identify()` and reports the selected model. `mac_identify()` selects an entry from `mac_data_table`, prepares SCC MMIO/IRQ resources, logs booter video/time/memory data, and initializes IOP, OSS, VIA, PSC, Baboon, CUDA, and PMU discovery. `mac_platform_init()` is an `arch_initcall` registering SCC, SWIM floppy, SCSI, IDE, and Ethernet platform devices based on table fields.

## Dependencies And Integration
Depends on m68k setup, bootinfo, machdep, Mac IRQ, VIA/OSS/PSC/IOP, ADB/CUDA/PMU, platform device, ATA, RTC, and model constants. It is the integration point for Mac board files and for legacy drivers such as `mac_scsi`, `mac_esp`, `pata_platform`, `macsonic`, `mac89x0`, and `macmace`.

## Risks And Test Signals
The hardcoded model table includes comments about guesswork; incorrect feature classification can crash early MMIO probing or register wrong devices. Address resources are model-specific and historically subtle. Test signals are boot logs showing detected model and booter data, correct serial console resources, successful platform-device probing, and power/reset/clock operations on representative II, Quadra, AV, and PowerBook systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/iop.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mac/iop.c

## Purpose
Implements management and message passing for Macintosh I/O Processor chips, 6502-based controllers used for SCC serial and ISM/ADB functions on the IIfx and some Quadras.

## APIs, Flow, And State
Public state is `iop_scc_present` and `iop_ism_present`. Internal state includes `iop_base[NUM_IOPS]`, `iop_msg_pool`, per-IOP/channel send queues, and listener slots. `iop_init()` discovers SCC and ISM IOP base addresses from `macintosh_config`, initializes message pools and listeners, and restarts/clears the ISM alive flag. `iop_register_interrupts()` requests the appropriate ISM interrupt. `iop_listen()` registers channel callbacks. `iop_send_message()` allocates a message, queues it, and starts transmission when idle. Interrupt handling reads IOP INT0/INT1 status bits, drains completed send buffers via `iop_handle_send()`, dispatches unsolicited receive messages via `iop_handle_recv()`, and requires listeners to call `iop_complete_message()`.

## Dependencies And Integration
Depends on `asm/mac_iop.h` shared-memory offsets/states, Mac model data, Mac IRQ numbers, and interrupt APIs. ADB and serial subsystems consume the listener and send-message interface. The code integrates with OSS/VIA interrupt mappings through the chosen IRQ line.

## Risks And Test Signals
The pool allocator returns `NULL` on exhaustion, but `iop_handle_recv()` assumes success. Message state machine errors can stall a channel because each channel has a depth of one. Callbacks run in interrupt context and must be brief or defer work. Test signals are ISM alive checks, ADB keyboard/mouse traffic on IOP machines, SCC compatible mode behavior, and absence of stuck `MSG_NEW`/`MSG_COMPLETE` channel states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/iop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/mac.h -->
# sources/distributed-fs/ceph-client/arch/m68k/mac/mac.h

## Purpose
Declares cross-file Macintosh platform entry points used by the m68k Mac board-support objects.

## APIs, Flow, And State
The header forward-declares `struct rtc_time` and prototypes `baboon_init()`, `iop_init()`, `mac_hwclk()`, `mac_mksound()`, `oss_init()`, `psc_init()`, `via_init()`, and `via_init_clock()`. It defines no state and contains no control flow.

## Dependencies And Integration
Included by the Mac implementation files so `config.c` can call hardware initializers and machdep hooks without exposing local definitions through broader architecture headers. It bridges board files for Baboon, IOP, RTC, sound, OSS, PSC, and VIA.

## Risks And Test Signals
The header is intentionally narrow; drift between prototypes and implementations would be caught at compile time. Its main design risk is hiding APIs that may need broader declaration if external drivers start calling them. Test signal is a clean m68k Mac build with no implicit declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/mac_penguin.S -->
# sources/distributed-fs/ceph-client/arch/m68k/mac/mac_penguin.S

## Purpose
Stores a raw bitmap-like byte asset for the Macintosh “penguin” boot graphic.

## APIs, Flow, And State
The file contains only `.byte` data, beginning with an SPDX marker and then a large sequence of hexadecimal bytes. There are no symbols, functions, branches, or mutable state in this source.

## Dependencies And Integration
Integration is by assembler inclusion or object linkage from nearby boot/logo code rather than by callable API. The data likely represents a 1-bit or nibble-oriented image payload consumed by m68k Macintosh boot display logic.

## Risks And Test Signals
The risk is asset-format fragility: any byte edit can corrupt the displayed logo, and the lack of local dimensions or symbol labels means consumers must know the implicit format. Test signals are visual boot-logo rendering on Macintosh m68k configurations and successful assembly of the data file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/mac_penguin.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/macboing.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mac/macboing.c

## Purpose
Implements the classic Macintosh beep path for m68k, including basic ASC and partial Enhanced ASC handling.

## APIs, Flow, And State
The public entry point is `mac_mksound(freq, length)`, wired into `mach_beep` when `CONFIG_INPUT_M68K_BEEP` is enabled. Persistent state includes ASC register pointer, wave table, sample rate, timer, bell duration, phase, phase increment, and `mac_special_bell`. `mac_init_asc()` selects model-specific ASC addresses and special bell handlers, then builds a triangular waveform. `mac_mksound()` initializes lazily, dispatches to the special handler when set, or programs regular ASC sample registers and a stop timer. `mac_quadra_start_bell()` and `mac_quadra_ring_bell()` stream a generated waveform into Enhanced ASC at timer cadence. AV Singer support is a stub.

## Dependencies And Integration
Depends on `macintosh_config`, `asm/mac_asc.h`, timers, jiffies, and local IRQ exclusion. Integrated through `config_mac()` as the platform beep implementation.

## Risks And Test Signals
There is an apparent early return when `mac_special_bell == NULL`, making the regular ASC block unreachable for models without a special handler. The file also documents unimplemented AV and some Quadra support. Test signals are audible beep behavior on Q630/P475, no timer leaks after sound stops, and no MMIO faults on unsupported models.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/macboing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/macints.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mac/macints.c

## Purpose
Defines the Macintosh m68k IRQ chip and dispatches generic Mac interrupt enable/disable operations to VIA, OSS, PSC, and Baboon hardware layers.

## APIs, Flow, And State
`mac_init_IRQ()` installs a `mac_irq_chip` over machine-specific IRQ sources, chains the hardware dispatchers for VIA or OSS, PSC, Baboon, and IOP, and registers level-7 NMI handling. `mac_irq_enable()` and `mac_irq_disable()` inspect `IRQ_SRC(irq)` and call the appropriate controller-specific mask functions. `mac_irq_startup()` and `mac_irq_shutdown()` special-case NuBus slot IRQs on non-OSS systems to use VIA NuBus startup/shutdown semantics. The NMI handler uses a static recursion guard and dumps registers.

## Dependencies And Integration
Depends on Mac IRQ numbering, VIA/OSS/PSC/IOP/Baboon globals and registration functions, m68k IRQ controller setup, `get_irq_regs()`, and processor debug helpers. It is called through `mach_init_IRQ` installed by `config_mac()`.

## Risks And Test Signals
The switch-based routing assumes IRQ source encoding remains stable. NuBus and Baboon interrupts are nested through multiple chained handlers, so incorrect masking can lose shared interrupts or create storms. Test signals include timer, ADB, SCSI, SCC, NuBus, PSC, OSS, and NMI behavior on the relevant model families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/macints.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/misc.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mac/misc.c

## Purpose
Provides Macintosh-specific PRAM/NVRAM, RTC, poweroff, reset, and hardware-clock support.

## APIs, Flow, And State
Public APIs include `mac_pram_read_byte()`, `mac_pram_write_byte()`, `mac_pram_get_size()`, `mac_poweroff()`, `mac_reset()`, and `mac_hwclk()`. The file stores a `rom_reset` function pointer and uses model state to choose VIA RTC, CUDA, or PMU backends. VIA RTC commands bit-bang VIA1 port B lines with interrupts disabled, support one-byte and extended XPRAM commands, and clear/set write-protect around writes. `via_read_time()` repeatedly reads four RTC second registers until stable and subtracts the 1904-to-1970 offset. Reset uses CUDA/PMU when possible, otherwise a 68030 transparent-translation sequence or ROM reset vector.

## Dependencies And Integration
Depends on Mac ADB type from `macintosh_config`, VIA/OSS globals, CUDA/PMU APIs, m68k MMU/cache registers, `machdep` hooks, and Linux RTC/time helpers. `config_mac()` wires these functions into `mach_hwclk`, `mach_reset`, and `mach_halt`.

## Risks And Test Signals
RTC reads can fail to stabilize; CUDA shutdown intentionally avoids infinite polling on models whose PSU is not CUDA-controlled. Reset code is CPU- and mapping-sensitive and disables interrupts before MMU/register manipulation. Test signals are PRAM read/write, stable clock reads/writes, shutdown behavior on VIA/OSS/CUDA/PMU systems, and successful reset on 030 and non-030 machines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/oss.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mac/oss.c

## Purpose
Handles the IIfx Operating System Services chip, which replaces VIA2 and provides programmable interrupt levels.

## APIs, Flow, And State
Global state is `int oss_present` and `volatile struct mac_oss *oss`. `oss_init()` detects `MAC_MODEL_IIFX`, maps `OSS_BASE`, marks OSS present, and disables all interrupt sources by setting their level to zero. `oss_register_interrupts()` chains autovectors for ISM IOP, SCSI, NuBus, SCC IOP, and VIA1, then enables the VIA1 source. Handler functions translate OSS source events into Mac IRQs, including NuBus pending-bit fan-out. `oss_irq_enable()` and `oss_irq_disable()` map Mac IRQs to OSS source level registers, with VIA1 delegated to VIA routines.

## Dependencies And Integration
Depends on `asm/mac_oss.h`, VIA1 interrupt handling, Mac IRQ encodings, and `macintosh_config`. It integrates with `macints.c`, `iop.c`, and IIfx SCSI/SCC/ADB behavior.

## Risks And Test Signals
The file notes uncertainty about clearing pending OSS IRQs. Wrong level mapping can block IIfx ADB, SCSI, SCC, or NuBus. Test signals are IIfx boot IRQ routing, working ISM/SCC IOP interrupts, SCSI interrupts, NuBus slot dispatch, and poweroff via `oss->rom_ctrl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/oss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/psc.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mac/psc.c

## Purpose
Initializes and dispatches interrupts for the Apple Peripheral System Controller used on AV Macs.

## APIs, Flow, And State
The exported global is `volatile __u8 *psc`. `psc_init()` detects Centris 660AV and Quadra 840AV, assigns `PSC_BASE`, kills DMA channels with `psc_dma_die_die_die()`, optionally dumps registers, and masks/clears PSC interrupt groups 3 through 6. `psc_register_interrupts()` chains autovectors 3-6 to `psc_irq()` with group offsets. `psc_irq()` reads enabled pending bits from PSC IFR/IER registers, clears the bit, and dispatches `generic_handle_irq()` for `irq << 3 | index`. `psc_irq_enable()` and `psc_irq_disable()` set or clear individual IER bits.

## Dependencies And Integration
Depends on `asm/mac_psc.h`, Mac IRQ encodings, AV model detection, and generic IRQ chained handlers. It serves MACE Ethernet, SCC, DMA, and other AV-specific interrupt sources routed through `macints.c`.

## Risks And Test Signals
DMA shutdown and some PSC IFR groups are explicitly uncertain. A persistent interrupt condition on unused levels can cause storms if accidentally enabled. Test signals include AV Mac boot logs, MACE/SCC interrupt delivery, no unexpected PSC level 5/6 storms, and successful platform device probing for AV Ethernet/SCC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/psc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/via.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mac/via.c

## Purpose
Manages Macintosh VIA/RBV chips for interrupts, NuBus dispatch, RTC/ADB-related lines, L2 cache flush, and the VIA1 timer clocksource.

## APIs, Flow, And State
Public state includes `volatile __u8 *via1`, `via2`, `int rbv_present`, and exported `via_alt_mapping`. Internal state tracks RBV clear semantics, generic register offsets, `nubus_disabled`, and clock counters. `via_init()` maps VIA1/VIA2 or RBV based on `macintosh_config`, disables and clears interrupts, initializes timers, configures RTC lines, selects alternate Quadra interrupt mapping, initializes NuBus, and configures VIA2 PCR. Interrupt dispatchers read IFR/IER masks and call `generic_handle_irq()`. NuBus dispatch reads active-low slot lines and applies RBV SIER or VIA DirA masking. `via_irq_enable/disable()` manipulate VIA/RBV IER/SIER and manage the NuBus umbrella interrupt. `via_init_clock()` installs the timer IRQ and clocksource; `mac_read_clk()` derives continuous ticks from VIA T1 high byte and wrap flags.

## Dependencies And Integration
Depends on Mac model data, VIA/RBV register definitions, OSS/PSC presence, generic IRQ, clocksource, and legacy timer tick. It is the default IRQ and timing backend for non-OSS Macs and is also used by OSS for VIA1.

## Risks And Test Signals
NuBus masking on genuine VIA hardware is constrained by electrical behavior, so the `nubus_disabled` workaround must be preserved. Clocksource accuracy trades low overhead for high-byte-only reads. Test signals include timer ticks, monotonic clocksource behavior, VIA/RBV IRQ routing, NuBus cards, SCSI DRQ, floppy head select export, and IIci L2 cache flush behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mac/via.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/math-emu/Makefile

## Purpose
Builds the m68k floating-point emulator object set.

## APIs, Flow, And State
The Makefile adds `fp_entry.o`, `fp_scan.o`, `fp_util.o`, `fp_move.o`, `fp_movem.o`, `fp_cond.o`, `fp_arith.o`, `fp_log.o`, and `fp_trig.o` to `obj-y`. Optional debug flags for assembler and C are present but commented out.

## Dependencies And Integration
Consumed by Kbuild when the m68k FPU emulator is enabled. The listed objects form a pipeline: trap entry, instruction scan/decode, user-memory move/movem/condition handling, conversions/finalization, and C arithmetic/log/trig kernels.

## Risks And Test Signals
Object order matters mainly through symbol availability during linkage, not runtime sequencing. Enabling debug flags would change logging volume in trap context. Test signals are successful m68k FPU-emulator builds and execution of trapped FPU instructions on systems without hardware FPU or for unsupported instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_arith.c -->
# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_arith.c

## Purpose
Implements core arithmetic kernels for the m68k floating-point emulator using the internal unpacked extended format.

## APIs, Flow, And State
Exports constant operands `fp_QNaN` and `fp_Inf`, plus functions declared in `fp_arith.h`: sign operations, add/sub/compare/test, multiply/divide, single-precision multiply/divide variants, modulo/remainder, integer rounding, and scale. The functions mutate `dest` in place, may mutate `src` in some paths, and update emulated FPSR/FPCR state through `FPDATA`. Add/sub align exponents using `fp_denormalize()`, combine mantissas, and handle signed zero and infinities. Mul/div use 128-bit mantissa helpers. `fp_roundint()` implements FPCR rounding modes and sets inexact. `modrem_kernel()` computes quotient, rounds it, subtracts the product, and stores quotient bits.

## Dependencies And Integration
Depends on `fp_emu.h` macros and `multi_arith.h`. Called by opcode dispatch tables in `fp_scan.S`, with final normalization performed by `fp_util.S`.

## Risks And Test Signals
Many operations rely on normalized inputs and exact internal format invariants. `fp_fsub()` and comparison flip `src->sign`, so caller ownership matters. Mod/remainder are marked as potentially inefficient. Test signals are FADD/FSUB/FMUL/FDIV/FCMP/FMOD/FREM/FINT/FSCALE instruction tests across zeros, infinities, NaNs, denormals, rounding modes, overflow, underflow, and divide-by-zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_arith.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_arith.h -->
# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_arith.h

## Purpose
Declares the C arithmetic kernels used by the m68k floating-point emulator dispatch layer.

## APIs, Flow, And State
The header exposes functions operating on `struct fp_ext *dest` and `struct fp_ext *src`: `fp_fabs`, `fp_fneg`, `fp_fadd`, `fp_fsub`, `fp_fcmp`, `fp_ftst`, `fp_fmul`, `fp_fdiv`, `fp_fsglmul`, `fp_fsgldiv`, `fp_fmod`, `fp_frem`, `fp_fint`, `fp_fintrz`, and `fp_fscale`. It defines no state or inline behavior.

## Dependencies And Integration
Requires the `struct fp_ext` definition from `fp_emu.h`/`asm/math-emu.h` before use. Included by `fp_arith.c` and other C math modules, while assembly dispatch references the compiled symbols directly.

## Risks And Test Signals
The ABI is pointer-based and mutating; callers must know operand ordering used by the emulator, especially for divide, modulo, and subtract. Compile-time coverage catches declaration drift; runtime instruction tests verify that dispatch table entries match the intended prototype and operand convention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_arith.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_cond.S -->
# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_cond.S

## Purpose
Implements floating-point conditional instructions for the emulator: FDBcc, FScc, FBcc word/long, and condition-code computation.

## APIs, Flow, And State
Global entry points are `fp_fscc`, `fp_fbccw`, and `fp_fbccl`; `fp_fdbcc` is reached through the FScc decode table. Branch handlers compute target PCs from extension displacements and update emulated PC when `fp_compute_cond()` returns true. `fp_fscc` decodes destination effective addresses, writes `0xff` or `0x00` to data register or user memory, and handles data-register byte replacement. `fp_fdbcc` decrements a data register low word when the condition is false and branches if it has not underflowed. `fp_compute_cond()` reads `FPD_FPSR`, optionally raises NaN-related exception bits, and evaluates the 16 Motorola ordered/unordered condition predicates from NAN/Z/N bits.

## Dependencies And Integration
Depends on `fp_decode.h` addressing macros, `fp_emu.h` FPSR offsets, register accessor helpers from `fp_entry.S`, user access fixups, and `fp_end`.

## Risks And Test Signals
Condition behavior is tightly coupled to FPSR bit layout and unordered NaN semantics. Effective-address macros intentionally do not reject every invalid mode. Test signals are FScc/FDBcc/FBcc instruction suites covering all condition codes, NaN comparisons, data-register and memory destinations, PC-relative displacements, and user-access faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_cond.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_decode.h -->
# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_decode.h

## Purpose
Defines assembler macros for decoding m68k FPU instruction classes, operand formats, addressing modes, extension words, and effective addresses.

## APIs, Flow, And State
The file is macro-only. It documents register conventions: `d2` holds instruction words, `d1` often holds size/count, `a0/a1` hold effective/source addresses, and `a2` points at task/FP state. Macros dispatch through PC-relative jump tables for instruction type and addressing mode, extract bitfields, fetch extension words, compute base/index/outer displacements, handle PC-relative modes unless disabled, and update address registers for postincrement/predecrement. Build-time variables such as `do_fmovem`, `do_fmovem_cr`, `do_no_pc_mode`, and `do_fscc` alter macro behavior.

## Dependencies And Integration
Included by `fp_scan.S`, `fp_move.S`, `fp_movem.S`, and `fp_cond.S`. Depends on user access macros, register accessor routines, debug-print macros, and labels such as `fp_ill` and `fp_err_ua1`.

## Risks And Test Signals
This is a high-risk shared decode layer: a macro bug can affect many instructions. The file explicitly allows some disallowed addressing modes if they do not crash emulation. Test signals are broad effective-address coverage, stack-pointer byte-move adjustment tests, PC-relative addressing, full extension word indexing, and user fault recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_decode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_emu.h -->
# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_emu.h

## Purpose
Provides shared C and assembly definitions for the m68k floating-point emulator, including status manipulation, normalization linkage, and core operand helpers.

## APIs, Flow, And State
For C, it defines `IS_INF`, `IS_ZERO`, `fp_set_sr()`, `fp_set_quotient()`, `fp_copy_ext()`, monadic/dyadic normalization checks, `fp_set_nan()`, `fp_set_ovrflw()`, and inline-assembly calls into conversion routines such as `fp_normalize_ext()` and `fp_conv_ext2long()`. For assembly, it defines `fp_set_sr`, `fp_clr_sr`, and `fp_tst_sr` macros that operate on the emulated FPSR in `FPDATA`. It declares external constants `fp_QNaN` and `fp_Inf`.

## Dependencies And Integration
Includes `asm/math-emu.h`, and for assembler includes `asm/asm-offsets.h`. It is included by nearly every math-emulator C and assembly file, making it the glue between `struct fp_ext`, `FPDATA`, and low-level labels in `fp_util.S`.

## Risks And Test Signals
Inline assembly constraints and register assumptions are ABI-sensitive. The `fp_conv_long2ext` macro appears to jump to `fp_conv_ext2long`, so conversion helper naming should be verified against actual behavior. Test signals are compile tests, trap instruction tests, status-register bit tests, and C/assembly interop around `a0/d0` clobbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_emu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_entry.S -->
# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_entry.S

## Purpose
Provides the trap entry point for FPU emulation and helper routines for accessing saved integer/address registers during instruction decoding.

## APIs, Flow, And State
The global entry `fpu_emu` saves interrupt context, gets `current`, adjusts 040/060 PC state when needed, calls `fp_scan`, handles 68060 trace delivery, and returns via `ret_from_exception`. User-access fixup labels `fp_err_ua1` and `fp_err_ua2` repair the stack and call `fpemu_signal(SIGSEGV, SEGV_MAPERR, a0)`. The file also exports `fp_get_data_reg`, `fp_put_data_reg`, `fp_get_addr_reg`, and `fp_put_addr_reg`, using jump tables to read/write saved registers in the trap frame, live callee-saved registers, or USP for A7. `fp_debugprint` stores debug masks.

## Dependencies And Integration
Depends on `SAVE_ALL_INT`, `GET_CURRENT`, m68k pt_regs offsets, `fp_scan`, `fpemu_signal`, `ret_from_exception`, CPU feature symbols, and `fp_emu.h`. Decode and move files call the register helper labels.

## Risks And Test Signals
Register accessor offsets assume the exact saved exception stack layout. User-access fixup stack adjustment must match call depth. Test signals are trapped FPU instructions using every data/address register, user-memory fault tests, 040/060 PC handling, and ptrace/trace behavior on 68060.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_log.c -->
# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_log.c

## Purpose
Implements selected logarithmic/exponential-class FPU emulator operations, with full square-root support and stubs for many transcendental functions.

## APIs, Flow, And State
Functions declared in `fp_log.h` operate on `struct fp_ext` operands. `fp_fsqrt()` normalizes input, rejects negative nonzero operands as NaN, handles zero/infinity, creates an initial approximation, and applies nine Newton iterations using existing add/div kernels before rebiasing the exponent. `fp_fgetexp()` converts the unbiased exponent to an extended integer value, while `fp_fgetman()` returns the mantissa with exponent set to one. `fp_fetoxm1`, `fp_fetox`, `fp_ftwotox`, `fp_ftentox`, `fp_flogn`, `fp_flognp1`, `fp_flog10`, and `fp_flog2` log unimplemented status through `uprint()`, run monadic checks, and return the copied source.

## Dependencies And Integration
Depends on `fp_arith.h` for Newton operations, `fp_emu.h` status/normalization, and dispatch entries in `fp_scan.S`.

## Risks And Test Signals
Many advertised operations are effectively unimplemented pass-throughs, so programs using transcendentals may get incorrect results without a hard fault. `fp_fsqrt()` modifies temporary operands through arithmetic helpers. Test signals include FSQRT accuracy/exception tests and explicit coverage showing which transcendental opcodes are unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_log.h -->
# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_log.h

## Purpose
Declares logarithmic, exponential, square-root, and exponent/mantissa extraction helpers for the floating-point emulator.

## APIs, Flow, And State
The header declares `fp_fsqrt`, `fp_fetoxm1`, `fp_fetox`, `fp_ftwotox`, `fp_ftentox`, `fp_flogn`, `fp_flognp1`, `fp_flog10`, `fp_flog2`, `fp_fgetexp`, and `fp_fgetman`. All use the internal `struct fp_ext *dest, *src` convention and return `dest`. It defines no state.

## Dependencies And Integration
Includes `fp_emu.h` for `struct fp_ext` and emulator status definitions. It is included by `fp_log.c`; assembly dispatch resolves the compiled symbols.

## Risks And Test Signals
The declarations expose operations that are only partially implemented in `fp_log.c`. Consumers must not infer full Motorola 68881 transcendental accuracy from the prototypes. Test signals are compile-time prototype matching and runtime opcode tests that distinguish implemented FSQRT/FGETEXP/FGETMAN from pass-through unimplemented operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_move.S -->
# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_move.S

## Purpose
Implements `fmove` from emulated FP registers to integer registers or memory in the m68k FPU emulator.

## APIs, Flow, And State
The global entry is `fp_fmove_fp2mem`. It clears current exception status, decodes destination format and effective address, fetches the source FP register into a temporary stack-backed copy, normalizes it, converts to byte/word/long/single/double/extended as requested, writes to data registers or user memory, and jumps to `fp_final`. Packed decimal output is explicitly unsupported and routes to `fp_ill`. Data-register writes preserve unaffected bytes/words by reading the existing register and replacing only the requested portion.

## Dependencies And Integration
Depends on `fp_decode.h`, `fp_emu.h`, register accessors from `fp_entry.S`, conversion/finalization routines in `fp_util.S`, and user access exception labels. Called from `fp_scan.S` when the decoded move type is register-to-effective-address.

## Risks And Test Signals
Stack use around 12-byte temporary operands must match cleanup paths, especially unsupported packed formats. Correctness depends on destination-size conversion and rounding status. Test signals are FMOVE from FP registers to all supported data sizes, register partial writes, postincrement/predecrement address updates, user-memory fault handling, and packed-format illegal-instruction behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_move.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_movem.S -->
# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_movem.S

## Purpose
Implements FPU multiple-register moves for data FP registers and FP control registers.

## APIs, Flow, And State
Global entries are `fp_fmovem_fp` and `fp_fmovem_cr`. `fp_fmovem_fp` decodes static or dynamic FP register masks, counts selected registers for addressing updates, decodes memory effective address, and moves 12-byte extended register images between user memory and `FPD_FPREG`, supporting incremental and decremental order. `fp_fmovem_cr` moves FPCR/FPSR/FPIAR between data/address registers, immediate/memory operands, and `FPDATA`; after writes it masks reserved bits and derives cached `FPD_RND` and `FPD_PREC` fields from FPCR.

## Dependencies And Integration
Depends on decode macros configured with `do_fmovem` and `do_fmovem_cr`, user access helpers, `FPDATA` offsets, and register helpers. It is selected by `fp_scan.S` move-type dispatch for `fmovem` encodings.

## Risks And Test Signals
Register masks, predecrement order, and 12-byte extended layout are easy to regress. Control-register reserved-bit masking affects later rounding and precision globally for the task’s emulated FPU state. Test signals are FMOVEM static/dynamic masks, predecrement/postincrement modes, FPCR rounding/precision effects, FPSR/FPIAR transfer tests, and user fault recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_movem.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_scan.S -->
# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_scan.S

## Purpose
Decodes trapped FPU instructions and dispatches them to move, conditional, arithmetic, log, trig, and finalization routines.

## APIs, Flow, And State
The global entry is `fp_scan`, with `fp_datasize` exported as an operand-format size table. `fp_scan` fetches the current user PC, verifies the coprocessor opcode byte, reads the first two instruction words, advances PC, and dispatches by condition/move instruction type. For source-effective-address operations it decodes operand format, converts source data into `FPD_TEMPFP1`, resolves the destination FP register, pushes source/dest pointers and a finalization return, and jumps through a 128-entry operation table. It also handles FPU ROM constants (`fmovecr`) via a constant table and rewrites dispatch for single/double precision variants.

## Dependencies And Integration
Depends on PC get/put and user access macros, `fp_decode.h`, conversion routines from `fp_util.S`, C arithmetic/log/trig symbols, move/movem/condition entries, and `fp_finalrounding`.

## Risks And Test Signals
The opcode dispatch table is the emulator’s central routing point; wrong indices silently bind opcodes to the wrong implementation. Packed BCD and nonstandard opcodes are unsupported. Test signals are instruction decode coverage for every supported operation, operand format conversions, immediate operands, fmovecr constants, single/double precision opcode variants, and illegal-instruction paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_scan.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_trig.c -->
# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_trig.c

## Purpose
Provides placeholder implementations for trigonometric and hyperbolic FPU emulator operations.

## APIs, Flow, And State
Functions include `fp_fsin`, `fp_fcos`, `fp_ftan`, `fp_fasin`, `fp_facos`, `fp_fatan`, `fp_fsinh`, `fp_fcosh`, `fp_ftanh`, `fp_fatanh`, and `fp_fsincos0..7`. Most call `uprint()` with the opcode name, run `fp_monadic_check(dest, src)`, and return the copied/normalized source rather than computing the mathematical function. The `fsincos` variants only log and return `dest`, without copying `src`.

## Dependencies And Integration
Depends on `fp_emu.h` and `fp_trig.h`. The functions are reached from the `fp_scan.S` opcode table for 68881 trigonometric instructions.

## Risks And Test Signals
These routines are not mathematically implemented, so any workload relying on them receives incorrect pass-through or stale results. The risk is functional rather than memory-safety oriented. Test signals should assert current unsupported behavior or, preferably, fail expected-accuracy tests until real implementations are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_trig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_trig.h -->
# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_trig.h

## Purpose
Declares trigonometric, inverse-trigonometric, hyperbolic, and `fsincos` helpers for the floating-point emulator.

## APIs, Flow, And State
The public prototypes are `fp_fsin`, `fp_fcos`, `fp_ftan`, `fp_fasin`, `fp_facos`, `fp_fatan`, `fp_fsinh`, `fp_fcosh`, `fp_ftanh`, `fp_fatanh`, and `fp_fsincos0` through `fp_fsincos7`. All use the emulator’s internal `struct fp_ext *dest, *src` convention. The header contains no state.

## Dependencies And Integration
Includes `fp_emu.h`. It is used by `fp_trig.c`; assembly dispatch references the emitted C symbols through the operation table.

## Risks And Test Signals
The prototypes imply broad operation coverage, but the implementation is placeholder. Test signals are compile-time declaration matching and runtime instruction tests documenting unsupported trig behavior until real algorithms are implemented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_trig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_util.S -->
# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_util.S

## Purpose
Provides conversion, normalization, rounding, final status, and completion helpers for the m68k floating-point emulator.

## APIs, Flow, And State
Global labels include `fp_ill`, `fp_end`, conversions from long/single/double/extended to internal extended, normalization routines for extended/single/double precision, conversions back to double/single/integer sizes, precision-specific finalization labels, `fp_finaltest`, and `fp_final`. Source conversions unpack external formats into `struct fp_ext`. `fp_conv_ext2ext` and `fp_normalize_ext` normalize mantissas, identify NaNs/infinities, and handle optional extra precision. Single/double normalization implement IEEE-style rounding modes, underflow/overflow handling, denormals, sticky bits, and inexact/overflow/underflow FPSR bits. Integer conversion is generated by `conv_ext2int`. Finalization sets condition-code bits and accrued exception bits, then returns through `fp_end`.

## Dependencies And Integration
Depends on `FPDATA` layout from `fp_emu.h`, user access fixup labels, debug macros, and all dispatch code that needs operand conversion or final status. It is the main ABI boundary between assembly decode and C arithmetic results.

## Risks And Test Signals
This file is dense and bit-level; off-by-one exponent bias, sticky-bit, or rounding-mode mistakes affect many opcodes. `fp_final` has an optimized accrued-exception path marked historically untested. Test signals are exhaustive format conversion tests, rounding-mode matrices, NaN/signaling-NaN behavior, denormal underflow, overflow to infinity/max finite depending on rounding, integer conversion saturation, and FPSR condition/accrual bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_util.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/multi_arith.h -->
# sources/distributed-fs/ceph-client/arch/m68k/math-emu/multi_arith.h

## Purpose
Defines specialized multi-precision integer helpers used to implement extended-precision floating-point mantissa arithmetic.

## APIs, Flow, And State
The header provides inline helpers for denormalizing/overnormalizing `struct fp_ext`, adding/subtracting 64-bit mantissas with low guard byte, propagating carry, 64-bit multiply/divide macros, 64/96-bit add/sub macros, 128-bit mantissa multiply/divide, and writing normalized 128-bit results back to `fp_ext`. The helpers mutate their operand structures directly and set FPSR exception bits through `fp_set_sr()` in overflow/rounding-relevant paths.

## Dependencies And Integration
Depends on `fp_emu.h`, m68k inline assembly instructions such as `bfffo`, `mulu.l`, `divu.l`, `addx`, and `subx`, and `union fp_mant64/fp_mant128` definitions from architecture math-emu headers. Used by `fp_arith.c` for add/sub alignment, multiplication, division, and result packing.

## Risks And Test Signals
The routines are explicitly not general-purpose; they assume normalized ranges and emulator-specific mantissa layout. Inline assembly constraints and carry semantics are architecture-sensitive. Test signals are arithmetic identity tests for FP add/mul/div, mantissa boundary cases, denormal shifts across 8/32/64-bit boundaries, and compiler build tests across supported m68k CPU variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/math-emu/multi_arith.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/mm/Makefile

## Purpose
Selects m68k memory-management objects according to MMU family configuration.

## APIs, Flow, And State
Always builds `init.o`. With `CONFIG_MMU`, it adds `cache.o` and `fault.o`. Motorola MMU builds add `kmap.o`, `memory.o`, `motorola.o`, and `hwtest.o`; Sun3 builds add `sun3kmap.o`, `sun3mmu.o`, and `hwtest.o`; ColdFire MMU builds add `kmap.o`, `memory.o`, and `mcfmmu.o`. There is no runtime state in this file.

## Dependencies And Integration
Consumed by Kbuild for the m68k architecture. It connects the common page-fault/cache code in this work item to the broader MMU implementations and platform-specific memory setup.

## Risks And Test Signals
Incorrect object selection can either omit required MMU handlers or link incompatible implementations. Build-matrix coverage across `CONFIG_MMU_MOTOROLA`, `CONFIG_MMU_SUN3`, and `CONFIG_MMU_COLDFIRE` is the primary test signal, followed by boot-time paging and cache behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/cache.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mm/cache.c

## Purpose
Implements m68k instruction-cache flushing for user ranges, kernel ranges, and individual user pages across ColdFire, 68040/060, and older CACR-based CPUs.

## APIs, Flow, And State
`virt_to_phys_slow()` translates virtual addresses for 040/060 cache push operations: 060 uses `plpar` with exception-table fixup returning zero on translation failure; 040 uses `ptestr` and `mmusr`. `flush_icache_user_range()` handles ColdFire set-index flushing with wraparound, 040/060 page-by-page `cpushp %bc` using translated physical addresses, or older `cacr` instruction-cache flush. `flush_icache_range()` temporarily switches function code to supervisor data, flushes, restores user data, and is exported. `flush_icache_user_page()` flushes one page using the same CPU-family split.

## Dependencies And Integration
Depends on `asm/cacheflush.h`, `asm/traps.h`, CPU feature macros, ColdFire cache helpers, page structures, exception tables, and function-code helpers. Used by text modification, module loading, signal trampolines, and user-page executable updates.

## Risks And Test Signals
The slow translation path can produce physical zero on failure, so callers should operate on valid mappings. ColdFire set-mask wrap logic and 040/060 physical cache pushes are CPU-specific. Test signals include module load/execute, signal trampoline execution, self-modifying/JIT-style user code, and cache-flush behavior on ColdFire, 040, 060, and older m68k CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/fault.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mm/fault.c

## Purpose
Handles m68k MMU page faults, mapping/protection errors, OOM faults, kernel fixups, and user signal delivery.

## APIs, Flow, And State
Public functions are `send_fault_sig()` and `do_page_fault()`. Fault metadata is persisted temporarily in `current->thread.signo`, `code`, and `faddr`. `do_page_fault()` rejects faults when the handler is disabled or no `mm` exists, marks user faults, emits perf page-fault events, locks the mmap, finds/expands the VMA including grow-down stack checks against `rdusp()`, validates access from the m68k error code, and calls `handle_mm_fault()`. It handles completed faults, pending signals, retry, OOM, SIGSEGV map/protection errors, and SIGBUS address errors. `send_fault_sig()` either calls `force_sig_fault()` in user mode or tries `fixup_exception()` before printing kernel access diagnostics and killing the task.

## Dependencies And Integration
Depends on Linux mm, mmap locking, perf events, uaccess exception fixups, `die_if_kernel()`, m68k trap regs, and `fault.h`. Called from m68k trap handlers and from code such as `sys_m68k.c` that simulates write faults.

## Risks And Test Signals
Lock/unlock paths are label-heavy; every error path must release mmap exactly when held. Stack growth heuristics include a 256-byte predecrement allowance. Kernel faults rely on exception-table fixups. Test signals are user SIGSEGV/SIGBUS cases, stack expansion, write-protect faults, OOM handling, retry faults, kernel copy_from_user fixups, and null-pointer kernel oops diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/fault.h -->
# sources/distributed-fs/ceph-client/arch/m68k/mm/fault.h

## Purpose
Declares the m68k MMU page-fault handling entry points shared with trap and syscall code.

## APIs, Flow, And State
Forward-declares `struct pt_regs` and prototypes `do_page_fault(struct pt_regs *regs, unsigned long address, unsigned long error_code)` and `send_fault_sig(struct pt_regs *regs)`. It defines no state or inline behavior.

## Dependencies And Integration
Included by `fault.c` and other m68k code paths that need to invoke page-fault handling directly, such as simulated write-fault logic. The declarations bind callers to the architecture-specific fault metadata contract in `current->thread`.

## Risks And Test Signals
The header is small; compile-time mismatch is the main concern. Because callers depend on return semantics documented in `fault.c`, runtime tests should verify that nonzero return still indicates a bad access and zero indicates a handled fault.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/fault.h -->
