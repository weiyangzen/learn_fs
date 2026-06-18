# `sources/distributed-fs/ceph-client/include/linux/if_tap.h`

Purpose: internal TAP character-device/netdevice bridge definitions, exposing queue/socket accessors, queue limits, TAP device state, and cdev/minor helpers.

Important APIs/types/functions: `tap_get_socket`, `tap_get_ptr_ring`, `MAX_TAP_QUEUES`, `struct tap_dev`, `struct tap_queue`, `tap_handle_frame`, queue deletion/resizing, minor allocation/freeing, and cdev create/destroy.

Control flow and state: `tap_dev` tracks active RCU queue pointers, all queue list entries, queue counts, features, minor, and callbacks for feature/drop accounting. `tap_queue` embeds sock/socket, virtio-net header size, ring, file, flags, queue index, and enabled state.

Dependencies/integration: depends on socket, `skb_array`/`ptr_ring`, char device infrastructure, netdevice RX handlers, and `CONFIG_TAP` stubs.

Risks: multiqueue RCU pointer lifetime, ring resizing under active traffic, disabled-config callers receiving `ERR_PTR(-EINVAL)`, file/socket lifetime coupling, and virtio header size mismatches.

Test signals: TAP open/close, multiqueue attach/detach up to queue limits, queue resize, RX handler delivery, cdev minor allocation cleanup, disabled-config compile, and virtio-net header compatibility.
