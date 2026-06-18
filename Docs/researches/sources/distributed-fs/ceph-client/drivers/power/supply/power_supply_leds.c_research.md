
# sources/distributed-fs/ceph-client/drivers/power/supply/power_supply_leds.c

## Purpose
This optional companion file creates LED triggers for power_supply devices and updates them when supply state changes. Battery supplies get charging/full-oriented triggers; non-battery supplies get an online trigger.

## Important APIs, Types, and Functions
`struct power_supply_led_trigger` wraps `struct led_trigger` with a backpointer to the power_supply. Key functions are `power_supply_register_led_trigger()`, `power_supply_unregister_led_trigger()`, `power_supply_update_bat_leds()`, `power_supply_create_bat_triggers()`, `power_supply_update_gen_leds()`, `power_supply_create_gen_triggers()`, `power_supply_update_leds()`, `power_supply_create_triggers()`, and `power_supply_remove_triggers()`.

## Control Flow
During power_supply registration the core calls `power_supply_create_triggers()`. Battery devices register five triggers based on the supply name; non-battery devices register one `%s-online` trigger. On `power_supply_changed()` work, the core calls `power_supply_update_leds()`. Battery LED updates read `POWER_SUPPLY_PROP_STATUS` and set solid, off, blink, or multicolor orange/green patterns for full, charging, or other states. Non-battery updates read `ONLINE` and switch the online trigger.

## State and Persistence
Trigger objects and names are dynamically allocated and freed at unregister. LED state is external to the driver and updated from current power_supply properties; no persistent data is kept.

## Dependencies and Integration Points
This file depends on `CONFIG_LEDS_TRIGGERS`, LED trigger APIs, multicolor trigger support calls, and power_supply property reads. It is wired into `power_supply_core.c` through private header declarations.

## Risks and Test Signals
Risks include allocation/unwind correctness when one of several battery triggers fails, property-read failures silently leaving stale LED state, and assumptions that status/online properties exist for all supplies. Tests should cover registration/unregistration leak checks, trigger names, activation sync callback, status transitions, non-battery online transitions, and configs without LED trigger support.
