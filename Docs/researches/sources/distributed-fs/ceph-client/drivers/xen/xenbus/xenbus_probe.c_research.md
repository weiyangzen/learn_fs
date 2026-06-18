# sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_probe.c

## Purpose
`xenbus_probe.c` is the common Xenbus probe and Xenstore initialization layer. It initializes access to the Xenstore shared interface for PV, HVM, and local xenstored modes, exposes global Xenstore state, registers readiness notifiers, provides common Linux device probe/remove helpers, handles otherend watches, and creates/destroys `xenbus_device` instances from Xenstore paths.

## Important APIs, Types, And Functions
Exports include `xen_store_evtchn`, `xen_store_interface`, `xen_store_domain_type`, `xenbus_match()`, `xenbus_read_otherend_details()`, `xenbus_otherend_changed()`, `xenbus_dev_probe()`, `xenbus_dev_remove()`, `xenbus_register_driver_common()`, `xenbus_unregister_driver()`, `xenbus_probe_node()`, `xenbus_probe_devices()`, `xenbus_dev_changed()`, suspend/resume helpers, and Xenstore notifier registration. Init functions include `xenbus_init()` and `xenbus_probe_initcall()`.

## Control Flow
Early init determines Xenstore mode: PV start-info event channel/page, HVM hvm_params, or local dom0 allocation. It initializes ring ops, maps the interface, binds late-init IRQs if HVM Xenstore is not ready, calls `xs_init()` when safe, and registers resume notifiers. When Xenstore becomes ready, `xenbus_probe()` marks readiness, maps late HVM interface if needed, frees temporary IRQs, initializes XS for deferred HVM, and notifies frontend/backend probe modules. Device probing allocates `xenbus_device`, derives bus id, registers with the Linux device model, calls the matched Xenbus driver's probe under reclaim semaphore, and installs otherend state watches.

## State And Persistence
Global state includes Xenstore event channel, interface pointer, store GFN, store domain type, readiness flag, and notifier chain. Each `xenbus_device` stores nodename, devicetype, otherend path/id, state, vanished flag, completion, reclaim semaphore, and sysfs attributes/stat counters.

## Dependencies And Integration Points
It depends on Xen HVM/PV platform data, event channels, memory remapping, Xenstore XS helpers, Linux bus/device model, notifiers, PM callbacks, and frontend/backend probe files.

## Risks
Risks include HVM Xenstore not yet ready, invalid store PFN values, backend crash causing frontend state reset, vanished Xenstore nodes, shutdown-time watch events, and stale otherend details after resume. The code handles these with deferred probe threads, vanished flags, re-reading otherend details, and state checks.

## Test Signals
Boot PV, HVM, and dom0/local Xenstore cases; verify frontend/backend buses populate after Xenstore readiness, sysfs device attributes exist, suspend/resume restores watches, backend restart triggers reconnect, and Xenstore notifier callbacks fire exactly once when ready.
