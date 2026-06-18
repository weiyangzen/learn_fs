# sources/distributed-fs/ceph-client/arch/um/include/asm/hardirq.h Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/hardirq.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/hardirq.h

### Purpose
`hardirq.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `static inline void ack_bad_irq(unsigned int irq)`; `DECLARE_PER_CPU_SHARED_ALIGNED(irq_cpustat_t, irq_stat);`; `pr_crit("unexpected IRQ trap at vector %02x\n", irq);`; `#define __ASM_UM_HARDIRQ_H`; `#define __ARCH_IRQ_EXIT_IRQS_DISABLED 1`; `#define __ARCH_IRQ_STAT`; `#define inc_irq_stat(member)	this_cpu_inc(irq_stat.member)`. The file has 31 lines and includes or relies on `linux/cache.h`, `linux/threads.h`, `linux/irq.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/cache.h`, `linux/threads.h`, `linux/irq.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/hardirq.h -->
