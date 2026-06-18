# sources/distributed-fs/ceph-client/drivers/rtc/rtc-digicolor.c

## Purpose
Conexant Digicolor RTC platform driver. It exposes a command-driven MMIO RTC that stores a reference value plus a running time counter and alarm offset.

## Important APIs, types, and functions
- `struct dc_rtc` stores RTC device and MMIO base.
- `dc_rtc_cmds()` writes command codes with `GO_BUSY` and polls until hardware clears busy.
- `dc_rtc_read()` issues read/nop commands, reads reference and stable time counter by repeated sampling, and returns `reference + time`.
- `dc_rtc_write()` writes a reference value and sends write/nop/reset/nop commands.
- RTC ops convert between seconds and `rtc_time`, read/write alarm offset relative to reference, and toggle interrupt enable.
- `dc_rtc_irq()` clears the interrupt flag and reports `RTC_AF`.
- Probe maps MMIO, allocates RTC, requests IRQ, sets `range_max = U32_MAX`, and registers the RTC.

## Control flow
All time reads and writes pass through explicit hardware command sequences. Alarm programming is simpler: it directly writes `ALARM` as target time minus current reference and enables/disables the interrupt byte.

## State and persistence behavior
Hardware stores reference seconds, elapsed counter, alarm offset, interrupt enable, and interrupt flag. Software stores only MMIO and RTC pointers.

## Dependencies and integration points
Depends on platform MMIO, `readb_relaxed_poll_timeout()`, RTC class, IRQ framework, and OF compatible `"cnxt,cx92755-rtc"`.

## Risks
- Command polling timeout is large (`500 * 10 ms`), so hung hardware can stall operations for seconds.
- Alarm pending calculation uses `alarm_reg + reference > now`, which describes future scheduled alarms rather than a latched interrupt flag.
- Alarm set with a target before reference underflows into a large `u32` offset.
- No PM/wakeup support is implemented.

## Test signals
Command timeout injection, stable double-read behavior, time set/read round trip, past alarm programming, IRQ clear/report, and interrupt enable toggling.
