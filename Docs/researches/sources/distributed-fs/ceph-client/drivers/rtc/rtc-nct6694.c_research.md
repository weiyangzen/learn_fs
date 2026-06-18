# sources/distributed-fs/ceph-client/drivers/rtc/rtc-nct6694.c

Purpose: implements the Nuvoton NCT6694 RTC subdevice over the parent USB-MFD command protocol, providing BCD time, hour/min/sec alarm, IRQ-domain alarm events, and wake capability.

Important APIs/types/functions: packed protocol structs `nct6694_rtc_time`, `nct6694_rtc_alarm`, and `nct6694_rtc_status` are wrapped by `union nct6694_rtc_msg`. `struct nct6694_rtc_data` stores parent device, RTC, shared message buffer, and mapped IRQ. RTC callbacks build static `nct6694_cmd_header` instances for time, alarm, and status commands and call `nct6694_read_msg()`/`write_msg()`. `nct6694_irq()` clears pending status and reports `RTC_AF`.

Control flow: probe allocates state and the message union, maps `NCT6694_IRQ_RTC` from the parent IRQ domain, registers a devm cleanup action to dispose the mapping, initializes wakeup, allocates RTC, sets 2000-2099 range, stores driver data, requests a threaded IRQ, and registers the RTC. Time reads/writes transfer the full seven-byte BCD structure. Alarm reads/writes transfer three BCD fields plus enable/pending bytes. Alarm IRQ enable writes status command fields with interrupt/GPO enable bits.

State and persistence: hardware/firmware persists BCD time, alarm, alarm enable/pending, and status. The driver reuses one shared message union for all callbacks and IRQ handler, relying on RTC core locking only where explicitly used in the IRQ path.

Dependencies and integration: depends on the parent `nct6694` MFD, USB command helpers, IRQ domain, platform subdevice name `nct6694-rtc`, and RTC class.

Risks and test signals: `nct6694_rtc_alarm_irq_enable()` modifies `sts->irq_en` without first reading current status, so stale union contents can affect enable state. The shared union has no explicit lock in normal read/set callbacks, while the IRQ path uses `rtc_lock()`. Alarm date is not supported, only sec/min/hour. Test concurrent RTC ops and IRQ, IRQ mapping cleanup, status enable from cold zeroed buffer, BCD conversion, parent command failures, wakeup init failure, and no-domain/no-IRQ cases.
