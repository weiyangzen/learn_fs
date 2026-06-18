# sources/distributed-fs/ceph-client/net/psp/psp.h

## Purpose
`psp.h` is the private PSP subsystem header shared by the core, netlink, and socket association implementation. It declares global device registry state, core helper prototypes, association helpers, and inline PSP device reference helpers.

## Important APIs, types, and functions
The header declares `extern struct xarray psp_devs` and `extern struct mutex psp_devs_lock`. Core helpers include `psp_dev_free()` and `psp_dev_check_access()`. Netlink notification is `psp_nl_notify_dev()`. Association helpers include `psp_assoc_create()`, `psp_dev_get_for_sock()`, `psp_dev_tx_key_del()`, `psp_sock_assoc_set_rx()`, `psp_sock_assoc_set_tx()`, and `psp_assocs_key_rotated()`.

Inline helpers `psp_dev_get()`, `psp_dev_tryget()`, `psp_dev_put()`, and `psp_dev_is_registered()` implement refcount handling and registered-state checks. `psp_dev_is_registered()` asserts the instance lock is held and treats non-NULL `ops` as registered.

## Control flow and state
The header itself has no complex flow. Its inline `psp_dev_put()` calls `psp_dev_free()` on the final reference, tying refcount lifetime to xarray removal and RCU freeing in `psp_main.c`.

## Dependencies and integration points
It includes `net/psp.h` for public PSP structs, networking namespace/socket headers, list/mutex/lockdep primitives, and is included by PSP implementation files. It defines the lock ordering convention used in `psp_main.c`: global `psp_devs_lock` before per-device `psd->lock`.

## Risks and edge cases
Risks center on lifetime and locking. Callers must not call `psp_dev_is_registered()` without holding `psd->lock`, must balance successful gets with puts, and must respect xarray plus RCU lifetime rules. Changing `psp_dev_put()` semantics affects every PSP device/association path.

## Test signals
Build coverage plus lockdep-enabled tests for netlink device lookup, driver unregister while netlink/socket associations hold references, key deletion paths, and final RCU freeing.
