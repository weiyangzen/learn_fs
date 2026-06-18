# File Research: sources/block-storage/linux-dm/drivers/md/dm-target.c

## Purpose
Maintains the global registry of DM target types and provides the built-in `error` target.

## Target Registry
- `_targets`: global list of registered `struct target_type`.
- `_lock`: rwsem protecting target lookup, registration, iteration, and module refcount updates.

## Public Surface
- `dm_get_target_type()` looks up a target, requests module `dm-<name>` if missing, then retries lookup.
- `dm_put_target_type()` drops the module reference.
- `dm_target_iterate()` iterates registered target types under read lock.
- `dm_register_target()` adds a target type unless the name already exists.
- `dm_unregister_target()` removes a target type and BUGs if it is not registered.
- Exports `dm_register_target` and `dm_unregister_target`.

## Built-in Error Target
- Name: `error`
- Version: `{1, 5, 0}`
- Feature: `DM_TARGET_WILDCARD`
- Constructor sets `num_discard_bios = 1` so discards fail as I/O errors instead of unsupported operations.
- Bio and request mapping always return `DM_MAPIO_KILL`.
- DAX direct access returns `-EIO`.

## Control Flow
- `dm_target_init()` registers the built-in error target.
- `dm_target_exit()` unregisters it.
- Module autoload uses `request_module("dm-%s", name)`.

## Risk and Test Focus
- Registry operations rely on callers balancing `dm_get_target_type()` and `dm_put_target_type()`.
- Duplicate registrations return `-EEXIST`; unregistering an unknown target is fatal.
- Error target is the fallback for holes or deliberately failing table regions, so discard/request/DAX behavior should stay consistently failing.
