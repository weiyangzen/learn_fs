# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates.c

### Purpose
ABB Socrates 85xx board support. It initializes MPIC, adds a Socrates FPGA PIC cascade, initializes SMP/PCI, and publishes common devices.

### Important APIs, Types, And Functions
Functions are `socrates_pic_init()`, `socrates_setup_arch()`, and `define_machine(socrates)` with compatible `abb,socrates`. It finds `abb,socrates-fpga-pic` and calls `socrates_fpga_pic_init()`. Setup calls `mpc85xx_smp_init()` and `fsl_pci_assign_primary()`.

### Control Flow
PIC init allocates MPIC and initializes it before finding and registering the FPGA interrupt controller. Setup runs standard SMP/PCI board initialization. Common devices are published by machine arch initcall.

### State, Persistence, And Dependencies
State includes MPIC domain, FPGA PIC domain/cascade, SMP ops, PCI host assignment, and OF platform devices. No persistent storage is touched. Dependencies include Socrates FPGA PIC code, OF matching, MPIC, and FSL PCI.

### Integration Points
Connects the board's FPGA interrupt controller to Linux IRQ handling and standard 85xx platform infrastructure.

### Risks
Cascade ordering matters: MPIC must be ready before FPGA PIC setup. Missing compatible nodes should not block core board boot except for dependent devices.

### Test Signals
Boot Socrates DTB, verify FPGA interrupt sources, MPIC interrupts, PCI, SMP, and common platform-device probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates.c -->
