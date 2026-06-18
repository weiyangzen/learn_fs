# sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc86xads.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc86xads.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc86xads.h

### Purpose
Board-specific constants for MPC86xADS support.

### Important APIs, Types, And Functions
Provides preprocessor definitions for MPC86xADS board-control register offsets, bits, and memory layout consumed by `mpc86xads_setup.c`.

### Control Flow
No runtime control flow. Constants are compiled into the board setup file.

### State, Persistence, And Dependencies
No state is owned. It depends on the board hardware layout matching the constants.

### Integration Points
Supports BCSR setup, peripheral enablement, and board-specific register manipulation in the MPC86xADS machine file.

### Risks
Incorrect constants directly affect board-control MMIO writes and can disable peripherals or reset lines.

### Test Signals
Build MPC86xADS support and boot-test board-control paths that consume these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc86xads.h -->
