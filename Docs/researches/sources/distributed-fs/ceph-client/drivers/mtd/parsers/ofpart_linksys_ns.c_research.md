# sources/distributed-fs/ceph-client/drivers/mtd/parsers/ofpart_linksys_ns.c

Purpose: Linksys Northstar fixed-partition post-parse quirk that names the active firmware slot using CFE NVRAM.

Important APIs/types/functions: `linksys_ns_partitions_post_parse()` is invoked from `ofpart_core.c`. `ofpart_linksys_ns_bootpartition()` reads NVRAM key `bootpartition` through `bcm47xx_nvram_getenv()`.

Control flow: the helper tries to parse `bootpartition` into an integer, warning when the key is missing or malformed and defaulting to 0. The post-parse loop increments a firmware-slot index for partitions compatible with `linksys,ns-firmware`; the indexed active slot becomes `firmware`, all others become `backup`.

State and persistence: persistent state is CFE NVRAM and device-tree partition compatibility. Runtime state is only mutated partition names. The code is read-only with respect to flash/NVRAM.

Dependencies and integration: depends on BCM47XX NVRAM support and the fixed-partition quirk hook. Risks include NVRAM absence, invalid slot indexes, assumptions about firmware-node ordering, and defaulting to slot 0. Test signals include missing and malformed bootpartition, multiple firmware nodes, slot indexes beyond count, and Kconfig enabled/disabled builds.
