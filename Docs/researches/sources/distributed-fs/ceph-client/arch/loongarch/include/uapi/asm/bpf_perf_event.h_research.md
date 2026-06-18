<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/bpf_perf_event.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/bpf_perf_event.h

Purpose: defines the register type BPF programs see for LoongArch perf events.
Important APIs and types: typedefs `bpf_user_pt_regs_t` to `struct user_pt_regs`.
Control flow: BPF helper/verifier paths use this type when exposing perf-event register context to programs.
State and persistence: no state; this is UAPI type binding.
Dependencies and integration: depends on UAPI `ptrace.h`, perf events, eBPF tracing, and libbpf-generated skeletons.
Risks and test signals: wrong context type breaks BPF programs reading registers. Signals include BPF selftests for kprobe/perf-event contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/bpf_perf_event.h -->
