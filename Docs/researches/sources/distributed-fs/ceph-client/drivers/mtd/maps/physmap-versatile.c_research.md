<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-versatile.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-versatile.c

Purpose: Versatile/Integrator/RealView physmap add-on that supplies flash protection and VPP callbacks using syscon and, for Integrator/AP, EBI registers.

Important APIs, types, and functions: `of_flash_probe_versatile()` is the physmap hook. Helpers `ap_flash_init()`, `ap_flash_set_vpp()`, `cp_flash_set_vpp()`, and `versatile_flash_set_vpp()` program platform-specific protection bits. `syscon_match[]` identifies the system controller flavor.

Control flow: the helper acts only for `arm,versatile-flash`. On first use it finds a matching syscon regmap and records the flash-protection type. Integrator/AP additionally maps the EBI, clears protection, unlocks EBI, enables write cycles, and relocks it. The helper installs the correct `map->set_vpp` callback for AP, CP, Versatile, or RealView systems.

State and persistence: runtime state is a static syscon regmap pointer and selected protection type. Hardware state includes VPP/write-protect bits and Integrator EBI write-enable state.

Dependencies and integration points: physmap OF initialization, syscon/regmap, OF address mapping, ARM platform compatibles, and `map_info.set_vpp`.

Risks: static syscon state assumes one protection domain. AP initialization directly touches EBI registers and must match hardware manuals. VPP errors are logged but not propagated during callbacks. Test signals are syscon discovery, AP EBI write enable, VPP toggling on AP/CP/Versatile/RealView, and normal physmap probing afterward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/physmap-versatile.c -->
