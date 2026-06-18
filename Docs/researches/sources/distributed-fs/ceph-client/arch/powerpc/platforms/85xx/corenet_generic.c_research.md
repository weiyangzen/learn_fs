# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/corenet_generic.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/corenet_generic.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/corenet_generic.c

### Purpose
Generic CoreNet/QorIQ 85xx machine support for many P/Q/T-series boards, including hypervisor-aware ePAPR variants. It avoids per-board source files by matching a list of compatible strings and common devices.

### Important APIs, Types, And Functions
Main functions are `corenet_gen_pic_init()`, `corenet_gen_setup_arch()`, `corenet_gen_publish_devices()`, `corenet_generic_probe()`, and `define_machine(corenet_generic)`. Device matches include `simple-bus`, mdio muxes, FPGA PIXIS/QIXIS, SRIO, PCIe generations, and QE. The probe path recognizes many board root compatibles and handles ePAPR hypervisor PIC selection through `epapr_paravirt_early_init()` and `ppc_md.get_irq`.

### Control Flow
Probe checks board compatible strings and may activate paravirtual interrupt behavior. Setup initializes SMP, PCI primary assignment, SWIOTLB for high memory, and board logging. PIC init allocates MPIC unless the hypervisor path is active.

### State, Persistence, And Dependencies
State lives in `ppc_md`, MPIC/EPAPR interrupt state, PCI host state, and OF platform devices. No persistent data is written. Dependencies include MPIC, EPAPR paravirt, FSL PCI, SWIOTLB, OF matching, and `mpc85xx_smp_init()`.

### Integration Points
Integrates many CoreNet boards with common Linux drivers without dedicated board files. It also shares `smp_85xx_ops` and common device publication patterns.

### Risks
The broad compatible list makes regressions high-impact. Hypervisor detection and interrupt-controller selection are sensitive; wrong behavior can break guests or bare-metal interrupt routing.

### Test Signals
Boot bare-metal and ePAPR guest DTBs, verify selected machine, interrupt source, SMP, PCI, SWIOTLB detection, and publication of buses listed in `of_device_ids`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/corenet_generic.c -->
