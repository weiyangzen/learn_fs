# sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_probe_frontend.c

## Purpose
`xenbus_probe_frontend.c` implements the Xen frontend bus (`xen`). It enumerates frontend device nodes under `device`, registers frontend drivers, watches backend state changes, handles frontend shutdown and PM restore, waits for boot-critical PV devices, and resets stale frontend/backend state after kexec/kdump-style transitions.

## Important APIs, Types, And Functions
Key functions include `frontend_bus_id()`, `xenbus_probe_frontend()`, `xenbus_uevent_frontend()`, `xenbus_frontend_dev_probe()`, `xenbus_frontend_dev_shutdown()`, `read_backend_details()`, `wait_for_devices()`, `__xenbus_register_frontend()`, `xenbus_reset_state()`, and `frontend_probe_and_watch()`. The static `xenbus_frontend` bus uses root `device`, depth 2, Linux bus name `xen`, common probe/remove handlers, shutdown, and PM ops.

## Control Flow
Subsystem init registers the frontend bus and a Xenstore readiness notifier. Once ready, it optionally resets HVM frontend state, enumerates `device/<type>/<id>`, and watches `device`. Probe ignores legacy `console/0`, creates bus IDs as `<type>-<id>`, reads backend details, probes the matched driver, and watches the backend state. Shutdown moves connected devices to `Closing` and waits briefly for `xenbus_frontend_closed()`. Late init waits for nonessential devices up to 30 seconds and essential devices up to a total 270 seconds before warning.

## State And Persistence
Frontend state is stored both in `xenbus_device.state` and Xenstore node `state`. `ready_to_wait_for_devices` gates boot waiting. `backend_state` plus `backend_state_wq` coordinate reset-state waits. Device readiness can also depend on a driver's optional `is_ready()` callback.

## Dependencies And Integration Points
It depends on common Xenbus probe helpers, Xenstore directory/watch APIs, Linux bus/PM/shutdown model, platform PCI callback readiness for HVM, and frontend drivers registered through `xenbus_register_frontend()`.

## Risks
Boot can stall on devices that never connect, though bounded by timeouts. Resetting frontend state must coordinate with backend transitions to avoid stale `Connected` or `Closed` nodes. Local Xenstore restore is deferred via workqueue because backend state is temporarily inaccessible. Shutdown ignores non-connected devices.

## Test Signals
Boot with PV block/net/input frontends, module-load a frontend driver and observe wait behavior, simulate backend state changes, test kexec/kdump reconnect paths, suspend/resume with local Xenstore, and verify `MODALIAS=xen:<type>` uevents.
