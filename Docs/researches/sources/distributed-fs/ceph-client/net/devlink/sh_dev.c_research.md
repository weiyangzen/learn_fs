
# sources/distributed-fs/ceph-client/net/devlink/sh_dev.c

## Purpose
This file implements shared devlink instances keyed by a string identifier such as a serial number. It lets multiple callers obtain the same devlink object and shared driver-private storage when they represent the same underlying device, while enforcing that all callers agree on ops, private size, and driver identity.

## Important APIs, Types, And Functions
`struct devlink_shd` is embedded in the devlink private area. It stores a global-list node, duplicated identifier string, reference count, private data size, and aligned flexible private-data bytes.

Internal helpers are `devlink_shd_lookup()`, `devlink_shd_create()`, and `devlink_shd_destroy()`. Exported APIs are `devlink_shd_get()`, `devlink_shd_put()`, and `devlink_shd_get_priv()`.

## Control Flow
`devlink_shd_get()` takes the global `shd_mutex`, looks for an existing shared object by ID, and creates one if absent. Creation allocates a devlink with `__devlink_alloc()` in `init_net`, duplicates the ID, sets refcount and private size, registers the devlink under the devlink lock, and adds it to the global list.

If an existing ID is found, `devlink_shd_get()` verifies that `ops`, `priv_size`, and `driver` match the existing devlink. A mismatch triggers `WARN_ON_ONCE()` and returns `NULL`. Otherwise it increments the shared refcount and returns the owning `struct devlink`.

`devlink_shd_put()` takes the same mutex, decrements the refcount, and destroys the shared devlink when the count reaches zero. Destruction removes it from the list, unregisters the devlink, frees the duplicated ID, and frees the devlink object. `devlink_shd_get_priv()` returns the private payload after the `struct devlink_shd` header.

## State And Persistence
Shared state is process-kernel memory only: the global `shd_list`, each shared devlink instance, the ID string, refcount, and private payload. There is no persistence across module unload or reboot. The shared devlink is registered while the first reference exists and unregistered when the last reference is put.

## Dependencies And Integration Points
The file depends on `net/devlink.h`, `devl_internal.h`, `__devlink_alloc()`, `devlink_priv()`, `priv_to_devlink()`, `devl_register()`, `devl_unregister()`, and `devlink_free()`. Drivers such as mlx5 shared-device support use this API to group physical functions by serial/VPD-derived identity.

## Risks And Edge Cases
All global-list and refcount manipulation is serialized by `shd_mutex`, so lookup/create/put are straightforward. The main risk is caller discipline: every successful `devlink_shd_get()` must be paired with `devlink_shd_put()`, and all callers for a given ID must pass identical ops, private size, and driver pointer.

`devlink_shd_create()` does not check the return value of `devl_register()`. In current devlink internals this may be expected to be void, but if registration semantics change this path would need revisiting. The API uses `init_net` and a `NULL` device, so consumers should be aware that the shared instance is not tied to an individual device object.

## Test Signals
Useful tests are paired get/put creating and destroying exactly one shared instance, repeated get with matching metadata increasing the refcount, mismatched metadata returning `NULL`, private pointer alignment and isolation, and driver unload paths that must release all references. Existing mlx5 shared-devlink usage in this tree is the main integration signal.
