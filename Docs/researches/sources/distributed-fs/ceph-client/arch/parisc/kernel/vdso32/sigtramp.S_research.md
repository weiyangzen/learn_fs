<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/sigtramp.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/sigtramp.S

### Purpose
`sigtramp.S` implements the 32-bit vDSO realtime signal-return trampoline and unwind metadata for debuggers.

### Important APIs, Types, And Functions
It exports `__kernel_sigtramp_rt`, embeds `SIGFRAME_CONTEXT_REGS32`, and emits `.eh_frame` CIE/FDE records with register save offsets.

### Control Flow
The trampoline contains two entry sequences: one for signals delivered outside syscalls and one for in-syscall delivery. Each loads `in_syscall` into `%r25`, loads `__NR_rt_sigreturn` into `%r20`, and branches to the fixed gateway entry. The unwind metadata describes where the 32-bit signal context registers live relative to `%sp`.

### State, Persistence, And Dependencies
The code lives in the mapped vDSO. It depends on exact offsets expected by GDB, `generated/asm-offsets.h`, the upward-growing PA-RISC signal frame, and syscall gateway ABI.

### Integration Points
`signal.c` selects this trampoline for compat or 32-bit tasks and may skip the first four instructions for in-syscall delivery.

### Risks
Comments warn GDB depends on exact instruction sequences and 64-byte alignment. Offset drift in signal frame structs breaks unwinding and sigreturn.

### Test Signals
Deliver signals to 32-bit tasks, run GDB backtraces through handlers, test in-syscall and interrupt-context returns, and inspect `.eh_frame`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/sigtramp.S -->
