# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/ge_imp3a.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/ge_imp3a.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/ge_imp3a.c

### Purpose
GE Intelligent Platforms IMP3A board support. It provides MPIC setup, optional FPGA cascaded interrupt setup, primary PCI host selection, FPGA register mapping, CPU information, and machine registration.

### Important APIs, Types, And Functions
Key functions are `ge_imp3a_pic_init()`, `ge_imp3a_pci_assign_primary()`, `ge_imp3a_setup_arch()`, `ge_imp3a_show_cpuinfo()`, and `define_machine(ge_imp3a)`. It uses compatible `ge,IMP3A`, GE FPGA PIC compatibles, `fsl,mpc8540-pci`, `fsl,mpc8548-pcie`, `fsl,p2020-pcie`, and `ge,imp3a-fpga-regs`.

### Control Flow
PIC init skips secondary thread behavior for CAMP variants, allocates MPIC, initializes it, then finds and initializes the GE FPGA PIC cascade if present. Setup initializes SMP, maps FPGA registers for board information, and assigns primary PCI based on discovered bridge ranges.

### State, Persistence, And Dependencies
State includes global mapped FPGA registers, MPIC and cascaded GE PIC domains, and PCI controller selection. No durable persistence exists. Dependencies include OF resource parsing, `gef_pic_init()`, MPIC, FSL PCI, and seq_file CPU info.

### Integration Points
Connects GE-specific FPGA interrupt and metadata hardware to the generic 85xx platform and Linux PCI/interrupt subsystems.

### Risks
Board register offsets and cascade-compatible matching are hardware-specific. Incorrect PCI primary selection affects legacy I/O routing and device enumeration.

### Test Signals
Boot IMP3A, check `/proc/cpuinfo` board fields, cascaded FPGA interrupts, PCI root bridge assignment, and successful OF device publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/ge_imp3a.c -->
