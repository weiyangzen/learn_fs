# sources/distributed-fs/ceph-client/arch/sparc/kernel/etrap_64.S

## Purpose
`etrap_64.S` prepares sparc64 V9 trap entry frames. It saves trap state, handles user/kernel window spill cases, switches context/register globals safely, and provides TL>1 trap capture.

## Important APIs, Types, and Functions
Global labels are `etrap`, `etrap_irq`, `etrap_syscall`, and `etraptl1`. It relies on patch sections `.fast_win_ctrl_1insn_patch`, `.sun4v_1insn_patch`, and `.sun_m7_1insn_patch`, and uses `TRAP_LOAD_THREAD_REG`, `LOAD_PER_CPU_BASE`, and `PT_V9_*` offsets.

## Control Flow and State
Normal entry reads PIL/TSTATE/TPC/TNPC/TT/Y, chooses task-stack or current stack based on privilege, clears or preserves FPU state based on `TSTATE_PEF`, saves register globals and ins, switches to privileged interrupt-enabled TSTATE, and returns with `done` to the assembly caller's continuation. If no clean windows are available it reassigns `otherwin`, `wstate`, primary context, and saves user or kernel windows. `etraptl1` snapshots TSTATE/TPC/TNPC/TT for multiple trap levels and then rejoins the common trap-frame setup.

## Persistence and Dependencies
It writes `pt_regs`, `thread_info` FP bookkeeping, trap-level save areas, context registers, PSTATE/TSTATE, WSTATE, and per-cpu base state. Dependencies include V9 privileged registers, sun4v and M7 runtime patches, trap block layout, and `rtrap_64.S`.

## Integration Points, Risks, and Test Signals
Integration points include all sparc64 trap-table handlers, syscalls, IRQ entry, FPU traps, ADI/M7 tagged memory behavior, and TL1 error handling. Risks include corrupting global sets, losing user register windows, disabling ADI enforcement, and mishandling sun4v context ASI differences. Test signals are syscall/interrupt entry stability, ADI tests on M7+, FPU lazy state tests, TL1 error reporting, and register-window stress under SMP.
