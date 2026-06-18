<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm.h

### Purpose
Declares internal S3C PM globals, callbacks, and helper functions shared across common and SoC-specific PM files.

### Important APIs, Types, And Functions
The header exposes `s3c_pm_flags`, wake mask globals, `pm_cpu_prep`, `pm_cpu_sleep`, `s3c_irqext_wake()`, `s3c_pm_init()`, core save/restore hooks, GPIO save/restore hooks, UART save/restore helpers, and PM debug/check hooks.

### Control Flow
No direct runtime flow; it defines the linkage used by the suspend sequence.

### State, Persistence, And Dependencies
State is held in extern globals implemented in `pm.c` and SoC PM files. Conditional declarations depend on PM and debug configuration.

### Integration Points
Included by S3C64xx PM, GPIO PM, and IRQ wake code.

### Risks
Global callback pointers and masks make initialization order important. Missing config stubs can hide untested PM paths.

### Test Signals
Compile coverage across PM enabled/disabled configs and suspend/resume runtime tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm.h -->
