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
