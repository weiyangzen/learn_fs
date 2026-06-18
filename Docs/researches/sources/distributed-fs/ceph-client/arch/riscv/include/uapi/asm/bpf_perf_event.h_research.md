<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/bpf_perf_event.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/bpf_perf_event.h

Purpose: Provides RISC-V BPF perf event UAPI register mapping.

Important APIs/types/functions: Includes generic BPF perf event definitions or architecture register access definitions.

Control flow: BPF/perf tooling uses the definitions to read sampled register state.

State and persistence: No persistent state in the header.

Dependencies and integration points: Used by eBPF helpers, perf events, and tracing tools.

Risks: Register-index mismatch breaks BPF programs that inspect perf contexts.

Test signals: BPF selftests, perf trace tests, and headers_install.

Source read size: 9 lines, 261 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/bpf_perf_event.h -->
