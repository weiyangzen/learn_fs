<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_pci.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_pci.h

Purpose: Freescale PCI/PCIe register layout and exported helper declarations.

Important APIs/types/functions: register constants for BRR1, LTSSM, class-code CSR, inbound/outbound window attributes, PME bits, structures `pci_outbound_window_regs`, `pci_inbound_window_regs`, and large `ccsr_pci`, plus declarations for bus/PHB fixups, `mpc83xx_add_bridge()`, `fsl_pci_immrbar_base()`, `fsl_pci_primary`, `fsl_pci_assign_primary()`, and `fsl_pci_mcheck_exception()`.

Control flow: no runtime logic except config-dependent inline stubs for primary assignment and machine-check handling when PCI/FSL PCI is disabled.

State and persistence: describes the memory-mapped controller state used by `fsl_pci.c`, including config, outbound/inbound ATMUs, error capture, debug, CSR, and PME registers.

Dependencies and integration points: included by Freescale PCI/MSI/EDAC-related code and depends on kernel-only build context plus `struct pci_bus`, `pci_controller`, and `pt_regs` declarations from included headers.

Risks: structure padding and offsets must match hardware. Incorrect masks or bit definitions can program invalid ATMU or PME state.

Test signals: compile-time offset-sensitive users, successful PCI bridge setup, ATMU programming, and PME operations validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_pci.h -->
