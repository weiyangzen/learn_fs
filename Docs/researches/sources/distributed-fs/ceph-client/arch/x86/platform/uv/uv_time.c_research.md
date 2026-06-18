<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/uv/uv_time.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/uv/uv_time.c

## Purpose
Registers the UV real-time clock as a clocksource and optional per-CPU clock-event device backed by UV RTC MMRs.

## Important APIs, Types, And Functions
Defines `clocksource_uv`, per-CPU `clock_event_device`, `struct uv_rtc_timer_head`, `uv_rtc_next_event()`, `uv_rtc_shutdown()`, `uv_rtc_interrupt()`, `uv_rtc_setup_clock()`, and the `uvrtcevt` early parameter.

## Control Flow
Init exits on non-UV or missing clock frequency, registers the RTC clocksource, and optionally allocates per-blade timer heads, sets up IRQs through `uv_setup_irq()`, and registers per-CPU clockevents. Timer programming tracks each CPU's expiry in a per-blade sorted list and programs the hub for the earliest event; interrupt dispatch sends IPIs to CPUs with expired timers.

## State And Persistence
Per-CPU clock-event devices and per-blade timer lists persist after init. Hardware RTC compare registers hold next expiry. `uv_rtc_evt_enable` is boot-parameter state.

## Dependencies And Integration Points
Depends on UV hub RTC registers, `uv_setup_irq()`, clocksource/clockevents core, CPU work scheduling, IPIs, and UV frequency discovery.

## Risks And Edge Cases
Per-blade list locking and next-event recalculation must avoid missed deadlines. Optional event mode can fail partway through allocation/IRQ setup and must deallocate. RTC frequency assumptions affect timekeeping accuracy.

## Test Signals
Clocksource registration, stable timekeeping, timer interrupt delivery on UV systems, `uvrtcevt` clockevent activation, and no missed timer warnings validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/uv/uv_time.c -->
