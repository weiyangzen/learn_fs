# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/qemu_e500.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/qemu_e500.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/qemu_e500.c

### Purpose
QEMU e500 virtual machine platform support. It supplies a compact machine descriptor for emulated FSL e500 systems with MPIC, SMP, PCI, and common OF device publication.

### Important APIs, Types, And Functions
Functions are `qemu_e500_pic_init()`, `qemu_e500_setup_arch()`, `machine_arch_initcall(qemu_e500, mpc85xx_common_publish_devices)`, and `define_machine(qemu_e500)` with compatible `fsl,qemu-e500`. It uses MPIC, `mpc85xx_smp_init()`, `fsl_pci_assign_primary()`, PCI fixups, and `mpic_get_irq`.

### Control Flow
The emulated DT root compatible selects the machine. Setup initializes SMP and PCI. PIC init allocates MPIC. Common devices are published by arch initcall.

### State, Persistence, And Dependencies
State is virtual hardware initialization state: MPIC, SMP ops, PCI bridge state, and OF platform devices. No persistence exists. Dependencies include QEMU-provided device tree, MPIC, FSL PCI, and common 85xx helpers.

### Integration Points
Allows the same 85xx kernel paths to run under QEMU for development and regression testing.

### Risks
Emulated device-tree assumptions can differ from real boards. PCI and interrupt regressions here may affect CI-style coverage for 85xx.

### Test Signals
Boot `qemu-system-ppc` e500 machine, verify machine selection, virtio/PCI devices, interrupts, SMP if enabled, and common device publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/qemu_e500.c -->
