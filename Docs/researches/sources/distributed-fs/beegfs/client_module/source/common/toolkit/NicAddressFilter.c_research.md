# sources/distributed-fs/beegfs/client_module/source/common/toolkit/NicAddressFilter.c

## Purpose
Implements ordered filtering and prioritization of local NIC addresses. Filter rows can match interface name, IP address, address family, NIC type, and can be inverted with `!` to forbid a match.

## Important APIs and control flow
`NicAddressFilter_getPosition` walks the filter array in order and returns the first matching non-inverted position or `SIZE_MAX` for no match or inverted match. `NicAddressFilter_isAllowed` permits all NICs when the filter is empty and otherwise requires a valid position. `parse_NicAddressFilterEntry` tokenizes whitespace-delimited rows with a small `Reader`, supports `*` wildcards per column, validates interface names, parses IPv4/IPv6 addresses, accepts family `4`/`6`, and maps `tcp`/`rdma` to NIC address types. `NicAddressFilter_construct` allocates a maximal array from a `StrCpyList`, parses every row, and aborts construction on the first invalid row. `NicAddressFilter_destruct` frees the array and object.

## State, dependencies, integration
State is an ordered in-memory array of parsed match entries. Dependencies include `NicAddress`, kernel address parsers, `StrCpyListIter`, and BeeGFS NIC type definitions. The order doubles as preference ranking because callers can use returned positions.

## Risks and test signals
Unlike `NetFilter`, any malformed row fails the entire filter. Token buffers are fixed at 64 bytes and names are bounded by `IFNAMSIZ`. Test row parsing with wildcards, inverted first match, overlapping allow/deny rows, IPv4-mapped comparisons, RDMA/TCP type matching, and invalid extra columns.
