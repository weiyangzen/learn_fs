# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_ds.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_ds.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_ds.c

### Purpose
Machine support for MPC8544 DS and MPC8572 DS boards. It provides MPIC setup, SMP/PCI initialization, CAMP-aware interrupt setup, and common device publication.

### Important APIs, Types, And Functions
Functions include `mpc85xx_ds_pic_init()`, `mpc85xx_ds_setup_arch()`, and two `define_machine()` descriptors: `mpc8544_ds` compatible `MPC8544DS` and `mpc8572_ds` compatible `fsl,MPC8572DS`. Both use `mpc85xx_common_publish_devices()`, `mpc85xx_smp_init()`, `fsl_pci_assign_primary()`, PCI fixup hooks, and `mpic_get_irq`.

### Control Flow
PIC initialization adjusts for the `fsl,MPC8572DS-CAMP` variant before allocating MPIC. Setup initializes SMP and PCI. Arch initcalls publish common 85xx platform devices for both machine descriptors.

### State, Persistence, And Dependencies
State includes MPIC IRQ state, SMP ops, PCI host controller state, and OF platform devices. Dependencies include OF machine compatibility, MPIC, FSL PCI, and common 85xx helpers. No durable storage is involved.

### Integration Points
Board descriptor glue connects DS reference boards to generic 85xx subsystems and common driver binding.

### Risks
CAMP handling and single-destination MPIC flags are sensitive for multi-core partitioned boot. Compatible strings are historical and must be preserved.

### Test Signals
Boot MPC8544DS and MPC8572DS DTBs, including CAMP when available; check interrupts, SMP, PCI, and device publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_ds.c -->
