<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-gemini.h -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-gemini.h

Purpose: declares or stubs the Gemini physmap OF add-on entry point.

Important APIs, types, and functions: `of_flash_probe_gemini(struct platform_device *, struct device_node *, struct map_info *)` is declared when `CONFIG_MTD_PHYSMAP_GEMINI` is enabled; otherwise an inline stub returns 0.

Control flow: `physmap-core.c` can call the helper unconditionally during OF map setup. The stub preserves build/link behavior when the feature is disabled.

State and persistence: none.

Dependencies and integration points: depends on `linux/of.h`, `linux/mtd/map.h`, and a forward-visible `platform_device` type through included kernel headers.

Risks: the helper is expected to be side-effect-free when incompatible or disabled. Test signals are successful builds with the config enabled and disabled, and no behavior change for non-Gemini physmap nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-gemini.h -->
