<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/identify.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/arc/identify.c

**Purpose:** Identifies ARC/ARCS machine type from the root firmware component and sets Linux system type and PROM behavior flags.

**Important APIs/types/functions:** `mach_table[]` maps ARC names to Linux names and flags. `string_to_mach()` resolves names or panics. `prom_identify_arch()` reads the root child component via `ArcGetChild()`. `get_system_type()` returns `system_type`.

**Control flow:** During ARC init, the code obtains the first child of `PROM_NULL_COMPONENT`, uses its `iname`, prints it, maps it, and stores `system_type` plus `prom_flags`.

**State, dependencies, integration:** Owns globals `prom_flags` and `system_type`. Flags drive console enablement, ARCS memory type interpretation, and whether temporary PROM memory may be freed.

**Risks and test signals:** Unknown firmware identifiers panic, so new ARC platforms require table updates. Test each known SGI, Jazz, and SNI identifier, plus failure behavior for unknown strings and null component handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/identify.c -->
