## sources/distributed-fs/ceph-client/drivers/virtio/virtio_rtc_ptp.c

Purpose: this file exposes virtio RTC clocks as Linux PTP hardware clocks, including optional cross timestamp support when both platform and device support a compatible hardware counter.

Important APIs/types/functions: `struct viortc_ptp_clock` owns the registered `ptp_clock`, backing `viortc_dev`, `ptp_clock_info`, clock ID, and `have_cross`. `struct viortc_ptp_cross_ctx` carries a pre-fetched device time and system counter value into `get_device_system_crosststamp()`. Key functions are `viortc_ptp_register()`, `viortc_ptp_unregister()`, `viortc_ptp_gettimex64()`, `viortc_ptp_getcrosststamp()`, `viortc_ptp_do_xtstamp()`, and `viortc_ptp_get_cross_cap()`.

Control flow: registration allocates a PTP wrapper, copies a template `ptp_clock_info`, sets the name, queries platform cross-timestamp parameters, asks the virtio device whether that clock/counter pair supports cross timestamps, disables `.getcrosststamp` if unsupported, then registers the PTP clock. `gettimex64` brackets `viortc_read()` with `ptp_read_system_prets/postts`. `getcrosststamp` verifies the active clocksource ID, fetches the device/counter pair first because virtio access may be slow, then passes the captured values into `get_device_system_crosststamp()`.

State and persistence behavior: PTP state is devm allocated but explicitly freed only after successful `ptp_clock_unregister()`. Device time is read on demand; no time state is persisted.

Dependencies and integration points: integrates with Linux PTP clock APIs, clocksource snapshots, virtio RTC read/cross-cap requests, and optional arch helpers like `virtio_rtc_arm.c`.

Risks: cross timestamp accuracy depends on device-provided counter cycles matching the active Linux clocksource. Large nanosecond values above `KTIME_MAX`/`S64_MAX` are rejected. Time adjustment and set operations deliberately return `-EOPNOTSUPP`, so consumers must treat these as read-only PHCs.

Test signals: PTP registration, name truncation failure path, `gettimex64`, cross timestamp enabled/disabled paths, clocksource mismatch, unsupported platform helper, unregister on remove, and read values near overflow limits.
