# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/reg_fsl_emb.h

Purpose: This header defines Freescale Embedded Performance Monitor register accessors and PMR numbers/bitfields for BookE embedded performance monitoring.

Important APIs/types/functions: In C builds, `mfpmr(unsigned int rn)` and `mtpmr(unsigned int rn, unsigned int val)` emit e300 `mfpmr`/`mtpmr` instructions inside `.machine` push/pop blocks. PMR definitions cover counters `PMRN_PMC0` through `PMRN_PMC5`, local control A/B registers, global control, user counters and user local controls. Bitfields include `PMLCA_FC`, supervisor/user/PMM freeze bits, condition enable, guest/hypervisor freeze bits, event mask/shift, threshold fields, and `PMGC0_FAC`, `PMGC0_PMIE`, `PMGC0_FCECE`.

Control flow: Embedded perf code reads and writes PMRs through the inline helpers, programs event selection in PMLCA, thresholds in PMLCB, and global freeze/interrupt behavior in PMGC0, then reads counters from privileged or user PMR ranges as allowed.

State and persistence: PMR state persists in the processor performance monitor facility: counters, event selectors, freeze controls, threshold controls, interrupt enable, and user-visible PMU registers.

Dependencies and integration points: It depends on stringification and assembler support for e300 machine mode. It is included by `reg.h` only under `CONFIG_FSL_EMB_PERFMON`, integrating Freescale embedded PMU support with perf and low-level PMU code.

Risks and test signals: The inline `mtpmr` constraint should be checked carefully because the asm names an output-like operand for a write-only operation. PMR numbers and event masks are hardware ABI. Tests include FSL embedded perf build coverage, counter start/stop/read, event selection, PMU interrupts, user counter access policy, and objdump checks for `mfpmr`/`mtpmr` emission.
