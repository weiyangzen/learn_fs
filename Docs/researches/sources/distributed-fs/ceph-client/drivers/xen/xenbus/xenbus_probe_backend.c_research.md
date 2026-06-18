# sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_probe_backend.c

## Purpose
`xenbus_probe_backend.c` implements the Xen backend bus (`xen-backend`). It enumerates backend Xenstore nodes, generates backend device IDs, emits backend uevents, registers backend drivers, watches the `backend` tree, and offers a memory-pressure reclaim hook for backend drivers.

## Important APIs, Types, And Functions
Key routines are `backend_bus_id()`, `xenbus_uevent_backend()`, `xenbus_probe_backend()`, `xenbus_probe_backend_unit()`, `backend_changed()`, `read_frontend_details()`, `xenbus_dev_is_online()`, `__xenbus_register_backend()`, `backend_probe_and_watch()`, and `backend_shrink_memory_count()`. The static `xenbus_backend` `xen_bus_type` defines root `backend`, depth 3, Linux bus name `xen-backend`, and common probe/remove handlers.

## Control Flow
On subsystem init the backend bus is registered, a Xenstore readiness notifier is installed, and a shrinker is registered. Once Xenstore is ready, `backend_probe_and_watch()` enumerates all backend devices and registers a watch on `backend`. Directory traversal follows `backend/<type>/<frontend>/<id>`, then calls common `xenbus_probe_node()`. Driver registration sets `read_otherend_details` to read `frontend-id` and `frontend`, then uses `xenbus_register_driver_common()`.

## State And Persistence
Backend device state is represented by Linux device objects and Xenstore nodes. `xenbus_dev_is_online()` reads the backend node `online` flag, which influences removal behavior in backend drivers. The shrinker holds no object count; it only triggers backend driver `reclaim_memory()` callbacks opportunistically.

## Dependencies And Integration Points
It depends on common Xenbus probe/client helpers, Linux bus and shrinker APIs, Xenstore directory reads, and backend drivers such as pciback and scsiback.

## Risks
Backend bus IDs depend on valid `frontend-id` and existing frontend path; malformed Xenstore nodes fail enumeration. The watch filter permits only one pending frontend state event per watch, which avoids queue buildup but can coalesce transitions. Shrinker callbacks must avoid blocking if a device is already in probe/remove due to `down_trylock()`.

## Test Signals
Create backend nodes for multiple device types/frontends, verify `MODALIAS=xen-backend:<type>` uevents, driver binding through `xenbus_register_backend()`, online-flag removal behavior, and reclaim callbacks under memory pressure.
