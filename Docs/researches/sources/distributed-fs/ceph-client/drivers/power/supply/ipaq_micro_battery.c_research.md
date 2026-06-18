# sources/distributed-fs/ceph-client/drivers/power/supply/ipaq_micro_battery.c

## Purpose
This platform driver exposes battery and AC state from the HP iPAQ h3xxx Atmel microcontroller companion. It polls the MFD microcontroller every 100 seconds, caches the returned battery fields and thermal sensor value, and registers `main-battery` plus `ac` power supplies.

## Important APIs, Types, and Functions
`struct micro_battery` stores the parent `ipaq_micro`, a private workqueue, delayed update work, and cached AC, chemistry, voltage, temperature, and flag values. `micro_battery_work()` sends synchronous `MSG_BATTERY` and `MSG_THERMAL_SENSOR` messages through `ipaq_micro_tx_msg_sync()`, decodes the response, and requeues itself. `get_capacity()` maps high/low/critical flags to rough 100/50/5 percent values. `get_status()` maps unknown/full/charging flags to power-supply status. `micro_batt_get_property()` and `micro_ac_get_property()` serve cached values.

## Control Flow
Probe allocates state, gets the parent microcontroller object, creates a reclaimable per-CPU workqueue, registers autocancel delayed work, stores driver data, queues the first update almost immediately, then registers battery and AC supplies. Suspend cancels the delayed work synchronously. Resume queues the next update after the normal polling period.

## State and Persistence
All telemetry is cached in `struct micro_battery` and refreshed only by delayed work. There is no register programming or persistent hardware policy in this driver. `micro_batt_power` and `micro_ac_power` are file-scope pointers to devm-registered supplies, so only one instance is effectively expected.

## Dependencies and Integration Points
The driver depends on the `ipaq-micro` MFD transport and message IDs, the power-supply core, devm work helpers, and system sleep PM. Battery properties are marked `use_for_apm`, reflecting the legacy handheld platform integration.

## Risks
`micro_battery_work()` logs but does not abort when `rx_len < 4`, then still indexes response bytes up to 4, so malformed microcontroller replies can feed stale or invalid data. Thermal sensor response length is not checked. Property reads are unlocked while work updates fields, which is acceptable for simple integer fields but not strongly synchronized. The capacity mapping is coarse and flag-dependent, not coulomb or voltage based.

## Test Signals
Validate message decoding with normal and short replies, periodic requeue, suspend cancel/resume requeue, battery chemistry mapping, status priority for full versus charging, AC online reporting, and behavior when a second battery is reported. Hardware or mocked MFD tests should confirm response endian/scale for voltage and temperature.
