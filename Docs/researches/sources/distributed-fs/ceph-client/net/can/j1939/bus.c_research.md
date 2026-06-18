# sources/distributed-fs/ceph-client/net/can/j1939/bus.c

## Purpose
This file manages J1939 ECU objects and the in-memory bus address map for one CAN netdevice. It tracks NAME-address associations, local socket user counts, delayed address-claim activation, and ECU object lifetimes.

## Important APIs, Types, And Functions
The main APIs are `j1939_ecu_create_locked()`, `j1939_ecu_put()`, `j1939_ecu_unmap_locked()`, `j1939_ecu_unmap()`, `j1939_ecu_unmap_all()`, `j1939_ecu_timer_start()`, `j1939_ecu_timer_cancel()`, `j1939_ecu_get_by_addr()`, `j1939_ecu_get_by_name()`, `j1939_name_to_addr()`, `j1939_local_ecu_get()`, and `j1939_local_ecu_put()`.

`struct j1939_ecu` instances are linked in `priv->ecus`, keyed by NAME for lookup, optionally mapped into `priv->ents[addr].ecu`, and refcounted with `kref`.

## Control Flow
ECU creation initializes the object with idle address, NAME, timer, refcount, and a reference to `j1939_priv`, then appends it to the ECU list. Mapping requires a unicast address and an empty address slot; it takes an ECU reference and adds the ECU's local-user count to the address entry. Unmapping clears the address entry, subtracts local users, and drops the map-held ECU reference.

Address-claim processing starts `j1939_ecu_timer_start()`, which holds the ECU and schedules a 250 ms soft hrtimer. The timer handler maps the ECU under `priv->lock` and drops the timer-held reference. Cancellation drops that reference if the timer was pending.

Socket bind/rebind uses `j1939_local_ecu_get()` to increment local user counts for source address and/or NAME, creating an ECU for a named local user if needed. Release/rebind uses `j1939_local_ecu_put()` to decrement those counts and drop the ECU reference.

## State And Persistence
All state is per `j1939_priv` and lasts until netdevice stop/unregister or all references are released. ECU objects are reference-counted by list ownership, active address map slots, timers, local users, and transient lookups. No state persists outside memory.

`priv->lock` protects both the ECU list and address-entry table. Some lookups return referenced ECUs, while `_find_` helpers return borrowed pointers and require the lock to remain held.

## Dependencies And Integration Points
`address-claim.c` uses these APIs to resolve and update J1939 network-management state. `socket.c` uses local ECU get/put to mark local source identities and help transport logic identify local endpoints. `main.c` calls `j1939_ecu_unmap_all()` on netdevice events and releases `j1939_priv` references after ECU cleanup.

## Risks And Edge Cases
Mapping and local-user accounting share `priv->ents[addr].nusers`. Bugs in bind/release balance can underflow counts or mislabel received frames as local/not local.

`j1939_ecu_map_locked()` warns and skips if a slot is already mapped. Address-claim conflict logic must unmap previous occupants first to avoid silently losing mappings.

Timers hold ECU references. Every timer start must be paired with either timer handler completion or successful cancellation.

`j1939_name_to_addr()` returns idle or no-address sentinel values when no active mapping exists; callers must distinguish unclaimed names from broadcast/no-name behavior.

## Test Signals
Test address-claim timer activation/cancel, duplicate NAME lookup, address contention, local user count increments/decrements for named and address-only binds, netdevice down unmapping, and final release assertions that ECU and priv lists are empty.
