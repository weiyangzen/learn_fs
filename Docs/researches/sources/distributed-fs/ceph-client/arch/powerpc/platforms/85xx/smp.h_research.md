# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/smp.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/smp.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/smp.h

### Purpose
Local header for 85xx SMP/PM initialization declarations.

### Important APIs, Types, And Functions
Declares `mpc85xx_smp_init()` and `mpc85xx_setup_pmc()` when SMP is enabled, with an inline empty `mpc85xx_smp_init()` when `CONFIG_SMP` is disabled. It includes `linux/init.h` for `__init` annotations.

### Control Flow
No runtime control flow exists in the header. Kernel configuration selects real SMP initialization or no-op stubbing.

### State, Persistence, And Dependencies
No state is owned here. Dependencies are limited to build-time config and implementation files `smp.c` and `mpc85xx_pm_ops.c`.

### Integration Points
Board setup files call `mpc85xx_smp_init()` unconditionally while this header hides non-SMP build differences.

### Risks
Prototype mismatch or wrong stubbing can break SMP builds or create unresolved symbols in UP builds.

### Test Signals
Build 85xx with `CONFIG_SMP=y` and disabled; verify board files link and SMP setup is included only when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/smp.h -->
