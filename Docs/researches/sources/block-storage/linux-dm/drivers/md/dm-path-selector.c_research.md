# File Research: sources/block-storage/linux-dm/drivers/md/dm-path-selector.c

## Purpose

`dm-path-selector.c` implements registration, lookup, module reference management, and unregister for multipath path selector types.

## Registry

The registry stores private `ps_internal` wrappers containing a copied `path_selector_type` and a list node. `_path_selectors` is protected by `_ps_lock`, an rwsem. Lookup compares selector names. `dm_register_path_selector()` copies the provided type, rejects duplicates with `-EEXIST`, and inserts it under the write lock. `dm_unregister_path_selector()` removes the registered copy and frees it.

## Lookup And Module Loading

`dm_get_path_selector()` first looks up the selector and attempts `try_module_get()` under the read lock. If not found, it requests module `dm-<name>` and retries. `dm_put_path_selector()` finds the registered selector by name and drops the module reference if it is still registered.

## Invariants And Risks

- Registered selector structs are copied, so later mutation of the caller’s static `path_selector_type` is not reflected.
- Module references are taken only for found registered selectors.
- Unregister frees the internal copy; callers must not retain stale selector pointers beyond the get/put contract.
- The name string itself is copied only as a pointer inside the struct copy, so selector modules must keep names static or otherwise stable.

## Test Focus

Test duplicate registration, unregister of missing selectors, autoload success/failure, get/put around concurrent unregister, module reference balancing, and selectors with stable static name storage.
