# sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/m8xx_setup.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/m8xx_setup.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/m8xx_setup.c

### Purpose
Shared MPC8xx setup helpers for timer/decrementer calibration, RTC access, and restart.

### Important APIs, Types, And Functions
Key functions are `mpc8xx_calibrate_decr()`, `mpc8xx_set_rtc_time()`, `mpc8xx_get_rtc_time()`, and `mpc8xx_restart()`. Internal helpers include `timebase_interrupt()` and `get_freq()`.

### Control Flow
Decrementer calibration unlocks protected clock/timebase registers, forces clock divide-by-16, reads CPU frequency from the CPU node or uses a fallback, configures RTC/timebase control registers, maps the CPU timer IRQ, and requests the timebase interrupt. RTC helpers unlock, read/write, and relock keep-alive RTC registers. Restart disables IRQs, requests reset/checkstop behavior, and panics if it fails.

### State, Persistence, And Dependencies
State includes global `ppc_proc_freq`, `ppc_tb_freq`, timebase/RTC hardware registers, and requested IRQs. RTC time persists in hardware during power conditions, but the file does not write filesystem state. Dependencies include OF CPU properties, 8xx IMMR registers, IRQ mapping, RTC conversion helpers, and `mpc8xx_immr`.

### Integration Points
Machine descriptors use these callbacks for timebase, RTC, and restart behavior across 8xx boards.

### Risks
Register unlock ordering is hardware-sensitive. Incorrect frequency fallback, IRQ mapping, or restart bit handling affects system time or reset.

### Test Signals
Boot 8xx boards, verify decrementer frequency, timer interrupts, RTC read/write, and restart behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/m8xx_setup.c -->
