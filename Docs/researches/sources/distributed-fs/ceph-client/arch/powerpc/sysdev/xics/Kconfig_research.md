<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/Kconfig

Purpose: Defines internal Kconfig symbols for the legacy XICS interrupt controller stack.

Important APIs/types/functions: Symbols are `PPC_XICS`, `PPC_ICP_NATIVE`, `PPC_ICP_HV`, `PPC_ICS_RTAS`, and `PPC_ICS_NATIVE`. `PPC_XICS` selects `PPC_SMP_MUXED_IPI` and `HARDIRQS_SW_RESEND`.

Control flow: No runtime behavior; platform Kconfig selects the relevant ICP/ICS backends.

State and persistence: No state.

Dependencies and integration points: Controls compilation of `xics-common.o`, ICP backends, and ICS backends through the sibling Makefile.

Risks: These are `def_bool n` internal symbols; missing platform selects produce no XICS implementation even if the hardware exists.

Test signals: Build coverage for pseries/PowerNV native, hypervisor, RTAS, and native source-controller combinations.

Source read size: 17 lines, 250 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/Kconfig -->
