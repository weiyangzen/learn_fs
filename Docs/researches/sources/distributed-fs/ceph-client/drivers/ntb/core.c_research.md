# sources/distributed-fs/ceph-client/drivers/ntb/core.c

## Purpose

This file implements the generic Linux NTB bus/framework. Hardware drivers register `struct ntb_dev` instances on the `ntb` bus, and client drivers register `struct ntb_client` drivers that bind to those devices. The core also manages client context callbacks for link, doorbell, and message events and provides default two-port topology helpers.

## Important APIs, types, and functions

Exported framework APIs include `__ntb_register_client()`, `ntb_unregister_client()`, `ntb_register_device()`, `ntb_unregister_device()`, `ntb_set_ctx()`, `ntb_clear_ctx()`, `ntb_link_event()`, `ntb_db_event()`, `ntb_msg_event()`, `ntb_default_port_number()`, `ntb_default_peer_port_count()`, `ntb_default_peer_port_number()`, and `ntb_default_peer_port_idx()`.

The internal bus callbacks are `ntb_probe()`, `ntb_remove()`, and `ntb_dev_release()`. `ntb_bus` is registered at module init and unregistered at exit.

## Control flow and state behavior

Client registration validates `ntb_client_ops`, initializes the embedded `driver`, assigns the NTB bus, module owner, and driver name, then calls `driver_register()`. Device registration validates the NTB device, PCI device, and hardware ops, initializes the release completion, sets the bus, parent, release method, device name from `pci_name()`, clears client context, initializes `ctx_lock`, and calls `device_register()`.

When a client binds, `ntb_probe()` takes a device reference, converts the generic device/driver to NTB types, and calls the client's probe. If probe fails, it drops the reference. Remove invokes the client's remove callback and drops the reference. `ntb_unregister_device()` calls `device_unregister()` and waits for `ntb_dev_release()` to complete, giving hardware drivers a clear lifetime boundary before freeing the enclosing object.

Client callback context is protected by `ctx_lock`. `ntb_set_ctx()` rejects invalid ops and existing context, then stores `ctx` and `ctx_ops` under the spinlock. Clear and event-dispatch functions also use the spinlock, making event callbacks callable from interrupt paths but requiring callbacks to obey atomic-context constraints if invoked there.

## Dependencies and integration points

The file depends on `linux/ntb.h` for NTB structures/validation helpers, PCI for parent naming, and the Linux driver core bus API. Hardware drivers such as AMD and EPF call `ntb_register_device()` and event helpers; client drivers call `ntb_register_client()` wrappers and `ntb_set_ctx()`.

## Risks and edge cases

Event callbacks run while `ctx_lock` is held, so callback implementations must not call back into APIs that attempt to take the same lock or sleep if the event comes from IRQ context. `ntb_set_ctx()` checks `ntb->ctx_ops` before acquiring the spinlock, so concurrent double-set attempts rely on external client serialization. Lifetime is tied to reference balancing in probe/remove and release completion; missing `put_device()` paths would leak NTB devices.

## Test signals

Validation should include registering/unregistering dummy hardware devices and clients, failed client probe paths, context set/clear rejection paths, event dispatch with and without callbacks, unregister waiting for release, and default topology helper outputs for primary, secondary, B2B upstream/downstream, and invalid topology.
