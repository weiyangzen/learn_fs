# sources/distributed-fs/ceph-client/arch/sh/kernel/kgdb.c

Purpose: implements SuperH KGDB register access, breakpoint instruction definition, single-step emulation, and die-notifier integration.

Important APIs and control flow: branch opcode macros support `get_step_address()`, which computes where to plant a temporary trap for single-step. `do_single_step()` overwrites the next-flow instruction with `STEP_OPCODE`; `undo_single_step()` restores it. `dbg_reg_def[]`, `dbg_set_reg()`, and `dbg_get_reg()` map GDB registers to `pt_regs`, including VBR readback. `sleeping_thread_to_gdb_regs()` extracts saved thread state. `kgdb_arch_handle_exception()` handles continue/step/detach/kill packets and optional PC updates. `singlestep_trap_handler` adjusts PC and calls KGDB. A low-priority die notifier forwards breakpoints to KGDB.

State, dependencies, and risks: state includes global `stepped_address`/`stepped_opcode`, KGDB single-step flags, and die notifier registration. Dependencies include SH instruction encoding, icache flushes, trap table entry 0x3d/0x3c, and task register layout. Risks include global single-step state on SMP, delay-slot stepping limitations documented in comments, and unsafe instruction patching if address computation is wrong. Test signals are remote KGDB break/continue/step, sleeping thread register dumps, and delay-slot branch stepping.
