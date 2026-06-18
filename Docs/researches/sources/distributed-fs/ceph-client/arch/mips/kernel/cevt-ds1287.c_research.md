<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-ds1287.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-ds1287.c

### Purpose
`cevt-ds1287.c` implements a periodic-only clockevent using the DS1287/MC146818 RTC periodic interrupt.

### Important APIs, Types, And Functions
Public functions are `ds1287_timer_state()`, `ds1287_set_base_clock()`, and `ds1287_clockevent_init()`. Internal pieces include `ds1287_shutdown()`, `ds1287_set_periodic()`, `ds1287_interrupt()`, and `ds1287_clockevent`.

### Control Flow
Base clock setup maps selected Hz values to RTC rate codes. Periodic state sets or clears `RTC_PIE` under `rtc_lock`. The interrupt handler acknowledges by reading `RTC_REG_C` and invokes the clockevent handler. Oneshot programming is unsupported and returns `-EINVAL`.

### State, Persistence, And Dependencies
State lives in CMOS RTC registers A/B/C, global `rtc_lock`, and the clockevent struct. Dependencies include MC146818 RTC macros, clockevents, IRQ APIs, and MIPS time setup.

### Integration Points
Used by platforms with DS1287 RTC timer support, and by DEC I/O ASIC clocksource calibration through `ds1287_timer_state()`.

### Risks
Only three base frequencies are accepted. Periodic-only operation limits dynamic tick behavior. RTC register locking must be respected by other RTC users.

### Test Signals
Verify 128/256/1024 Hz setup, periodic interrupt delivery, RTC PIE enable/disable, IRQ request errors, and coexistence with RTC drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-ds1287.c -->
