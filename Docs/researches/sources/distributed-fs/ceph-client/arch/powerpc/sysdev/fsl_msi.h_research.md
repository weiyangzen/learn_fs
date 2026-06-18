<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_msi.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_msi.h

Purpose: private Freescale MSI controller definitions shared by the MSI implementation.

Important APIs/types/functions: constants for MSIIR/MSIIR1 register counts, interrupts per MSIR, maximum hwirqs, PIC type feature bits, endian erratum flag, forward `fsl_msi_cascade_data`, and `struct fsl_msi`.

Control flow: no executable logic. The constants define hwirq geometry and feature decoding used by `fsl_msi.c`.

State and persistence: `struct fsl_msi` models one MSI controller's persistent runtime state: irqdomain, cascade IRQ, MSIIR offset/bit shifts, MMIO registers, feature flags, cascade data array, bitmap allocator, global list node, and OF phandle.

Dependencies and integration points: depends on OF phandles and the PowerPC `msi_bitmap` allocator. Used by Freescale PCI/MSI code.

Risks: changing register counts or bit shifts without matching hardware support can make hwirq composition collide or exceed bitmap size. The maximum is based on MSIIR1 geometry and must cover all supported variants.

Test signals: compile coverage and runtime MSI allocation across MPIC, IPIC, and v4.3 MSIIR1-compatible controllers validate the definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_msi.h -->
