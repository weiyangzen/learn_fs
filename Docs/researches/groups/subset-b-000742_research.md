# subset-b-000742 Research

Grouped research for MIPS kernel support files in `sources/distributed-fs/ceph-client/arch/mips/kernel`. Each source file section is wrapped with deterministic file markers so the reconciliation lane can split this report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/fpu-probe.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/fpu-probe.c

### Purpose
`fpu-probe.c` discovers MIPS FPU capabilities, records hardware or emulator feature bits in `struct cpuinfo_mips`, and applies boot-time policy for IEEE 754 legacy NaN versus 2008 NaN behavior. It supports both real CP1 hardware and the in-kernel FPU emulator, and it exposes the `nofpu` and `ieee754=` boot controls used during early CPU setup.

### Important APIs, Types, And Functions
The externally visible functions are `__cpu_has_fpu()`, `cpu_set_fpu_opts()`, `cpu_set_nofpu_opts()`, and the global `mips_fpu_disabled`. Internal helpers include `cpu_get_fpu_id()`, `cpu_set_fpu_fcsr_mask()`, `cpu_set_fpu_2008()`, `cpu_set_nofpu_2008()`, `cpu_set_nan_2008()`, and `cpu_set_nofpu_id()`. The local `ieee754` enum accepts `STRICT`, `EMULATED`, `LEGACY`, `STD2008`, and `RELAXED`, selected by `early_param("ieee754", ...)`.

### Control Flow
Hardware probing temporarily enables CP1 with `__enable_fpu(FPU_AS_IS)`, reads FIR/FCSR, probes writable FCSR mask bits by writing forced-zero and forced-one patterns, and restores CP0 status and FCSR. NaN/ABS2008 support is inferred from FIR and FCSR writability, then filtered by `ieee754=`. The `nofpu` setup path calls `cpu_set_nofpu_opts()` on `boot_cpu_data`, clears `MIPS_CPU_FPU`, builds an emulated FIR, and sets `mips_fpu_disabled`.

### State, Persistence, And Dependencies
State is stored in `boot_cpu_data` or the supplied `cpuinfo_mips`: `fpu_id`, `fpu_csr31`, `fpu_msk31`, `options`, and `ases`. Global policy state includes `mips_use_nan_legacy`, `mips_use_nan_2008`, `mips_nofpu_msk31`, and `mips_fpu_disabled`. The file depends on CP0/CP1 register accessors, `asm/fpu.h`, CPU feature flags, and ELF NaN compatibility globals.

### Integration Points
This code is consumed by MIPS CPU probing, ELF binary compatibility checks, lazy FPU ownership, FPU exception handling, and the software FPU emulator. `fpu-probe.h` provides no-op stubs when `CONFIG_MIPS_FP_SUPPORT` is absent.

### Risks
The riskiest behavior is writing and restoring FCSR/CP0 state during early CPU probing. Wrong FCSR masks can expose unsupported user-visible floating-point modes, and an incorrect NaN policy can reject valid binaries or allow binaries whose NaN encoding the hardware cannot execute. `nofpu` relies on the boot CPU mask saved from hardware probing, so boot ordering matters.

### Test Signals
High-signal tests include booting with `ieee754=strict`, `legacy`, `2008`, `emulated`, and `relaxed`, booting with `nofpu`, checking ELF NaN acceptance/rejection paths, running FPU exception tests, and validating `/proc/cpuinfo`/feature flags on CPUs with and without real CP1 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/fpu-probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/fpu-probe.h -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/fpu-probe.h

### Purpose
`fpu-probe.h` is the local interface for MIPS FPU capability detection. It lets CPU probing code call the same names regardless of whether `CONFIG_MIPS_FP_SUPPORT` is enabled.

### Important APIs, Types, And Functions
With `CONFIG_MIPS_FP_SUPPORT`, it declares `mips_fpu_disabled`, `__cpu_has_fpu()`, `cpu_set_fpu_opts()`, and `cpu_set_nofpu_opts()`. Without FPU support, it defines `mips_fpu_disabled` as `1`, returns `FPIR_IMP_NONE` from a local `cpu_get_fpu_id()` stub, returns false from `__cpu_has_fpu()`, and makes the option setters no-ops.

### Control Flow
There is no runtime control flow beyond inline stubs. The preprocessor selects either the real declarations or the fallback implementation at build time.

### State, Persistence, And Dependencies
The header has no independent mutable state. It depends on `struct cpuinfo_mips`, `FPIR_IMP_NONE`, and `CONFIG_MIPS_FP_SUPPORT`. The stub value for `mips_fpu_disabled` becomes a compile-time constant for builds without FP support.

### Integration Points
The file is included by `fpu-probe.c` and MIPS CPU setup code that needs to probe or disable FPU behavior. It provides a stable local ABI between CPU feature detection and optional FP support.

### Risks
Because the !FP configuration uses stubs, callers must not expect side effects such as `cpuinfo_mips` fields being normalized. Any code added behind this header should preserve the same semantics for both configurations.

### Test Signals
Build coverage matters most: compile MIPS kernels with and without `CONFIG_MIPS_FP_SUPPORT`, then confirm no unresolved references to the real FPU probe functions remain in the no-FP build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/fpu-probe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/ftrace.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/ftrace.c

### Purpose
`ftrace.c` implements MIPS dynamic ftrace code patching, function graph return-address hijacking, and syscall address lookup for ftrace syscall tracing. It rewrites `_mcount` call sites between NOP/branch sequences and calls into `ftrace_caller`.

### Important APIs, Types, And Functions
Key APIs include `arch_ftrace_update_code()`, `ftrace_make_nop()`, `ftrace_make_call()`, `ftrace_update_ftrace_func()`, `ftrace_dyn_arch_init()`, `ftrace_enable_ftrace_graph_caller()`, `ftrace_disable_ftrace_graph_caller()`, `prepare_ftrace_return()`, and `arch_syscall_addr()`. Internal instruction helpers generate JAL, branch, NOP, and long-call sequences using `uasm`.

### Control Flow
Dynamic ftrace boot initialization precomputes patch instructions and removes the boot-time branch around `ftrace_caller`. Later, ftrace core calls `ftrace_make_call()` or `ftrace_make_nop()` per callsite. Kernel text can use direct JAL, while modules use an address-load sequence when `_mcount` is outside direct jump range. Function graph tracing locates or receives the caller's saved return address, replaces it with `return_to_handler`, and calls `function_graph_enter()`.

### State, Persistence, And Dependencies
Patch templates are stored in read-mostly globals such as `insn_jal_ftrace_caller`, `insn_la_mcount`, and `insn_j_ftrace_graph_caller`. Runtime state is in text memory and the current task's graph tracing state. The file depends on safe text load/store helpers, icache flushing, `core_kernel_text()`, syscall tables, `mcount.S` symbols, and `CONFIG_DYNAMIC_FTRACE`/`CONFIG_FUNCTION_GRAPH_TRACER`.

### Integration Points
It integrates with Linux ftrace core, function graph tracer, syscall tracing, MIPS module callsite layout, and architecture-specific `_mcount` assembly. The code must match the exact instruction sequences emitted by GCC and represented in `mcount.S`.

### Risks
Risks are instruction patch atomicity, icache coherency, jump-range limits, module long-call encoding, and stack return-address discovery. The 32-bit path patches two instructions and uses different write ordering for call enablement, so partial patching bugs can execute malformed code.

### Test Signals
Useful tests are booting with dynamic ftrace, enabling/disabling function tracing repeatedly, tracing module functions, enabling function graph tracing with and without `KBUILD_MCOUNT_RA_ADDRESS`, and checking syscall tracepoints on O32/N32/64-bit ABI builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/genex.S -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/genex.S

### Purpose
`genex.S` provides MIPS general exception, interrupt, EJTAG debug, NMI, vectored interrupt, WAIT skipover, and common exception handler entry assembly. It is core trap-entry code that saves processor state and dispatches to C handlers such as `do_ade`, `do_fpe`, `plat_irq_dispatch`, `ejtag_exception_handler`, and `nmi_exception_handler`.

### Important APIs, Types, And Functions
Exported assembly labels include `except_vec3_generic`, `except_vec3_r4000`, `r4k_wait`, `skipover_handle_int`, `handle_int`, `except_vec4`, `except_vec_ejtag_debug`, `except_vec_vi`, `except_vec_vi_handler`, `ejtag_debug_handler`, `except_vec_nmi`, `nmi_handler`, many `handle_*` exception handlers built by `BUILD_HANDLER`, and `handle_ri_rdhwr`. It also exports EJTAG debug buffers and counts VCED/VCEI under procfs configurations.

### Control Flow
General exception vectors index `exception_handlers` from CP0 Cause. The R4000 variant special-cases virtual coherency exceptions and performs cache writeback/invalidation before `eret`. Interrupt entries use `SAVE_ALL`, disable interrupts, switch to the per-CPU IRQ stack if needed, call the platform or vectored handler, restore the original stack, and jump to `ret_from_irq`. The WAIT skipover prologue detects interrupts landing in the idle wait window and rewrites EPC to skip the `wait` instruction. Generic exception handlers save registers, prepare exception-specific state, call `do_*`, then return through `ret_from_exception`.

### State, Persistence, And Dependencies
State lives in CP0 status/cause/EPC/badvaddr/debug registers, `thread_info`, `irq_stack`, EJTAG buffers, and optional exception counters. The file depends on `stackframe.h`, `asmmacro.h`, CP0 hazard macros, exception handler tables, and exact pt_regs offsets.

### Integration Points
This is the assembly bridge for traps, IRQ core, idle wait code in `idle.c`, kgdb/EJTAG, NMI handling, vectored interrupt tables, and reserved-instruction RDHWR emulation for TLS.

### Risks
Entry code is sensitive to vector size limits, delay slots, CP0 hazards, stack switching, IRQ tracing state, and microMIPS/64-bit differences. Bugs can corrupt pt_regs, return to the wrong EPC, lose IRQ stack unwindability, or deadlock EJTAG SMP debug buffer locking.

### Test Signals
High-signal validation includes boot/interrupt storm testing, exception tests for address errors, break/trap, RI, FPU/MSA, watchpoints, NMI/debug entry on supported boards, idle wakeup tests, and stack unwinding through IRQ stack transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/genex.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/gpio_txx9.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/gpio_txx9.c

### Purpose
`gpio_txx9.c` is a simple GPIO chip driver for Toshiba TXx9 SoC PIO registers. It maps the PIO register block and exposes GPIO get, set, direction input, and direction output operations through gpiolib.

### Important APIs, Types, And Functions
The public initializer is `txx9_gpio_init(unsigned long baseaddr, unsigned int base, unsigned int num)`. The `gpio_chip` methods are `txx9_gpio_get()`, `txx9_gpio_set()`, `txx9_gpio_dir_in()`, and `txx9_gpio_dir_out()`. `txx9_gpio_set_raw()` performs the shared read-modify-write of the output register.

### Control Flow
Initialization `ioremap()`s `struct txx9_pio_reg`, fills `gpio_chip.base` and `ngpio`, and registers the chip. Runtime operations directly read `din`, modify `dout`, and modify `dir`. Mutating operations take `txx9_gpio_lock`, perform raw MMIO updates, call `mmiowb()`, and release the lock with IRQ state restored.

### State, Persistence, And Dependencies
State is the mapped `txx9_pioptr`, static `gpio_chip`, and the hardware PIO registers. GPIO output and direction persist in the SoC register block until changed or reset. The code depends on `asm/txx9pio.h`, gpiolib, raw MMIO accessors, and a global spinlock.

### Integration Points
Board setup code calls `txx9_gpio_init()` with the correct physical base and GPIO numbering. Consumers use normal gpiolib descriptors or legacy numbers. The driver is paired with TXx9 interrupt and board support rather than a device-tree platform driver.

### Risks
There is no `iounmap()` or unregister path, which is acceptable for early platform setup but not hotplug. Incorrect `baseaddr`, `base`, or `num` exposes wrong GPIO numbers or writes unrelated registers. Raw read-modify-write means concurrent hardware-side changes are not merged beyond the protected CPU-side access.

### Test Signals
Test by registering the chip on TXx9 hardware, toggling outputs, reading inputs, switching direction, checking gpiolib numbering, and confirming no MMIO faults or lost writes under concurrent GPIO users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/gpio_txx9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/head.S -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/head.S

### Purpose
`head.S` is the primary MIPS kernel entry assembly. It reserves exception-vector space, sets initial CP0 status, clears BSS, records firmware arguments, creates the first kernel stack, optionally relocates the kernel, and transfers control to `start_kernel`. It also defines the SMP secondary entry point.

### Important APIs, Types, And Functions
Important labels and macros are `_stext`, optional `__kernel_entry`, `kernel_entry`, `smp_bootstrap`, `setup_c0_status`, `setup_c0_status_pri`, and `setup_c0_status_sec`. It uses platform-provided `kernel_entry_setup` and `smp_slave_setup` macros from `kernel-entry-init.h`.

### Control Flow
Primary entry runs CPU-specific setup, disables interrupts while configuring kernel mode and 64-bit address support when needed, jumps to the linked address, zeros `.bss`, saves `a0` through `a3` into `fw_arg*`, clears CP0 context registers, initializes `$28` and `sp` from `init_thread_union`, records saved stack pointer, and then either calls `relocate_kernel` or jumps to `start_kernel`. SMP secondaries execute the board slave setup, use secondary CP0 status that clears BEV, and jump to `start_secondary`.

### State, Persistence, And Dependencies
Persistent early state includes `.bss` zeroing, firmware argument globals, CP0 Status/Context/XContext, initial thread stack, and saved kernel stack pointer. The file depends on linker symbols, stackframe offsets, MIPS CP0 hazard sequencing, and optional relocatable kernel support.

### Integration Points
This is the bridge from firmware or raw boot to the generic Linux kernel. It integrates with platform entry setup, relocation code, `start_kernel`, SMP startup, and exception-vector layout expected by `genex.S`.

### Risks
Entry code has no recovery path. Wrong CP0 status bits, stack placement, BSS bounds, or relocation jump target will fail before console diagnostics. The reserved exception fill must match link address and platform vector expectations.

### Test Signals
Validation is architecture boot coverage: raw and ELF boot paths, 32-bit and 64-bit configs, relocatable and non-relocatable kernels, firmware argument parsing, SMP secondary bring-up, and early exception handling before `trap_init`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/i8253.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/i8253.c

### Purpose
`i8253.c` wires the legacy 8253/PIT timer into MIPS clockevent and optional clocksource support. It handles IRQ0 timer interrupts and initializes the PIT as a periodic clock event.

### Important APIs, Types, And Functions
The public initializer is `setup_pit_timer()`. Internal pieces are `timer_interrupt()` and `init_pit_clocksource()` registered by `arch_initcall`.

### Control Flow
`setup_pit_timer()` initializes `i8253_clockevent` in periodic mode and requests IRQ0 with `IRQF_NOBALANCING | IRQF_TIMER`. The IRQ handler calls `i8253_clockevent.event_handler()` and returns `IRQ_HANDLED`. The clocksource init path enables `clocksource_i8253_init()` only on single-CPU systems and only while the clockevent is periodic.

### State, Persistence, And Dependencies
State is primarily in the shared `i8253_clockevent` object, the PIT hardware registers managed by the generic i8253 code, and the registered IRQ descriptor. It depends on `linux/i8253.h`, clocksource/clockevent core, IRQ core, and `num_possible_cpus()`.

### Integration Points
Platform timer setup calls `setup_pit_timer()` on MIPS systems with legacy PIT hardware. The clockevent feeds the scheduler tick, and the optional clocksource provides timekeeping only when the PIT is not disqualified by SMP or mode.

### Risks
The PIT does not scale for SMP, so using it as a clocksource on multi-CPU systems would be unsafe. IRQ0 request failures leave the system without a working tick and only log an error. Hardware routing must map IRQ0 to the correct interrupt controller.

### Test Signals
Boot tests should verify periodic ticks, timer interrupt counts, scheduler progress, `clocksource` selection on single-CPU systems, and that SMP systems do not select the PIT clocksource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/i8253.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/idle.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/idle.c

### Purpose
`idle.c` selects and exposes the CPU-specific MIPS idle wait implementation. It handles CPUs whose `wait` instruction is safe, unsafe, erratum-affected, or requires interrupts enabled.

### Important APIs, Types, And Functions
The exported function pointer is `cpu_wait`. Important functions include `r4k_wait_irqoff()`, `check_wait()`, `arch_cpu_idle()`, and `mips_cpuidle_wait_enter()`. Internal wait variants include `r3081_wait()`, `rm7k_wait_irqoff()`, and `au1k_wait()`. The `nowait` boot option disables wait selection.

### Control Flow
`check_wait()` inspects `current_cpu_data`, `cpu_has_mips_r6`, CPU type, processor revision, config7 WII, and selected kernel options. It chooses `r4k_wait`, `r4k_wait_irqoff`, an erratum workaround, an Alchemy-specific IRQ-enabled sequence, or leaves `cpu_wait` unset. `arch_cpu_idle()` calls the selected function if present. cpuidle calls the same path and returns the selected state index.

### State, Persistence, And Dependencies
Mutable state is the global `cpu_wait` pointer and `nowait` boot flag. Wait paths manipulate CP0 Config/Status and interrupt state. Dependencies include CPU type tables, `need_resched()`, `local_irq` helpers, CP0 register accessors, and assembly label `r4k_wait` from `genex.S`.

### Integration Points
The file integrates CPU probe, idle loop, cpuidle, scheduler reschedule checks, and exception skipover support. The selected wait implementation controls power behavior for every idle CPU.

### Risks
Using `wait` on CPUs with broken wake semantics can hang the CPU. The irq-off variant is only safe on CPUs where masked interrupts wake `wait`; `check_wait()` encodes those hardware contracts. Alchemy stops core clock, so its variant must enable interrupts before waiting.

### Test Signals
Test boot with and without `nowait`, idle wakeups from timer and device interrupts, cpuidle entry/exit, reschedule latency, CPU families with config7 WII, and erratum-specific CPUs such as RM7000, 20Kc, Loongson64, and Alchemy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/idle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/irq-gt641xx.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/irq-gt641xx.c

### Purpose
`irq-gt641xx.c` implements IRQ chip and dispatch support for GT641xx system controller interrupts. It masks, unmasks, acknowledges, initializes, and dispatches interrupt bits from the GT interrupt cause and mask registers.

### Important APIs, Types, And Functions
Public functions are `gt641xx_irq_dispatch()` and `gt641xx_irq_init()`. IRQ-chip callbacks are `ack_gt641xx_irq()`, `mask_gt641xx_irq()`, `mask_ack_gt641xx_irq()`, and `unmask_gt641xx_irq()`. The `gt641xx_irq_chip` is registered for interrupts `GT641XX_IRQ_BASE + 1` through `+29`.

### Control Flow
Initialization disables all GT interrupts, clears cause, and installs a level IRQ handler for supported bits. Dispatch reads cause and mask, intersects them, scans bits 1 through 29, and calls `do_IRQ()` for the first active source. If no source is found it increments `irq_err_count`.

### State, Persistence, And Dependencies
State is in GT interrupt MMIO registers and protected by `gt641xx_irq_lock` for mask/cause read-modify-write. The file depends on `GT_READ`, `GT_WRITE`, `GT_INTRCAUSE_OFS`, `GT_INTRMASK_OFS`, Linux IRQ core, and `irq_err_count`.

### Integration Points
Platform interrupt code calls `gt641xx_irq_init()` and `gt641xx_irq_dispatch()` when the CPU interrupt line represents GT641xx aggregated interrupts. Child device drivers receive Linux IRQ numbers under `GT641XX_IRQ_BASE`.

### Risks
The dispatcher ignores summary bits 0, 30, and 31 and handles only one pending bit per entry. Incorrect base numbering or summary-bit interpretation can drop interrupts. Ack and mask operations share one lock but direct hardware behavior depends on cause bits being write-clear by writing the masked value.

### Test Signals
Exercise each usable GT interrupt input, verify masking/unmasking, confirm spurious counts only rise on real spurious events, and inspect `/proc/interrupts` for expected child IRQ numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/irq-gt641xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/irq-msc01.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/irq-msc01.c

### Purpose
`irq-msc01.c` supports the MIPS SOC-it MSC01 interrupt controller. It maps the controller registers, configures edge or level IRQ lines, dispatches vector interrupts, and optionally binds EIC vectors.

### Important APIs, Types, And Functions
Public functions are `ll_msc_irq()` and `init_msc_irqs()`. Important callbacks are `mask_msc_irq()`, `unmask_msc_irq()`, `level_mask_and_ack_msc_irq()`, `edge_mask_and_ack_msc_irq()`, and `msc_bind_eic_interrupt()`. Two IRQ chips are defined: `msc_levelirq_type` and `msc_edgeirq_type`.

### Control Flow
Initialization maps the controller, resets it, installs `board_bind_eic_interrupt`, loops over a board-provided `msc_irqmap_t` array, sets chip/handler type, configures edge or level support registers, records `irq_base`, and enables interrupt generation. Runtime dispatch reads `MSC01_IC_VEC`, converts valid vectors below 64 to Linux IRQs, and calls `do_IRQ()`.

### State, Persistence, And Dependencies
State includes `_icctrl_msc`, macro-derived register addresses, global `irq_base`, controller registers, and board EIC binding callback. The code depends on `ioremap`, `asm/msc01_ic.h`, `cpu_has_veic`, IRQ core, and board-provided interrupt maps.

### Integration Points
This file is called by board-specific arch init code for SOC-it systems. It integrates with EIC/VEIC modes, the generic IRQ subsystem, and platform interrupt dispatch.

### Risks
The code uses direct volatile register pointers rather than accessor wrappers, and the edge clear path differs for VEIC versus non-VEIC. The `MSC01_IC_SUP + irq * 8` expression uses the full Linux IRQ in the VEIC edge clear path, so the register map and base assumptions must match board usage.

### Test Signals
Test edge and level sources, VEIC and non-VEIC configurations, EOI behavior, spurious vector handling, and board map entries that cover low and high interrupt banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/irq-msc01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/irq.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/irq.c

### Purpose
`irq.c` provides generic MIPS IRQ plumbing: per-CPU IRQ stacks, bad/spurious IRQ accounting, `/proc/interrupts` architecture lines, IRQ initialization, and wrappers that enter and exit generic IRQ handling.

### Important APIs, Types, And Functions
Important exports are `irq_stack[NR_CPUS]`, `ack_bad_irq()`, `arch_show_interrupts()`, `spurious_interrupt()`, `init_IRQ()`, `do_IRQ()`, and `do_domain_IRQ()` when IRQ domains are enabled. `irq_err_count` tracks bad or spurious IRQs.

### Control Flow
`init_IRQ()` marks all IRQs noprobe, clears status interrupt mask bits for VEIC CPUs, calls platform `arch_init_irq()`, and allocates an IRQ stack for every possible CPU. `do_IRQ()` and `do_domain_IRQ()` wrap generic IRQ handling with `irq_enter()`, optional stack overflow check, generic dispatch, and `irq_exit()`.

### State, Persistence, And Dependencies
State includes `irq_stack`, `irq_err_count`, allocated page stacks, IRQ descriptor flags, and CP0 status interrupt mask bits. Dependencies include generic IRQ core, procfs seq output, stack debug config, IRQ domains, and platform `arch_init_irq()`.

### Integration Points
`genex.S` switches to `irq_stack` and calls platform dispatch, which eventually calls `do_IRQ()` or `do_domain_IRQ()`. `/proc/interrupts` uses `arch_show_interrupts()` to display the `ERR` line.

### Risks
IRQ stack allocation is unchecked for failure in this version, so low-memory early boot could leave null stacks. Stack overflow checking assumes standard thread stack layout. VEIC mask clearing must happen before platform IRQ init to avoid stale CPU interrupt enables.

### Test Signals
Validate boot IRQ stack allocation, interrupt delivery through legacy and IRQ-domain paths, `/proc/interrupts` `ERR` count, debug stack overflow warnings, and interrupt storms on SMP systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/irq_txx9.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/irq_txx9.c

### Purpose
`irq_txx9.c` implements the Toshiba TXx9 interrupt controller driver. It maps IRC registers, configures interrupt priorities and trigger modes, masks/acknowledges/unmasks sources, and returns the current pending IRQ.

### Important APIs, Types, And Functions
Public functions are `txx9_irq_init()`, `txx9_irq_set_pri()`, and `txx9_irq()`. IRQ chip callbacks are `txx9_irq_unmask()`, `txx9_irq_mask()`, `txx9_irq_mask_ack()`, and `txx9_irq_set_type()`. The file defines `struct txx9_irc_reg` and per-line `txx9irq[]` level/mode state.

### Control Flow
Initialization maps the IRC, assigns default priority and low-level mode to each line, registers all lines as level IRQs, masks all interrupts, clears interrupt level registers, sets control registers to low-active, enables interrupt control, and sets enabled priority level. Runtime type changes update control-register two-bit fields. Masking writes the disabled priority to the selected ILR slot; unmasking writes the stored priority. Edge ack clears edge detection through `scr`.

### State, Persistence, And Dependencies
State is split between `txx9_ircptr`, the `txx9irq[]` software shadow for priority/mode, and IRC MMIO registers. The file depends on `asm/txx9irq.h`, gpiolib-adjacent TXx9 board setup, IRQ core, raw MMIO, and `mmiowb()`.

### Integration Points
Board interrupt dispatch calls `txx9_irq()` to obtain the pending Linux IRQ number and then dispatches it. Device drivers use IRQs starting at `TXX9_IRQ_BASE`.

### Risks
Register field math for ILR offsets is compact and easy to break. `txx9_irq()` returns `-1` when the current-status flag indicates no interrupt, so callers must handle spurious cases. Defaulting all handlers to level IRQs means edge users must call `irq_set_type()`.

### Test Signals
Test priority changes, all four trigger types, edge clear behavior, masking/unmasking, spurious `-1` returns, and interrupt numbering against `TXX9_IRQ_BASE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/irq_txx9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/jump_label.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/jump_label.c

### Purpose
`jump_label.c` implements MIPS static-key patching. It rewrites NOP slots into architecture-appropriate unconditional jumps or branches and applies module jump-label NOP initialization.

### Important APIs, Types, And Functions
The main entry is `arch_jump_label_transform(struct jump_entry *e, enum jump_label_type type)`. With modules, `jump_label_apply_nops(struct module *mod)` initializes module entries whose type is NOP. The code uses `union mips_instruction` and ISA-specific constants for MIPS, microMIPS, and MIPS R6 branch encodings.

### Control Flow
For `JUMP_LABEL_JMP`, the transformer validates target alignment and ISA bit, then emits either R6 `bc6`, microMIPS `j32`, or classic MIPS `j`. For NOP it writes zero. The text patch is serialized by `text_mutex`, written as halfwords for microMIPS or a full instruction otherwise, flushed from icache, and unlocked.

### State, Persistence, And Dependencies
The persistent state is patched kernel or module text. Dependencies include `linux/jump_label.h`, `asm/inst.h`, `msk_isa16_mode()`, MIPS ISA revision macros, `text_mutex`, and `flush_icache_range()`.

### Integration Points
The file integrates with Linux static keys and module finalization. `module.c` calls `jump_label_apply_nops()` during module finalization when jump labels are enabled.

### Risks
Jump range and alignment checks are critical. Classic J jumps cannot cross their region boundary, while R6 branch offsets must fit in 26 signed bits. microMIPS requires halfword ordering and ISA-bit preservation. A wrong patch can execute invalid text on every static-key site.

### Test Signals
Enable static keys in built-in and module code, toggle keys repeatedly, load modules with jump entries, test microMIPS and R6 configs, and use runtime branch patch assertions or objdump spot checks for emitted encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/jump_label.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/kgdb.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/kgdb.c

### Purpose
`kgdb.c` provides MIPS architecture support for the kernel debugger. It maps pt_regs and FPU state to GDB registers, emits breakpoints, translates traps to signals, hooks die notifications, handles continue commands, and defines the MIPS breakpoint instruction bytes.

### Important APIs, Types, And Functions
Important data includes `hard_trap_info[]`, `dbg_reg_def[]`, and `arch_kgdb_ops`. Key functions are `dbg_set_reg()`, `dbg_get_reg()`, `arch_kgdb_breakpoint()`, `sleeping_thread_to_gdb_regs()`, `kgdb_arch_set_pc()`, `kgdb_mips_notify()`, `kgdb_ll_trap()`, `kgdb_arch_handle_exception()`, `kgdb_arch_init()`, and `kgdb_arch_exit()`.

### Control Flow
Register access validates register numbers, copies general registers directly from `pt_regs`, and saves/restores FPU state only when CP1 is enabled. The die notifier ignores userspace traps, delegates NMI callbacks when kgdb is active, calls `kgdb_handle_exception()`, advances EPC past `breakinst` during breakpoint setup, enables interrupts, flushes caches, and stops notifier propagation. The architecture exception handler supports the GDB `c` command with an optional new PC.

### State, Persistence, And Dependencies
State is in the current task FPU context, `pt_regs`, kgdb global flags, die notifier registration, and cache state after patching breakpoints. Dependencies include kgdb core, kdebug notifier chains, FPU save/restore, instruction encoding definitions, SMP callbacks, and cache flushing.

### Integration Points
This file integrates trap handling, low-level debug exceptions, kgdb I/O modules, breakpoints, and MIPS register layout expected by GDB remote protocol.

### Risks
FPU register access is conditional on `ST0_CU1`; missing saves can expose stale values. The notifier deliberately enables local IRQs before cache flush because SMP cache flush may IPI, which is sensitive during panic/debug paths. Trap filtering must avoid consuming kprobes page-fault notifications.

### Test Signals
Use kgdb over a registered I/O backend, set and hit breakpoints, read/write general and FPU registers, continue with and without an address, debug SMP/NMI paths, and verify endian-specific breakpoint bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/kgdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/kprobes.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/kprobes.c

### Purpose
`kprobes.c` implements MIPS kprobes and kretprobes. It replaces target instructions with breakpoints, single-steps a copied instruction in an executable slot, handles branch delay slots, and routes kretprobe returns through a trampoline.

### Important APIs, Types, And Functions
Architecture entry points include `arch_prepare_kprobe()`, `arch_arm_kprobe()`, `arch_disarm_kprobe()`, `arch_remove_kprobe()`, `kprobe_exceptions_notify()`, `arch_prepare_kretprobe()`, `arch_trampoline_kprobe()`, and `arch_init_kprobes()`. Internal handlers include `kprobe_handler()`, `post_kprobe_handler()`, `kprobe_fault_handler()`, `prepare_singlestep()`, `resume_execution()`, and `evaluate_branch_instruction()`.

### Control Flow
Preparation rejects LL/SC, compact branches, and branch-delay-slot targets; allocates an instruction slot; copies either the probed instruction or its delay-slot instruction; appends a second breakpoint; and saves the original opcode. A probe hit disables preemption, sets per-CPU current probe state, runs the pre-handler, redirects EPC to the copied instruction, and waits for the second breakpoint. Branch probes compute target EPC and may skip a NOP delay slot. Post handling runs the post-handler, resumes EPC, restores interrupt state, and clears or restores nested probe state.

### State, Persistence, And Dependencies
State is per-CPU `current_kprobe` and `kprobe_ctlblk`, patched kernel text, allocated instruction slots, saved opcodes, pt_regs EPC/status, and kretprobe instances. Dependencies include MIPS branch decoding, break exception notifications, text icache flushing, preempt control, and `probes-common.h`.

### Integration Points
The file integrates Linux kprobes core, die notifier values `DIE_BREAK`, `DIE_SSTEPBP`, and `DIE_PAGE_FAULT`, MIPS exception handling, and kretprobe trampoline registration.

### Risks
MIPS lacks native single-step, so correctness depends on SSOL slots and breakpoint recursion handling. Branch delay slots are fragile, LL/SC probes are refused to preserve atomicity, and faults during single-step must restore EPC/status without leaving preemption disabled.

### Test Signals
Run kprobes and kretprobes on ordinary instructions, branches with and without delay-slot work, nested probes, faulting copied instructions, module functions, and refused LL/SC or compact-branch targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/kprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/linux32.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/linux32.c

### Purpose
`linux32.c` implements 32-bit compatibility syscall wrappers for 64-bit MIPS kernels. It reconstructs split 64-bit arguments using ABI endianness rules and delegates to native kernel syscall helpers.

### Important APIs, Types, And Functions
Key wrappers include `sys32_truncate64`, `sys32_ftruncate64`, `sys32_llseek`, `sys32_pread`, `sys32_pwrite`, `sys32_personality`, `sys32_readahead`, `sys32_sync_file_range`, `sys32_fadvise64_64`, and `sys32_fallocate`. The central helper macro is `merge_64()`, which differs for `__MIPSEB__` and `__MIPSEL__`.

### Control Flow
Each syscall wrapper receives 32-bit ABI argument words, merges high/low halves into a 64-bit offset or length where needed, and calls the common helper such as `ksys_truncate`, `ksys_ftruncate`, `sys_llseek`, `ksys_pread64`, `ksys_pwrite64`, or `ksys_fallocate`. `sys32_personality()` translates between `PER_LINUX32` and `PER_LINUX` on input and output to preserve 32-bit user ABI behavior.

### State, Persistence, And Dependencies
The wrappers do not maintain persistent state except via delegated syscalls. They depend on compat syscall ABI definitions, uaccess, filesystem helpers, personality flags, and correct MIPS endian argument ordering.

### Integration Points
This file is linked into MIPS compat syscall tables and used by 32-bit user programs running on a 64-bit kernel. It integrates with VFS, mm, ipc, networking includes, and generic compat infrastructure.

### Risks
Wrong `merge_64()` ordering silently corrupts offsets and lengths. The dummy padding arguments must match the o32 syscall ABI; changing prototypes can break syscall table calling conventions. Personality translation must preserve legacy user-space expectations.

### Test Signals
Run 32-bit compat tests for large-file truncate/ftruncate, llseek, pread/pwrite beyond 4 GiB, sync_file_range, fadvise64_64, fallocate, readahead, and personality transitions on both big-endian and little-endian MIPS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/linux32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/machine_kexec.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/machine_kexec.c

### Purpose
`machine_kexec.c` implements MIPS machine-specific kexec and crash-kexec handoff. It prepares new-kernel arguments, shuts down other CPUs, copies relocation code to the control page, rewrites indirection entries to virtual addresses, flushes caches, and jumps to the new kernel.

### Important APIs, Types, And Functions
Public entry points include `machine_kexec_prepare()`, `machine_kexec_cleanup()`, `machine_shutdown()`, `machine_crash_shutdown()`, `kexec_reboot()`, and `machine_kexec()`. Platform hooks are `_machine_kexec_prepare`, `_machine_kexec_shutdown`, `_machine_crash_shutdown`, and `_crash_smp_send_stop`. SMP helpers include `kexec_shutdown_secondary()` and `kexec_nonboot_cpu_jump()`.

### Control Flow
Preparation checks SMP nonboot CPU support and invokes an optional platform prepare hook. UHI boot prepare scans image segments for an FDT and sets `kexec_args`. Shutdown invokes platform shutdown, sends secondaries into a wait loop, and waits until only one CPU remains online. `machine_kexec()` installs relocation code into `image->control_code_page`, sets `kexec_start_address` and `kexec_indirection_page`, converts page-list physical addresses to virtual, marks the boot CPU offline, disables IRQs, flushes caches, releases secondary CPUs, and calls `kexec_reboot()`.

### State, Persistence, And Dependencies
State includes `reboot_code_buffer`, relocation globals, atomic `kexec_ready_to_reboot`, relocated SMP wait function pointer, CPU online masks, `kexec_args`, and the kimage page list. Dependencies include kexec core, cache flushing, FDT helpers, SMP support, and platform-specific hooks.

### Integration Points
This code integrates Linux kexec/kdump, MIPS relocation assembly, platform shutdown code, firmware boot argument conventions, and CPU hotplug visibility for crash analysis tools.

### Risks
Cache coherency and address translation are critical. If indirection entries are not converted correctly or relocation code is not visible in icache, the handoff fails after interrupts are disabled. SMP shutdown depends on all secondaries reaching the wait loop.

### Test Signals
Run normal kexec, crash kexec/kdump, UHI FDT handoff, SMP kexec with secondary CPUs, and failure injection for missing nonboot CPU support. Verify crash dumps see expected online CPU state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/machine_kexec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mcount.S -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/mcount.S

### Purpose
`mcount.S` implements MIPS `_mcount`, `ftrace_caller`, function graph caller support, and `return_to_handler` assembly. It is the low-level callsite ABI used by `ftrace.c` for dynamic and non-dynamic function tracing.

### Important APIs, Types, And Functions
Exported labels include `_mcount`, `ftrace_caller`, `ftrace_call`, `ftrace_graph_call`, `ftrace_stub`, `ftrace_graph_caller`, and `return_to_handler`. Register save/restore macros are `MCOUNT_SAVE_REGS`, `MCOUNT_RESTORE_REGS`, and `RETURN_BACK`.

### Control Flow
In dynamic ftrace builds, `_mcount` initially branches to `ftrace_stub`; patched callsites jump into `ftrace_caller + 8`, save caller-saved registers, compute the traced function address, call the patched tracing function via `ftrace_call`, optionally call graph tracing, restore registers, and return with the original parent return address restored from `AT`. Non-dynamic builds call `ftrace_trace_function` directly when not equal to `ftrace_stub`, then check graph tracer hooks. Graph tracing passes the parent return-address slot, self return address, and frame pointer to `prepare_ftrace_return()`.

### State, Persistence, And Dependencies
State is on the temporary pt_regs-like stack frame, the caller's return address in `AT`/`ra`, optional `$12` return-address slot from `KBUILD_MCOUNT_RA_ADDRESS`, and patched instruction placeholders. Dependencies include `asm/ftrace.h`, `stackframe.h`, `ftrace.c`, and compiler-generated `_mcount` callsite layout.

### Integration Points
The assembly must match `ftrace_make_call()`/`ftrace_make_nop()` patch expectations and function graph return handling in `ftrace.c`. `return_to_handler` calls `ftrace_return_to_handler()` and jumps to the real parent address.

### Risks
The ABI is very narrow: wrong stack adjustment, saved-register set, module callsite offset, or return-address handling corrupts traced functions. 32-bit builds include legacy stack adjustment in delay slots, which dynamic patching removes.

### Test Signals
Enable function tracing and graph tracing on 32-bit and 64-bit MIPS, trace modules, test builds with and without `KBUILD_MCOUNT_RA_ADDRESS`, and compare callsite disassembly against `ftrace.c` patch comments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mcount.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mips-cm.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/mips-cm.c

### Purpose
`mips-cm.c` probes and manages the MIPS Coherence Manager GCR space. It maps the GCR region, configures default targets and optional L2-only sync space, serializes access to redirected "other" core/VP registers, reports CM errors, and identifies whether the current CPU is the first online CPU in a cluster.

### Important APIs, Types, And Functions
Globals include `mips_gcr_base`, `mips_cm_l2sync_base`, `mips_cm_is64`, and `mips_cm_is_l2_hci_broken`. Important APIs are `mips_cm_phys_base()`, `mips_cm_l2sync_phys_base()`, `mips_cm_update_property()`, `mips_cm_probe()`, `mips_cm_lock_other()`, `mips_cm_unlock_other()`, `mips_cm_error_report()`, and `mips_cps_first_online_in_cluster()`.

### Control Flow
Probe reads CP0 config registers for CMGCRBase support, maps the GCR base, validates the mapped base register, sets the default target to memory, disables CM regions, probes and maps L2-only sync for CM major revision >= 6, computes register width, and initializes per-CPU locks. `mips_cm_lock_other()` disables preemption and locks either per-current-core or per-CPU, writes `GCR_CL_OTHER`, and issues a memory barrier before redirected register access. Error reporting decodes CM2 or CM3 error causes into human-readable fields, prints address/multiplicity registers, then reprimes the cause register.

### State, Persistence, And Dependencies
State lives in mapped GCR registers, per-CPU locks/flags, DT-derived EyeQ6 quirk state, and CPS cluster masks. Dependencies include `asm/mips-cps.h`, CP0 CM registers, bitfield macros, device tree, SMP/CPS support, and spinlocks.

### Integration Points
The file is shared by CPS SMP bring-up, CPC access, cache/coherency error handling, L2 sync users, and platform quirks. `mips-cpc.c` depends on CM presence and revision behavior.

### Risks
Redirected "other" accesses are race-prone without the locks and preemption disable. Misdetecting CM base or width causes invalid MMIO. Error decode tables are revision-specific and can misreport newer hardware if fields change.

### Test Signals
Boot CM2, CM3, and CM3.5+ systems, validate GCR mapping, redirected core/VP access under SMP, CM error injection/logging where available, L2-only sync mapping on revision >= 6, and EyeQ6 device-tree quirk behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mips-cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mips-cpc.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/mips-cpc.c

### Purpose
`mips-cpc.c` probes and maps the MIPS Cluster Power Controller and serializes redirected CPC core access on older CM revisions.

### Important APIs, Types, And Functions
The exported state is `mips_cpc_base`. Important functions are `mips_cpc_default_phys_base()`, `mips_cpc_probe()`, `mips_cpc_lock_other()`, and `mips_cpc_unlock_other()`. The internal `mips_cpc_phys_base()` uses CM GCR CPC status/base registers to locate or enable CPC.

### Control Flow
Default base discovery first looks for a device-tree node compatible with `mti,mips-cpc`. Probe initializes per-CPU locks, obtains a physical base by checking CM presence and CPC existence, leaves an already enabled CPC at its existing base, or enables it at the default DT base, then `ioremap()`s the register space. For CM revisions below CM3, lock/unlock disables preemption, locks the current core's CPC redirect register, writes `CPC_Cx_OTHER_CORENUM`, and barriers before access. CM3+ uses CM-level locking instead, so CPC lock functions return.

### State, Persistence, And Dependencies
State is the mapped CPC base and per-CPU core locks/IRQ flags. CPC enablement persists in GCR CPC base registers. Dependencies include device tree address parsing, CM probe helpers, bitfield macros, CPC register accessors, and CPU core numbering.

### Integration Points
The CPC is used by MIPS CPS CPU power, idle, and hotplug paths. Its locking complements `mips_cm_lock_other()` for register spaces that expose an "other core" selector.

### Risks
Probe requires a working CM mapping. Missing or wrong DT address prevents enabling CPC. On older CM revisions, failing to serialize `CPC_CL_OTHER` can race with other VPEs and redirect register operations to the wrong core.

### Test Signals
Boot DT and non-DT CPC systems, confirm CPC enable bit/base, exercise CPU hotplug or power-state operations, and stress parallel cross-core CPC access on CM2-era hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mips-cpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mips-mt-fpaff.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/mips-mt-fpaff.c

### Purpose
`mips-mt-fpaff.c` adds MIPS MT FPU affinity policy by wrapping scheduler affinity syscalls. It keeps FP-heavy tasks on VPEs/TCs that have an FPU while preserving the user's requested CPU mask.

### Important APIs, Types, And Functions
Public state includes `mt_fpu_cpumask` and `mt_fpemul_threshold`. Public syscall wrappers are `mipsmt_sys_sched_setaffinity()` and `mipsmt_sys_sched_getaffinity()`. Helpers include `find_process_by_pid()`, `check_same_owner()`, `fpaff_thresh()`, and `mt_fp_affinity_init()`.

### Control Flow
`sched_setaffinity` copies the user mask, finds and pins the target task under CPU and RCU locks, checks ownership/capability and LSM scheduler permission, records the user mask in `p->thread.user_cpus_allowed`, then intersects it with `mt_fpu_cpumask` when the task has `TIF_FPUBOUND`. If a concurrent cpuset update changes allowed CPUs, it retries with the cpuset mask. `sched_getaffinity` reports the union of saved user mask and current effective mask, restricted to active CPUs. Boot parameter `fpaff=` overrides the emulation threshold; otherwise init derives it from `loops_per_jiffy`.

### State, Persistence, And Dependencies
State is task `thread.user_cpus_allowed`, `TIF_FPUBOUND`, global FPU-capable CPU mask, and the emulation threshold. Dependencies include scheduler affinity APIs, cpusets, credentials, security hooks, uaccess, and MIPS MT FP emulation accounting.

### Integration Points
The wrappers replace normal affinity syscalls on MIPS MT systems so FPU emulation can trigger binding to FPU-capable CPUs without hiding the user's original affinity request.

### Risks
The source comments note this code mirrors scheduler core logic and must stay in sync with upstream permission and cpuset behavior. The local `cpumask_var_t new_mask` declaration shadows the earlier stack variable pattern and must be handled carefully by compilers/configs. Races with cpuset updates are explicitly retried.

### Test Signals
Test affinity set/get for current and remote tasks, permission failures, cpuset changes during affinity updates, FP-bound tasks intersecting `mt_fpu_cpumask`, and `fpaff=` threshold override.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mips-mt-fpaff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mips-mt.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/mips-mt.c

### Purpose
`mips-mt.c` provides general MIPS MT configuration support. It parses boot options limiting VPEs/TCs, overriding 34K Config7 behavior, and mapping the Inter-Thread Communication block, then registers the MT sysfs class.

### Important APIs, Types, And Functions
Public globals are `vpelimit`, `tclimit`, and `mt_class`. Important functions are `mips_mt_set_cpuoptions()` and init parsers for `maxvpes=`, `maxtcs=`, `rpsctl=`, `nblsu=`, `config7=`, and `itcbase=`.

### Control Flow
Boot option parsers store requested limits or override values. `mips_mt_set_cpuoptions()` reads CP0 Config7, applies return prediction stack and ALU/LSU sync overrides, optionally forces the full Config7 value, writes it with `sync` and `ehb`, then optionally enables ITC register access through ErrCtl and programs ITC granularity/base using cache tag operations. `mips_mt_init()` registers the `mt` class at `subsys_initcall`.

### State, Persistence, And Dependencies
State includes boot-option globals, CP0 Config7, ErrCtl, DTagLo, ITC control state, and sysfs class registration. Dependencies include MIPS MT CP0 register access, cache ops, CPU feature setup, and Linux device class infrastructure.

### Integration Points
The code is used by MIPS MT CPU setup, VPE/TC management, board-specific MT initialization, and userspace-visible MT class devices.

### Risks
Config7 and ITC programming are hardware-specific and can destabilize CPUs if wrong values are forced. `itcbase=` assumes 34K-specific cache tag control paths. Boot options bypass conservative defaults, so they are powerful diagnostics but risky production knobs.

### Test Signals
Boot with each MT option, inspect Config7 logs, verify VPE/TC limits, validate ITC mapping on 34K-family hardware, check `/sys/class/mt`, and run SMP/SMVP scheduling and interrupt tests after overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mips-mt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mips-r2-to-r6-emul.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/mips-r2-to-r6-emul.c

### Purpose
`mips-r2-to-r6-emul.c` emulates user-space MIPS R2/R5 instructions removed or changed by MIPS R6. It lets older binaries run on R6 CPUs by handling reserved-instruction traps, emulating arithmetic, branch-likely delay-slot behavior, unaligned load/store forms, LL/SC, and FPU instructions, with optional debugfs statistics.

### Important APIs, Types, And Functions
The main exported decoder is `mipsr2_decoder(struct pt_regs *regs, u32 inst, unsigned long *fcr31)`. Boot option `mipsr2emu` enables `mipsr2_emulation`. Important helpers include `mipsr6_emul()` for fast delay-slot emulation, instruction-specific functions such as `jr_func()`, `movf_func()`, `movt_func()`, `movz_func()`, `mfhi_func()`, `mult_func()`, `div_func()`, `dmult_func()`, `madd_func()`, `mul_func()`, `clz_func()`, and decoder tables `spec_op_table` and `spec2_op_table`. Debugfs show functions expose and clear per-CPU counters.

### Control Flow
The decoder computes the normal return EPC, switches on opcode, emulates SPECIAL/SPECIAL2 functions through mask/code tables, handles branch-likely and link branches by recomputing target EPC and emulating or trampoline-running delay-slot instructions, delegates FPU opcodes to `fpu_emulator_cop1Handler()`, implements left/right word/doubleword loads and stores with endian-specific byte assembly, emulates LL/SC only when `cpu_has_rw_llb`, and skips PREF. After a successful instruction it attempts up to `MIPS_R2_EMUL_TOTAL_PASS` sequential emulations before returning to user mode.

### State, Persistence, And Dependencies
State is modified in `pt_regs` general registers, HI/LO, EPC, Cause BD bit, current task FPU state, `thread.cp0_baduaddr`, and optional per-CPU debugfs counters. Dependencies include MIPS instruction macros, branch EPC computation, user access/ex-table fixups, FPU emulator, `mips_dsemul()`, Config5 LLB support, debugfs, and endian/32-bit/64-bit config guards.

### Integration Points
This file is called from reserved-instruction handling for user mode on R6-capable systems. It integrates with FPU emulation, delay-slot emulation, signal delivery by returning SIG* values, and `mips_debugfs_dir` for observability.

### Risks
Instruction semantics must exactly match older ISA behavior, including sign extension, zero-register writes, delay-slot branch-likely nullification, and endian-specific unaligned memory byte order. Division by zero follows hardware-like behavior only if callers expect it. LL/SC emulation without Config5 LLB is intentionally fatal because atomicity cannot be preserved.

### Test Signals
Run old R2/R5 user-space ISA tests on R6 hardware or QEMU, including MOVF/MOVT, HI/LO ops, multiply/divide, DSP-like MADD/MSUB, branch-likely delay slots, JR with delay slots, unaligned LWL/LWR/SWL/SWR and LDL/LDR/SDL/SDR on both endian modes, LL/SC atomics, FPU traps, SIGSEGV/SIGBUS fault paths, and debugfs counter clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mips-r2-to-r6-emul.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/module.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/module.c

### Purpose
`module.c` applies MIPS ELF relocations for loadable modules, initializes module jump-label NOPs, and tracks module data bus error exception tables.

### Important APIs, Types, And Functions
Public entry points are `apply_relocate()`, optional `apply_relocate_add()`, `search_module_dbetables()`, `module_finalize()`, and `module_arch_cleanup()`. Relocation helpers include `apply_r_mips_32()`, `apply_r_mips_26()`, `apply_r_mips_hi16()`, `apply_r_mips_lo16()`, `apply_r_mips_pc*()`, `apply_r_mips_64()`, `apply_r_mips_higher()`, `apply_r_mips_highest()`, `reloc_handler()`, and `__apply_relocate()`. `struct mips_hi16` records deferred HI16 relocations.

### Control Flow
Relocation iterates relocation records, locates target section memory and symbol, ignores unresolved weak symbols, computes REL or RELA values, and dispatches by relocation type. REL HI16 records are queued until a matching LO16 supplies carry information; errors or unmatched queues free the chain and fail loading. Module finalization applies jump-label NOPs, scans ELF sections for `__dbe_table`, and adds the module's architecture data to a global protected list. Cleanup removes that list entry.

### State, Persistence, And Dependencies
State includes patched module text/data, `me->arch.r_mips_hi16_list`, global `dbe_list`, `dbe_lock`, and module architecture exception-table bounds. Dependencies include ELF MIPS relocation macros, module loader core, exception table search, jump labels, kmalloc/kfree, and spinlocks.

### Integration Points
This file integrates MIPS modules with the generic module loader, exception-table lookup for data bus errors, and static-key initialization through `jump_label_apply_nops()`.

### Risks
Relocation overflow checks are critical for branch/jump reachability. HI16/LO16 pairing is stateful and malformed modules can trigger dangerous relocation errors. DBE list entries must be removed at unload to avoid stale exception-table pointers.

### Test Signals
Load modules exercising R_MIPS_32, 26, HI16/LO16, PC16/21/26, 64, HIGHER, HIGHEST, unresolved weak symbols, jump labels, and `__dbe_table`; then unload under exception-table lookup stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/octeon_switch.S -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/octeon_switch.S

### Purpose
`octeon_switch.S` implements Cavium Octeon-specific context switching and coprocessor state save/restore. It saves normal thread state, optional CVMSEG state, COP2 crypto/CRC/LLM state, and Octeon multiplier state variants.

### Important APIs, Types, And Functions
Exported assembly functions include `resume`, `octeon_cop2_save`, `octeon_cop2_restore`, `octeon_mult_save`, `octeon_mult_save2`, `octeon_mult_save3`, `octeon_mult_restore`, `octeon_mult_restore2`, and `octeon_mult_restore3`, plus end labels used for patching/copying. It uses structure offsets such as `THREAD_STATUS`, `THREAD_CVMSEG`, `OCTEON_CP2_*`, `PT_MTP`, and `PT_MPL`.

### Control Flow
`resume(prev, next, next_ti)` saves CP0 status and nonscratch registers to the previous task, optionally copies user-enabled CVMSEG memory into thread storage and disables access, updates the stack canary on UP stack-protector builds, switches `$28` to the next thread info, restores nonscratch registers, updates saved SP, merges selected status bits, and returns the previous task. COP2 save/restore reads `CvmCtl` feature-disable bits, saves/restores CRC state, optional DFA/LLM state, optional crypto state, and selects pass1, later Octeon, or Octeon III register maps by processor ID. Multiplier save/restore has stub space and Octeon II/III variants.

### State, Persistence, And Dependencies
State is stored in task thread structs, pt_regs, CP0 status/CvmCtl/CvmMemCtl, CVMSEG memory, COP2 registers, and multiplier pseudo-registers. Dependencies include Octeon ISA, assembler offsets, stackframe macros, and CPU revision IDs.

### Integration Points
This file plugs into the MIPS scheduler switch path, Octeon COP2 lazy/context management, exception save/restore macros, and runtime patching of multiplier helpers.

### Risks
Register ordering and delay slots are critical. Missing a COP2 register corrupts crypto/hash state across context switches. CVMSEG copying depends on configured size and user-enable bit. Processor-ID conditionals must match Octeon pass-specific register layouts.

### Test Signals
Run context-switch stress on Octeon I/II/III, user CVMSEG tests, COP2 crypto/hash workloads across preemption, multiplier state tests, stack-protector canary checks on UP, and scheduler switch tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/octeon_switch.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/perf_event.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/perf_event.c

### Purpose
`perf_event.c` provides MIPS perf kernel callchain collection. It records kernel return addresses either by stack scanning or by symbolic unwinding, while leaving userspace callchains empty.

### Important APIs, Types, And Functions
The visible architecture hook is `perf_callchain_kernel(struct perf_callchain_entry_ctx *entry, struct pt_regs *regs)`. The helper `save_raw_perf_callchain()` scans words from a stack pointer and stores values that are kernel text addresses.

### Control Flow
`perf_callchain_kernel()` starts with register SP from `regs->regs[29]`. With kallsyms support, it uses raw stack scanning if `raw_show_trace` is set or the current PC is not a kernel text address; otherwise it repeatedly stores the current PC and calls `unwind_stack()` until unwinding returns zero or the callchain is full. Without kallsyms it always performs raw stack scanning after validating stack bounds in the caller path.

### State, Persistence, And Dependencies
The function only appends to the supplied perf callchain entry. It reads the current task stack, `pt_regs`, and optional unwind state. Dependencies include perf event core, task stack helpers, `__kernel_text_address()`, and MIPS stacktrace unwinder.

### Integration Points
The code is called by perf sampling when kernel callchains are requested on MIPS. It integrates with stack unwinding, kallsyms/raw trace configuration, and perf's bounded callchain buffer.

### Risks
Raw stack scanning can include false positives from any stack word that looks like a kernel text address. Unwinding depends on reliable frame/return-address conventions. Userspace callchains are intentionally absent, limiting profiling completeness.

### Test Signals
Run `perf record -g` on kernel workloads, compare raw versus unwind callchains, test truncated callchain limits, validate behavior with kallsyms disabled, and verify no out-of-stack reads when SP is near thread stack bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/perf_event.c -->
