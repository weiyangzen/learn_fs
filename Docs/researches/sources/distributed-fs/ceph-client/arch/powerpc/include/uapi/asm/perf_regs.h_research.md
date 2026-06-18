<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/perf_regs.h

Purpose: Enumerates PowerPC register IDs and masks for perf sample register capture.

Important APIs/types/functions: `enum perf_event_powerpc_regs`, `PERF_REG_PMU_MASK`, `PERF_REG_PMU_MASK_300`, and `PERF_REG_PMU_MASK_31`.

Control flow: Userspace perf requests sample_regs masks; kernel validates and captures GPRs, special registers, and PMU SPRs depending on CPU generation.

State and persistence: No state owned; masks describe per-sample register payload state.

Dependencies and integration points: Integrated with perf core, PowerPC PMU code, perf tools, and CPU feature gating for ISA 3.0/3.1.

Risks: Enum order is ABI. Masks must match actually readable registers or perf samples become invalid or fault-prone.

Test signals: perf sample_regs tests, POWER9/POWER10 PMU register capture, and perf tool decoding checks.

Source read size: 95 lines, 2763 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/perf_regs.h -->
