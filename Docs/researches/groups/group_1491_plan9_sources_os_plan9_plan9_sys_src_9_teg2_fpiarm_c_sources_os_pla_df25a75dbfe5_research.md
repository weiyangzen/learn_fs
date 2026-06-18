# Group Research: group_1491_plan9_sources_os_plan9_plan9_sys_src_9_teg2_fpiarm_c_sources_os_pla_df25a75dbfe5

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/plan9`.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/fpiarm.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/fpiarm.c

Implements software emulation for old ARM FPA/FPA-like floating point instructions, layered on Plan 9’s portable `../port/fpi.h` internal floating-point routines.

Key behavior:
- Decodes ARM conditional execution, FPA load/store, register transfer, compare, unary, and binary arithmetic opcodes.
- Maintains emulated FP state in `up->fpsave`, switching process FP state to `FPemu` on first use.
- Supports constants and 8 legacy FPA registers under `ARM7500`.
- Advances `ureg->pc` over each emulated instruction and stops when the instruction stream is no longer an FPA opcode.

Important functions:
- `fpiarm(Ureg*)`: top-level emulator entry used from undefined-instruction trap handling.
- `fpemu(...)`: decodes and executes one FP opcode.
- `fcmp`, `fld`, `fst`, arithmetic helpers: implement individual operations using `fpi*` helpers.

Notes:
- Does not fully model ARM floating-point trap status or properties beyond what the Plan 9/Inferno environment needs.
- Raises errors for unsupported opcodes and for mixing emulated FPA state with VFP mode.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/fpiarm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/init9.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/init9.s

Small assembly entry wrapper for the first user-space boot program.

Key behavior:
- Sets Plan 9 static base register `R12`.
- Passes `/boot/boot` style argument pointers to `startboot`.
- Calls `startboot(SB)` and then loops forever if it returns.

Notes:
- Kept in assembly because setting `SB` in C would pull in too much runtime code.
- Matches the conceptual C shape `main(argv0) { startboot(argv0, &argv0); }`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/init9.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/io.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/io.h

Machine I/O definitions for the Tegra2 Plan 9 port, focused mostly on PCI identity, class, BAR, and device structures.

Key contents:
- Bus encoding macros: `MKBUS`, `BUSBNO`, `BUSDNO`, `BUSFNO`, `BUSTYPE`.
- PCI config register offsets and class/subclass constants.
- `Pcidev` structure used by `pci.c` and drivers for discovered PCI devices.
- Vendor IDs and BAR bit definitions.
- `PCIWADDR` translation macro for PCI windows.

Notes:
- Provides shared ABI between PCI probing, device drivers, and formatted `%T` bus identifiers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/kbd.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/kbd.c

Reduced PS/2-style scan-code translator used for simulated or external keyboard input on systems without a native keyboard.

Key behavior:
- Maps scan codes through normal, shift, escaped, AltGr, and control tables.
- Tracks modifier state, compose/Latin sequences, caps/num state, and mouse-button pseudo keys.
- Sends translated runes to `kbdq` via `kbdputc`.
- Exposes runtime keymap mutation and enumeration through `kbdputmap` and `kbdgetmap`.

Important functions:
- `kbdputsc(int c, int external)`: central scan-code state machine.
- `kbdenable()`: initializes internal scan state.
- `kbdputmap`, `kbdgetmap`: map editing APIs.

Notes:
- Contains a VM focus workaround: control-alt does not start a compose sequence.
- `F11`/`F12` toggle keyboard debug output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/kbd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/l.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/l.s

Main ARMv7/Tegra2 low-level assembly for early boot, secondary CPU startup, CP15 accessors, cache/MMU helpers, interrupt-level primitives, and atomic lock support.

Key behavior:
- `_start` enters from U-Boot or another kernel with MMU off, initializes CPU0, builds early L1 mappings, enables caches/MMU, warps into `KZERO`, and calls `main`.
- Nonzero CPUs wait with `WFI` until `cpus_proceed`, then run `cpureset`.
- `cpureset` initializes secondary CPUs, installs per-CPU page tables, enables MMU, and calls `cpustart`.
- Provides address conversion helpers, `setmach`, memory diagnostics, cache-line operations, TLB invalidation, CP15 register get/set functions, `splhi/spllo/splx`, labels, `wfi`, and `coherence`.
- Implements `tas` using ARM `LDREX/STREX`.

Notes:
- Boot prints characters directly for progress diagnostics.
- Comments document ordering constraints around SCU, L1/L2 caches, SMP mode, and MMU transitions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/lexception.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/lexception.s

ARM exception vector and trap-entry assembly.

Key behavior:
- Defines vector stubs and vector table entries for reset, undefined instruction, SWI, aborts, hypervisor, IRQ, and FIQ.
- `_vrst` starts additional CPUs through `cpureset`.
- `_vsvc` builds a `Ureg` for system calls, restores kernel `SB`, sets `m`/`up`, calls `syscall`, then returns to user mode.
- `_vswitch` handles undefined, abort, and IRQ paths by switching to SVC mode, building `Ureg`, and calling `trap`.
- Separates user-origin and kernel/SVC-origin trap frames.
- `rfue` and `forkret` paths return through ARMv7 `RFE`.

Notes:
- Carefully avoids ambiguous `MOVM.W` behavior by separating store-multiple and stack adjustment.
- FIQ and hypervisor entries only print diagnostics and return.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/lexception.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/lproc.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/lproc.s

Small process-transition assembly support.

Key behavior:
- `touser(SP)`: performs the first jump from kernel to user mode by installing user SP, setting user-mode SPSR, pushing PC `UTZERO+0x20`, and using `RFEV7W`.
- `forkret`: returns a newly forked process through the same saved-`Ureg` return path as traps.

Notes:
- This file is the bridge between scheduler-created kernel frames and first user-mode execution.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/lproc.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/main.c

Main C boot and machine-initialization path for the Plan 9 Tegra2 ARM kernel.

Key behavior:
- Parses boot arguments and low-memory `plan9.ini` configuration.
- Initializes `Mach` structures, active CPU accounting, caches, L2 page allocator, MMU, traps, memory sizing, clock/timers, devices, PCI, paging, swap, and first user process.
- Creates the first process with stack/text segments and copies `initcode`.
- Starts secondary CPUs after user-process infrastructure is ready.
- Implements shutdown, exit, and reboot through the low-memory reboot trampoline.
- Provides `confinit`, `isaconfig`, `idlehands`, `wakewfi`, and CPU active/offline helpers.

Important functions:
- `main()`: complete bootstrap sequence.
- `mach0init`, `machinit`, `launchinit`: CPU/Mach setup.
- `confinit`: memory and kernel pool sizing.
- `userinit`, `init0`, `bootargs`: first process setup.
- `reboot`: coordinated shutdown and trampoline execution.

Notes:
- Assumes TrimSlice/Tegra2-style 1 GiB DRAM, then verifies memory by probing.
- Uses cache writeback/invalidation aggressively for stability.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/mem.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/mem.h

Shared C/assembly memory-layout and machine-constant header for the Tegra2 port.

Key contents:
- Page, stack, CPU, cache-line, and page-table sizes.
- Register conventions: `R9` as `up`, `R10` as `m`.
- Kernel/user virtual layout: `KZERO`, `L1`, `CONFADDR`, `CACHECONF`, `KTZERO`, `USTKTOP`, `USTKSIZE`.
- Physical MMIO and remapped windows: DRAM, IO, L2 cache controller, EVP, console UART, AHB, NOR.
- PTE flag definitions and reboot trampoline address.

Notes:
- Documents the low-memory layout around Mach, L1/L2 tables, config data, and kernel text.
- `USTKTOP` is kept below 1 GiB to avoid MMIO and high-vector collisions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/mmu.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/mmu.c

ARMv7 MMU management for kernel mappings, per-process user mappings, and per-CPU L1 tables.

Key behavior:
- Dumps and summarizes L1 page-table ranges for diagnostics.
- Maps MMIO sections, high vectors, AHB/NOR aliases, and private memory region attributes.
- Expands L1 section mappings into L2 page tables when page-granular control is needed.
- Allocates early L2 tables from high reserved memory.
- Maintains per-process L2 page-table pages and swaps them into the current CPU’s L1 table on `mmuswitch`.
- Implements `putmmu`, `flushmmu`, `mmurelease`, `mmuuncache`, `mmukmap`, `mmukunmap`, `vmap`, and `vunmap`.

Notes:
- Uses both L1 and L2 cache operations around page-table writes due to observed hardware behavior.
- User mappings are cleared broadly from `L1lo` to `L1hi`; a narrower optimization is disabled as buggy.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/pci.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/pci.c

Tegra2 PCI/PCIe support code for configuration-space access, device scanning, and basic PCI helpers.

Key behavior:
- Models the Tegra PCI controller register layout and memory-mapped config windows.
- Initializes controller access if the expected NVIDIA/Realtek IDs are present.
- Scans buses/devices/functions with conservative TrimSlice limits to avoid hangs.
- Builds global and tree-linked `Pcidev` lists, sizes BARs, and descends PCI bridges.
- Provides `pcimatch`, `pcimatchtbdf`, `pcihinv`, `pcireset`, config read/write wrappers, bus-master/io/mwi toggles, and PCI power-management helpers.
- Dismisses PCIe interrupt status through AFI magic register writes.

Notes:
- Comments call out that this needs a rewrite and contains board-specific assumptions.
- Bus scanning starts at bus 1 for TrimSlice.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/pci.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/rebootcode.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/rebootcode.s

Relocatable ARMv7 reboot trampoline copied to `REBOOTADDR`.

Key behavior:
- Disables caches, reinstalls temporary double mappings, invalidates TLBs, and switches from `KZERO` to physical DRAM addressing.
- Turns off the MMU.
- Copies a loaded replacement kernel from physical source to physical destination.
- Branches to the new kernel entry in physical addressing.

Important functions:
- `main(entry, code, size)`: trampoline entry.
- `cachesoff`: cache/MMU preparation before final MMU disable.
- `_r15warp`: segment-adjusts return PC and SP.
- `panic` and `pczeroseg`: local stubs required by included cache code.

Notes:
- Must fit below the page-table area, per `mem.h`.
- Includes `cache.v7.s` so the trampoline is self-contained after copying.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/rebootcode.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/softfpu.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/softfpu.c

Fallback software-FPU integration file.

Key behavior:
- Most process/FPU lifecycle hooks are stubs.
- `fpuemu(Ureg*)` calls `fpiarm(ureg)` under an error handler, posts a debug note on failure, and returns whether FP instructions were emulated.
- `fpon`, `fpoff`, and `fpuinit` are empty.

Notes:
- This is the no-real-VFP or software-only counterpart to `vfp3.c`.
- Allows portable proc/syscall code to call machine FPU hooks even when they do nothing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/softfpu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/syscall.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/syscall.c

ARM machine-dependent syscall and Plan 9 note handling.

Key behavior:
- `syscall(Ureg*)` validates user mode, reads syscall number from `r0`, copies syscall args from the user stack, dispatches through `systab`, writes return value to `r0`, handles tracing, notes, delayed scheduling, and `kexit`.
- `notify` builds an `NFrame` on the user stack and redirects execution to `up->notify`.
- `noted` validates and restores user register state after note handling, preserving privileged PSR bits.
- `execregs` sets entry PC and stack for `exec`.
- `forkchild` creates a saved return frame for a forked child so it returns `0` in user mode.

Notes:
- Uses explicit cache writeback calls around syscall/note paths because the system was more stable with them.
- Hooks into FPU lifecycle for notes, `rfork`, and `exec`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/trap.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/trap.c

ARM MPCore GIC v1 interrupt controller, trap, exception, and fault core.

Key behavior:
- Defines GIC distributor and CPU-interface register layouts.
- Installs high and low exception vectors from `lexception.s`.
- Sets exception-mode stack slots in `Mach`.
- Configures GIC groups, priorities, trigger modes, CPU targets, masks, pending/active state, and CPU interface.
- Provides IRQ registration/removal through `irqenable` and `irqdisable`.
- Handles IRQ dispatch, interrupt timing histograms, page faults, data abort decoding, prefetch faults, breakpoints, undefined instructions, and FPU emulation.
- Provides diagnostic register/stack dumping and `probeaddr`.

Important functions:
- `trapinit`, `trap`, `irq`, `datafault`, `faultarm`.
- `intcunmask`, `intcmask`, `intrcpu`, `intrshutdown`.
- `dumpregs`, `dumpstack`, `probeaddr`.

Notes:
- GIC register comments document banked-per-CPU surprises.
- Distributor `memset`/`memmove` is avoided because it can generate external aborts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/uarti8250.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/uarti8250.c

8250-like UART driver for the Tegra console.

Key behavior:
- Defines 8250 register offsets and bit masks.
- Provides one console UART at `PHYSCONS` with IRQ `Uartirq`.
- Supports status reporting, FIFO setup, modem control, parity/stop/bits, break, kick/output, interrupt receive/transmit, enable/disable, polling getc, and putc.
- Uses early brute-force polled output before normal console queues are ready.
- `i8250console` wires UART input/output queues into `kbdq`, `serialoq`, and `consuart`.

Important functions:
- `i8250enable`, `i8250interrupt`, `i8250kick`, `i8250putc`, `serialputc`, `_uartputs`, `i8250console`.

Notes:
- Baud-rate programming is disabled; the driver records requested baud but leaves hardware speed unchanged.
- OMAP-style `Mdr` mode register support remains in the common 8250-derived code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/uarti8250.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/usbehci.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/usbehci.h

Local EHCI USB controller definitions for the Tegra2 port.

Key contents:
- Overrides debug macros from the generic USB code.
- Forward-declares EHCI private types.
- Defines `Poll`, `Ctlr`, and operational register structure `Eopio`.
- Declares EHCI linkage and memory/run helpers.

Notes:
- `Ctlr` captures async/periodic queue state, frame list, interrupt counters, and polling rendezvous.
- `Eopio` includes standard EHCI operational registers plus implementation-specific `insn` registers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/usbehci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/v7-arch.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/v7-arch.c

Small ARMv7 helper routines outside cache-specific assembly.

Key behavior:
- `ispow2(uvlong)`: returns whether a 64-bit value is a power of two.
- `log2(ulong)`: returns the exponent of the smallest power of two greater than or equal to `n`, using `clz`.

Notes:
- Filename avoids `arch*.c` because Plan 9 mk scripts treat that pattern specially.
- Comments expect these helpers to be cheap and replaceable once `5c` improves `vlong` codegen.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/v7-arch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/vfp3.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/teg2/vfp3.c

VFPv2/VFPv3 floating-point unit detection, configuration, lazy activation, save/restore, and trap integration.

Key behavior:
- Detects FP coprocessor access and VFP subarchitecture via CP15/FPSID.
- Configures FPSCR with default NaN, flush-to-zero, rounding, and exception masks.
- Lazily enables VFP on first user FP instruction and restores saved registers only when needed.
- Saves FP state for scheduling, `rfork`, and note delivery.
- Prevents FP use inside note handlers.
- Handles pending FP exceptions by posting Plan 9 debug notes.
- Falls back to `fpiarm` for old FPA opcodes.

Important functions:
- `havefp`, `fpinit`, `fpon`, `fpoff`, `fpsave`, `fprestore`.
- `fpuprocsave`, `fpusysprocsetup`, `fpunotify`, `fpunoted`.
- `fpuemu(Ureg*)`: trap-facing FP instruction handler.

Notes:
- Tracks stuck FP traps per CPU/process/PC to catch retry loops.
- Supports 16 or 32 VFP registers depending on hardware access bits.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/teg2/vfp3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5a/a.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5a/a.h

Shared header for the Plan 9 ARM assembler `5a`.

Key contents:
- Includes `../5c/5.out.h` for ARM object/instruction definitions.
- Defines assembler constants, buffered input state, symbol table structures, operand `Gen`, and history records.
- Declares global assembler state: symbols, include paths, pass number, output file, PC, current token, line number, and output buffer.
- Declares lexer, parser, macro, I/O, object emission, history, and compatibility functions.

Notes:
- The assembler is a two-pass tool sharing object ABI with `5c` and the linker.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5a/a.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5a/a.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5a/a.y

Yacc grammar for Plan 9 ARM assembly syntax.

Key behavior:
- Parses labels, variable definitions, directives, instructions, conditions, operands, register lists, shifts, constants, names, and expressions.
- Emits object records through `outcode`.
- Supports ARM data-processing, moves, branches, SWI, comparisons, MOVM, swaps, RET/RFE, TEXT/GLOBL/DATA/WORD/END, floating-point ops, MRC/MCR, multiply-long, and multiply-accumulate forms.
- Encodes `MRC/MCR` directly into `AWORD` using constructed ARM instruction bits.
- Handles conditional suffixes and addressing-mode suffix bits.

Notes:
- Branch labels resolve differently in pass 1 versus pass 2.
- Register list syntax expands to bitmasks used by `MOVM`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5a/a.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5a/l.s -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5a/l.s

Small assembler syntax test/sample file for ARM `5a`.

Key contents:
- Demonstrates ADD forms, shifts, conditional suffixes, PSR/FPR moves, memory operands, MRC, MOVM register lists, CMN, and RET.
- Uses a local loop label and conditional branch.

Notes:
- Not kernel boot assembly; it is an assembler input example/regression-style source.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5a/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5a/lex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5a/lex.c

Lexer, driver, symbol initialization, and object emission support for ARM assembler `5a`.

Key behavior:
- `main` parses assembler options, supports parallel assembly of multiple files on non-Windows systems, and selects ARM or Thumb output suffix.
- `assemble` runs pass 1 and pass 2, handles include paths and `-D` macros, creates output, and emits history.
- `itab` maps registers, condition suffixes, addressing suffixes, mnemonics, and directives to parser tokens/opcodes.
- `cinit` initializes symbols and assembler globals.
- `zname`, `zaddr`, `outcode`, and `outhist` serialize names, operands, instructions, and file history to the object stream.
- Includes shared C compiler lexer/macro/compat bodies.

Notes:
- Converts `B.cond` into the corresponding conditional branch opcode in `outcode`.
- Maintains a small object symbol table with `ANAME` records.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5a/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/5.out.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/5.out.h

ARM object-format and opcode definition header shared by Plan 9 ARM tools.

Key contents:
- Register conventions for ARM code generation: return, argument, temp, SB, SP, link, PC, and FP registers.
- `enum as` opcode numbers for ARM instructions, pseudo-ops, branches, FP operations, exclusive operations, and end marker.
- Condition/suffix bit definitions.
- Addressing type/name constants such as `D_REG`, `D_OREG`, `D_CONST`, `D_BRANCH`, `D_SHIFT`, `D_EXTERN`, `D_AUTO`, and `D_PARAM`.
- `Ieee` simulated IEEE floating-point representation.
- `SYMDEF` archive symbol-table name.

Notes:
- Comments warn not to reorder conditional branch opcodes because predication depends on their order.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/5.out.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/cgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/cgen.c

Main expression and aggregate code generator for the ARM C compiler backend `5c`.

Key behavior:
- `cgen`/`cgenrel` lower C expression trees to backend `Prog` instructions.
- Handles assignments, bitfields, arithmetic, division/modulo by powers of two, multiply optimization, compound assignments, address-of, calls, indirect loads, comparisons, logical ops, casts, comma, conditionals, and pre/post increments.
- `lcgen` and `reglcgen` compute lvalue addresses, including optimized small offsets.
- `boolgen` lowers boolean expressions and branches, including short-circuit logic and relational comparisons.
- `sugen` copies structures/unions and handles aggregate constants, structure literals, function-return aggregates, conditional aggregates, and multiword copy loops.

Notes:
- Carefully orders evaluation when both sides have function-call complexity.
- Uses ARM multi-register moves for small or looped structure copies.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/cgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/enam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/enam.c

Opcode-name table for the ARM compiler backend.

Key contents:
- `anames[]` maps `enum as` opcode numbers from `5.out.h` to printable mnemonic strings.
- Includes integer, branch, FP, move, pseudo-op, multiply-long, branch-exchange, exclusive load/store, and sentinel names.

Notes:
- Must stay aligned with the opcode enum; used by listing/debug formatting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/enam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/gc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/gc.h

Central ARM `5c` backend header.

Key contents:
- ARM data-size constants and backend flags.
- `Adr`, `Prog`, `Case`, `C1`, `Multab`, `Hintab`, `Var`, `Reg`, and `Rgn` structures.
- Global compiler backend state for generated instruction lists, registers, regions, variables, cases, constants, and optimization data.
- Register allocator and optimizer bitset macros.
- Prototypes for code generation, text emission, switch lowering, bitfield handling, listing, register optimization, peephole optimization, predicate optimization, and multiply optimization.

Notes:
- Defines `BTRUE` relation flag and ARM-specific register allocation ranges.
- `NRGN` is raised for large source files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/gc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/list.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/list.c

Formatting and listing helpers for ARM backend instructions and operands.

Key behavior:
- Installs custom formatters for opcodes, programs, string constants, names, bitsets, operands, and register lists.
- `Pconv` formats full `Prog` instructions with condition/suffix decorations.
- `Dconv` formats ARM operand addressing modes, constants, shifts, registers, PSR, branches, FP/string constants.
- `Nconv` formats named operands by storage class: extern, static, auto, param.
- `Rconv` formats MOVM register-list masks.
- `Bconv` formats optimizer bitsets as variable names or offsets.

Notes:
- Used for compiler debugging, listings, and diagnostics rather than final code emission.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/mul.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/mul.c

Constant-multiply strength-reduction support for ARM `5c`.

Key behavior:
- Searches for short sequences of shifts, adds, and subtracts to replace multiplication by constants.
- Caches generated sequences in `multab`.
- Uses a hint table for constants the generic search misses.
- Recursively builds candidate sequences with `gen1`, `gen2`, and `gen3`.
- `docode` verifies and materializes a compact operation encoding.

Important data:
- `maxmulops = 3` limits replacement sequence length.
- `hintab[]` lists exceptional constants and hand-coded sequences.
- `hintabsize` exposes table size.

Notes:
- Supports later backend code that emits optimized multiply-by-constant instruction sequences instead of `MUL`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/5c/mul.c -->