## sources/distributed-fs/ceph-client/drivers/virtio/virtio_rtc_class.c

Purpose: this file exposes one suitable virtio RTC clock as a Linux RTC class device, translating RTC operations into virtio RTC request helpers.

Important APIs/types/functions: `struct viortc_class` stores the backing `viortc_dev`, `rtc_device`, virtio clock ID, and a `stopped` flag protected by `rtc_lock()`. RTC operations are `viortc_class_read_time()`, `viortc_class_read_alarm()`, `viortc_class_set_alarm()`, and `viortc_class_alarm_irq_enable()`. Integration helpers are `viortc_class_init()`, `viortc_class_register()`, `viortc_class_stop()`, and `viortc_class_alarm()`.

Control flow: RTC reads call `viortc_read()` and convert nanoseconds to `rtc_time`. Alarm reads and writes call `viortc_read_alarm()`, `viortc_set_alarm()`, and `viortc_set_alarm_enabled()`, converting between seconds and nanoseconds with overflow checks. Alarm notifications from the core call `viortc_class_alarm()`, which verifies the clock ID and reports `RTC_AF | RTC_IRQF` through `rtc_update_irq()`. Removal calls `viortc_class_stop()` to reject subsequent RTC ops with `-EBUSY`.

State and persistence behavior: state is devm-managed and tied to the virtio device. Alarm state and clock readings live in the virtio device, not in this wrapper. The `stopped` bit is local runtime state used to guard teardown.

Dependencies and integration points: integrates with Linux RTC class APIs, time conversion helpers, overflow helpers, and virtio RTC core request functions declared in `virtio_rtc_internal.h`.

Risks: only whole-second RTC values are exposed, so subsecond precision from virtio RTC is discarded. Alarm setting rejects negative or overflowing times. Stale notifications for a non-registered clock are ignored with a warning.

Test signals: test RTC reads, alarm read/set/enable flows, alarm notification delivery, teardown racing with RTC ops, and configuration without alarm support where `RTC_FEATURE_ALARM` is cleared.
