# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc8536_ds.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc8536_ds.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc8536_ds.c

### Purpose
Freescale MPC8536 DS reference board support. It supplies minimal machine glue for MPIC, SMP, PCI, and common OF device publication.

### Important APIs, Types, And Functions
Key functions are `mpc8536_ds_pic_init()`, `mpc8536_ds_setup_arch()`, `machine_arch_initcall(mpc8536_ds, mpc85xx_common_publish_devices)`, and `define_machine(mpc8536_ds)` with compatible `fsl,mpc8536ds`. It uses `mpc85xx_smp_init()`, `fsl_pci_assign_primary()`, `fsl_pcibios_fixup_bus`, and `mpic_get_irq`.

### Control Flow
The machine descriptor matches the root compatible, setup initializes SMP and PCI and emits progress, then the arch initcall publishes common 85xx devices.

### State, Persistence, And Dependencies
Only kernel hardware-init state is affected: MPIC, SMP ops, PCI host selection, and platform devices. There is no persistent storage. Dependencies are OF, MPIC, FSL PCI, and common 85xx helpers.

### Integration Points
Provides board-specific machine registration while delegating most functionality to common 85xx code and Linux PCI/OF subsystems.

### Risks
Small-file risks center on boot matching and MPIC flags. Omitting bus fixups can affect PCI resource setup.

### Test Signals
Boot with an MPC8536DS DTB, verify machine name, interrupts, PCI fixups, SMP initialization, and common OF devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc8536_ds.c -->
