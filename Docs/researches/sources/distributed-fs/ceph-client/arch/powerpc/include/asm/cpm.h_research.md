## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpm.h

Purpose: PowerPC compatibility include for Freescale Communication Processor Module definitions.

Important APIs/types/functions: re-exports `<soc/fsl/cpm.h>` without adding local declarations.

Control flow: include forwarding only.

State and persistence: no state; all CPM state contracts are in the SoC header and the CPM1/CPM2 architecture headers.

Dependencies and integration: lets older PowerPC code include `asm/cpm.h` while sharing the common Freescale SoC CPM definitions. Used by CPM serial, Ethernet, GPIO, and board support code.

Risks and test signals: risk is include-path drift or incompatible SoC header changes. Test signals are CPM1/CPM2 platform builds and drivers that include `asm/cpm.h`.
