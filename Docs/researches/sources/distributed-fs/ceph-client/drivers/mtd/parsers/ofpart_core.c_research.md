# sources/distributed-fs/ceph-client/drivers/mtd/parsers/ofpart_core.c

Purpose: core device-tree MTD partition parser. It supports modern `fixed-partitions`, optional vendor quirks, direct-child legacy fallback, and an obsolete `partitions` property parser.

Important APIs/types/functions: `parse_fixed_partitions()` handles nodes and subnodes. `parse_ofoldpart_partitions()` handles the old flat binding. `struct fixed_partitions_quirks` allows post-parse callbacks from BCM4908 and Linksys NS helpers. `ofpart_parser_init()` registers both `fixed-partitions` and `ofoldpart` parsers.

Control flow: for master devices, the parser prefers a `partitions` child and otherwise scans direct children; for MTD partitions, it parses the node itself. Dedicated `partitions` nodes must match the parser OF table. Direct-child fallback skips nodes with `compatible` to avoid consuming real devices. It counts usable children, allocates the partition array, validates each `reg` length against address and size cells, computes offset/size, stores `of_node`, selects `label` or `name`, and maps `read-only`, `lock`, and `slc-mode` properties into MTD flags. Vendor `post_parse` hooks may rename slots. Failure unwinds nodes and allocations.

State and persistence: persistent inputs are device-tree properties. Runtime state is the partition array and referenced OF nodes; no flash writes occur. `ofoldpart` reads big-endian offset/length pairs, treats low length bit as read-only, and derives names from `partition-names`.

Dependencies and integration: integrates with OF, MTD parser core, and vendor quirk files. Risks include fallback behavior for invalid direct child nodes, incorrect `#size-cells = <0>` workaround, OF node lifetime mistakes, and partition name absence. Test signals include dedicated and direct-child layouts, compatible child skipping, bad/missing `reg`, read-only/lock/slc flags, quirk callbacks, old binding with name exhaustion, and module aliases for parser autoloading.
