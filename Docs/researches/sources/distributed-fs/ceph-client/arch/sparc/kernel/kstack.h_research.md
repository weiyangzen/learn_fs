# sources/distributed-fs/ceph-client/arch/sparc/kernel/kstack.h

Purpose: Provides SPARC kernel stack validation helpers and hardirq stack switching primitives used by diagnostics such as the NMI watchdog.

Important APIs/types/functions: `kstack_valid()` validates a stack pointer, already adjusted for `STACK_BIAS`, against the current thread stack and optional per-CPU hardirq/softirq stacks. `kstack_is_trap_frame()` checks whether a `pt_regs` pointer lies in a valid stack area and contains a `PT_REGS_MAGIC` value. `set_hardirq_stack()` switches `%sp` to the per-CPU hardirq stack unless already on it, and `restore_hardirq_stack()` restores the saved stack pointer.

Control flow: Validation first checks alignment and the thread stack bounds, then falls back to hardirq and softirq stacks if allocated. Trap-frame validation shares the same bounds logic and then checks the magic field. Hardirq switching reads the current `%sp`, compares it to the hardirq stack interval, and writes a top-of-stack value adjusted for frame size and `STACK_BIAS`.

State and persistence: The functions do not allocate state. They read `thread_info`, per-CPU `hardirq_stack`/`softirq_stack`, and directly mutate `%sp` for a bounded critical section.

Dependencies and integration points: It depends on SPARC stack-frame layout, `thread_info`, IRQ stack arrays, `pt_regs`, `sparc_stackf`, `THREAD_SIZE`, and inline assembly. `nmi.c` uses it to run pseudo-NMI work on the hardirq stack.

Risks and test signals: Bad bounds or bias math can make stack unwinding accept invalid frames or switch to an invalid stack. Useful tests include lockup watchdog interrupts, stack traces from normal/hardirq/softirq contexts, trap-frame detection across stack edges, and SMP systems with and without separate IRQ stacks.
