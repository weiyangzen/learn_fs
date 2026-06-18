<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp.h

Purpose: local compatibility include for PXA MFP definitions.

Important APIs/types: simply includes `linux/soc/pxa/mfp.h` under the legacy architecture include guard.

Control flow and integration: source files expecting the historical mach-level `mfp.h` can include this and receive the common SoC MFP definitions.

State and persistence: none.

Dependencies: depends entirely on `linux/soc/pxa/mfp.h`.

Risks and test signals: low risk; compile coverage verifies include path compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp.h -->
