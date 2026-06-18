# sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec_power.c

## Purpose
Power-supply driver exposing NVEC AC and battery information through Linux `power_supply`.

## Important APIs, Types, And Functions
`struct nvec_power` stores notifier/work state, EC pointer, AC online flag, battery presence/status/measurements, capacity, temperature, and strings. `struct bat_response` overlays EC responses. Key functions are `nvec_power_probe()`, `nvec_power_remove()`, `nvec_power_poll()`, `nvec_power_notifier()`, `nvec_power_bat_notifier()`, `get_bat_mfg_data()`, and the AC/battery `get_property` callbacks.

## Control Flow
The NVEC parent creates two `nvec-power` cells with ids for AC and battery. AC probe registers a system-status notifier, power_supply named `ac`, and a delayed poller that requests AC status and one battery metric every five seconds. Battery probe registers a battery notifier, requests manufacturer/model/type/capacity data, and registers power_supply named `battery`. Notifiers parse `NVEC_SYS` and `NVEC_BAT` responses into cached fields and signal `power_supply_changed()` on online/presence/status changes.

## State And Persistence
All readings are cached in `struct nvec_power`; static globals hold the registered AC and battery power_supply pointers, and a static `counter` rotates polled battery commands. No durable state exists.

## Dependencies And Integration Points
Depends on NVEC notifier/write APIs, platform MFD children, delayed work, `power_supply` core, and EC battery/system command formats.

## Risks
The same notifier field is used for AC and battery instances but registered with a broad event argument; correctness depends on event-type filtering. Static globals and poll counter make multi-controller support unsafe. Manufacturer/model/type copies trust `res->length - 2` to fit 30-byte arrays. Polling deliberately spaces requests because the EC can be overloaded.

## Test Signals
AC and battery cell probe by id, property reads before/after EC responses, status transitions, battery insert/remove triggering manufacturer refresh, string response bounds, delayed poll cadence, remove canceling work, and power_supply_changed notifications.
