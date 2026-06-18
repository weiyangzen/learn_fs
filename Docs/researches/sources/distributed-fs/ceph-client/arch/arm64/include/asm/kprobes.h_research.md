# sources/distributed-fs/ceph-client/arch/arm64/include/asm/kprobes.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kprobes.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kprobes.h

### Purpose
`kprobes.h` declares ARM64 kprobe and kretprobe control state, trampoline hooks, and breakpoint handlers used for dynamic kernel instrumentation.

### Important APIs, Types, And Functions
Key items are `__ARCH_WANT_KPROBES_INSN_SLOT`, `MAX_INSN_SIZE`, `flush_insn_slot()`, `kretprobe_blacklist_size`, `struct prev_kprobe`, `struct kprobe_ctlblk`, `arch_remove_kprobe()`, `kprobe_fault_handler()`, `__kretprobe_trampoline()`, `trampoline_probe_handler()`, and BRK handlers for kprobe, single-step, and kretprobe.

### Control Flow
Kprobe insertion copies/patches probed instructions and routes BRK exceptions to architecture handlers. Return probes use the trampoline path to recover saved return state. Fault handling decides whether an exception belongs to an active probe.

### State, Persistence, And Dependencies
Per-CPU probe state lives in `struct kprobe_ctlblk`, including current and previous probes. It depends on generic kprobes, `pt_regs`, `percpu`, and `asm/probes.h`.

### Integration Points
Tracing, perf, ftrace-like diagnostics, and live debugging tools depend on these hooks. Ceph client functions can be instrumented through this architecture layer.

### Risks
Instruction-slot sizing, exception recursion, and return-address restoration are high risk. Probing code that is not kprobe-safe can deadlock or corrupt context.

### Test Signals
Run kprobe/kretprobe selftests on ARM64; probe normal and faulting paths; verify blacklisted/trampoline behavior and nested probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kprobes.h -->
