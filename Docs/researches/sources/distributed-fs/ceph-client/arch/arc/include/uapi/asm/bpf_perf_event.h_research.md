# sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/bpf_perf_event.h

BPF perf event register ABI glue for ARC. It includes asm/ptrace.h and aliases bpf_user_pt_regs_t to user_regs_struct. Control flow is BPF/perf tooling using this type to interpret sampled user registers. State is ABI layout from uapi ptrace.h. Dependencies are stable user_regs_struct fields. Risks are BPF programs assuming pt_regs-like fields that ARC intentionally decouples. Test signals are BPF perf event programs, libbpf register access, and headers_install.
