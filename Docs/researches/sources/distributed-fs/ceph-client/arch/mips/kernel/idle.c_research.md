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
