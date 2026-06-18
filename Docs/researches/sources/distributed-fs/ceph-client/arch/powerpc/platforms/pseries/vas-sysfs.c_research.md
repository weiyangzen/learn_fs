# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vas-sysfs.c

Purpose: Builds pSeries VAS sysfs hierarchy for GZIP default and QoS capability credit accounting and QoS credit updates.

Important APIs/types/functions: Defines `struct vas_caps_entry`, `struct vas_sysfs_entry`, read/store helpers, capability kobj types, `sysfs_add_vas_caps()`, miscdevice `vas`, and `sysfs_pseries_vas_init()`.

Control flow: Init registers `/dev/vas`, creates `vas0` below the misc device, and creates a `gzip` directory when GZIP capability bits are present. Each capability added later allocates a `vas_caps_entry`, chooses default or QoS kobject type based on descriptor, and creates `default_capabilities` or `qos_capabilities`. Reads report atomic total/used credits. QoS writes parse a new total and call `vas_reconfig_capabilties()` to close/reopen windows as needed.

State and persistence: Global kobject pointers track the VAS root and gzip directory. Each capability kobject owns a heap `vas_caps_entry` pointing at live capability state maintained by the VAS core.

Dependencies and integration points: Depends on VAS core types/functions in `vas.h`, miscdevice sysfs, kobject lifetime, atomic credit counters, and management-console DLPAR QoS notifications.

Risks: `vas_caps_kobj_name()` returns `"Unknown"` without initializing a kobject for unexpected descriptors; caller currently avoids `kobject_add()` when parent is NULL but still leaks the allocated entry. QoS store maps all reconfiguration failures to `-EINVAL`, hiding detail.

Test signals: Sysfs hierarchy for default and QoS capabilities, read credit counters while windows open/close, QoS credit update via drmgr path, unsupported descriptors, kobject release cleanup, and `CONFIG_SYSFS=n` stubs.

Source read size: 281 lines, 7410 bytes.
