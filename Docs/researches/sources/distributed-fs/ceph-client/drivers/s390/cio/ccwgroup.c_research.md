# sources/distributed-fs/ceph-client/drivers/s390/cio/ccwgroup.c

Purpose: implements the ccwgroup bus, allowing multiple ccw slave devices to be grouped into one higher-level device for drivers that need multi-subchannel units.

Important APIs/types/functions: exports `ccwgroup_set_online`, `ccwgroup_set_offline`, `ccwgroup_create_dev`, `dev_is_ccwgroup`, `ccwgroup_driver_register`, `ccwgroup_driver_unregister`, `ccwgroup_probe_ccwdev`, and `ccwgroup_remove_ccwdev`. Defines sysfs attributes `online` and `ungroup`, symlink helpers, bus type `ccwgroup_bus_type`, and notifier-driven ungroup work.

Control flow: create parses comma-separated bus ids, gets ccw devices, verifies same driver and driver_info, prevents devices from being in multiple groups by setting ccw drvdata under lock, optionally calls group driver setup, adds the group device, and creates bidirectional sysfs links. Online/offline call group driver hooks under an atomic on/off gate. Ungroup removes sysfs links and unregisters the group only when offline.

State and persistence: `struct ccwgroup_device` owns the grouped ccw device references, online/offline state, registration mutex, on/off atomic gate, and ungroup work. State is runtime-only and removed on ungroup or slave removal.

Dependencies and integration: depends on ccw device lookup and locks, Linux driver core bus/driver/device APIs, sysfs links, bus notifiers, and external `struct ccwgroup_driver` definitions from asm headers.

Risks: create/unwind must clear drvdata and put device refs via release; online/offline/ungroup races are serialized with `onoff`; if any slave ccw device disappears, the whole group is unregistered; bus id parsing is strict and ignores cssid in stored id beyond parsed fields.

Test signals: group creation with valid/invalid bus lists, duplicate grouping rejection, sysfs online/offline/ungroup, group driver unbind notifier, slave removal teardown, and driver register/unregister paths.
