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
