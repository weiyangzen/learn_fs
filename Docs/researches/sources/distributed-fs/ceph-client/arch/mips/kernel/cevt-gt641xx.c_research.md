<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-gt641xx.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-gt641xx.c

### Purpose
This file implements clockevent support for GT641xx timer 0.

### Important APIs, Types, And Functions
Public functions are `gt641xx_set_base_clock()` and `gt641xx_timer0_state()`. Internal functions include `gt641xx_timer0_set_next_event()`, shutdown/oneshot/periodic state setters, `gt641xx_timer0_interrupt()`, and initcall `gt641xx_timer0_clockevent_init()`.

### Control Flow
The base clock must be set before initcall. Init programs timer 0, computes rating and delta bounds, registers the clockevent, and requests `GT641XX_TIMER0_IRQ`. Runtime state setters update timer control under a raw spinlock, choosing periodic select or one-shot behavior.

### State, Persistence, And Dependencies
State includes `gt641xx_base_clock`, GT timer count/control registers, `gt641xx_timer_lock`, and the clockevent device. Dependencies are GT64120 register access macros and clockevents.

### Integration Points
GT641xx-based MIPS boards call the base-clock setter during platform setup; generic tick code uses the registered event device.

### Risks
If the base clock is never set, init silently does nothing. Timer control register updates are shared with hardware, so locking and bit masks are essential.

### Test Signals
Board boot should verify base-clock setup, periodic ticks, oneshot next-event programming, timer0 state detection, and IRQ delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/cevt-gt641xx.c -->
