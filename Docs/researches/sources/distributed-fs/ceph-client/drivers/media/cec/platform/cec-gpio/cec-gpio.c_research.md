# sources/distributed-fs/ceph-client/drivers/media/cec/platform/cec-gpio/cec-gpio.c

Purpose: This platform driver implements a generic GPIO-backed CEC adapter using the `cec-pin` software transceiver. It optionally monitors HDMI HPD and 5V GPIOs and integrates with an HDMI notifier when an `hdmi-phandle` is present.

Important APIs, types, and functions: `struct cec_gpio` stores adapter, notifier, device, CEC GPIO/IRQ/state, optional HPD GPIO/IRQ/state/timestamp, and optional 5V GPIO/IRQ/state/timestamp. Pin ops include `cec_gpio_read()`, `cec_gpio_high()`, `cec_gpio_low()`, IRQ enable/disable, status, `read_hpd`, and `read_5v`. IRQ handlers cover CEC pin edge updates (`cec_pin_changed()`), HPD events (`cec_queue_pin_hpd_event()`), and 5V events (`cec_queue_pin_5v_event()`). Probe/remove register and unregister the pin adapter.

Control flow and state: Probe parses HDMI phandle; if absent, it adds `CEC_CAP_PHYS_ADDR` so userspace can set the physical address. It gets the CEC open-drain GPIO as output-high, optional HPD/5V inputs, allocates a pin adapter with monitor capabilities, requests CEC edge IRQ with `IRQF_NO_AUTOEN`, requests threaded HPD/5V IRQs, optionally registers a notifier, registers the CEC adapter, and stores driver data. CEC low/high ops drive the open-drain line and maintain `cec_is_low` to avoid reading a line actively driven low. HPD/5V hard IRQs timestamp edges and threaded handlers read sleepable GPIO values before queueing events.

State and persistence behavior: All state is volatile. The pin engine stores CEC protocol state; this driver stores physical GPIO state snapshots for status and event filtering. Physical address either comes from notifier or userspace depending on DT.

Dependencies and integration points: Depends on platform devices, GPIO descriptors, IRQs, CEC notifier, and `cec_pin_allocate_adapter()`. The device tree compatible is `"cec-gpio"` with GPIO names `"cec"`, optional `"hpd"`, optional `"v5"`, and optional `hdmi-phandle`.

Risks and edge cases: Software CEC timing depends on low latency; PREEMPTION dependency in Kconfig reflects that. Open-drain semantics are important: driving high means releasing the line. CEC IRQ is enabled/disabled by the pin engine, not always-on. HPD/5V IRQs use sleepable reads in threaded context. If the HDMI phandle lookup fails with a non-deferral error, userspace must set physical address manually.

Test signals: Test DT probe with and without HDMI phandle, CEC line TX/RX compliance, monitor-pin mode, IRQ enable/disable transitions, HPD/5V event initial and edge behavior, debugfs status, suspend/resume IRQ behavior if platform-specific, and remove while userspace has device open.
