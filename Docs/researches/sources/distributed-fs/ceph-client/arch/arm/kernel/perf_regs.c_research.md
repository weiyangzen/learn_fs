# sources/distributed-fs/ceph-client/arch/arm/kernel/perf_regs.c

Purpose: maps ARM `pt_regs` to perf register sampling ABI and validates requested register masks.

Important APIs/types/functions: `perf_reg_value`, `perf_reg_validate`, and `perf_reg_abi`. The code indexes ARM general registers and CPSR according to perf's architecture register IDs.

Control flow: validation checks mask bits fit within supported registers. Sampling returns requested register values from `pt_regs`; ABI reports 32-bit ABI.

State and persistence: stateless.

Dependencies and integration: used by perf sampling, BPF/perf register consumers, and user ABI definitions.

Risks: incorrect mapping breaks profiling/debug tooling; masks must reject unsupported IDs. Test signals include perf register sampling tests and comparing sampled register dumps with ptrace/core dumps.
