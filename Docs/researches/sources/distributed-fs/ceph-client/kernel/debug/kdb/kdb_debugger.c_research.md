# sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_debugger.c

## Purpose
This file is the KDB-to-KGDB bridge. It translates KGDB trap state into KDB reasons, initializes KDB's global current CPU/task/register context, removes and reinstalls KDB breakpoints around the interactive command loop, and returns the correct KGDB core action when KDB exits.

## Important APIs, Types, And Functions
`kdb_poll_funcs` exports the poll input chain, initially backed by `dbg_io_get_char`. `kdb_common_init_state()` and `kdb_common_deinit_state()` populate and clear `kdb_initial_cpu`, `kdb_current_task`, and `kdb_current_regs` from `kgdb_info`. `kdb_stub()` is the main KGDB callback. `kdb_gdb_state_pass()` forwards raw remote protocol state into `gdbstub_state()`.

## Control Flow
`kdb_stub()` records the current `kgdb_state`, classifies the entry reason from reentry state, breakpoint setup, NMI/oops/signo state, and the KDB breakpoint table, then removes KDB breakpoints before running `kdb_main_loop()`. If delayed software breakpoint single-step repair is already complete, it skips the user loop. On exit it either passes control to KGDB, reinstalls breakpoints, requests single-step or continue in the gdbstub state machine, handles CPU switch reentry, or returns the architecture-specific resume state.

## State, Persistence, And Dependencies
The persistent state is global debugger state, not filesystem state: `kdb_ks`, `kdb_initial_cpu`, `kdb_current_task`, `kdb_current_regs`, `KDB_STATE_*`, `KDB_FLAG(CATASTROPHIC)`, `kgdb_single_step`, `dbg_switch_cpu`, and entries in `kdb_breakpoints`. It depends on KGDB core state (`kgdb_active`, `kgdb_info`, `kgdb_arch_pc()`, `kgdb_arch_set_pc()`, `gdbstub_state()`), KDB breakpoint helpers, and CPU/NMI helpers.

## Integration Points
This is entered by the KGDB core when KDB is selected as the frontend. It calls into `kdb_main_loop()` in `kdb_main.c`, breakpoint management in the KDB breakpoint file, and KGDB debug core internals from `debug_core.h`.

## Risks
Incorrect reason classification can either swallow a non-KDB trap or expose the interactive debugger on the wrong event. Breakpoint delay state is delicate: failing to set or clear `SSBPT`/`DOING_SS` correctly can leave patched instructions or repeated traps. Catastrophic detection relies on every online CPU's `enter_kgdb` state, so stuck CPUs force conservative behavior. `kdb_ks` is a global pointer valid only while in the debugger.

## Test Signals
Useful signals are keyboard entry, system NMI entry, oops entry, software breakpoint hit and continue, single-step over breakpoint, `kgdb` command transition, and `cpu` command switching back through `DBG_SWITCH_CPU_EVENT`.
