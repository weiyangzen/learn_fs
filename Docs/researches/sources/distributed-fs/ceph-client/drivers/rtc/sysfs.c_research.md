## sources/distributed-fs/ceph-client/drivers/rtc/sysfs.c

Purpose: Implements the generic RTC subsystem sysfs attributes and helper APIs for adding extra RTC attribute groups. It is shared by RTC devices rather than tied to one hardware driver.

Important APIs/types/functions: Attribute show/store methods cover `name`, `date`, `time`, `since_epoch`, `max_user_freq`, `hctosys`, `wakealarm`, `offset`, and `range`. Visibility is controlled by `rtc_attr_is_visible` and `rtc_does_wakealarm`. Public helpers are `rtc_get_dev_attribute_groups`, `rtc_add_groups`, and `rtc_add_group`.

Control flow: Read-only date/time attributes call `rtc_read_time`, format with `%ptR*`, or convert via `rtc_tm_to_time64`. `max_user_freq_store` parses an unsigned long and accepts values 1..4095. `hctosys_show` reports whether this RTC matched `CONFIG_RTC_HCTOSYS_DEVICE` and successfully set system time. `wakealarm_show` returns an epoch only for enabled alarms. `wakealarm_store` reads current RTC time, parses absolute, relative `+N`, or push `+=N` values, rejects clobbering an active alarm unless pushing, disables alarms by programming a valid future dummy time when the requested epoch is not in the future, and calls `rtc_set_alarm`. Offset store delegates to RTC class offset callbacks. Visibility hides `wakealarm` if parent cannot wake or alarm feature is absent, hides `offset` without `set_offset`, and hides `range` when min/max are equal.

State and persistence: Most state is in the underlying RTC driver and hardware. `max_user_freq` is mutable in `struct rtc_device`. `rtc_add_groups` replaces `rtc->dev.groups` with a devm-allocated merged array and frees prior non-default group arrays.

Dependencies/integration: Uses RTC core APIs, sysfs attribute groups, kstrto parsing, wakeup capability, `RTC_FEATURE_ALARM`, and exported symbols for drivers that attach extra sysfs groups.

Risks: `wakealarm_store` has only minimal locking and documents that it cannot fully prevent concurrent alarm clobbering through other interfaces. It assumes RTC times are in the RTC’s timezone. `rtc_add_groups` must preserve the default group pointer ownership distinction.

Test signals: Attribute visibility matrix, wakealarm absolute/relative/push/disable cases, EBUSY on active alarm overwrite, max_user_freq bounds, offset show/store on capable and incapable RTCs, range hiding, and multiple group additions without leaking or dropping default groups.
