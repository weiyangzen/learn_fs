<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ljca.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ljca.c

## Purpose
`gpio-ljca.c` exposes GPIO lines on Intel La Jolla Cove Adapter USB devices through the LJCA auxiliary bus. It provides GPIO get/set/direction, pin configuration, valid masks, and event-driven child IRQs using LJCA command packets.

## Important APIs, types, and functions
`struct ljca_gpio_dev` stores the LJCA client, gpiochip, firmware GPIO info, bitmaps for IRQ states and output direction, per-line connect modes, transfer buffers, mutexes, and a re-enable work item. Packet helpers are `ljca_gpio_config()`, read, write, and `ljca_enable_irq()`. IRQ flow uses `ljca_gpio_event_cb()`, mask/unmask, type setup, bus lock/unlock, and `ljca_gpio_async()`.

## Control flow
Probe obtains the LJCA client and platform GPIO info, allocates `connect_mode`, initializes mutexes, fills a can-sleep gpiochip with valid-mask callbacks, registers an LJCA event callback, configures a simple child irqchip, initializes work, and registers the gpiochip. GPIO operations serialize USB command transfers. IRQ events from firmware dispatch child IRQs immediately and schedule work to re-enable any still-unmasked lines.

## State and persistence behavior
Software tracks output-enabled state for `get_direction`, desired IRQ mask/enabled state, lines needing re-enable, and per-line pull/interrupt mode in `connect_mode`. Hardware state lives in the LJCA device and is updated by command packets; there is no durable persistence.

## Dependencies and integration points
The driver is an auxiliary driver for `usb_ljca.ljca-gpio`, imports namespace `LJCA`, uses ACPI name fallback for labels, gpiolib valid masks from `ljca_gpio_info`, and simple child IRQ domains.

## Risks and edge cases
`connect_mode` is shared between pin configuration and IRQ type configuration, so a later pinconf operation can overwrite interrupt configuration. Event callback does not validate packet length beyond command type. IRQ re-enable is asynchronous, leaving a small masked window after events.

## Test signals
Test LJCA transfer success/failure, valid pin mask enforcement, direction/output state tracking, pinconf pull-up/down, all IRQ trigger types, event callback demux, re-enable work cancellation on remove, and hot-unplug during pending transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ljca.c -->
