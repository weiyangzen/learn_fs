# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_mds.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_mds.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_mds.c

### Purpose
Support for MPC8568 MDS, MPC8569 MDS, and P1021 MDS boards. It handles QE/UCC Ethernet details, PHY clock/reset quirks, board fixups, MPIC setup, PCI/SMP setup, and device publication.

### Important APIs, Types, And Functions
Important paths include `mpc8568_fixup_125_clock()`, `mpc8568_mds_phy_fixups()`, `mpc85xx_mds_reset_ucc_phys()`, `mpc85xx_mds_qe_init()`, `board_fixups()`, `mpc85xx_publish_devices()`, `mpc85xx_mds_pic_init()`, and machine descriptors `mpc8568_mds`, `mpc8569_mds`, and `p1021_mds`. It registers PHY fixups, manipulates QE par_io, maps GUTS, and calls `mpc85xx_common_publish_devices()`.

### Control Flow
Setup emits progress, initializes SMP, QE-specific pin and reset handling when configured, assigns PCI, and logs the board. Early arch initcalls perform PHY board fixups and publish devices. PIC setup allocates MPIC with single destination CPU semantics.

### State, Persistence, And Dependencies
State includes PHY fixup registrations, GUTS/QE register programming, MPIC state, PCI setup, and platform devices. No filesystem persistence is used. Dependencies include PHYLIB, QE, OF address/resource APIs, MPIC, and FSL PCI.

### Integration Points
This file is the bridge between MDS board hardware quirks and generic Ethernet/QE/PHY/platform drivers.

### Risks
PHY reset/clock code and par_io muxing are hardware-specific. Incorrect fixups can make Ethernet unreliable or invisible.

### Test Signals
Boot all three MDS variants, validate UCC/FEC Ethernet link, PHY clock fixups, QE pins, MPIC interrupts, PCI, and common device enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_mds.c -->
