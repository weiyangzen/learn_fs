## sources/distributed-fs/ceph-client/arch/arm64/kernel/stacktrace.c

### Purpose
`stacktrace.c` implements ARM64 kernel and userspace stack unwinding using frame records, pt_regs metadata, per-CPU stack descriptors, ftrace graph recovery, kretprobe recovery, pointer-auth stripping, and compat frame-tail handling.

### Important APIs, Types, And Functions
Key APIs are `arch_stack_walk`, `arch_stack_walk_reliable`, `arch_bpf_stack_walk`, `dump_backtrace`, `show_stack`, and `arch_stack_walk_user`. Internals include `struct kunwind_state`, `kunwind_init_*`, `kunwind_next_frame_record`, `kunwind_next_regs_pc`, `kunwind_recover_return_address`, and consume callbacks.

### Control Flow
An unwind starts from pt_regs, the current caller, or a blocked task's saved frame pointer and PC. The walker validates each frame against known task, IRQ, overflow, SDEI, and EFI stacks, consumes the current PC, advances through the frame record, handles pt_regs frame metadata, strips PAC bits, and recovers original return addresses for fgraph/kretprobe trampolines. Reliable unwinding stops at exception boundaries. User unwinding reads AArch64 or compat frame tails from userspace with page faults disabled and requires frame pointers to progress upward.

### State, Persistence, And Dependencies
State is per-walk stack metadata, current frame pointer/PC, ftrace graph index, optional kretprobe cursor, source flags, and temporary userspace frame copies. It persists no data beyond emitted stack entries.

### Integration Points
Consumers include oops reporting, lockdep/perf/BPF stack capture, scheduler diagnostics, ftrace, kprobes, EFI and SDEI paths, and generic stacktrace APIs. It relies on frame-pointer ABI and ARM64 `stack_info` helpers.

### Risks
Malformed frame records, missing frame pointers, exception boundaries, fgraph/kretprobe trampolines, PAC, inaccessible per-CPU stacks, and concurrent blocked-task execution can make unwinds incomplete or unreliable. User unwinding is best-effort and can fault or stop on nonmonotonic frame chains.

### Test Signals
Validate normal oops traces, reliable livepatch-style checks, BPF stack collection, ftrace graph and kretprobe stacks, EFI/SDEI/NMI stack paths, pointer-auth builds, compat user stacks, and blocked task stack dumps.
