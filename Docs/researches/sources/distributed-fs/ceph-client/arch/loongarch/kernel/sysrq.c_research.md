## sources/distributed-fs/ceph-client/arch/loongarch/kernel/sysrq.c

### Purpose
`sysrq.c` registers a LoongArch SysRq command that dumps TLB registers and entries. It serializes output and, on SMP, schedules work to request dumps from other CPUs.

### Important APIs, Types, And Functions
The file defines `sysrq_tlbdump_single`, `sysrq_tlbdump_othercpus`, `sysrq_handle_tlbdump`, `sysrq_tlbdump_op`, and `loongarch_sysrq_init`. It uses `dump_tlb_regs`, `dump_tlb_all`, `register_sysrq_key`, `smp_call_function`, a spinlock, and a work item.

### Control Flow
Pressing SysRq `x` dumps the current CPU under `show_lock`, then schedules work that calls the same dump routine on other CPUs via SMP call-function. Registration runs at `arch_initcall`.

### State, Persistence, And Dependencies
Only the spinlock and work item persist. The command depends on TLB dump helpers, SysRq being enabled, and SMP call-function availability.

### Integration Points
Generic SysRq dispatch invokes the registered key operation. TLB diagnostics integrate with LoongArch MMU and SMP subsystems.

### Risks
Dumping all TLB entries can be verbose and runs in diagnostic contexts; the spinlock prevents interleaved output but can delay CPUs. Scheduled work means remote CPU dumps may occur after the triggering context returns.

### Test Signals
Enable SysRq, trigger `x`, verify current and remote CPU dumps appear without interleaving, and test on UP/SMP and with CPUs hotplugged offline.
