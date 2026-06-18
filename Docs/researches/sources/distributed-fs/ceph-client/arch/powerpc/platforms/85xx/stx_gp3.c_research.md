# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/stx_gp3.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/stx_gp3.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/stx_gp3.c

### Purpose
Silicon Turnkey/Storm STx GP3-8560 board support. It supplies MPIC initialization, board setup, CPU info, and common device publication.

### Important APIs, Types, And Functions
Functions are `stx_gp3_pic_init()`, `stx_gp3_setup_arch()`, `stx_gp3_show_cpuinfo()`, `declare_of_platform_devices()` through common publication, and `define_machine(stx_gp3)` with compatible `stx,gp3-8560`. It uses `mpc85xx_common_publish_devices()`, MPIC, and `udbg_progress`.

### Control Flow
Machine matching selects the board. Setup emits progress and logs board identity. PIC init allocates MPIC. The machine initcall publishes common 85xx devices.

### State, Persistence, And Dependencies
State is runtime MPIC/platform-device state and optional `/proc/cpuinfo` output. Dependencies include OF, MPIC, seq_file, and common 85xx helper code. No persistent storage is used.

### Integration Points
Connects the board to generic 85xx interrupt and platform-driver infrastructure.

### Risks
CPU info must tolerate missing model properties. Minimal board glue still controls interrupt initialization.

### Test Signals
Boot STx GP3 DTB, verify machine selection, interrupts, common device publication, and `/proc/cpuinfo` board data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/stx_gp3.c -->
