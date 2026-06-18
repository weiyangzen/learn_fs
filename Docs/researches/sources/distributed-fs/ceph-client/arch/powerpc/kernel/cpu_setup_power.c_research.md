<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_power.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_power.c

Purpose: C implementation of low-level setup/restore for POWER7, POWER8, POWER9, and POWER10 Book3S 64-bit CPUs.

Important APIs/types/functions: Helpers `init_hvmode_206`, `init_LPCR_ISA300`, `init_LPCR_ISA206`, `init_FSCR*`, `init_HFSCR`, `init_PMU*`, `init_DEXCR`, and setup/restore entry points `__setup_cpu_power7/8/9/10` plus matching restore functions.

Control flow: Setup initializes user-visible facility control, PMU registers, DEXCR/hash key state for POWER10, then if HV mode is available resets LPID/PID/AMOR/PCR/PSSCR as appropriate, programs LPCR for the ISA generation, enables HFSCR facilities, and resets HV PMU controls. Non-HV setup clears HV-related CPU feature bits.

State and persistence: Mutates FSCR, HFSCR, LPCR, LPID, PID, AMOR, PCR, PSSCR, MMCR/MMCRA/MMCRS/MMCRH/MMCRC/MMCR3, DEXCR, HASHKEYR, and CPU feature flags.

Dependencies and integration points: Depends on SPR definitions, sync helpers, CPU spec feature flags, Book3S HV mode, PMU/TM/DEXCR architecture features, and CPU setup dispatch from cputable.

Risks: Feature exposure and SPR initialization must match CPU generation. Running HV-only programming outside HV mode is avoided; mistakes can break guests, PMU, TM, or security controls.

Test signals: POWER7-POWER10 boot and secondary CPU bring-up, KVM HV guest tests, PMU/perf tests, facility availability tests for SCV/prefix/DEXCR, and suspend/restore smoke tests.

Source read size: 288 lines, 5551 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_power.c -->
