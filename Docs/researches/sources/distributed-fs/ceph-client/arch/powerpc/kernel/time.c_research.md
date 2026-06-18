# sources/distributed-fs/ceph-client/arch/powerpc/kernel/time.c

## Purpose
Provides common PowerPC timebase, clocksource, decrementer clockevent, delay, virtual CPU accounting, timer interrupt, persistent clock, RTC, suspend IRQ, and scheduler clock logic.

## Important APIs, Types, and Functions
- `clocksource_timebase` exposes `get_tb()` as a continuous clocksource.
- `decrementer_clockevent`, per-CPU `decrementers`, and `decrementers_next_tb` implement one-shot timer events.
- Time globals include `tb_ticks_per_jiffy`, `tb_ticks_per_usec`, `tb_ticks_per_sec`, `ppc_proc_freq`, `ppc_tb_freq`, `decrementer_max`, `boot_tb`, and conversion scale/shift.
- Vtime functions account kernel, idle, hardirq, softirq, guest, steal, and scaled cputime.
- `__delay()`/`udelay()` spin on timebase unless `tb_invalid`.
- `arch_irq_work_raise()` marks pending irq work and programs decrementer.
- `timer_interrupt()` handles decrementer interrupts, irq work, machine-check irq-context handlers, and clockevent dispatch/rearm.
- `time_init()` calibrates frequencies, computes `tb_to_ns` scale, initializes VDSO/systemcfg data, decrementer, clocksource, broadcast ticks, OF clocks, and sched-clock irqtime.
- Persistent clock helpers read/write RTC through `ppc_md`; optional `rtc-generic` device is registered.

## Control Flow and State
Boot calls platform or generic calibration from device tree, computes timebase conversion, registers clocksource and the boot CPU decrementer, and initializes clock infrastructure. Secondary CPUs call `secondary_cpu_time_init()`. Timer interrupts optionally hard-enable IRQs after parking the decrementer, run irq work, compare `get_tb()` to `decrementers_next_tb`, invoke the event handler or reprogram the decrementer.

## State and Persistence Behavior
Maintains global frequency/conversion state, per-CPU next decrementer deadlines, per-task/per-CPU accounting accumulators, RTC timezone offset, boot timebase, and `tb_invalid` recovery behavior. Persistent clock updates go to platform RTC.

## Dependencies and Integration Points
Integrates with clocksource/clockevents, VDSO data page, pseries SPLPAR stolen time, KVM host decrementer rearm, irq_work, machine-check handlers, suspend hooks, RTC platform hooks, OF clock init, and scheduler/accounting code.

## Risks
Frequency calibration errors affect all timekeeping. Decrementer max/large decrementer setup must match CPU features and firmware `ibm,dec-bits`. Timer interrupt ordering with hard IRQ enable, irq work, and watchdog is subtle. Vtime accounting assumes interrupts disabled and correct SPURR/PURR behavior.

## Test Signals
Clocksource stability tests, high-resolution timers, CPU hotplug timer init, KVM HV decrementer paths, pseries stolen time, suspend/resume IRQ disable/enable, RTC read/write, `udelay` under TB error injection, and cputime accounting validation.
