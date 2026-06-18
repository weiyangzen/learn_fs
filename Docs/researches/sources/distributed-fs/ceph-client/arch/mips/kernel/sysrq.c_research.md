## sources/distributed-fs/ceph-client/arch/mips/kernel/sysrq.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/sysrq.c` adds a MIPS-specific SysRq key that dumps TLB registers and entries. It supports dumping the local CPU immediately and other CPUs asynchronously on SMP systems.

### Important APIs, Types, And Functions
Key functions are `sysrq_tlbdump_single()`, `sysrq_tlbdump_othercpus()`, `sysrq_handle_tlbdump()`, and `mips_sysrq_init()`. Important state is `show_lock`, the optional `DECLARE_WORK(sysrq_tlbdump, ...)`, and `sysrq_tlbdump_op`.

### Control Flow
SysRq key `x` invokes `sysrq_handle_tlbdump()`. The local CPU takes `show_lock`, prints CPU ID, dumps TLB registers and all entries, and releases the lock. On SMP, work is scheduled to call `smp_call_function()` so other CPUs run the same dump routine without doing cross-CPU calls directly from the SysRq path.

### State, Persistence, And Dependencies
No persistent state is modified. The spinlock serializes console output. Dependencies include `linux/sysrq.h`, workqueues, SMP call functions, and MIPS TLB debug helpers `dump_tlb_regs()` and `dump_tlb_all()`.

### Integration Points
The file registers with the generic SysRq subsystem at `arch_initcall`. It provides operational diagnostics for TLB code in `traps.c`, `smp.c`, and MMU context handling.

### Risks
TLB dumping can be noisy and may run in distressed system states. Cross-CPU work must avoid deadlocks, and serialization is only for output readability. The feature depends on `SYSRQ_ENABLE_DUMP`.

### Test Signals
Trigger SysRq `x` on UP and SMP systems, verify every online CPU is represented, check output serialization, and test under high interrupt or TLB activity load.
