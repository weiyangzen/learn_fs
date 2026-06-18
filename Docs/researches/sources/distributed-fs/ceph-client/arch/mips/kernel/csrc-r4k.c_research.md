<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-r4k.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-r4k.c

### Purpose
`csrc-r4k.c` registers CP0 Count as the common MIPS R4K-style clocksource, optional VDSO clock mode, and sched_clock source.

### Important APIs, Types, And Functions
Important functions are `c0_hpt_read()`, `r4k_read_sched_clock()`, `rdhwr_count()`, `rdhwr_count_usable()`, `count_can_be_sched_clock()`, CPU-frequency notifier helpers, and `init_r4k_clocksource()`.

### Control Flow
Initialization checks for a CPU counter and known high-precision timer frequency, computes rating, verifies user-mode `rdhwr $2` is not broken before enabling VDSO R4K mode, registers the clocksource, and registers sched_clock only when CPU frequency/SMP stability conditions allow. CPU frequency transitions mark the clocksource unstable.

### State, Persistence, And Dependencies
State includes CP0 Count, `clocksource_mips`, optional `r4k_clock_unstable`, cpufreq notifier registration, and sched_clock state. Dependencies include CPU feature flags, MIPS timer frequency, VDSO clock mode, and cpufreq.

### Integration Points
Generic timekeeping, VDSO time reads, sched_clock, and R4K compare clockevents rely on this source.

### Risks
Broken RDHWR implementations are explicitly filtered. CPU frequency changes and unsynchronized per-CPU counters can make sched_clock or clocksource unstable.

### Test Signals
Clocksource monotonicity, VDSO clock_gettime under R2/R6, QEMU RDHWR workaround, CPU frequency transition tests, and SMP sched_clock stability checks are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-r4k.c -->
