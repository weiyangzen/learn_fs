## sources/distributed-fs/ceph-client/sound/hda/core/sysfs.c

Purpose: exposes HD-audio codec identity attributes and a widget-tree sysfs hierarchy under each codec device.

Important APIs, types, and functions: `hdac_dev_attr_groups`, `struct hdac_widget_tree`, `struct widget_attribute`, `hda_widget_sysfs_init()`, `hda_widget_sysfs_exit()`, `hda_widget_sysfs_reinit()`, `widget_tree_create()`, and per-attribute show callbacks for caps, pin config, PCM caps/formats, amps, power, GPIO, and connections.

Control flow: codec device attributes are installed through attribute groups. Widget init creates a `widgets` kobject, per-node kobjects named by NID, optional AFG kobject, and attribute groups. Show callbacks parse the NID from kobject names, recover the codec from the parent device, then read cached widget caps or issue HD-audio parameter/verb reads.

State and persistence: `codec->widgets` owns the root, AFG kobject, and node array. Reinit duplicates the tree metadata, prunes old NIDs, adds new ones, then swaps the tree pointer. Exit removes groups and releases kobjects.

Dependencies and integration points: depends on sysfs/kobject APIs, HDA codec parameter helpers, connection-list helpers, and internal `local.h` declarations. Device identity attributes are consumed by userspace diagnostics and modalias matching.

Risks: creation paths must unwind correctly after partial allocation; reinit currently ignores `add_widget_node()` return values while adding new nodes, which can hide failures. Attribute reads can trigger codec verbs and may depend on device power state handled by lower layers. NID parsing assumes stable two-hex-digit names.

Test signals: inspect `/sys/bus/hdaudio/.../widgets`, hot-reconfigure codecs with changed node ranges, run kmemleak/kobject reference checks, read all attributes during suspend/resume and after codec removal.
