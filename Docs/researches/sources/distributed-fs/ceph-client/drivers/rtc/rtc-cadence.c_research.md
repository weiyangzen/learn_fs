# sources/distributed-fs/ceph-client/drivers/rtc/rtc-cadence.c

## Purpose
Cadence RTC platform driver for `cdns,rtc-r109v3`. It provides timekeeping, calendar, alarm interrupts, wake support, and clock validation for a register-mapped RTC block.

## Important APIs, types, and functions
- `struct cdns_rtc` stores the RTC device, peripheral/reference clocks, MMIO base, and IRQ.
- `cdns_rtc_set_enabled()` and `cdns_rtc_get_enabled()` control the time/calendar counters via `CDNS_RTC_CTLR`.
- `cdns_rtc_time2reg()` and `cdns_rtc_reg2time()` translate BCD time fields using bitfield helpers.
- `cdns_rtc_read_time()` disables counting, samples time and calendar registers, decodes full date including century, then re-enables.
- `cdns_rtc_set_time()` writes time/calendar and retries until valid flags `VT|VC` appear in status.
- Alarm ops program time/date/month alarm registers, retry until `VTA|VCA`, and toggle alarm event/interrupt masks.
- `cdns_rtc_irq_handler()` reads the event flag register, which clears it, and reports `RTC_AF`.
- Probe maps registers, obtains `pclk` and `ref_clk`, requires ref clock of 1 or 100 Hz, requests IRQ, sets range 1900-2999, forces 24-hour mode, keeps RTC values, and enables wakeup.

## Control flow
The driver gates read/set sequences with the enable bit to avoid racing hardware updates. Probe enables clocks before touching hardware and unwinds them on failures. Suspend/resume only toggles IRQ wake when the device is wake-capable.

## State and persistence behavior
Hardware holds date/time, alarm date/time, enabled state, event flags, and keep-RTC configuration. Software state is limited to clock handles and MMIO pointers. Alarm enabled state is read from hardware only implicitly through register masks, not cached.

## Dependencies and integration points
Depends on platform devices, OF, MMIO, `clk`, `bitfield`, RTC class, interrupt handling, and PM wake IRQ support. Registers as a platform driver named `"cdns-rtc"`.

## Risks
- Reference clock acceptance is strict: only 1 Hz or 100 Hz is allowed.
- `cdns_rtc_read_time()` returns `-EINVAL` if the RTC is disabled, so boot firmware state matters.
- Alarm read returns only day/month and time, not year or enabled/pending fields.
- Set loops retry only three times before `-EIO`.

## Test signals
Probe with valid/invalid ref clocks, read/set across century boundaries, alarm set/read/IRQ delivery, wake from suspend, and injected invalid status flag failures.
