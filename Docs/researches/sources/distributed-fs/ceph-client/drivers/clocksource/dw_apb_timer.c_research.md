# sources/distributed-fs/ceph-client/drivers/clocksource/dw_apb_timer.c

Purpose: provides reusable clockevent and clocksource support for Synopsys DesignWare APB timers.

Important APIs/types/functions: `dw_apb_clockevent_init()`, `dw_apb_clockevent_register()`, `dw_apb_clocksource_init()`, `dw_apb_clocksource_start()`, `dw_apb_clocksource_register()`, `dw_apb_clocksource_read()`, and internal APBT state callbacks.

Control flow: clockevent init allocates a `dw_apb_clock_event_device`, configures min/max deltas, requests the IRQ, and returns it for registration. Clockevent state callbacks program periodic/free-running oneshot modes and load deltas. Clocksource init starts a masked, free-running down-counter and exposes its inverted value as an up-counting source.

State and persistence: allocated wrapper structs store MMIO base, IRQ, frequency, and clockevent/clocksource objects. Hardware timer control/load/current registers persist state.

Dependencies and integration points: exported through `linux/dw_apb_timer.h` and used by `dw_apb_timer_of.c` and other platform code. Depends on IRQ, MMIO, clockevents, and clocksource core.

Risks: oneshot mode is emulated using free-running mode. Programming requires careful enable/load ordering and a small delay for periodic mode. IRQ is requested during init, so users must call cleanup elsewhere if registration is abandoned. Minimum delta is fixed conservatively.

Test signals: direct users of exported init/register APIs, IRQ EOI handling, oneshot/periodic transition tests, and clocksource wrap/monotonicity checks.
