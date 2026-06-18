# sources/distributed-fs/ceph-client/drivers/md/dm-target.c

## Purpose
Implements the DM target registry and built-in `error` target. The registry allows target modules to register by name, be autoloaded, and be referenced safely during table construction.

## Important APIs, Types, And Functions
The global `_targets` list is protected by `_lock`. Public functions are `dm_get_target_type()`, `dm_put_target_type()`, `dm_target_iterate()`, `dm_register_target()`, and `dm_unregister_target()`. The error target optionally stores `struct io_err_c` with a backing device and start sector and implements bio/request failure, device iteration, queue hints, DAX failure, and optional zoned reporting.

## Control Flow
Table loading calls `dm_get_target_type()`, which looks up a target, attempts `request_module("dm-%s")` if absent, and returns with a module reference held. Modules register/unregister under the write lock. The error target constructor accepts zero args or `<dev> <sector>`, then maps all bios and requests to failure while advertising discard failure as IO error rather than unsupported.

## State And Persistence
Registry state is global in-memory kernel state. Error target state is optional per-target backing-device context. Nothing is persisted on disk.

## Dependencies And Integration Points
Depends on module refs, kmod autoloading, DM core, bio/request mapping, DAX, and zoned reporting. `dm-table.c` uses the registry for every target load. `dm_target_init()` and `dm_target_exit()` register the built-in error target.

## Risks
Locking and module refs must prevent target code unload while in use. Duplicate registrations must fail, and unregistering an unknown target is fatal. The error target must keep queue-limit and zoned behavior coherent even though all IO fails.

## Test Signals
Test target module autoload, duplicate registration rejection, unregister paths, and error target bio/request failure, discard error behavior, optional backing-device queue limits, zoned reporting, and DAX `-EIO`.
