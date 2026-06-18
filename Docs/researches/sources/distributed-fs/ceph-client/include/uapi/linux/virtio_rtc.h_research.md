<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_rtc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_rtc.h

Purpose: defines the virtio RTC ABI for reading virtual clocks, cross-reading clocks with hardware counters, querying clock capabilities, and configuring alarms.

Important APIs and types: feature `VIRTIO_RTC_F_ALARM` gates alarm support. Request types include read, cross read, config, clock capability, cross capability, read alarm, set alarm, and alarm enable. Common request/response/notification headers carry message type and status. Clock types include UTC, TAI, monotonic, and smeared UTC variants; counter IDs include ARM virtual counter and x86 TSC. Unions group requestq responses and alarmq notifications.

Control flow, state, and persistence: the guest sends control/read requests and receives status plus clock/alarm data; alarm events arrive on an alarm queue. Alarm state persists in the device until changed or reset.

Dependencies and integration points: integrates with virtio core, RTC/timekeeping, clocksource calibration, and alarm/timer subsystems.

Risks and test signals: risks include time type confusion, leap smear semantics, cross-counter race handling, alarm enable flags, and status mapping. Test all request types, unsupported clocks, alarm notifications, cross reads around migration, and invalid clock IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_rtc.h -->
