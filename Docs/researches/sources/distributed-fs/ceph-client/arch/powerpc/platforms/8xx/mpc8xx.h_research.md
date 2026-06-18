# sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc8xx.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc8xx.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc8xx.h

### Purpose
Local header declaring shared MPC8xx setup helpers.

### Important APIs, Types, And Functions
Declares `mpc8xx_calibrate_decr()`, `mpc8xx_restart()`, `mpc8xx_set_rtc_time()`, and `mpc8xx_get_rtc_time()` for board machine descriptors.

### Control Flow
No runtime flow. Board files reference these callbacks in `define_machine()` or setup paths.

### State, Persistence, And Dependencies
No state is owned. Depends on `linux/rtc.h` types and implementation in `m8xx_setup.c`.

### Integration Points
Provides common timebase, RTC, and restart callbacks to all 8xx board files.

### Risks
Prototype mismatch breaks builds; wrong callback use affects timekeeping or restart.

### Test Signals
Build all 8xx boards and boot-test decrementer, RTC, and restart callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc8xx.h -->
