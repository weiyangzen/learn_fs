# sources/distributed-fs/ceph-client/tools/lib/thermal/thermal.c

Purpose: Provides high-level libthermal helpers for iterating thermal arrays, finding thermal zones, discovering full zone details, and managing handler lifecycle.

Important APIs/types/functions: Iterators: `for_each_thermal_threshold()`, `for_each_thermal_cdev()`, `for_each_thermal_trip()`, `for_each_thermal_zone()`. Finders: `thermal_zone_find_by_name()` and `thermal_zone_find_by_id()`. Lifecycle/discovery: `thermal_zone_discover()`, `thermal_init()`, and `thermal_exit()`.

Control flow: Iterators walk sentinel-terminated arrays and OR callback return values. Zone discovery first fetches zones, then for each zone fetches trips, thresholds, and governor. `thermal_init()` allocates a handler, stores ops, then initializes events, sampling, and command channels in order. `thermal_exit()` calls all three exit functions then frees the handler.

State and persistence: Uses heap-allocated `struct thermal_handler` and data arrays from command calls. No automatic freeing for discovered zone arrays/trips/thresholds is provided here.

Dependencies/integration: Calls command/event/sampling APIs declared in `thermal.h` and uses private `thermal_nl.h` for handler layout.

Risks: `thermal_init()` leaks partially initialized netlink resources if a later init step fails. `thermal_exit()` assumes `th` is non-NULL and all channels were initialized. `thermal_zone_discover()` leaks `tz` if per-zone detail fetch fails. Iterators OR all callback returns, so they do not short-circuit on failure.

Test signals: Iterator sentinel behavior, finder success/failure, discovery success and partial failure, init failure at each stage with leak checks, and exit with normal/partial handlers.
