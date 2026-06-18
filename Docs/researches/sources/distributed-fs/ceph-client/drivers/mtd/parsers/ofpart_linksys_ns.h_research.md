# sources/distributed-fs/ceph-client/drivers/mtd/parsers/ofpart_linksys_ns.h

Purpose: conditional declaration header for the Linksys NS fixed-partition post-parse quirk.

Important APIs/types/functions: declares `linksys_ns_partitions_post_parse(struct mtd_info *mtd, struct mtd_partition *parts, int nr_parts)` only under `CONFIG_MTD_OF_PARTS_LINKSYS_NS`.

Control flow and state: no executable logic or persistence. It provides a compile-time boundary between the optional quirk implementation and `ofpart_core.c`.

Dependencies and integration: relies on including files to have MTD declarations in scope. Risks are build-only: missing guard symmetry would cause unresolved symbols or unused references. Test signals are allmodconfig and builds with the option disabled.
