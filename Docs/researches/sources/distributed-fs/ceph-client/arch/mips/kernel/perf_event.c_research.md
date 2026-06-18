<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/perf_event.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/perf_event.c

### Purpose
`perf_event.c` provides MIPS perf kernel callchain collection. It records kernel return addresses either by stack scanning or by symbolic unwinding, while leaving userspace callchains empty.

### Important APIs, Types, And Functions
The visible architecture hook is `perf_callchain_kernel(struct perf_callchain_entry_ctx *entry, struct pt_regs *regs)`. The helper `save_raw_perf_callchain()` scans words from a stack pointer and stores values that are kernel text addresses.

### Control Flow
`perf_callchain_kernel()` starts with register SP from `regs->regs[29]`. With kallsyms support, it uses raw stack scanning if `raw_show_trace` is set or the current PC is not a kernel text address; otherwise it repeatedly stores the current PC and calls `unwind_stack()` until unwinding returns zero or the callchain is full. Without kallsyms it always performs raw stack scanning after validating stack bounds in the caller path.

### State, Persistence, And Dependencies
The function only appends to the supplied perf callchain entry. It reads the current task stack, `pt_regs`, and optional unwind state. Dependencies include perf event core, task stack helpers, `__kernel_text_address()`, and MIPS stacktrace unwinder.

### Integration Points
The code is called by perf sampling when kernel callchains are requested on MIPS. It integrates with stack unwinding, kallsyms/raw trace configuration, and perf's bounded callchain buffer.

### Risks
Raw stack scanning can include false positives from any stack word that looks like a kernel text address. Unwinding depends on reliable frame/return-address conventions. Userspace callchains are intentionally absent, limiting profiling completeness.

### Test Signals
Run `perf record -g` on kernel workloads, compare raw versus unwind callchains, test truncated callchain limits, validate behavior with kallsyms disabled, and verify no out-of-stack reads when SP is near thread stack bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/perf_event.c -->
