<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/perf_regs.h

Purpose: Defines perf register numbers for RISC-V sampled register dumps.

Important APIs/types/functions: Enumerates `PERF_REG_RISCV_*` GPR indices and `PERF_REG_RISCV_MAX`.

Control flow: Perf encodes sampled registers using these indices; userspace decodes samples accordingly.

State and persistence: Perf sample ABI state.

Dependencies and integration points: Used by perf, eBPF stack/register sampling, and unwind tooling.

Risks: Index changes break perf.data compatibility and tooling.

Test signals: perf record/report register sampling, BPF perf_event tests, and headers ABI checks.

Source read size: 42 lines, 920 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/perf_regs.h -->
