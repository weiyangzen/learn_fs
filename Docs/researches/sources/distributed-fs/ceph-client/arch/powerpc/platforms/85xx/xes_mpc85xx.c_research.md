# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/xes_mpc85xx.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/xes_mpc85xx.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/xes_mpc85xx.c

### Purpose
X-ES MPC85xx board family support. It covers several X-ES board variants with common MPIC/SMP/PCI setup, board-specific compatible matching, and CPU info.

### Important APIs, Types, And Functions
Important functions are `xes_mpc85xx_pic_init()`, `xes_mpc85xx_setup_arch()`, board probe/matching helpers, CPU info display, and one or more `define_machine()` descriptors for X-ES compatibles. It uses MPIC, `mpc85xx_smp_init()`, `fsl_pci_assign_primary()`, PCI fixups, and common platform-device publication.

### Control Flow
Compatible matching selects the X-ES machine descriptor. Setup emits progress, initializes SMP and PCI, and logs board information. PIC setup allocates MPIC, and common devices are published through initcall.

### State, Persistence, And Dependencies
State includes MPIC, SMP ops, PCI configuration, OF platform devices, and CPU info output. No durable state. Dependencies include OF, MPIC, FSL PCI, seq_file, and common 85xx code.

### Integration Points
Allows multiple X-ES hardware designs to share standard 85xx driver binding and interrupt/PCI infrastructure.

### Risks
Family-wide matching may miss board-specific quirks. CPU info and compatible lists must remain aligned with DTS files.

### Test Signals
Boot supported X-ES DTBs, verify compatible matching, interrupts, PCI, SMP, common devices, and CPU info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/xes_mpc85xx.c -->
