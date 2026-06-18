# sources/distributed-fs/ceph-client/drivers/pps/clients/pps-gpio.c

Purpose: platform driver that turns GPIO edges into PPS assert/clear events, optionally driving an echo GPIO for a bounded active pulse.

Important APIs/types/functions: `struct pps_gpio_device_data`, `pps_gpio_probe()`, `pps_gpio_remove()`, `pps_gpio_irq_handler()`, `pps_gpio_echo()`, `pps_gpio_setup()`, and `get_irqf_trigger_flags()`.

Control flow: probe allocates per-device data, obtains an input GPIO, reads `assert-falling-edge`, optionally obtains an `echo` GPIO and validates `echo-active-ms`, maps the GPIO to an IRQ, fills `pps_source_info`, registers a PPS source, then requests the IRQ with rising/falling/both-edge flags. The IRQ handler timestamps immediately with `pps_get_ts()`, samples GPIO value when clear capture is enabled, emits assert or clear with `pps_event()`, or rate-limited warns if the edge direction does not map. Echo mode sets the echo GPIO and arms a timer to clear it.

State and persistence: per-device state is devm-managed except the PPS source, IRQ, and timer. Remove frees IRQ, unregisters PPS, deletes echo timer, and forces echo low.

Dependencies/integration: platform bus, firmware properties, gpiod consumer API, IRQ subsystem, timers, jiffies, and PPS core.

Risks: `capture_clear` is never populated from firmware in this file, so clear capture appears disabled unless initialized elsewhere; remove calls `gpiod_set_value()` even if echo GPIO is absent; IRQ value sampling after timestamp can race edge bounce; echo timer uses `add_timer()` rather than modifying an active timer; bad `echo-active-ms` rejects probe.

Test signals: device-tree compatible `pps-gpio`, assert edge selection, optional echo GPIO pulse duration, IRQ cleanup, PPS sysfs sequence increments, and clear-capture behavior if firmware support is added.
