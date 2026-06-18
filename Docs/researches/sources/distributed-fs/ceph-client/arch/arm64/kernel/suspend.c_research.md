## sources/distributed-fs/ceph-client/arch/arm64/kernel/suspend.c

### Purpose
`suspend.c` is the C half of ARM64 CPU suspend/resume. It wraps the assembly context save/restore path, manages suspend-only architectural state, restores feature bits after resume from reset, and allocates the MPIDR-indexed resume stash.

### Important APIs, Types, And Functions
Important APIs are `cpu_suspend_set_dbg_restorer`, `__cpu_suspend_exit`, `cpu_suspend`, and `cpu_suspend_init`. It consumes `__cpu_suspend_enter` from `sleep.S` and publishes `sleep_save_stash`.

### Control Flow
`cpu_suspend()` validates finalized CPU capabilities, reports async MTE faults, saves DAIF, pauses graph tracing, switches cpuidle IRQ context, enters context tracking idle, and calls `__cpu_suspend_enter`. A nonzero return calls the platform finisher and treats a normal return as failure. A zero return is the resume path: it exits idle context and runs `__cpu_suspend_exit`, which uninstalls the idmap, restores CnP, DIT, PAN, HW breakpoints, Spectre v4 mitigation, SME, MTE, and pointer authentication state before DAIF restoration.

### State, Persistence, And Dependencies
State includes the stack-local `sleep_stack_data`, allocated `sleep_save_stash`, optional `hw_breakpoint_restore` hook, DAIF flags, cpuidle IRQ context, and architectural feature registers reset by firmware. No filesystem persistence exists.

### Integration Points
The file connects cpuidle, CPU PM/suspend finishers, `sleep.S`, MTE, SME, ptrauth, debug monitors, uaccess/PAN, Spectre mitigations, alternatives, CnP, ftrace graph tracing, and context tracking.

### Risks
Suspend before alternatives finalize can lose required PSTATE setup. Resume ordering is delicate: idmap removal, debug restoration, and mitigation state must occur before normal execution. A finisher returning zero is treated as unsupported because successful suspend resumes through a different path.

### Test Signals
Run idle and system suspend cycles with MTE, SME, ptrauth, HW breakpoints, pseudo-NMI/PMR, graph tracing, and Spectre-v4 policy variations; fault-inject finisher failure returns.
