# sources/distributed-fs/ceph-client/include/clocksource/timer-goldfish.h

Purpose: register definitions and init declaration for the Goldfish emulator timer.

Important APIs/types/functions: `TIMER_TIME_LOW/HIGH`, `TIMER_ALARM_LOW/HIGH`, `TIMER_IRQ_ENABLED`, `TIMER_CLEAR_ALARM`, `TIMER_ALARM_STATUS`, `TIMER_CLEAR_INTERRUPT`, and `goldfish_timer_init`.

Control flow: driver reads low time before high time to latch a coherent counter, programs alarms through low/high registers, enables IRQs, and clears alarm/interrupt status through dedicated offsets.

State and persistence: hardware/emulator MMIO registers hold current time, alarm, and IRQ state.

Dependencies and integration points: used by emulator platform clocksource setup.

Risks: wrong read ordering can produce inconsistent 64-bit time. Alarm clear/interrupt clear confusion can produce interrupt storms or missed events.

Test signals: Goldfish emulator boot, alarm scheduling tests, and clocksource watchdog checks.
