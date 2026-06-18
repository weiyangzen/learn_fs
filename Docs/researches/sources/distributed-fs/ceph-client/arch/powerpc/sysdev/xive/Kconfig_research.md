<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/Kconfig

Purpose: Defines build symbols for the newer PowerPC XIVE interrupt controller stack.

Important APIs/types/functions: Symbols are `PPC_XIVE`, `PPC_XIVE_NATIVE`, and `PPC_XIVE_SPAPR`. `PPC_XIVE` selects muxed SMP IPIs and software hardirq resend; native depends on PowerNV; native and sPAPR select common XIVE.

Control flow: No runtime behavior; symbols control compilation of XIVE common/native/sPAPR objects.

State and persistence: No state.

Dependencies and integration points: Used by the xive Makefile and platform Kconfig for PowerNV and pseries XIVE support.

Risks: Missing selection omits interrupt-controller support. The native dependency on `PPC_POWERNV` must stay aligned with platform firmware capabilities.

Test signals: Build coverage for PowerNV native XIVE, sPAPR XIVE, and disabled XIVE configurations.

Source read size: 14 lines, 227 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/Kconfig -->
