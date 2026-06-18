# sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/mpc86xx.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/mpc86xx.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/mpc86xx.h

### Purpose
Local 86xx platform header declaring shared SMP and interrupt initialization helpers.

### Important APIs, Types, And Functions
Declares `mpc86xx_smp_init()` and `mpc86xx_init_irq()`, with an inline empty `mpc86xx_smp_init()` for non-SMP builds.

### Control Flow
No runtime control flow. Build configuration decides whether the real SMP implementation is linked.

### State, Persistence, And Dependencies
No state is owned. Dependencies are compile-time `CONFIG_SMP`, `linux/init.h`, and the implementations in `mpc86xx_smp.c` and `pic.c`.

### Integration Points
Used by 86xx board files to call common interrupt and SMP setup without local ifdefs.

### Risks
Prototype mismatches break board builds. Incorrect stubbing can hide SMP initialization or create unresolved symbols.

### Test Signals
Build SMP and non-SMP 86xx configs and verify board files link cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/mpc86xx.h -->
