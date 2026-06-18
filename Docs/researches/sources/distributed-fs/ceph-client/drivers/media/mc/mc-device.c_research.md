# sources/distributed-fs/ceph-client/drivers/media/mc/mc-device.c

Purpose: implements the media-controller device object, userspace ioctls for graph/topology/link/request allocation, entity registration/unregistration, sysfs/debugfs hooks, and PCI/USB initialization helpers.

Important APIs/types/functions: userspace ioctl handlers include `media_device_get_info()`, `media_device_enum_entities()`, `media_device_enum_links()`, `media_device_setup_link()`, `media_device_get_topology()`, and `media_device_request_alloc()`. Registration exports include `media_device_init()`, `media_device_cleanup()`, `__media_device_register()`, `media_device_unregister()`, `media_device_register_entity()`, `media_device_unregister_entity()`, entity notify registration, `media_device_pci_init()`, and `__media_device_usb_init()`.

Control flow: device registration allocates a `media_devnode`, installs media-device file ops, registers `/dev/mediaX`, creates the model sysfs attribute, and optionally debugfs request counters. Ioctls copy arguments into a stack or heap buffer, optionally take `graph_mutex`, execute the handler, and copy results back. Entity registration assigns an internal ID, creates graph objects for entity and pads, calls notifiers, and resizes the PM graph walk. Unregistration clears the devnode registered bit, removes all entities, notifiers, interfaces, debugfs/sysfs, and unregisters the devnode.

State/persistence: `struct media_device` contains runtime graph lists, topology version, mutexes, IDA, request counters, bus/model/serial strings, and devnode pointer. Topology state is kernel memory only; userspace can observe it through ioctls.

Dependencies/integration: depends on `mc-devnode`, `mc-entity`, `mc-request`, Linux media uAPI structs, compat ioctl handling, debugfs, PCI/USB core helpers, and driver-provided `media_device_ops`.

Risks/test signals: topology enumeration must handle changing counts and userspace buffer sizes with `-ENOSPC`. Link setup depends on graph locking and entity callbacks. Request allocation is available only when request ops exist. Tests should cover all media ioctls, compat enum-links path, static topology version behavior, dynamic entity registration/unregistration, sysfs model read, debugfs counters, PCI/USB bus info formatting, and error unwinds after devnode registration.
