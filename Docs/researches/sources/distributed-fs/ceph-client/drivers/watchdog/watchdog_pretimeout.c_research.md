# sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_pretimeout.c

## Purpose
`watchdog_pretimeout.c` manages watchdog pretimeout governors. It tracks registered governors, assigns a default governor to watchdog devices that can emit pretimeout events, exposes sysfs-facing governor list/get/set helpers, and dispatches pretimeout notifications.

## Important APIs, types, and functions
Important state includes `default_gov`, `pretimeout_list`, `governor_list`, `pretimeout_lock`, and `governor_lock`. Internal wrappers are `struct watchdog_pretimeout` and `struct governor_priv`. Public functions are `watchdog_register_governor`, `watchdog_unregister_governor`, `watchdog_register_pretimeout`, `watchdog_unregister_pretimeout`, `watchdog_notify_pretimeout`, `watchdog_pretimeout_available_governors_get`, `watchdog_pretimeout_governor_get`, and `watchdog_pretimeout_governor_set`.

## Control flow
Governors register by name under `governor_lock`; duplicate names fail. If the registered name matches `WATCHDOG_PRETIMEOUT_DEFAULT_GOV`, it becomes `default_gov` and is assigned to pretimeout-capable devices without an explicit governor. Watchdog registration allocates a list entry when `watchdog_have_pretimeout(wdd)` is true and initializes `wdd->gov`. Sysfs set resolves a governor by `sysfs_streq` and updates `wdd->gov`. Pretimeout notification takes the spinlock and calls the selected governor callback if present.

## State and persistence
The lists are global runtime state. Device-to-governor binding lives in `wdd->gov` and changes with sysfs writes or governor unregister. There is no persistent storage; settings reset when devices or governors unregister.

## Dependencies and integration points
It depends on the watchdog core, sysfs formatting helpers, slab allocation, mutexes, spinlocks, and list APIs. It integrates with `watchdog_dev.c` sysfs attributes and with pretimeout governor modules such as noop or panic governors.

## Risks and test signals
Risks include callbacks invoked while holding `pretimeout_lock`, governor module unload races, default governor replacement semantics, allocation failure during watchdog registration, and sysfs writes racing notification. Test signals include duplicate governor registration, default governor late registration, unregistering the active governor, devices without pretimeout support, sysfs list/get/set paths, and notification while governors are absent.
