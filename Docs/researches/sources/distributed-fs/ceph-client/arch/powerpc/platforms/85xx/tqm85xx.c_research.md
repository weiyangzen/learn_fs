# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/tqm85xx.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/tqm85xx.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/tqm85xx.c

### Purpose
TQ Components TQM85xx board support. It handles MPIC, CPM2/QE I/O where configured, PCI/SMP setup, CPU info, and common platform-device publication.

### Important APIs, Types, And Functions
Key functions are `tqm85xx_pic_init()`, `tqm85xx_setup_arch()`, `tqm85xx_show_cpuinfo()`, and `define_machine(tqm85xx)` with TQM85xx-compatible matching. The setup path uses common 85xx helpers, optional CPM2/QE initialization from `mpc85xx.h`, `mpc85xx_smp_init()`, and `fsl_pci_assign_primary()`.

### Control Flow
Machine selection leads to board setup, optional communication-processor pin/IRQ initialization, SMP setup, PCI primary selection, and logging. Device publication occurs through the common 85xx init path.

### State, Persistence, And Dependencies
State is hardware register and kernel platform state for MPIC, communication processor, PCI, SMP, and OF devices. No durable persistence. Dependencies include OF, MPIC, CPM2/QE conditionals, FSL PCI, and seq_file.

### Integration Points
Bridges TQM85xx board quirks with generic 85xx communication, PCI, and platform-driver subsystems.

### Risks
Optional CPM/QE code is configuration-sensitive. Mux and IRQ setup errors can break serial/Ethernet hardware.

### Test Signals
Build with and without CPM2/QE, boot TQM85xx DTB, validate interrupts, PCI, serial/Ethernet, and CPU info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/tqm85xx.c -->
