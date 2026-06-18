<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/perf_regs.h

Purpose: enumerates LoongArch register IDs exposed in perf sample register masks.
Important APIs and types: defines `enum perf_event_loongarch_regs` for GPRs, original argument, PC, BADVADDR, and max register count.
Control flow: perf records selected register values in samples; userspace perf tooling decodes by these enum IDs.
State and persistence: enum ordering is perf UAPI.
Dependencies and integration: tied to `pt_regs`, perf callchain/sampling, BPF perf-event contexts, and tooling decoders.
Risks and test signals: enum drift breaks perf data interpretation. Signals include perf record/report with register sampling and BPF perf tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/perf_regs.h -->
