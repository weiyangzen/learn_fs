# sources/distributed-fs/ceph-client/arch/arm/kernel/kgdb.c

Purpose: supplies ARM architecture support for KGDB register access, breakpoints, exception handoff, and sleeping-thread register reconstruction.

Important APIs/types/functions: `dbg_reg_def`, `dbg_get_reg`, `dbg_set_reg`, `sleeping_thread_to_gdb_regs`, `kgdb_arch_set_pc`, `kgdb_arch_handle_exception`, `kgdb_arch_init`, `kgdb_arch_exit`, `kgdb_arch_set_breakpoint`, `kgdb_arch_remove_breakpoint`, and `arch_kgdb_ops`. Undef hooks catch normal and compiled break instructions in ARM and Thumb modes.

Control flow: init registers a die notifier and undef hooks. Break traps call `kgdb_handle_exception`; continue/detach commands optionally update PC and compiled breakpoints skip the trapping instruction. Software breakpoint install saves the original instruction with nofault copy and patches text with `__patch_text`.

State and persistence: `compiled_break` remembers whether KGDB should advance PC. Breakpoint objects hold saved instructions; text remains patched until removed.

Dependencies and integration: integrates with kgdb core, die notifiers, undef instruction dispatcher, text patching, and task thread contexts.

Risks: breakpoint instruction size must match patching width; wrong PC adjustment loops forever; register offsets define the remote ABI. Test signals include kgdb attach, software breakpoint set/remove, Thumb and ARM break traps, sleeping task backtraces, and resume after compiled breakpoints.
