<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-core.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-core.c

Purpose: generic physical-memory map driver for NOR, ROM, RAM, and LPDDR-like devices described by platform data, Device Tree, or legacy Kconfig compatibility.

Important APIs, types, and functions: `struct physmap_flash_info` stores maps, per-map MTDs, concatenated MTD, VPP state, probe/partition types, GPIO address extension state, and static partitions. Major functions are `physmap_flash_probe()`, `physmap_flash_remove()`, `physmap_flash_of_init()`, `physmap_flash_pdata_init()`, `physmap_set_vpp()`, GPIO-assisted map hooks, and `physmap_flash_shutdown()`.

Control flow: probe validates OF/platform data, counts memory resources, allocates maps and MTD pointers, obtains optional address GPIOs, enables runtime PM, initializes OF or platform properties, maps each resource, installs GPIO/SoC/simple map hooks, probes a specific or fallback map type (`cfi_probe`, `jedec_probe`, `qinfo_probe`, `map_rom`), concatenates multiple maps when present, associates OF node, parses/registers partitions, and returns. Remove unregisters the combined MTD, destroys maps, calls platform exit, and disables PM.

State and persistence: runtime state is per-device map/MTD arrays, VPP refcount, optional GPIO address bank value, and concatenated MTD. Persistent state is backing flash/RAM content.

Dependencies and integration points: platform driver `physmap-flash`, OF match table, partition parsers, MTD concat, CFI endian settings, GPIO descriptors, runtime PM, and optional Gemini/IXP4xx/Versatile add-ons.

Risks: multiple feature combinations make ordering important, especially custom map hooks before `simple_map_init()`. GPIO-assisted addressing supports only one map. `pm_runtime_get_sync()` errors are not explicitly checked. Test signals are OF and platform-data probe paths, multi-map concatenation, GPIO address switching, VPP callbacks, partition parser selection, and shutdown suspend/resume reset-to-read behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-core.c -->
