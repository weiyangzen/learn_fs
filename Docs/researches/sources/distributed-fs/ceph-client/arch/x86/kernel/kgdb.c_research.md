# sources/distributed-fs/ceph-client/arch/x86/kernel/kgdb.c

Purpose: Supplies x86 architecture support for KGDB, including GDB register mapping, software breakpoint patching, hardware breakpoint management, NMI CPU roundup, die-notifier exception routing, and PC adjustment for x86 trap semantics.

Important APIs/types/functions: defines `dbg_reg_def`, `dbg_set_reg()`, `dbg_get_reg()`, `sleeping_thread_to_gdb_regs()`, `kgdb_arch_handle_exception()`, `kgdb_roundup_cpus()`, `kgdb_ll_trap()`, `kgdb_arch_init()`, `kgdb_arch_late()`, `kgdb_arch_exit()`, `kgdb_skipexception()`, `kgdb_arch_pc()`, `kgdb_arch_set_pc()`, `kgdb_arch_set_breakpoint()`, `kgdb_arch_remove_breakpoint()`, and `arch_kgdb_ops`. Hardware breakpoint state lives in `breakinfo[]` and `early_dr7`.

Control flow: KGDB registers die and NMI handlers. Exceptions enter `__kgdb_notify()`, which ignores user-mode traps except special single-step cases, calls `kgdb_handle_exception()`, and touches the NMI watchdog. Continue and single-step packets clear or set TF in `pt_regs`. SMP roundup uses NMI IPIs. Late init preallocates wide perf hardware breakpoints for each debug register slot; setting/removing KGDB hardware watchpoints reserves/releases slots and later `kgdb_correct_hw_break()` installs them per CPU.

State and persistence: register values are transient in `pt_regs` or sleeping task frames. Breakpoint state persists in memory while KGDB is active: software breakpoints save original bytes in `kgdb_bkpt`, and hardware breakpoints track enabled address, type, length, and per-CPU perf events. No state survives reboot.

Dependencies and integration points: depends on KGDB core, die notifiers, x86 debug registers, APIC NMIs, perf hardware breakpoint APIs, text patching, user-copy-safe kernel memory access, and `text_mutex` coordination with other patchers.

Risks: software breakpoint insertion falls back to `text_poke_kgdb()` only when normal copy fails and `text_mutex` is not locked. Hardware breakpoint reservations must avoid leaking perf slots on partial failures. NMI handling uses `was_in_debug_nmi` to consume follow-up unknown NMIs. PC for int3 is reported as `ip - 1`, matching x86 breakpoint trap behavior.

Test signals: KGDB tests should read/write GDB registers on 32-bit and 64-bit builds, set and remove software breakpoints in read-only kernel text, set execute/write/access hardware breakpoints, single-step kernel code, round up secondary CPUs with NMIs, and verify removed int3 skip handling.
