# sources/distributed-fs/ceph-client/drivers/power/supply/sbs-battery.c

## Purpose
Smart Battery System gas-gauge driver for SBS batteries and TI BQ20Z65/BQ20Z75 variants. It exposes rich battery telemetry, identity strings, manufacture date, capacity/energy values, health, presence, and status.

## Important APIs, Types, and Functions
`sbs_data[]` maps power_supply properties to SBS command addresses and ranges. `struct sbs_info` tracks I2C client, power supply, presence GPIO, cached strings, cached chemistry, retry counts, delayed work, mode mutex, and variant flags. Key paths include `sbs_update_presence()`, `sbs_read_word_data()`, `sbs_read_string_data()`, `sbs_get_property()`, `sbs_get_battery_capacity()`, `sbs_status_correct()`, `sbs_external_power_changed()`, and `sbs_suspend()`.

## Control Flow
Probe copies a descriptor, reads firmware/platform retry counts, acquires optional battery-detect GPIO, optionally verifies presence, initializes delayed work, registers the power supply, and requests GPIO IRQ if available. Property reads check GPIO presence when configured, then dispatch to presence/health, string, numeric, capacity-mode, serial, or manufacture-date handlers. External power changes start a short polling loop to detect status changes.

## State and Persistence
Driver state is volatile but includes meaningful caches: `is_present`, `technology`, string buffers, `last_state`, and `poll_time`. Presence changes disable PEC, invalidate cached strings/chemistry, and optionally disable charger broadcasts. It may write BatteryMode capacity mode temporarily and TI manufacturer sleep command on suspend.

## Dependencies and Integration Points
Depends on I2C SMBus word/block access, optional GPIO, OF/platform data, power_supply, delayed work, and SMBus alert callback. Compatible strings include generic SBS and TI variants. Module parameter `force_load` allows binding without detected battery.

## Risks and Test Signals
Global `sbs_serial` is shared across devices. Fallback string reads disable PEC and require byte/I2C-block functions. Capacity reads temporarily switch BatteryMode and rely on `mode_lock`. Presence changes can occur during property reads and trigger `power_supply_changed()`. Test PEC negotiation, no-GPIO and GPIO presence, TI health mapping, block-read fallback, concurrent capacity reads, suspend sleep command, and external-power polling.
