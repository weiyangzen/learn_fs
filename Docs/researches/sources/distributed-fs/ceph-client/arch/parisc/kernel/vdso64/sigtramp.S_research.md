<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/sigtramp.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/sigtramp.S

### Purpose
`sigtramp.S` implements the 64-bit vDSO realtime signal-return trampoline and debugger unwind metadata.

### Important APIs, Types, And Functions
It exports `__kernel_sigtramp_rt`, embeds `SIGFRAME_CONTEXT_REGS`, and emits `.eh_frame` entries with 64-bit data alignment and register save offsets.

### Control Flow
Two instruction sequences load `in_syscall` as 0 or 1, set `%r20` to `__NR_rt_sigreturn`, and branch to the fixed syscall gateway. The FDE describes where GPRs, FP registers, SAR, and IAOQ are saved in the 64-bit signal frame.

### State, Persistence, And Dependencies
The trampoline and `.eh_frame` live in `vdso64.so`. Dependencies include exact signal frame offsets, GDB expectations, PA-RISC gateway ABI, and generated asm offsets.

### Integration Points
Selected by `signal.c` for native 64-bit handlers through `VDSO64_SYMBOL(current, sigtramp_rt)`.

### Risks
Instruction order and alignment are ABI/debugger-sensitive. Frame offset drift will break unwinding and possibly sigreturn.

### Test Signals
Native 64-bit signal delivery, GDB unwinding through handlers, syscall-interrupted handlers, and `readelf --debug-dump=frames` are useful validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/sigtramp.S -->
