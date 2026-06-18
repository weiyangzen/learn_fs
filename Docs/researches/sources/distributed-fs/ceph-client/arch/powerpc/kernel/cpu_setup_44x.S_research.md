<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_44x.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_44x.S

Purpose: Provides low-level setup routines and errata workarounds for 44x-class PowerPC CPUs.

Important APIs/types/functions: `__setup_cpu_440ep`, `__setup_cpu_440epx`, `__setup_cpu_440grx`, `__setup_cpu_460ex/gt/sx`, `__setup_cpu_apm821xx`, `__setup_cpu_440x5/440gx/440spe`, `__init_fpu_44x()`, and `__plb_disable_wrp()`.

Control flow: CPU-specific setup branches call FPU APU enablement, PLB write-pipelining disablement, and 440A machine-check fixup helpers as required, preserving LR around multi-call sequences.

State and persistence: Mutates CCR0 to enable FPU access and PLB DCR `DCRN_PLB4A0_ACR` to disable write pipelining. Other machine-check fixup state is handled externally.

Dependencies and integration points: Depends on 44x SPR/DCR definitions, CPU spec setup dispatch, and external `__fixup_440A_mcheck`.

Risks: These routines run during early CPU initialization. Incorrect DCR/CCR writes can break memory writes or FPU access; errata workarounds are CPU-revision-specific.

Test signals: 44x/460/APM821xx boot tests, FPU availability tests, memory stress for PLB write erratum, and config build coverage.

Source read size: 69 lines, 1459 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_44x.S -->
