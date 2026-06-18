# sources/distributed-fs/ceph-client/drivers/net/ipvlan/ipvtap.c

Purpose: Implements `ipvtap`, a tap character-device frontend layered on IPvlan. It creates rtnetlink `ipvtap` netdevices that use IPvlan forwarding semantics while exposing `/dev` tap queues for userspace packet I/O.

Important APIs and functions: `struct ipvtap_dev` embeds `struct ipvl_dev` and `struct tap_dev`, so the same private allocation supports both IPvlan and tap state. `ipvtap_newlink()` initializes tap queues and callbacks, registers `tap_handle_frame()` as the device RX handler, then delegates link creation to `ipvlan_link_new()`. `ipvtap_dellink()` unregisters the tap RX handler, deletes tap queues, and calls `ipvlan_link_delete()`. `ipvtap_device_event()` creates/destroys tap class devices and sysfs links and resizes queues. Module init/exit uses `tap_create_cdev()`, `class_register()`, netdevice notifiers, and `ipvlan_link_register()`.

Control flow: newlink sets `tap_features` to common tun offloads, wires drop-accounting and feature-update callbacks back into the embedded IPvlan stats/features, and ensures no failing operation is performed after `ipvlan_link_new()` succeeds. On `NETDEV_REGISTER`, the notifier allocates a tap minor, creates a namespaced class device named `tap<ifindex>`, and links it under the netdevice kobject. On unregister it removes the sysfs link, destroys the class device, and frees the minor. Queue length changes call `tap_queue_resize()`.

State and persistence: Persistent runtime state is the embedded `tap_dev` queue list, minor number, and tap feature mask plus the IPvlan state managed by `ipvlan_main.c`. Global module state includes `ipvtap_major`, `ipvtap_cdev`, and the `ipvtap_class`. Device nodes and sysfs links exist only while the netdevice is registered.

Dependencies and integration: Depends on the tap core (`if_tap.h`), IPvlan exported link helpers, netdevice notifier chain, class/cdev infrastructure, network namespace class support, and tun/virtio offload flags.

Risks and test signals: Risks include leaked tap minors if sysfs link creation fails after `device_create()`, RX-handler ordering with IPvlan setup, queue resize failures reported as notifier errors, and callback accounting correctness. Test module init rollback, link create/delete, `/dev/tapX` creation in netns, queue open/close and resize, tap feature updates changing IPvlan features, and traffic/drop stats through userspace tap queues.
