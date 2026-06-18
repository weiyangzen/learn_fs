<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/neighbour_tables.h -->
# sources/distributed-fs/ceph-client/include/net/neighbour_tables.h

## Purpose
`neighbour_tables.h` centralizes numeric neighbour table identifiers.

## Important APIs, types, and functions
It defines `NEIGH_ARP_TABLE`, `NEIGH_ND_TABLE`, `NEIGH_NR_TABLES`, and `NEIGH_LINK_TABLE` as a pseudo table used by `neigh_xmit`.

## Control flow
There are no functions. Neighbour table registration and xmit users share the same enum values for indexing.

## State and persistence
No state is stored.

## Dependencies and integration points
It is included by `neighbour.h` and consumers that need stable table IDs.

## Risks and test signals
Risks are accidental renumbering or adding real tables after the pseudo table without updating array sizing. Tests are compile/build coverage and targeted users of ARP, ND, and link pseudo-table xmit paths.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/neighbour_tables.h` completely for this pass (12 lines, 253 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/neighbour_tables.h -->
