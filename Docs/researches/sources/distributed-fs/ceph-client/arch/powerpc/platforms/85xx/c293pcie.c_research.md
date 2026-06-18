# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/c293pcie.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/c293pcie.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/c293pcie.c

### Purpose
Freescale C293 PCIe board support for the 85xx Book-E platform. It wires the C293PCIE device-tree compatible into the PowerPC machine table and supplies the minimal architecture, interrupt, PCI, SMP, and device publication hooks required for boot.

### Important APIs, Types, And Functions
Key entry points are `c293_pcie_pic_init()`, `c293_pcie_setup_arch()`, `machine_arch_initcall(c293_pcie, mpc85xx_common_publish_devices)`, and `define_machine(c293_pcie)`. The machine uses compatible string `fsl,C293PCIE`, MPIC big-endian single-destination interrupt setup, `mpc85xx_smp_init()`, `fsl_pci_assign_primary()`, and the generic `mpic_get_irq` path.

### Control Flow
During platform selection, `define_machine` matches the root compatible. Setup emits progress, initializes 85xx SMP, assigns the primary PCI host bridge, and logs the board name. Later the machine initcall publishes common OF platform devices.

### State, Persistence, And Dependencies
State is firmware/device-tree supplied and kernel-global through `smp_ops`, MPIC state, and PCI host bridge setup. There is no durable persistence. It depends on OF matching, MPIC, FSL PCI helpers, and common 85xx publication.

### Integration Points
Integrates with Linux PowerPC `ppc_md`, FSL Book-E interrupt setup, PCI bridge code, and drivers bound through `mpc85xx_common_publish_devices()`.

### Risks
The file is small, but compatible-string mismatch, wrong MPIC flags, or skipped PCI/SMP calls would prevent boot, interrupts, or PCI enumeration.

### Test Signals
Boot a C293PCIE DTB, verify machine selection, MPIC interrupts, secondary CPU bring-up when configured, PCI enumeration, and OF platform device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/c293pcie.c -->
