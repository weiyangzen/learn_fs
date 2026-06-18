# sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_internal.h

Purpose: private rpmsg core/backend interface. It defines internal conversion macros, exported class declaration, backend operation tables, channel helper prototypes, and the inline control-device registration wrapper.

Important APIs, types, and functions: `to_rpmsg_device()` and `to_rpmsg_driver()` convert device model objects. `struct rpmsg_device_ops` defines backend channel and endpoint operations plus optional announce hooks. `struct rpmsg_endpoint_ops` defines endpoint destroy/send/sendto/trysend/trysendto/poll/set_flow_control/get_mtu hooks. `rpmsg_find_device()`, `rpmsg_create_channel()`, and `rpmsg_release_channel()` are declared. `rpmsg_ctrldev_register_device()` wraps `rpmsg_register_device_override(rpdev, "rpmsg_ctrl")`.

Control flow: no runtime code except the inline control registration helper. Backends fill these ops tables and the core dispatches exported rpmsg APIs through them.

State and persistence: no state is stored here; it describes function-pointer contracts used by runtime objects.

Dependencies and integration points: includes public `linux/rpmsg.h` and `linux/poll.h`. It is included by rpmsg core, virtio, Qualcomm transports, char/control drivers, and name service.

Risks: operation table comments mark required and optional hooks, but runtime enforcement is uneven. A backend with missing required ops can pass compile and fail at runtime. The header is internal, so changes affect many transport implementations.

Test signals: compile all rpmsg backends after changing ops, exercise every exported rpmsg API against transports with and without optional hooks, and confirm control-device override binding to `rpmsg_ctrl`.
