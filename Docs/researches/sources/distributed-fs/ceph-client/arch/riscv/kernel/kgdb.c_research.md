# sources/distributed-fs/ceph-client/arch/riscv/kernel/kgdb.c

Purpose: Implements RISC-V KGDB register access, breakpoint handling, and software single-step emulation.

Important APIs/types/functions: Defines register metadata `dbg_reg_def`, `dbg_get_reg()`, `dbg_set_reg()`, `kgdb_arch_set_pc()`, `kgdb_arch_handle_exception()`, `kgdb_arch_init()`, `kgdb_arch_exit()`, `arch_kgdb_ops`, and helpers to decode branch/jump targets and install temporary breakpoints.

Control flow: On KGDB exceptions, command handling can read/write registers, continue, single-step by planting a breakpoint at the computed next PC, or recover the original opcode. A notifier catches break instructions and routes KGDB breakpoints into the debugger.

State and persistence: Maintains `stepped_address` and `stepped_opcode` for temporary single-step breakpoints, plus notifier registration and KGDB architecture ops.

Dependencies and integration points: Depends on KGDB core, RISC-V instruction decoding, text patching/breakpoint helpers, `pt_regs`, and trap notifiers.

Risks and test signals: Branch target decode and temporary breakpoint restoration must be exact or debugging changes program behavior. Test KGDB break/continue/single-step over compressed and normal control-flow instructions, register read/write, SMP breakpoints, and module text.
