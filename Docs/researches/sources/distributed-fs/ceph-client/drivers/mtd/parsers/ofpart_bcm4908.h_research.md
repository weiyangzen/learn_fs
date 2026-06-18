# sources/distributed-fs/ceph-client/drivers/mtd/parsers/ofpart_bcm4908.h

Purpose: tiny conditional declaration header for the BCM4908 fixed-partition post-parse quirk.

Important APIs/types/functions: declares `bcm4908_partitions_post_parse(struct mtd_info *mtd, struct mtd_partition *parts, int nr_parts)` only when `CONFIG_MTD_OF_PARTS_BCM4908` is enabled.

Control flow and state: there is no executable logic or persistent state. It constrains compilation so `ofpart_core.c` can refer to the quirk only under matching Kconfig.

Dependencies and integration: depends on forward-visible MTD types from including C files. Risks are limited to build configuration drift: if the C implementation or caller conditionals diverge from this guard, link or compile errors result. Test signals are build coverage with the option enabled and disabled.
