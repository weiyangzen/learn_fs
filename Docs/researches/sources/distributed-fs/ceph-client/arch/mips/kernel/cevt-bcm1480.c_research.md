<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-bcm1480.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-bcm1480.c

### Purpose
This file implements per-CPU clockevent devices for Broadcom/SiByte BCM1480 general-purpose timers.

### Important APIs, Types, And Functions
Key functions are `sibyte_set_periodic()`, `sibyte_shutdown()`, `sibyte_next_event()`, `sibyte_counter_handler()`, and `sb1480_clockevent_init()`. State is per-CPU `sibyte_hpt_clockevent` and per-CPU names.

### Control Flow
Initialization assigns timer IRQ `K_BCM1480_INT_TIMER_0 + cpu`, configures clockevent capabilities, registers it, masks/maps/unmasks the interrupt to IP4, sets affinity to the CPU, and requests the timer IRQ. Runtime oneshot/periodic programming writes timer config/init registers; the IRQ handler acknowledges and calls the event handler.

### State, Persistence, And Dependencies
State lives in SCD timer registers, BCM1480 interrupt mapper, per-CPU clockevent structs, and irq affinity. Dependencies are SiByte register definitions, raw MMIO accessors, clockevents, and IRQ APIs.

### Integration Points
Platform time initialization calls this for BCM1480 systems. Generic clockevents/tick code consumes the registered per-CPU device.

### Risks
The code assumes at most four CPUs/timers. Raw 64-bit register accesses and interrupt map offsets must match hardware. Request IRQ failures only log errors after registration.

### Test Signals
Boot on BCM1480, periodic and oneshot tick tests, per-CPU IRQ affinity checks, CPU hotplug if supported, and interrupt-map register validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-bcm1480.c -->
