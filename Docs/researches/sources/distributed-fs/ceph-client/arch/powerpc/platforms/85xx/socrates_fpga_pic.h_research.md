# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates_fpga_pic.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates_fpga_pic.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates_fpga_pic.h

### Purpose
Header declaring the Socrates FPGA PIC initializer for board code.

### Important APIs, Types, And Functions
Declares `void __init socrates_fpga_pic_init(struct device_node *pic);`.

### Control Flow
No runtime flow is present. `socrates.c` calls the declared initializer after MPIC setup when the FPGA PIC node is found.

### State, Persistence, And Dependencies
No state is owned here. It depends on `linux/init.h` and `linux/of.h` for annotations and `struct device_node`.

### Integration Points
Connects the board machine file to the FPGA interrupt-controller implementation without exposing internal irq_chip details.

### Risks
Prototype drift from the implementation breaks builds. Calling with an unreferenced or invalid node would fail in the implementation.

### Test Signals
Build Socrates support and boot with an `abb,socrates-fpga-pic` node to confirm linkage and initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates_fpga_pic.h -->
