# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/twr_p102x.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/twr_p102x.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/twr_p102x.c

### Purpose
P102x Tower board support. It provides shared initialization for Tower P1020/P1021-style boards, including MPIC, SMP, PCI, and common device publishing.

### Important APIs, Types, And Functions
Key functions include `twr_p102x_pic_init()`, `twr_p102x_setup_arch()`, probe or machine descriptors for Tower-compatible strings, and initcall linkage to `mpc85xx_common_publish_devices()`. It uses `mpc85xx_smp_init()`, `fsl_pci_assign_primary()`, PCI fixups, and `mpic_get_irq`.

### Control Flow
Machine matching selects the Tower board descriptor. Setup performs standard 85xx initialization and board logging. PIC init allocates MPIC, and the arch initcall publishes common platform devices.

### State, Persistence, And Dependencies
Runtime state includes MPIC, SMP ops, PCI host assignment, and OF platform devices. No persistent storage. Dependencies include OF compatible matching, MPIC, FSL PCI, and common 85xx helpers.

### Integration Points
Provides the machine layer between Tower DTBs and generic Linux platform/PCI/interrupt drivers.

### Risks
Shared board support must preserve all compatible variants. MPIC and PCI configuration are boot-critical.

### Test Signals
Boot Tower P102x DTBs, verify machine selection, interrupt delivery, PCI enumeration, SMP, and common device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/twr_p102x.c -->
