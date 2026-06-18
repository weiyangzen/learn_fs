# sources/distributed-fs/ceph-client/drivers/rtc/rtc-cpcap.c

## Purpose
Motorola CPCAP PMIC RTC platform driver. It exposes the PMIC day/time-of-day counters and alarm registers through the RTC class and requests both alarm and 1 Hz update interrupts, with the update IRQ deliberately disabled to avoid unnecessary wakeups.

## Important APIs, types, and functions
- `struct cpcap_time` represents PMIC split time as day plus two TOD register fragments.
- `struct cpcap_rtc` stores parent regmap, RTC device, vendor ID, alarm/update IRQs, and software IRQ-enable booleans.
- `cpcap2rtc_time()` and `rtc2cpcap_time()` convert between PMIC day/TOD fields and `rtc_time`.
- `cpcap_rtc_read_time()` samples `TOD2`, `DAY`, `TOD1`, `TOD2` and rereads day if rollover is detected.
- `cpcap_rtc_set_time()` disables active IRQs, writes time registers in vendor-specific order, then restores IRQs.
- Alarm ops read/write `DAYA/TODA2/TODA1` and control alarm IRQ state through `cpcap_rtc_alarm_irq_enable()`.
- IRQ handlers report `RTC_AF` and `RTC_UF`.
- Probe obtains parent regmap, vendor, IRQs, initializes wakeup, sets range from day mask, requests threaded IRQs, disables both initially, and registers the RTC.

## Control flow
The driver uses regmap for all PMIC access. Time setting is the highest-risk path because ST and non-ST vendors require different register write ordering to avoid inconsistent counters.

## State and persistence behavior
Time and alarm persist in CPCAP registers. Software tracks whether alarm/update IRQs are enabled because the IRQ framework state is not directly queried. The day field is 15-bit, so range is `(DAY_MASK + 1) * 86400 - 1`.

## Dependencies and integration points
Depends on parent Motorola CPCAP MFD regmap, CPCAP register definitions, platform IRQ resources, RTC class, and wakeup support. Binds to OF compatible `"motorola,cpcap-rtc"`.

## Risks
- `ret |= regmap_read/update_bits` combines errors; any nonzero result becomes generic `-EIO` in read paths and can obscure the first error.
- Alarm `set_alarm()` enables the IRQ on success regardless of `alrm->enabled`, which is worth testing against RTC core expectations.
- Time write ordering is vendor-sensitive and can break if vendor detection is wrong.
- Update IRQ is requested only to mask/own it; enabling it later depends on software state.

## Test signals
Vendor-specific set-time tests, rollover read around `TOD2`, alarm enable/disable and IRQ delivery, update IRQ staying disabled by default, wakeup initialization, and regmap error injection.
