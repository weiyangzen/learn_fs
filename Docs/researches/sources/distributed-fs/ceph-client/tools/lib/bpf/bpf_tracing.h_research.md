<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_tracing.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_tracing.h

## Purpose
`bpf_tracing.h` provides architecture-aware tracing convenience macros for BPF programs. It maps `struct pt_regs` register layouts to portable argument accessors and supplies wrappers for fentry/fexit, kprobe, kretprobe, syscall kprobe, uprobe, and uretprobe program signatures.

## Important APIs, types, and functions
The header detects target architecture through `__TARGET_ARCH_*` or compiler macros, defines per-architecture register names for normal calls, syscalls, return value, frame pointer, stack pointer, and instruction pointer, then exposes `PT_REGS_PARMn()`, `PT_REGS_PARMn_CORE()`, `PT_REGS_PARMn_SYSCALL()`, `PT_REGS_SYSCALL_REGS()`, `BPF_KPROBE_READ_RET_IP()`, and `BPF_KRETPROBE_READ_RET_IP()`. Program wrappers include `BPF_PROG`, `BPF_PROG2`, `BPF_KPROBE`, `BPF_KRETPROBE`, `BPF_KSYSCALL`, `BPF_KPROBE_SYSCALL`, `BPF_UPROBE`, and `BPF_URETPROBE`.

## Control flow
At compile time, the preprocessor selects one target mapping or emits pragma errors through placeholder accessors when no target is known. Wrapper macros generate a public BPF program function with raw context and a static inline implementation with typed arguments. `BPF_KSYSCALL` uses a `__kconfig` extern `LINUX_HAS_SYSCALL_WRAPPER` at runtime to decide how to interpret syscall pt_regs.

## State and persistence behavior
There is no mutable state in the header. It affects compiled BPF program prototypes, BTF, CO-RE relocations, and generated code. `LINUX_HAS_SYSCALL_WRAPPER` is resolved by libbpf as virtual kconfig data.

## Dependencies and integration points
It includes `bpf_helpers.h` and uses `BPF_CORE_READ()` from `bpf_core_read.h` paths via included helpers. It depends on architecture pt_regs definitions from `vmlinux.h` or UAPI/user-reg structs and is central to libbpf-style tracing programs.

## Risks and edge cases
Wrong or missing `__TARGET_ARCH_*` produces invalid register access or compile-time pragma errors. Some syscall ABI quirks are explicitly not hidden, including old mmap, clone backwards variants, socketcall, and compat syscalls. Frame-pointer based return-IP reading depends on architecture and kernel config.

## Test signals
BPF tracing selftests should compile for every supported architecture mapping, verify kprobe/uprobe/fentry wrappers pass typed arguments correctly, exercise `BPF_PROG2` struct arguments, validate syscall wrapper and non-wrapper kernels, and inspect CO-RE pt_regs reads for architectures using user-reg casts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_tracing.h -->
