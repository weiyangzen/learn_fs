<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/delay.c -->
## sources/distributed-fs/ceph-client/arch/parisc/lib/delay.c

### Purpose
`delay.c` implements precise busy-wait microsecond delays using PA-RISC CR16.

### Important APIs, Types, And Functions
`__cr16_delay()` performs cycle-based waiting and `__udelay()` converts microseconds using `boot_cpu_data.cpu_hz`; `__udelay` is exported.

### Control Flow
The delay loop disables preemption, records CR16 and CPU ID, polls until elapsed cycles exceed the requested loop count, periodically enables preemption to allow RT tasks, and compensates if migration to a different CPU occurs by subtracting elapsed cycles and restarting from the new CPU's CR16. `__udelay()` multiplies microseconds by CPU Hz per microsecond.

### State, Persistence, And Dependencies
No persistent mutable state. It depends on per-CPU CR16 counters, `boot_cpu_data.cpu_hz`, preemption control, and `smp_processor_id()`.

### Integration Points
Used by generic delay APIs and firmware/driver timing paths.

### Risks
CR16 is per-CPU and may differ between CPUs, so migration compensation is necessary but can extend delays. Large delays on 32-bit builds risk rollover, bounded by generic maximum delay settings.

### Test Signals
Delay calibration, RT preemption behavior, CPU migration during delay, and measured minimum delay length under SMP validate the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/delay.c -->
