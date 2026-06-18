# sources/distributed-fs/ceph-client/include/clocksource/timer-davinci.h

Purpose: platform configuration interface for TI DaVinci clocksource/clockevent timer registration.

Important APIs/types/functions: `DAVINCI_TIMER_*` IRQ indexes, `struct davinci_timer_cfg`, and `davinci_timer_register`.

Control flow: board code supplies register and IRQ resources plus optional compare-register offset; implementation registers timer halves as clocksource/clockevent.

State and persistence: the config struct persists only long enough for registration; implementation owns device state.

Dependencies and integration points: uses `linux/clk.h` and resource definitions; integrates with DaVinci platform clock and interrupt setup.

Risks: compare offset mode changes which timer half generates events, so IRQ/resource mismatch causes lost events. Early init failures can stop scheduler clock setup.

Test signals: DaVinci boot tests, clockevent tick tests, and compare-register configuration coverage.
