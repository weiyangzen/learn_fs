## sources/distributed-fs/ceph-client/drivers/rtc/rtc-wilco-ec.c

Purpose: Provides RTC read/write support for Google Wilco Embedded Controller systems. Unlike register-based RTC drivers, it sends legacy EC mailbox messages to read or update CMOS time-of-day.

Important APIs/types/functions: Protocol structs are `ec_rtc_read_request`, `ec_rtc_read_response`, and `ec_rtc_write_request`. The RTC callbacks are `wilco_ec_rtc_read` and `wilco_ec_rtc_write`, registered through `wilco_ec_rtc_ops`. `wilco_ec_rtc_probe` allocates and registers the RTC device with a fixed 2000-2099 range.

Control flow: Probe creates a devm RTC device, assigns read/set callbacks, sets owner and supported range, and registers. Reads build a `WILCO_EC_MSG_LEGACY` mailbox request using static `read_rq`, receive binary fields from the EC, translate month/year into Linux `rtc_time`, validate with `rtc_valid_tm`, and return `-EIO` if the EC reports invalid data. Writes convert Linux `rtc_time` into EC protocol fields, including BCD century/year/month/day/hour/min/sec and weekday remapped from Linux 0=Sunday to EC 0=Saturday, then send the mailbox message with no response payload.

State and persistence: Persistent state lives entirely inside the EC/CMOS. The driver keeps no private per-device state and relies on parent device drvdata to obtain `struct wilco_ec_device`. Weekday persistence matters because the EC uses it for battery charging schedules.

Dependencies/integration: Depends on `linux/platform_data/wilco-ec.h`, the Wilco EC mailbox core, RTC core, platform driver binding `"rtc-wilco-ec"`, and `timekeeping.h` for RTC structures.

Risks: Read responses are binary while writes are BCD, so protocol confusion would silently corrupt time. Static `read_rq` is shared, but immutable after initialization. The driver has no alarm support, no wakealarm, and no offset support. It trusts the parent EC device and mailbox transport for serialization and command completion.

Test signals: Mock or hardware-test mailbox read/write payloads, invalid EC time validation, weekday conversion for all seven days, century boundaries 2000 and 2099, and parent probe ordering where `dev_get_drvdata(dev->parent)` must be valid.
