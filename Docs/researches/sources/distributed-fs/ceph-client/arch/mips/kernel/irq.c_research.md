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
