# sources/distributed-fs/ceph-client/drivers/power/supply/generic-adc-battery.c

Purpose: implements a generic IIO-backed battery power-supply driver. It exposes status plus whichever of voltage/current/power/temperature channels are present on the device.

Important APIs/types/functions: `struct gab` holds the power supply descriptor, optional IIO channels, delayed status work, cached status, and optional `charged` GPIO. `gab_read_channel()` reads processed IIO values and scales them by 1000. `gab_work()` derives status from external supply state and the optional charge-finished GPIO. `gab_probe()` dynamically builds the property list from available IIO channels.

Control flow: probe allocates state, builds a descriptor named after the device, tries to acquire standard IIO channels `voltage`, `current`, `power`, and `temperature`, requires at least one channel, registers the power supply, sets up delayed work, optionally requests an IRQ on the `charged` GPIO, and schedules an immediate status check. External power changes and charged-GPIO interrupts schedule status work. Suspend cancels work and marks status unknown; resume reschedules with a small jitter.

State and persistence: only current status is cached. Channel readings are pulled from IIO on demand. There are no writable properties and no persistence.

Dependencies and integration: depends on platform/OF compatible `adc-battery`, IIO consumer channels, optional GPIO descriptor/IRQ, `power_supply_am_i_supplied()`, and devm delayed-work helpers.

Risks and test signals: the driver assumes all processed IIO channel units should be multiplied by 1000, which must match provider conventions for voltage/current/power/temp. Optional charged GPIO handling checks `IS_ERR()` incompletely after `devm_gpiod_get_optional()`. Test dynamic property enumeration, no-channel probe failure, each channel read, external-supply status transitions, charged IRQ jitter, and suspend/resume behavior.
