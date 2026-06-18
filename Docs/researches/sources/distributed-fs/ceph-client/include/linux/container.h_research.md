## sources/distributed-fs/ceph-client/include/linux/container.h

Purpose: This header defines the container bus device wrapper used by the base power/container subsystem.

Important APIs, types, and functions: It declares `extern const struct bus_type container_subsys`. `struct container_dev` embeds `struct device dev` and optional `offline(struct container_dev *)` callback. `to_container_dev(struct device *dev)` converts an embedded device pointer to the enclosing container device using `container_of`.

Control flow: Drivers or subsystem code use `to_container_dev()` after receiving a generic `struct device`. The `offline` callback, when present, is invoked by implementation code to offline a container.

State and persistence: State is the embedded `struct device` plus callback pointer; lifetime follows device-model registration. No state is stored in this header.

Dependencies and integration points: It depends on `linux/device.h`, the driver core bus model, and `drivers/base/power/container.c`.

Risks and test signals: Risks include applying `to_container_dev()` to a non-container device, stale callback pointers after unregister, and incorrect offline handling. Test signals include container bus registration, device hotplug, offline callback error propagation, and driver-core lifetime tests.
