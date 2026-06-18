
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bpf_perf_event.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/bpf_perf_event.h

## Purpose
Defines the UAPI context passed to BPF programs attached to perf events. It provides the common wrapper around architecture-specific register state and sample-period data.

## APIs, Control Flow, and State
The header includes `<asm/bpf_perf_event.h>` for the architecture-defined `bpf_user_pt_regs_t` and declares `struct bpf_perf_event_data` with `regs` and `sample_period`. There are no functions or control branches; the structure is populated by perf/BPF attachment paths and consumed by BPF programs and loaders that know the target architecture's register layout. No persistence is owned by the header.

## Dependencies, Integration, Risks, and Tests
The main dependency is the arch UAPI perf-event register definition. Integration points are `BPF_PROG_TYPE_PERF_EVENT`, perf sampling, tracing/profiling programs, and libbpf skeletons that expose the context type. Risks include architecture register-layout mismatches, user programs assuming portable register fields where the layout is arch-specific, and sample-period interpretation errors for different perf event modes. Test signals include building BPF perf-event programs on each supported architecture, perf sample-period validation, and verifier tests that access `ctx->regs` and `ctx->sample_period`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bpf_perf_event.h -->
