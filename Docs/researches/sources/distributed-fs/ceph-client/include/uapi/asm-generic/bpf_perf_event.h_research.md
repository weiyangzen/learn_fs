# sources/distributed-fs/ceph-client/include/uapi/asm-generic/bpf_perf_event.h

Purpose: Exposes the architecture pt_regs type used by BPF perf-event programs.

Important APIs/types/functions: Includes `linux/ptrace.h` and typedefs `struct pt_regs` to `bpf_user_pt_regs_t`.

Control flow: Header inclusion gives user BPF programs a stable alias for perf-event register context.

State/persistence: No runtime state.

Dependencies/integration: Used by libbpf/BPF programs and architecture UAPI ptrace definitions.

Risks: The alias must match actual perf-event register context; incompatible pt_regs exposure breaks BPF program compilation or register reads.

Test signals: Compile BPF perf-event samples against installed headers for architectures using asm-generic fallback.
