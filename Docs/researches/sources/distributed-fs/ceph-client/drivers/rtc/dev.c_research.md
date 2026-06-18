# sources/distributed-fs/ceph-client/drivers/rtc/dev.c

Purpose: `/dev/rtcN` character-device implementation for the RTC subsystem. It handles single-open access, blocking interrupt reads, poll/fasync, legacy and modern RTC ioctls, optional update-interrupt emulation, and char-device preparation.

Important APIs, types, and functions: `rtc_dev_open()` enforces `RTC_DEV_BUSY` and clears IRQ data. Optional UIE emulation uses `rtc_uie_task()`, `rtc_uie_timer()`, `set_uie()`, `clear_uie()`, and exported `rtc_dev_update_irq_enable_emul()`. User operations include `rtc_dev_read()`, `rtc_dev_poll()`, `rtc_dev_ioctl()`, compat ioctl handling, `rtc_dev_fasync()`, and `rtc_dev_release()`. Setup APIs are `rtc_dev_prepare()` and `rtc_dev_init()`.

Control flow: `rtc_dev_init()` allocates up to 16 RTC char-device numbers. `rtc_dev_prepare()` assigns `devt`, initializes optional UIE emulation work/timer, and initializes `char_dev` with file ops. Open rejects concurrent users, stores the RTC in `private_data`, and clears pending IRQ data. Read waits on `irq_queue` until `rtc->irq_data` is nonzero, nonblocking returns `-EAGAIN`, and signal interruption returns `-ERESTARTSYS`; it copies an `unsigned int` or `unsigned long` event word. Ioctl checks permissions, handles alarms, time read/set, PIE/AIE/UIE toggles, IRQ frequency, wake alarms, feature/correction params, driver-specific params, and fallback driver ioctls. Release disables UIE and PIE but leaves one-shot alarms intact, then clears busy.

State and persistence: state lives in the `rtc_device`: busy flag, IRQ data, IRQ frequency, max user frequency, async queue, UIE emulation flags/timer/work, and ops pointer. Time and alarms persist in hardware through `rtc_class_ops`.

Dependencies and integration points: depends on RTC interface helpers (`rtc_read_time`, `rtc_set_time`, `rtc_read_alarm`, `rtc_set_alarm`, `rtc_irq_set_state`, `rtc_update_irq_enable`, `rtc_alarm_irq_enable`, `rtc_read_offset`, `rtc_set_offset`), Linux cdev, wait queues, fasync, capabilities, compat ioctl, timers, and workqueues.

Risks: only one process can open a given RTC char device. `RTC_ALM_SET` emulates 24-hour wrap and cannot support wildcard periodic alarms. Permission checks are centralized and must stay aligned with security expectations (`CAP_SYS_TIME`, `CAP_SYS_RESOURCE`). UIE emulation polls hardware repeatedly and can be expensive. Release invokes ioctl-style UIE disable while tearing down, so ops locking and driver removal interactions matter.

Test signals: open exclusivity, blocking/nonblocking reads, poll/fasync delivery from `rtc_handle_legacy_irq()`, all standard ioctls with permission boundaries, compat ioctl translations, UIE emulation on hardware without update IRQs, release cleanup of repeating interrupts, and behavior when `rtc->ops` disappears during unregister.
