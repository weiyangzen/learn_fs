<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/gpio-ir-recv.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/gpio-ir-recv.c

Purpose: platform driver for simple GPIO-based IR receivers. It converts GPIO edges into rc-core raw IR events and optionally uses runtime PM/QoS to reduce first-edge latency on cpuidle-sensitive systems.

Important APIs and functions: `struct gpio_rc_dev` stores the rc device, GPIO descriptor, IRQ, optional PM device, and CPU latency QoS request. Main functions are `gpio_ir_recv_irq`, `gpio_ir_recv_probe`, `gpio_ir_recv_remove`, system suspend/resume callbacks, and runtime suspend/resume callbacks.

Control flow: probe requires a device-tree node, gets an input GPIO and maps it to an IRQ, allocates an `RC_DRIVER_IR_RAW` device, fills protocols/timeouts/keymap from `linux,rc-map-name` or `RC_MAP_EMPTY`, registers rc-core, configures optional autosuspend from `linux,autosuspend-period`, stores drvdata, and requests both-edge IRQ. The IRQ optionally runtime-resumes the device, reads GPIO level, stores an edge event (`val == 1` as pulse), and schedules autosuspend.

State and persistence: state is devm-managed per platform device. Runtime PM and QoS state persist while the driver is bound. No IR data is persisted beyond rc-core raw event queues.

Dependencies and integration points: depends on OF, GPIO descriptors, IRQ, runtime PM, CPU latency QoS, platform bus, and rc-core. Device-tree compatible is `gpio-ir-receiver`.

Risks: the QoS remove path is called during runtime suspend/remove, so it relies on runtime resume having added the request first. Edge polarity is hard-coded from GPIO value and may depend on device-tree GPIO flags. The IRQ is requested after rc registration, so a request failure leaves only devm cleanup and registered rc device rollback through managed resources.

Test signals: device-tree probe, both-edge IRQ capture, keymap property handling, wakeup-source suspend behavior, autosuspend-period PM behavior, and rc-core decoder output under tight pulse timings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/gpio-ir-recv.c -->
