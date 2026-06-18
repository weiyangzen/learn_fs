# sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_ns.c

Purpose: rpmsg name-service driver. It receives remote name-service announcements and creates or destroys rpmsg channels for advertised services.

Important APIs, types, and functions: `rpmsg_ns_register_device()` prepares an rpmsg device for the name-service address and registers it with driver override `rpmsg_ns`. `rpmsg_ns_cb()` parses `struct rpmsg_ns_msg`. `rpmsg_ns_probe()` creates the endpoint bound to `RPMSG_NS_ADDR` and name `name_service`.

Control flow: a backend that supports name service registers a special rpmsg device through `rpmsg_ns_register_device()`. Probe creates an endpoint at source and destination `RPMSG_NS_ADDR`. Incoming announcements are length-checked, name-terminated defensively, converted to `rpmsg_channel_info` with dynamic local source and advertised remote destination, and either passed to `rpmsg_create_channel()` or `rpmsg_release_channel()` depending on `RPMSG_NS_DESTROY`.

State and persistence: no private persistent state beyond `rpdev->ept`. Created channels become normal rpmsg devices owned by the backend/core. The callback mutates the received message buffer to force NUL termination.

Dependencies and integration points: depends on `linux/rpmsg/ns.h`, rpmsg core channel helpers, byteorder helpers through `rpmsg32_to_cpu()`, and backend name-service support such as virtio feature `VIRTIO_RPMSG_F_NS`.

Risks: malformed sizes are rejected, but remote announcements still control service names and destination addresses. Duplicate creates depend on backend duplicate detection. Destroy requests for nonexistent channels log backend errors. The log message intentionally reports create/destroy decisions but has the historical `"creat"` string for create.

Test signals: send valid create and destroy NS messages, malformed lengths, unterminated maximum-length names, duplicate creates, destroy missing channel, and verify dynamic channel devices bind to matching rpmsg drivers.
