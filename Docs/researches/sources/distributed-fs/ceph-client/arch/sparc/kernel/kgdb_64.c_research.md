# sources/distributed-fs/ceph-client/arch/sparc/kernel/kgdb_64.c

Purpose: Provides the SPARC64 architecture glue for KGDB register marshalling, breakpoint trap handling, SMP capture callbacks, and program-counter manipulation.

Important APIs/types/functions: `pt_regs_to_gdb_regs()` copies a live trap frame into GDB register slots, including globals, outs, locals/ins read through the register window at `UREG_FP + STACK_BIAS`, `tpc`, `tnpc`, `tstate`, and `y`. `sleeping_thread_to_gdb_regs()` synthesizes a stopped task view from `thread_info`, `switch_to_pc`, and `ret_from_fork`. `gdb_regs_to_pt_regs()` writes GDB state back while preserving the current-window pointer bits in `TSTATE_CWP`. `smp_kgdb_capture_client()` flushes windows and invokes `kgdb_nmicallback()` on SMP capture interrupts. `kgdb_arch_handle_exception()`, `kgdb_trap()`, `kgdb_arch_set_pc()`, and `arch_kgdb_ops.gdb_bpt_instr` implement continue/detach/kill and the `ta 0x72` breakpoint.

Control flow: A kernel breakpoint trap enters `kgdb_trap()`, rejects user traps via `bad_trap()`, flushes register windows, disables local IRQs, and calls `kgdb_handle_exception()`. KGDB remote commands can optionally set `tpc`, always keep `tnpc` one instruction ahead, and skip over `arch_kgdb_breakpoint` when continuing from the built-in breakpoint.

State and persistence: The file mutates only transient register state and KGDB global state. It relies on stack-resident register windows and task `thread_info`; no persistent data is allocated. The main invariant is preserving `TSTATE_CWP` when importing debugger-provided `tstate`.

Dependencies and integration points: It depends on KGDB core, kdebug/context tracking, SPARC trap/register-window layout, `flushw_all()`, `bad_trap()`, and the assembly breakpoint symbol from `misctrap.S`.

Risks and test signals: Wrong stack-bias/window handling corrupts locals/ins in debugger views. Incorrect `tnpc` adjustment can re-enter breakpoints or skip instructions. Test signals include SPARC64 KGDB attach, continue with and without address arguments, sleeping task backtraces, SMP CPU capture, and traps from user mode being rejected.
