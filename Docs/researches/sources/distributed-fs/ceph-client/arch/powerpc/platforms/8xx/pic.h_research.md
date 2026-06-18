# sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/pic.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/pic.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/pic.h

### Purpose
Header for MPC8xx PIC initialization and IRQ retrieval.

### Important APIs, Types, And Functions
Declares `mpc8xx_pic_init()` and `mpc8xx_get_irq()`.

### Control Flow
No runtime flow. Board machine descriptors reference these functions for `init_IRQ` and `get_irq`.

### State, Persistence, And Dependencies
No state is owned. Depends on `linux/irq.h` and the implementation in `pic.c`.

### Integration Points
Connects board files to the shared SIU PIC implementation.

### Risks
Prototype mismatch breaks builds or machine descriptor initialization.

### Test Signals
Build 8xx boards and verify `init_IRQ`/`get_irq` linkage at boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/pic.h -->
