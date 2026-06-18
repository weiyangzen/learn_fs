# sources/distributed-fs/ceph-client/drivers/thermal/testing/zone.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/testing/zone.c` implements synthetic thermal-zone templates for thermal core testing. It lets debugfs commands create templates, add editable trip templates, register a real `test_tz` thermal zone from a template, update its temperature, and clean everything up. The source was read as a complete 447-line file.

## Important APIs, Types, and Functions

The main private types are `struct tt_thermal_zone`, `struct tt_trip`, and `struct tt_work`. Public functions are `tt_add_tz()`, `tt_del_tz()`, `tt_zone_add_trip()`, `tt_zone_reg()`, `tt_zone_unreg()`, and `tt_zone_cleanup()`. Key helpers include `tt_zone_get_temp()`, `tt_zone_register_tz()`, `tt_zone_unregister_tz()`, `tt_get_tt_zone()`, `tt_put_tt_zone()`, and workqueue callbacks that create/remove debugfs files.

## Control Flow

`tt_add_tz()` allocates a template, assigns an ID, initializes locks/list/IDA, and schedules work to create `tzN` debugfs files. `tt_zone_add_trip()` gets a referenced template, allocates a trip, assigns a trip ID, appends it under the zone lock, and schedules debugfs files for `trip_N_temp` and `trip_N_hyst`. `tt_zone_reg()` copies trip templates into a temporary array, registers a thermal zone named `test_tz`, stores the initial temperature, and enables the zone. Writes to the template `temp` debugfs file update `tz_temp` and call `thermal_zone_device_update()`. Deletion refuses referenced templates, unregisters an active thermal zone, removes the template from the global list, and schedules debugfs removal/freeing.

## State and Persistence Behavior

All state is in memory: global `tt_thermal_zones`, global IDA, per-template trip IDA/list, debugfs dentries, current template temperature, registered-zone current temperature, and a `refcount` protecting async work/deletion. No state survives unload or reboot.

## Dependencies and Integration Points

It depends on debugfs, IDA, lists, mutex guards, workqueues, and the thermal zone registration API. It integrates with `command.c` through `thermal_testing.h` and with the thermal core by registering real test zones using `thermal_zone_device_register_with_trips()`.

## Risks and Edge Cases

Most debugfs mutations are deferred to workqueue context to avoid manipulating debugfs from debugfs write operations. This makes reference counting important: missed `tt_put_tt_zone()` calls could block deletion, while premature deletion could race async work. Trip templates are copied at registration, so later template trip-file writes do not update an already registered zone's trip array unless the thermal core sysfs files for that zone are used. `tt_int_set()` rejects values below `THERMAL_TEMP_INVALID`, but casts from `u64` to `int`, so very large writes can wrap.

## Test Signals

Exercise the full command flow: add zone, add trips, change template trip values, register, write `temp`, observe thermal core notifications/trip crossing, unregister, delete, and unload. Race-oriented tests should delete while async debugfs work is pending and attempt deletion while references are held.
