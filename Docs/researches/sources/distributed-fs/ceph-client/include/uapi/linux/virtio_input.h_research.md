<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_input.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_input.h

Purpose: defines the virtio input device UAPI used to expose keyboard, pointer, tablet, touchscreen, and other input devices through virtio queues and config-space selectors.

Important APIs and types: `enum virtio_input_config_select` selects name, serial, device IDs, property bits, event bits, and absolute-axis information. `struct virtio_input_absinfo`, `struct virtio_input_devids`, and `struct virtio_input_config` describe device capabilities. `struct virtio_input_event` mirrors Linux input events with type, code, and value fields.

Control flow, state, and persistence: drivers select config categories and subselectors to enumerate capabilities, then consume event queue entries. The header defines no persistent storage; device state is event stream and negotiated config.

Dependencies and integration points: depends on Linux integer types and integrates with virtio input drivers and the Linux input subsystem event model.

Risks and test signals: risks include bitmap sizing, endian conversion, invalid `size`, and absinfo mismatch with evdev expectations. Test device ID reads, event bitmap enumeration, absolute axes, multi-touch events, and malformed config responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_input.h -->
