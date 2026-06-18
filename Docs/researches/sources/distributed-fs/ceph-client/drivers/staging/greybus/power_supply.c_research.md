# sources/distributed-fs/ceph-client/drivers/staging/greybus/power_supply.c

## Purpose
Greybus Power Supply protocol driver. It discovers remote power supplies, maps Greybus properties to Linux `power_supply` properties, registers power_supply devices, polls/caches property values, handles update events, and forwards writable property changes.

## Important APIs, Types, And Functions
`struct gb_power_supplies` owns the connection, supply count, supply array, and lock. `struct gb_power_supply` contains descriptor, registered `power_supply`, name, remote strings/type, property arrays, cache state, delayed work, PM-acquired flag, and lock. `struct gb_power_supply_prop` maps Linux and Greybus property IDs and caches values. Key functions include `get_psp_from_gb_prop()`, description/descriptor fetchers, property update/get/set paths, delayed work polling, registration/setup helpers, and `gb_supplies_request_handler()`.

## Control Flow
Probe validates one power-supply CPort, creates a connection with events, enables TX only, queries supply count and descriptors, enables RX, registers all power supplies, schedules immediate delayed work, and drops runtime PM. `get_property()` refreshes cached values if expired, then returns cached integer or string data. Events invalidate cache and force status update. Polling backs off from `update_interval_init` to `update_interval_max` unless a change resets the interval.

## State And Persistence
Properties are cached in memory for `cache_time` milliseconds unless invalidated. Manufacturer/model/serial strings are fetched once from descriptions. Charging status may hold a runtime-PM reference via `pm_acquired` to keep the module awake while charging.

## Dependencies And Integration Points
Uses Greybus Power Supply protocol, Linux power_supply core, delayed work, runtime PM, mutexes, and bundle class matching.

## Risks
Property mapping drops unsupported kernel properties and compacts arrays; allocation and count adjustments must stay consistent. `_gb_power_supply_property_get()` logs errors but returns 0, which can hide missing properties. Delayed work and event handling must stop cleanly during unregister via `update_interval = 0` and `cancel_delayed_work_sync()`.

## Test Signals
Test supply count zero, descriptor/property mapping including unsupported props, string properties, cache hit/expiry/invalidation, writable property set, polling backoff, change notification thresholds, charging PM reference balance, events during unregister, and partial setup/register failure cleanup.
