## sources/distributed-fs/ceph-client/arch/mips/kernel/traps.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/traps.c` is the central MIPS exception, trap, vector, diagnostic, and instruction-emulation implementation. It installs exception vectors, configures CP0 status/HWREna/EBase, handles fatal and recoverable traps, reports register/stack state, emulates selected missing instructions, manages FPU/MSA enablement, and registers CPU PM restoration hooks.

### Important APIs, Types, And Functions
Important platform hooks are `board_be_init`, `board_be_handler`, `board_nmi_handler_setup`, `board_ejtag_handler_setup`, `board_bind_eic_interrupt`, `board_ebase_setup`, and `board_cache_error_setup`. Diagnostic functions include `show_stack()`, `show_regs()`, `show_registers()`, and `die()`. Exception handlers include `do_be()`, `do_ov()`, `do_fpe()`, `do_bp()`, `do_tr()`, `do_ri()`, `do_cpu()`, `do_msa_fpe()`, `do_msa()`, `do_watch()`, `do_mcheck()`, `do_mt()`, `do_dsp()`, `cache_parity_error()`, `do_ftlb()`, `do_gsexc()`, `ejtag_exception_handler()`, and `nmi_exception_handler()`. Vector setup functions are `set_except_vector()`, `set_vi_handler()`, `per_cpu_trap_init()`, `set_handler()`, `set_uncached_handler()`, and `trap_init()`.

### Control Flow
Boot calls `trap_init()`, allocates or selects EBase space, configures microMIPS mode, runs board EBase setup, performs per-CPU trap initialization, copies generic handlers, initializes default exception/VI vectors, configures cache parity, lets boards initialize bus errors, installs handlers for interrupt, TLB, address errors, syscall, break, reserved instruction, coprocessor unusable, overflow, trap, MSA/FPU, watch, machine check, thread, DSP, and cache errors, flushes icache, sorts bus-error exception tables, and registers the default CU2 notifier. Runtime exception handlers enter exception context, optionally notify die chains, decide user versus kernel handling, emulate instructions when supported, force appropriate signals, or call `die()`/`panic()`.

### State, Persistence, And Dependencies
State includes `ebase`, `exception_handlers[32]`, `vi_handlers[64]`, CP0 Compare/Perf/FDC IRQ numbers, `hwrena`, `ll_bit`, `ll_task`, raw notifier chains for CU2 and NMI, cache parity knobs, and board hook pointers. It mutates CP0 Status, Cause, EBase, HWREna, IntCtl, ErrCtl, MSA/FPU state, thread trap numbers, and per-task FPU/MSA flags. Dependencies span MIPS CP0 accessors, uasm code generation, TLB handlers, FPU emulator, MSA, DSP, kprobes/uprobes/kgdb die notifiers, CPU PM, memblock, cache/TLB debug, and platform CPU feature descriptors.

### Integration Points
This file is the hub for `smp.c` secondary initialization, `signal.c` FP/MSA context behavior, `unaligned.c` fault signaling, uprobes/kprobes breakpoints, CPU PM resume state restoration, board-specific vector relocation in BMIPS/CPS code, syscall and page fault assembly handlers, and MMU/TLB exception stubs. It exports `ebase`, IRQ numbers, and HWREna for other architecture code.

### Risks
Exception-vector installation and CP0 configuration are catastrophic failure points. User versus kernel mode checks must be exact or user faults can panic the kernel, while kernel faults can be hidden. Instruction emulation changes can break LL/SC atomics, RDHWR TLS/time reads, SYNC behavior, Loongson CPUCFG, and FPU fallback. FPU/MSA enablement has security risks if old vector register contents leak. Cache parity and FTLB handling deliberately panic on conditions considered unrecoverable.

### Test Signals
Exercise break/trap instructions, reserved instruction emulation, RDHWR UserLocal/Count reads, LL/SC emulation on LL/SC-less CPUs, FPU unavailable and FPU exception paths, MSA disabled and MSA FP exceptions, watchpoints, bus-error fixups, cache parity options, vectored interrupt setup, CPU PM suspend/resume, NMI notifier handling, and boot on microMIPS, VEIC/VINT, R2/R6, Loongson, and BMIPS/CPS platforms.
