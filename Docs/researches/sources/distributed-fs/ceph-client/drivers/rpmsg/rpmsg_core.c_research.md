# sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_core.c

Purpose: generic rpmsg bus core. It registers the `rpmsg` class and bus, provides exported helper APIs for endpoint/channel/message operations, handles driver matching/probe/remove, and exposes rpmsg device sysfs attributes.

Important APIs, types, and functions: exported wrappers include `rpmsg_create_channel()`, `rpmsg_release_channel()`, `rpmsg_create_ept()`, `rpmsg_destroy_ept()`, `rpmsg_send()`, `rpmsg_sendto()`, `rpmsg_trysend()`, `rpmsg_trysendto()`, `rpmsg_poll()`, `rpmsg_set_flow_control()`, `rpmsg_get_mtu()`, `rpmsg_find_device()`, `rpmsg_register_device_override()`, `rpmsg_register_device()`, `rpmsg_unregister_device()`, `__register_rpmsg_driver()`, and `unregister_rpmsg_driver()`. `rpmsg_class` and the private `rpmsg_bus` are central objects.

Control flow: backend transports create `rpmsg_device` instances with ops and call `rpmsg_register_device()`. The bus matches devices by `driver_override`, rpmsg id table service name, or OF match. During probe, the core attaches a PM domain, creates a default endpoint if the driver supplied a callback, calls the driver's probe, and optionally announces channel creation to the remote. Remove announces destruction, calls driver remove, and destroys the default endpoint. Message APIs validate pointers and dispatch to endpoint ops supplied by the backend.

State and persistence: core state lives in the Linux driver model: class, bus, devices, drivers, sysfs attributes, driver overrides, and endpoint pointers stored in `rpdev`. No messages are persisted in the core; backends own queues and buffers.

Dependencies and integration points: depends on `rpmsg_internal.h` operation tables, Linux device model, OF modalias helpers, PM domains, and backend transports such as virtio, GLINK, and SMD. Userspace sees sysfs attributes `name`, `src`, `dst`, `announce`, `driver_override`, and `modalias`.

Risks: backend ops are only partially checked; missing required endpoint ops can surface as `-ENXIO` or backend crashes. Probe error paths must destroy endpoints and detach state through the driver model correctly. `driver_override` changes affect matching and modalias behavior. Destroy announcement runs before driver remove and endpoint destruction.

Test signals: register/unregister rpmsg drivers, dynamic channel create/release, service-name and OF matching, driver override sysfs store/show, default endpoint creation, announce_create/destroy callbacks, PM domain attach failures, send wrappers against missing ops, and class/bus init/exit.
