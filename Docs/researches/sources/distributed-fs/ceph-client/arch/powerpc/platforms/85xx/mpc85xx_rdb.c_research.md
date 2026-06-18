# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_rdb.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_rdb.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_rdb.c

### Purpose
Board support for multiple P1020/P1021/P1024/P1025 RDB, MBG, UTM, and PD variants. It centralizes shared MPIC, SMP, PCI, and board-specific DIU mux setup.

### Important APIs, Types, And Functions
Main functions are `mpc85xx_rdb_pic_init()` and `mpc85xx_rdb_setup_arch()`. Machine descriptors cover `fsl,P1020RDB`, `fsl,P1021RDB-PC`, `fsl,P1025RDB`, `fsl,P1020MBG-PC`, `fsl,P1020UTM-PC`, `fsl,P1020RDB-PC`, `fsl,P1020RDB-PD`, and `fsl,P1024RDB`. The setup path may map `fsl,p1022-guts`-style registers for display-related muxing and always calls SMP and PCI helpers.

### Control Flow
PIC init allocates MPIC, with CAMP-aware handling for `fsl,MPC85XXRDB-CAMP`. Setup performs progress logging, optional DIU/GUTS configuration, SMP initialization, PCI primary assignment, and board logging. Each variant publishes common devices by arch initcall.

### State, Persistence, And Dependencies
State includes MPIC, GUTS register bits, SMP ops, PCI selection, and OF platform devices. No persistent data is written. Dependencies include OF compatible checks, MPIC, GUTS, FSL PCI, and common 85xx code.

### Integration Points
Provides one implementation for a family of related reference boards so common drivers can bind to the same device-tree structures.

### Risks
Variant compatibility must remain exact. Any display mux or CAMP change can have board-wide side effects.

### Test Signals
Boot each DTB variant when available; validate machine match, interrupts, PCI, display mux behavior where configured, and common platform devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_rdb.c -->
