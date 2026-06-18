<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/stacktrace.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/stacktrace.c

## Purpose
`stacktrace.c` prepares nVHE stacktrace information for host-side panic reporting. In non-protected mode it records stack bounds and starting FP/PC; in protected mode with `CONFIG_PKVM_STACKTRACE` it unwinds inside hyp into a shared per-CPU buffer.

## Important APIs, Types, and Functions
`overflow_stack` provides the per-CPU overflow stack used by assembly vectors. `kvm_stacktrace_info` stores non-protected reporting metadata. `hyp_prepare_backtrace()` records normal and overflow stack bases plus FP/PC. With protected stacktrace enabled, `pkvm_stacktrace` is the per-CPU output buffer, `stackinfo_get_overflow()` and `stackinfo_get_hyp()` define unwindable ranges, `pkvm_save_backtrace_entry()` stores PCs with a zero delimiter, and `pkvm_save_backtrace()` runs the nVHE unwinder. `kvm_nvhe_prepare_backtrace()` selects protected or non-protected behavior.

## Control Flow, State, and Persistence
The file writes per-CPU panic-report state only when a panic path calls `kvm_nvhe_prepare_backtrace()`. Protected mode avoids exposing live stack memory by copying PC entries into a bounded buffer. Non-protected mode leaves enough metadata for the host to unwind directly.

## Dependencies and Integration Points
It integrates with `host.S` overflow-stack vectors, `switch.c` panic handling, per-CPU init params, protected mode status, and optional `asm/stacktrace/nvhe.h` unwinding support.

## Risks and Test Signals
Risks include truncated protected traces, bad stack bounds after stack allocation changes, recursion or faults during panic unwinding, and exposing too much stack state outside protected mode. Test signals are induced hyp panic on normal and overflow stacks, protected and non-protected stacktrace dumps, bounded buffer delimiter correctness, and frame-pointer unwind validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/stacktrace.c -->
