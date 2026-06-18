<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/reg.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/reg.h

Purpose: defines numeric offsets for LoongArch ELF/core general register sets.
Important APIs and types: `LOONGARCH_EF_R0` through `LOONGARCH_EF_R31`, `LOONGARCH_EF_ORIG_A0`, CSR ERA/BADV/CRMD/PRMD/EUEN/ECFG/ESTAT indexes, and `LOONGARCH_EF_SIZE`.
Control flow: core dump, ptrace, and debugger code use indexes to map saved register arrays.
State and persistence: register numbering and size are ABI for ELF notes and tooling.
Dependencies and integration: tied to UAPI ptrace, GDB, perf, core dump generation, and signal/debug register conventions.
Risks and test signals: index drift corrupts debugger/core register display. Signals include core dump inspection, GDB, ptrace tests, and perf register sampling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/reg.h -->
