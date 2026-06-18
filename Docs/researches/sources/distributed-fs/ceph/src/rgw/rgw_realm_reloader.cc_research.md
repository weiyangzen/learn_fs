# sources/distributed-fs/ceph/src/rgw/rgw_realm_reloader.cc

## Purpose

Implements dynamic RGW realm reconfiguration. `RGWRealmReloader` reacts to realm notifications by pausing frontends, shutting down the current storage driver, reloading site configuration, creating a new driver, reinitializing dependent subsystems, and resuming frontends.

## Important APIs, Types, and Functions

`RGWRealmReloader` constructor initializes a `SafeTimer`; destructor shuts it down. `C_Reload` is a timer context that calls `reload()`. `handle_notify()` schedules one reload and wakes any retry loop. `reload()` performs the full driver replacement and subsystem reinitialization.

## Control Flow and Data Flow

Notifications are ignored while `env.driver` is null, which means reload is already in progress. Otherwise `handle_notify()` locks, avoids duplicate scheduled reloads, creates a `C_Reload`, wakes waiters, and schedules it immediately. `reload()` pauses frontends, finalizes usage logging, shuts down and closes the old driver, clears `env.driver`, then releases the scheduled marker early so later notifications are not missed.

The reload loop repeatedly loads `env.site` from the config store and attempts `DriverManager::get_storage()`. If creation fails, it waits on a condition variable until a new notification arrives. If a new notification arrives after a driver is created but before completion, it cancels that scheduled event, closes the just-created driver outside the lock, and loops again. Once stable, it registers the service map, reinitializes REST, usage logging, auth registry, Lua manager/background hooks, and resumes frontends with the new driver.

## State and Persistence Behavior

The class mutates process-local runtime state in `RGWProcessEnv`: driver pointer, site config, auth registry, Lua manager bindings, and service map registration. It does not directly write realm metadata, but it consumes persisted config-store periods/realms. It intentionally tolerates bad persisted realm config by waiting and retrying instead of aborting the process.

## Dependencies and Integration Points

Depends on `RGWProcessEnv`, auth registry, bucket/log/REST initialization, RADOS SAL driver manager, zone service, Lua manager, service map registration, `SafeTimer`, and frontend pause/resume abstraction. It is registered as an `RGWRealmWatcher::Watcher`.

## Risks and Edge Cases

`reload()` captures `cct` from the old driver before closing it and continues using it. Duplicate notifications are coalesced, but timing between clearing `reload_scheduled` and site load is subtle. Frontends must honor `pause()` or old driver use-after-close is possible. Constructor initializes `timer` with `env.driver->ctx()` before `mutex` member initialization order in the class definition, so member declaration order matters. Failure loops can leave frontends paused until a valid config arrives.

## Test Signals

Cover single notification reload, duplicate notification coalescing, notification during reload causing restart, driver creation failure followed by retry, service map registration failure ignored, Lua manager replacement for RADOS and non-RADOS drivers, frontend pause/resume ordering, destructor cancelling scheduled timer events, and behavior when notification arrives while `env.driver` is null.
