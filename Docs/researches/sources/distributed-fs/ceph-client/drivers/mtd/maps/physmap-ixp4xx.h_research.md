<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-ixp4xx.h -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-ixp4xx.h

Purpose: declares or stubs the IXP4xx physmap OF add-on entry point.

Important APIs, types, and functions: `of_flash_probe_ixp4xx(struct platform_device *, struct device_node *, struct map_info *)` is declared when `CONFIG_MTD_PHYSMAP_IXP4XX` is enabled and otherwise replaced with an inline zero-return stub.

Control flow: allows `physmap-core.c` to call the helper unconditionally while Kconfig controls whether custom IXP4xx hooks are linked.

State and persistence: none.

Dependencies and integration points: includes OF, platform device, and MTD map declarations and is included by `physmap-core.c`.

Risks: disabled stub must not mask required endian handling on actual IXP4xx boards; Kconfig defaults/selects are responsible. Test signals are build coverage for enabled/disabled configs and correct helper behavior on nonmatching OF nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-ixp4xx.h -->
