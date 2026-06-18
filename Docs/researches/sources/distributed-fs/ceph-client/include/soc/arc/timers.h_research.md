# sources/distributed-fs/ceph-client/include/soc/arc/timers.h

Purpose: lists ARC timer auxiliary registers, timer control bits, max counter value, and the timer build-configuration register layout.

Important APIs and types: constants identify TIMER0/TIMER1 limit, control, and count registers. `ARC_TIMER_CTRL_IE` enables interrupt-on-limit and `ARC_TIMER_CTRL_NH` continues counting only when the CPU is not halted. `ARC_TIMERN_MAX` defines the 32-bit limit. `struct bcr_timer` decodes version and timer/RTC/RTSC availability with endian-aware bitfields.

Control flow: clocksource/clockevent code reads `ARC_REG_TIMERS_BCR`, checks available timers, writes limit/control/count registers, and enables interrupting or halt-aware timer behavior.

State and persistence: timer state is per-core hardware counter/control state. No software state or persisted configuration is stored in the header.

Dependencies and integration points: depends on `arc_aux.h`; integrates ARC platform timer drivers and CPU-local auxiliary register access.

Risks and test signals: risks include selecting unavailable timers, using incorrect halt semantics for clocksource accounting, endian bitfield errors, and missing interrupt enable/clear ordering. Test clocksource and clockevent operation on timer0/timer1, suspend/halt behavior, BCR decoding, interrupt delivery, wraparound, and big-endian compile/runtime coverage.
