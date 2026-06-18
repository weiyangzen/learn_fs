<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/sleep-s3c64xx.S -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/sleep-s3c64xx.S

### Purpose
Provides low-level S3C64xx resume assembly support.

### Important APIs, Types, And Functions
The key symbol is the CPU resume entry used as the physical address written into the SoC `INFORM0` resume register before suspend.

### Control Flow
Suspend code writes the resume symbol address, CPU enters sleep, ROM/PM hardware jumps back to the resume entry, and the assembly path restores enough CPU context to return to the generic ARM suspend framework.

### State, Persistence, And Dependencies
State is CPU context and the hardware resume vector. It depends on ARM suspend conventions, cache/MMU state expectations, and the SoC wake path.

### Integration Points
Referenced by `pm-s3c64xx.c` through `__pa_symbol(s3c_cpu_resume)`.

### Risks
Assembly must be position/physical-address safe at resume time. Any mismatch with cache/MMU state or resume address bricks suspend until reset.

### Test Signals
Successful resume from memory sleep and return to the kernel after `cpu_suspend()` validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/sleep-s3c64xx.S -->
