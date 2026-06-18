# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_sysfs.c

Purpose: creates the DRM sysfs class, DRM minor and connector devices, connector attributes, EDID binary attribute, Type-C and DDC links, ACPI companion mapping, hotplug/property/lease uevents, and helper registration for class devices.

Important APIs/types/functions: `drm_sysfs_init()` and `drm_sysfs_destroy()` manage global `drm_class`. `drm_sysfs_connector_add()`, `_add_late()`, `_remove_early()`, and `_remove()` manage connector devices and links. Attribute handlers expose `status`, `enabled`, `dpms`, `modes`, `connector_id`, and binary `edid`; `status_store()` also forces/reprobes connector state. Uevent helpers include `drm_sysfs_lease_event()`, `drm_sysfs_hotplug_event()`, `drm_sysfs_connector_hotplug_event()`, and `drm_sysfs_connector_property_event()`. `drm_sysfs_minor_alloc()`, `drm_class_device_register()`, and `_unregister()` handle minor and auxiliary class devices.

Control flow: sysfs init creates class `drm`, adds a version attribute, installs a devnode callback returning `dri/<name>`, and registers the ACPI bus type. Connector add allocates a device, sets class/type/parent/groups/driver data/name, registers it, saves `connector->kdev`, and adds a Type-C component link if firmware node exists. Late add creates a DDC symlink. Status writes lock `mode_config.mutex`, update force state from strings, and invoke `fill_modes()` when force changes or detect is requested. Uevent helpers build environment strings and emit `KOBJ_CHANGE`.

State and persistence behavior: global `drm_class` persists between DRM core init and exit. Connector `kdev` persists while registered and is freed by `drm_sysfs_release()`. Sysfs reads reflect live connector state protected by locks or `READ_ONCE`; mode names come from connector mode list.

Dependencies and integration points: integrates Linux driver core, sysfs attributes, kobjects, ACPI bus matching, component framework for Type-C links, I2C DDC devices, PCI primary display detection, accel minors, DRM connector/mode/property internals, and userspace udev/hotplug consumers.

Risks: `status_store()` invokes `fill_modes()` under `mode_config.mutex`, so connector callbacks must obey expected locking. `modes_show()` uses `scnprintf()` into one PAGE_SIZE buffer and can truncate many modes. Uevent environment is fixed-size stack storage and must remain valid during call. Connector remove paths split early DDC unlink from device unregister and must be ordered by callers.

Test signals: class init/destroy, minor allocation for card/render/accel, connector sysfs add/remove and DDC link lifecycle, status force writes and invalid values, EDID binary reads, Type-C symlink creation/removal, hotplug/property/lease uevent environment, ACPI companion lookup, and primary boot display attribute visibility.
