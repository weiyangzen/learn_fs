<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/s3c64xx.h

### Purpose
Declares common S3C64xx initialization APIs and conditional S3C6410 hooks.

### Important APIs, Types, And Functions
Exports `s3c64xx_init_irq()`, `s3c64xx_init_io()`, crystal setters, timer source/timer init APIs, and S3C6410 `map_io`, `init_irq`, and `init` hooks when configured. It also declares timer mode enum use through `pwm-core.h`.

### Control Flow
No direct flow; board and CPU table code call these functions during machine initialization.

### State, Persistence, And Dependencies
State is held by implementations in `s3c64xx.c` and `s3c6410.c`. Depends on ARM `map_desc` and Samsung SoC config symbols.

### Integration Points
Included by S3C64xx board files, DT machine setup, and CPU-specific init.

### Risks
Config-dependent stubs returning `NULL` require callers to handle disabled CPU support.

### Test Signals
Build coverage for S3C6410 enabled/disabled configs and legacy board boot validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/s3c64xx.h -->
