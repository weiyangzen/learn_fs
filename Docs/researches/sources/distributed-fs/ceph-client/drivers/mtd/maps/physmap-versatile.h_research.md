<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-versatile.h -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-versatile.h

Purpose: declares or stubs the Versatile physmap OF add-on hook.

Important APIs, types, and functions: `of_flash_probe_versatile(struct platform_device *, struct device_node *, struct map_info *)` is declared under `CONFIG_MTD_PHYSMAP_VERSATILE`; otherwise an inline stub returns 0.

Control flow: `physmap-core.c` calls this hook unconditionally during OF setup, while the header hides config-specific linkage.

State and persistence: none.

Dependencies and integration points: includes OF and MTD map declarations and is paired with `physmap-versatile.c`.

Risks: if the config is disabled on a board requiring VPP/protection handling, flash may probe read-only or fail writes. Test signals are enabled/disabled build coverage and no-op behavior on non-Versatile nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-versatile.h -->
