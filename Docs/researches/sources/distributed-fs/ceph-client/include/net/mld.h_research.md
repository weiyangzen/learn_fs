<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mld.h -->
# sources/distributed-fs/ceph-client/include/net/mld.h

## Purpose
`mld.h` defines IPv6 Multicast Listener Discovery v1/v2 packet layouts, option macros, queue limits, and the MLDv2 maximum-response-code decoder.

## Important APIs, types, and functions
Types include `struct mld_msg`, `struct mld2_grec`, `struct mld2_report`, and `struct mld2_query`. Macros alias ICMPv6 header fields, decode MLDv2 floating-point MRC/QQIC fields, and define queue/SKB limits. `mldv2_mrc` converts the query response code to milliseconds/ticks-style units.

## Control flow
IPv6 multicast code parses ICMPv6 MLD messages using the structs and flexible arrays. `mldv2_mrc` handles linear values below 32768 and RFC3810 exponent/mantissa encoding above that threshold.

## State and persistence
The header defines no persistent state; runtime state is in multicast listener code queues and skbs using these layouts.

## Dependencies and integration points
It depends on IPv6 address and ICMPv6 headers and the architecture byteorder bitfield macros. It integrates with `igmp6`/MLD receive and report generation.

## Risks and test signals
Risks include bitfield endian mismatch, flexible-array bounds, MRC exponent overflow expectations, MLDv1 compatibility threshold errors, and queue-limit assumptions. Tests should parse v1 and v2 queries/reports, max/min MRC encodings, little/big-endian builds, and truncated source lists.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mld.h` completely for this pass (117 lines, 2918 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mld.h -->
