# sources/distributed-fs/ceph-client/arch/parisc/kernel/perf_asm.S

Purpose: provides the low-level PA-RISC assembly primitives used by `perf.c` to enable/disable performance counters and shift data into or out of remote diagnose registers on PCX-U and PCX-W style CPUs.

Important entry points are `perf_intrigue_enable_perf_counters`, `perf_intrigue_disable_perf_counters`, `perf_rdr_shift_in_W`, `perf_rdr_shift_out_W`, `perf_rdr_shift_in_U`, and `perf_rdr_shift_out_U`. Macros encode privileged diagnostic instructions: `MTDIAG_1`, `MTDIAG_2`, `MFDIAG_1`, `MFDIAG_2`, `STDIAG`, `SFDIAG`, plus the `DR2_SLOW_RET` bit required by errata/ERS before shifting remote diagnose registers.

Control flow for counter enable/disable temporarily sets the performance-coprocessor bit in `ccr`, issues `pmenb` or `pmdis`, synchronizes, then restores the coprocessor bit with required nops. RDR shift routines set `DR2_SLOW_RET`, branch through a table of fixed eight-instruction sequences based on RDR number, use `SFDIAG`/`MFDIAG` to read through staging register 28 or `MTDIAG`/`STDIAG` to write through staging register 25, and restore DR2 on return. Several short RDRs are shifted back after reads to preserve machine state; unsupported holes branch directly to the return path.

State is entirely CPU diagnostic register and performance-counter hardware state. It depends on the PA-RISC calling convention, privileged diagnostic opcodes encoded as words, cacheline-aligned sequence layout, and `perf.c` passing valid RDR numbers and widths from its tables.

Risks are high because these routines run privileged CPU-specific sequences with exact instruction ordering, branch-table sizing, and staging-register side effects. Wrong widths or RDR tables can leave diagnostic registers shifted, and unsupported CPUs can fault or hang. Test signals are limited to supported PA-RISC hardware: enabling/disabling counters, reading and writing all RDRs used by the image lists, repeated `PA_PERF_ON/OFF`, and absence of machine checks or corrupted PDC/diagnostic state.
