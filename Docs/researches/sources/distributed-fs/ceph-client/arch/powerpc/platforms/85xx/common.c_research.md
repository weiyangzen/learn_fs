# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/common.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/common.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/common.c

### Purpose
Shared 85xx/QorIQ platform helpers. It publishes common device-tree buses/devices and provides CPM2 and QE parallel I/O initialization glue used by multiple board files.

### Important APIs, Types, And Functions
Exports `qoriq_pm_ops` as a global PM operations pointer. `mpc85xx_common_publish_devices()` probes compatible devices including `soc`, `simple-bus`, `gianfar`, QE/CPM, SRIO, DMA, GUTS, GPIO LEDs, PCIe variants, and FMan. `mpc85xx_cpm2_pic_init()` finds `fsl,cpm2-pic`, initializes the CPM2 PIC, maps the cascade interrupt, and installs `cpm2_cascade()`. `mpc85xx_qe_par_io_init()` configures QE par_io for each `ucc_geth` child when QE support is enabled.

### Control Flow
Board files call the publish helper from `machine_arch_initcall()` or device initcall. CPM2 initialization finds the PIC node, initializes the secondary controller, maps the cascade, and sets chained IRQ handling. QE I/O initialization scans compatible nodes during board setup.

### State, Persistence, And Dependencies
State is kernel-global interrupt-domain and platform-device state plus `qoriq_pm_ops`. No persistent storage is written. Dependencies include OF platform probing, `irq_of_parse_and_map`, CPM2 PIC, QE par_io, and FSL SoC helpers.

### Integration Points
This is the common bridge between 85xx machine descriptors and normal Linux platform drivers. Board files rely on it to instantiate Ethernet, DMA, PCIe, SRIO, QE, and bus devices.

### Risks
Changing compatible lists can silently hide devices. Cascade IRQ setup must balance `of_node_put()` and must set chained handlers only after valid mappings.

### Test Signals
Boot representative 85xx boards and check OF devices, Ethernet/QE devices, CPM2 interrupt delivery, and absence of OF node leaks or failed platform probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/common.c -->
