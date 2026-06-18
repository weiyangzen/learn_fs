
# sources/distributed-fs/ceph-client/drivers/md/dm-path-selector.c

## Purpose
Implements the registry for dm multipath path selector types. Selectors such as round-robin or service-time register a `struct path_selector_type`; the multipath target looks them up by name during table construction.

## Important APIs, Types, And Functions
`struct ps_internal` copies a public `path_selector_type` and links it into `_path_selectors`. `_ps_lock` is an rwsem protecting the registry. `__find_path_selector_type()` searches by name. `dm_get_path_selector()` tries the current registry, requests module `dm-<name>` if absent, and returns a module-referenced type. `dm_put_path_selector()` drops the module reference if the type remains registered. `dm_register_path_selector()` rejects duplicate names and stores a copied descriptor. `dm_unregister_path_selector()` removes and frees the internal copy.

## Control Flow
Path selector modules call register at module init and unregister at exit. Multipath construction calls `dm_get_path_selector()`, then invokes the returned type's `create` and `add_path` callbacks. Destruction calls selector `destroy` and `dm_put_path_selector()`. Lookup uses a read lock plus `try_module_get()`; registration/unregistration use the write lock.

## State And Persistence
State is a process-lifetime in-kernel linked list of registered selector descriptors. There is no persistence. The registry stores a copy of the descriptor, not the caller's original object.

## Dependencies And Integration Points
Depends on Linux module reference counting, rwsems, list APIs, slab allocation, and `dm-path-selector.h`. It integrates directly with `dm-mpath.c` constructor/destructor flows and selector modules named for `request_module("dm-%s")`.

## Risks
Unregistering a selector still in use would be unsafe unless module references prevent module exit. The copied descriptor means later mutations to the original type object are not reflected. `dm_put_path_selector()` searches by name before module_put; mismatched names or double unregister can trigger warnings or leaks.

## Test Signals
Test duplicate registration, unregister unknown selector warning, module autoload by name, module reference balancing across table create/destroy failures, concurrent lookup/register/unregister, and multipath table construction with missing selector modules.
