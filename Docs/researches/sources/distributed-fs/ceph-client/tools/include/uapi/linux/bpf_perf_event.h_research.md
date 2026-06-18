# sources/distributed-fs/ceph-client/tools/include/uapi/linux/bpf_perf_event.h

Purpose: defines the perf-event context structure exposed to BPF programs/userspace tooling for perf event attachments. It is a minimal wrapper around architecture-specific register state plus event sample metadata.

Important APIs/types: `struct bpf_perf_event_data` contains `bpf_user_pt_regs_t regs`, `__u64 sample_period`, and `__u64 addr`. `regs` is imported from `<asm/bpf_perf_event.h>`, so its concrete layout is architecture-specific.

Control flow, state, and persistence: the header has no executable control flow. The runtime flow is kernel perf infrastructure populating the structure before invoking a BPF program or exposing metadata through helper-facing ABI. The structure is transient per event and does not describe persistent storage.

Dependencies and integration points: depends on the architecture UAPI header for register layout. It integrates perf events, BPF program contexts, and tracing tools that inspect sampled instruction/address data. The type is consumed by libbpf-like tooling and BPF C programs through generated or copied UAPI headers.

Risks and test signals: the main risk is arch layout mismatch or assuming register fields are portable. Tests should compile BPF perf-event programs on target architectures, validate sample period/address population, and verify CO-RE or generated bindings do not hard-code an incompatible `regs` shape.
