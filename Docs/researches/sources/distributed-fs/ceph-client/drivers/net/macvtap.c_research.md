# sources/distributed-fs/ceph-client/drivers/net/macvtap.c

Purpose: Implements `macvtap`, a tap character-device frontend for MACVLAN. It lets userspace open tap queues for a MACVLAN-like virtual device while preserving MACVLAN forwarding modes and lower-device integration.

Important APIs and functions: `struct macvtap_dev` embeds `struct macvlan_dev` and `struct tap_dev`. `macvtap_newlink()` initializes the tap queue list, offload feature mask, and accounting/feature callbacks, registers `tap_handle_frame()` as the MACVTAP device RX handler, and delegates creation to `macvlan_common_newlink()`. `macvtap_dellink()` unregisters the tap RX handler, deletes tap queues, and calls `macvlan_dellink()`. `macvtap_device_event()` owns tap minor allocation, class device creation/destruction, sysfs links, and queue resizing.

Control flow: module init creates the tap cdev, registers the namespaced class, registers the netdevice notifier, then registers a `macvtap` rtnetlink kind through `macvlan_link_register()` so it inherits MACVLAN validation/fill/changelink behavior. Netdevice registration events create `/dev` nodes named `tap<ifindex>` before register_netdevice completes. Unregister events reverse sysfs/device/minor state, and TX queue length changes resize tap queues.

State and persistence: Global state is `macvtap_major`, `macvtap_cdev`, and `macvtap_class`. Per-device state is the embedded tap queue/minor state plus embedded MACVLAN state. The character device and sysfs link are runtime artifacts tied to the netdevice lifetime.

Dependencies and integration: Depends on the tap core, MACVLAN exported helpers, network namespace class support, cdev/class/device APIs, netdevice notifier chain, tun/virtio offload flags, and rtnetlink.

Risks and test signals: Risks are minor/class-device leaks on partial notifier failures, ordering between tap RX handler and MACVLAN creation, feature update propagation to `vlan->set_features`, and queue resize errors. Test module init rollback, create/delete in multiple namespaces, device-node/sysfs lifetime, userspace tap queue open/close and traffic, feature negotiation, and lower MACVLAN mode behavior through macvtap links.
