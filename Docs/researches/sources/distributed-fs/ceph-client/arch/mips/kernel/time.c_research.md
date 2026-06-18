## sources/distributed-fs/ceph-client/arch/mips/kernel/time.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/time.c` provides common MIPS time initialization, cpufreq loops-per-jiffy adjustment, exported RTC/perf IRQ hooks, and R4k Count clocksource/clockevent setup decisions.

### Important APIs, Types, And Functions
Important state includes per-CPU `pcp_lpj_ref`, `pcp_lpj_ref_freq`, global `glb_lpj_ref`, `glb_lpj_ref_freq`, exported `rtc_lock`, `perf_irq`, and exported `mips_hpt_frequency`. Functions include `cpufreq_callback()`, `register_cpufreq_notifier()`, `null_perf_irq()`, `cpu_has_mfc0_count_bug()`, and `time_init()`.

### Control Flow
When CPU frequency changes, the notifier records baseline loops-per-jiffy values and rescales global and per-CPU delay calibration on pre-change or post-change depending on frequency direction. `time_init()` calls platform `plat_time_init()`, initializes the MIPS clockevent, and registers the Count clocksource unless the R4k Count read bug conflicts with reliable timer interrupt use.

### State, Persistence, And Dependencies
State includes delay calibration values, platform-set `mips_hpt_frequency`, function pointer `perf_irq`, and exported `rtc_lock`. Dependencies include CPU frequency notifiers, R4k timer code, platform time initialization, CPU type detection, and clocksource/clockevent infrastructure.

### Integration Points
Clockevent setup is used by SMP startup and Count synchronization. Platforms provide `plat_time_init()` and may set `mips_hpt_frequency`. Perf event code can override `perf_irq`. RTC drivers use `rtc_lock`.

### Risks
Incorrect frequency scaling breaks `udelay()` timing. R4000/R4400 Count read errata can break clocksource use if ignored. `mips_hpt_frequency` must be set before clockevent/clocksource init. Cpufreq notifier baseline capture must match online CPU state.

### Test Signals
Boot with R4k timer, verify clocksource registration on CPUs with and without Count bug, run cpufreq transitions and validate delay calibration, test SMP secondary timer interrupts, and exercise perf IRQ override paths.
