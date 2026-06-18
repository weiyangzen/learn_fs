# sources/distributed-fs/ceph-client/net/atm/atm_sysfs.c

Purpose: registers the ATM device class and exposes per-ATM-device attributes in sysfs.

Important APIs, types, and functions: attribute show functions include `type_show`, `address_show`, `atmaddress_show`, `atmindex_show`, `carrier_show`, and `link_rate_show`. Lifecycle functions are `atm_register_sysfs`, `atm_unregister_sysfs`, `atm_sysfs_init`, and `atm_sysfs_exit`. `atm_class` defines `.dev_release` and `.dev_uevent`.

Control flow: class init registers `atm_class`. Device registration initializes `adev->class_dev`, sets class/parent/driver data/name, calls `device_register`, then creates each attribute file. Failure removes already-created files and deletes the device. Unregistration calls `device_del`; object memory is freed by class release when the device refcount reaches zero.

State and persistence: sysfs state mirrors `struct atm_dev` fields: type, ESI MAC-like address, local ATM service addresses, device number, signal-derived carrier, and link rate. It is runtime sysfs state, not durable storage.

Dependencies and integration points: depends on device model class registration, ATM resources, `atm_dev` locks/address lists, and uevent environment construction. Userspace can discover devices through `/sys/class/atm` and uevents with `NAME=<type><number>`.

Risks: `atmaddress_show` formats all local addresses into one PAGE_SIZE buffer; many addresses can truncate output. `atm_register_sysfs` calls `device_del` on attribute failure but not `put_device`, so lifetime expectations depend on surrounding ATM registration code. Link-rate conversion has special cases and a generic cell-rate conversion.

Test signals: device register/unregister, sysfs attributes with zero/multiple local addresses, carrier changes after `atm_dev_signal_change`, uevent content, failure injection during attribute creation, and KASAN/refcount checks around class release.
