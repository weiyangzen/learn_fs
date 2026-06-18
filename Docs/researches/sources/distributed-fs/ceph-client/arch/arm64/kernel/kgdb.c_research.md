# sources/distributed-fs/ceph-client/arch/arm64/kernel/kgdb.c

Purpose: Provides arm64 KGDB register mapping, breakpoint patching, exception handling, single-step control, and die notifier integration.

Important APIs and state: `dbg_reg_def[]` maps GDB remote registers to `pt_regs` offsets, with vector registers stubbed as zero. Entry points include `dbg_get_reg()`, `dbg_set_reg()`, `sleeping_thread_to_gdb_regs()`, `kgdb_arch_set_pc()`, `kgdb_arch_handle_exception()`, breakpoint handlers, `kgdb_arch_init/exit()`, and `kgdb_arch_set/remove_breakpoint()`. `compiled_break` tracks compiled breakpoint PC adjustment.

Control flow: continue/detach/kill packets update PC if supplied, clear single-step state, and disable kernel single-step. Step packets update PC, set `kgdb_cpu_doing_single_step`, and enable or rewind kernel single-step. Breakpoint handlers invoke `kgdb_handle_exception()` and return handled. Dynamic KGDB breakpoints read the saved instruction and patch an AArch64 break instruction via text patching.

Dependencies and integration: depends on debug monitors, die notifiers, `asm/text-patching.h`, KGDB core, `pt_regs`, and kernel single-step helpers. `NOKPROBE_SYMBOL` avoids recursive probing of handlers.

Risks and test signals: risks are incorrect register offsets, endian mismatch for pstate, failing to advance compiled breakpoints, single-step conflicts with other debug users, and text patch failures. Test with kgdb over serial, continue/step/detach, dynamic breakpoints, compiled `kgdb_breakpoint()`, SMP stop, and big-endian builds.
