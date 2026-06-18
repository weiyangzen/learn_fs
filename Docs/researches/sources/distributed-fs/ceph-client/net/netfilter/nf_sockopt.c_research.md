# sources/distributed-fs/ceph-client/net/netfilter/nf_sockopt.c

## Purpose

`nf_sockopt.c` is the registry and dispatcher for legacy netfilter socket options. Netfilter modules register protocol-family-specific getsockopt and setsockopt numeric ranges, and this file routes user-context socket option calls to the owning module while preventing overlapping ranges.

## Important APIs, types, and functions

- `nf_sockopt_mutex` protects the global `nf_sockopts` list.
- `overlap()` checks exclusive numeric ranges.
- `nf_register_sockopt()` validates that a new `struct nf_sockopt_ops` does not overlap existing set or get ranges for the same protocol family, then links it into the registry.
- `nf_unregister_sockopt()` removes a registered ops block.
- `nf_sockopt_find()` searches by protocol family, option value, and get/set direction, acquiring a module reference with `try_module_get()`.
- `nf_setsockopt()` and `nf_getsockopt()` dispatch to the selected operation and release the module reference afterward.

## Control flow

Registration takes the mutex, walks all existing registrations, and compares both set and get ranges for the same `pf`. Any overlap returns `-EBUSY`; otherwise the new ops is added to `nf_sockopts`. Dispatch calls `nf_sockopt_find()`, which walks the list under the same mutex. For each matching protocol family it first tries to pin the owner module. If the requested value falls inside the relevant exclusive range, it returns that ops with the module pinned. If not, it drops the module reference and continues. No match returns `-ENOPROTOOPT`. The public get/set wrappers invoke the callback outside the mutex and then call `module_put()`.

## State and persistence behavior

The only state is the in-kernel linked list of registered `nf_sockopt_ops` entries. It lasts until modules unregister their entries. There is no per-network-namespace split here, and the file comments explain that sockopts are registered and called from user context, so a simple mutex is sufficient and callbacks may sleep.

## Dependencies and integration points

This file depends on Linux module reference counting, list APIs, mutexes, socket types, `sockptr_t`, and netfilter internal declarations from `nf_internals.h`. It is exported to netfilter modules that still expose control surfaces through socket options rather than newer netlink interfaces.

## Risks

The registry assumes modules unregister only entries they registered. Dispatch correctness depends on exclusive opt ranges and proper owner pointers. `try_module_get()` before range matching is conservative but means each same-family entry briefly pins and unpins while searching. Since callbacks run after releasing the mutex, the module reference is the key lifetime guard; missing owner setup would be unsafe. Because the registry is global by protocol family, option number allocation conflicts can block module load with `-EBUSY`.

## Test signals

Useful coverage includes registering non-overlapping and overlapping ranges, get and set dispatch to the right callback, `-ENOPROTOOPT` for unknown values, module reference behavior when an owner cannot be pinned, unregister followed by no-match behavior, and callback paths that sleep to confirm the mutex is not held during operation execution.
