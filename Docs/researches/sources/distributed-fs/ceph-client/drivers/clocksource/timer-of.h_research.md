# sources/distributed-fs/ceph-client/drivers/clocksource/timer-of.h

Purpose: private header defining the `timer_of` resource bundle used by many clocksource drivers to consolidate DT base, clock, IRQ, and clockevent state.

Important APIs/types/functions: flags `TIMER_OF_BASE`, `TIMER_OF_CLOCK`, and `TIMER_OF_IRQ` select resources. `struct of_timer_irq`, `of_timer_base`, and `of_timer_clk` describe requested resources and resulting handles. `struct timer_of` embeds a `clock_event_device`, device node, resource structs, and `private_data`. Inline accessors include `to_timer_of()`, `timer_of_base()`, `timer_of_irq()`, `timer_of_rate()`, and `timer_of_period()`.

Control flow: no executable control flow beyond inline conversion/access. Drivers fill fields before calling `timer_of_init()` from `timer-of.c`, then use accessors from callbacks and IRQ handlers.

State/persistence: this header defines caller-owned state layout; persistence depends on each driver’s allocation/static storage. `private_data` is an untyped extension point used by several drivers for SoC-specific offsets or width.

Dependencies/integration: `linux/clockchips.h` and the `timer_of_init()/timer_of_cleanup()` implementations. The embedded `clock_event_device` makes `container_of()` conversions central to IRQ and callback paths.

Risks: because `timer_of` embeds mutable `clock_event_device`, copying a preinitialized `clock_event_device` after IRQ request can change cleanup behavior. Accessors do not validate flags or NULL handles. Test signal is compile-time integration across all users and runtime init failure handling through cleanup.
