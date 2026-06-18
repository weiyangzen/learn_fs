<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/softirq_stack.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/softirq_stack.h

Purpose: declares x86 softirq stack handling. Important API is the architecture hook for running softirq work on an alternate stack when configured.

Control flow: interrupt/softirq code switches to a per-CPU softirq stack before executing softirq handlers to avoid exhausting task stacks. State is per-CPU softirq stack pointers declared elsewhere. Dependencies include interrupt entry, per-CPU stacks, and generic softirq code.

Risks: stack switching bugs corrupt task or IRQ stacks; nested softirq/interrupt handling must be controlled. Test signals include network/block softirq stress, IRQ stack overflow checks, lockdep/stack traces, and 32-bit stack configuration builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/softirq_stack.h -->
