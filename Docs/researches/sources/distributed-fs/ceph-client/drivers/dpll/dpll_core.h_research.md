# sources/distributed-fs/ceph-client/drivers/dpll/dpll_core.h

## Purpose

This private header defines the internal DPLL core object model shared by `dpll_core.c` and the DPLL netlink implementation. It exposes internal structs for devices, pins, and references, declares global xarrays and the global mutex, and provides helper prototypes used to retrieve provider ops/private data and send notifications.

## Important Types and APIs

`struct dpll_device` stores the subsystem ID, provider index, clock ID, owning module, DPLL type, pin reference xarray, refcount/ref-tracker state, and registration list. `struct dpll_pin` stores subsystem and provider indexes, clock ID, module, optional firmware node, xarrays for DPLL refs, parent refs, and reference-sync pins, copied pin properties, refcount/ref-tracker state, and an RCU head. `struct dpll_pin_ref` is a tagged reference to either a DPLL or parent pin with a registration list and refcount.

The header defines `DPLL_REGISTERED` as `XA_MARK_1`, the mark used in global xarrays to distinguish registered objects from merely allocated objects. It declares helper functions such as `dpll_priv()`, `dpll_pin_on_dpll_priv()`, `dpll_pin_on_pin_priv()`, `dpll_device_ops()`, `dpll_device_get_by_id()`, `dpll_pin_ops()`, `dpll_xa_ref_dpll_first()`, `dpll_device_notify()`, and `dpll_pin_notify()`.

## Control Flow and Integration

Netlink code includes this header to traverse registered DPLL objects, resolve references, and call provider callbacks with the right private pointers. Core code owns the backing storage and enforces locking; users of this header are expected to respect `dpll_lock` when walking or mutating xarrays and registration lists. The public API surface remains in `include/linux/dpll.h`; this header intentionally exposes implementation details only within the DPLL subsystem.

## State and Persistence

The structs describe in-memory kernel state only. Refcounts and ref-tracker directories are per object. Xarrays store relationship state: devices to pins, pins to DPLLs, pins to parent pins, and pins to reference-sync peers. Firmware-node handles are retained by the core and released during final pin teardown.

## Risks and Test Signals

Because this header exposes concrete struct layouts to internal users, changes require coordinated updates in `dpll_core.c` and `dpll_netlink.c`. Risks include accessing registration lists without holding `dpll_lock`, assuming a `dpll_pin_ref` union member without knowing which xarray supplied it, and using helpers after an object's registered mark was cleared. Compile tests for `CONFIG_DPLL` plus functional netlink/provider tests are the primary signals that the internal contract remains valid.
