# sources/distributed-fs/ceph-client/drivers/dpll/dpll_netlink.c

## Purpose
This file is the hand-written generic-netlink implementation for the Linux DPLL management framework. It translates userspace `dpll` netlink commands into DPLL core object lookups, driver callback calls, state changes, dumps, and multicast notifications. It is the behavioral half paired with the generated family definition in `dpll_nl.c`.

## Important APIs, types, and functions
The public notification APIs are `dpll_device_create_ntf()`, `dpll_device_delete_ntf()`, `dpll_device_change_ntf()`, `dpll_pin_create_ntf()`, `dpll_pin_delete_ntf()`, `__dpll_pin_change_ntf()`, and `dpll_pin_change_ntf()`. Netlink handlers include `dpll_nl_device_id_get_doit()`, `dpll_nl_device_get_doit()`, `dpll_nl_device_get_dumpit()`, `dpll_nl_device_set_doit()`, `dpll_nl_pin_id_get_doit()`, `dpll_nl_pin_get_doit()`, `dpll_nl_pin_get_dumpit()`, and `dpll_nl_pin_set_doit()`. Locking/preload hooks are `dpll_pre_doit()`, `dpll_post_doit()`, `dpll_lock_doit()`, `dpll_unlock_doit()`, `dpll_pin_pre_doit()`, and `dpll_pin_post_doit()`. Helpers serialize device attributes, pin attributes, parent relationships, supported frequency ranges, embedded sync, reference sync, measured frequency, fractional frequency offset, phase offset, phase adjustment, temperature, lock status, mode, and monitoring feature states.

## Control flow
GET paths allocate a reply skb, add a generic-netlink header, locate the requested registered object either by numeric ID or by identity attributes, serialize the object, end the message, and reply. Dump paths iterate `dpll_device_xa` or `dpll_pin_xa` from a saved callback cursor, stopping cleanly on `-EMSGSIZE`. SET paths walk the attributes in the original message and dispatch to narrowly scoped setters. Device setters validate supported mode/monitor operations before calling driver ops. Pin setters validate capability bits, frequency ranges, phase range/granularity, parent object existence, and reference-sync pair availability. Multi-DPLL pin operations such as frequency, phase adjust, esync, and reference sync update every DPLL reference for a shared pin and attempt rollback to the old value on partial failure.

## State and persistence
The file does not own persistent hardware state. It reads and writes framework state stored in `dpll_device`, `dpll_pin`, `dpll_pin_ref`, global xarrays, and driver-private state accessed through DPLL ops. State changes persist only through the lower driver callbacks. `dpll_lock` protects object lookup, serialization, and mutations in doit paths; dump paths lock around each traversal. Notifications update DPLL core notification state before multicasting a snapshot of the changed object.

## Dependencies and integration points
The implementation depends on `dpll_core.h` for object internals and xarrays, `dpll_nl.h` for generated family declarations and policies, `uapi/linux/dpll.h` for ABI constants, and generic netlink helpers. Driver integration is entirely via `struct dpll_device_ops` and `struct dpll_pin_ops`; the ZL3073x driver in this group supplies one such implementation.

## Risks and edge cases
Message construction must preserve ABI units, especially FFO in legacy PPM plus PPT and phase/frequency values using 64-bit netlink attributes. Rollback failures are reported but cannot fully restore a partially updated shared pin. `dpll_pin_available()` filters objects by registration marks and parent availability, so stale pins are hidden but callers must still hold the framework lock. The code assumes mandatory ops exist where the core contract requires them; missing driver ops become `-EOPNOTSUPP` for optional features.

## Test signals
Useful tests are YNL/netlink round trips for every command, dump pagination with small skb sizes, duplicated or missing lookup attributes, invalid modes/states/frequencies, rollback fault injection on multi-DPLL shared pin updates, multicast monitor reception, and lockdep coverage for pre/post hooks.
