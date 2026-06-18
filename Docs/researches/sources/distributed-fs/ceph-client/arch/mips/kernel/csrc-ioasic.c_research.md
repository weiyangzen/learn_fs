<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-ioasic.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-ioasic.c

### Purpose
`csrc-ioasic.c` registers the DEC I/O ASIC free-running counter as a clocksource and sched_clock after calibrating it against DS1287 periodic ticks.

### Important APIs, Types, And Functions
Key functions are `dec_ioasic_hpt_read()`, `dec_ioasic_read_sched_clock()`, and `dec_ioasic_clocksource_init()`, with static `clocksource_dec`.

### Control Flow
Initialization synchronizes with an RTC periodic tick, samples the I/O ASIC counter, waits for `HZ / 8` further periodic ticks, samples again, computes frequency as delta times eight, rejects zero-frequency early ASICs, logs frequency, registers clocksource, and registers sched_clock.

### State, Persistence, And Dependencies
State includes I/O ASIC counter register, DS1287 RTC periodic state, computed frequency, and clocksource registration. Dependencies are DEC I/O ASIC accessors and DS1287 timer state.

### Integration Points
DEC MIPS platforms use this for continuous timekeeping when the I/O ASIC counter is present.

### Risks
Calibration depends on DS1287 periodic tick behavior and busy-waits during init. Early ASICs without a counter return `-ENXIO`.

### Test Signals
DEC platform boot, measured frequency sanity, monotonic counter reads, sched_clock registration, and fallback behavior on zero-frequency ASICs are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/csrc-ioasic.c -->
