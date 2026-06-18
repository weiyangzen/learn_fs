# sources/distributed-fs/openafs/src/auth/netrestrict.c

## Purpose
Parses OpenAFS `NetInfo` and `NetRestrict` files to determine which IPv4 interfaces should be advertised or used by clients and servers.

## Important APIs, Types, and Functions
Key functions are `afsconf_ParseNetInfoFile`, `afsconf_ParseNetRestrictFile`, and `afsconf_ParseNetFiles`. Static helpers include `extract_Addr`, `ParseNetInfoFile_int`, `parseNetRestrictFile_int`, and `filterAddrs`.

## Control Flow
`NetInfo` parsing starts with kernel interface data from `rx_getAllAddrMaskMtu`, then filters/augments it with file entries, including optional fake addresses. `NetRestrict` starts with all kernel addresses plus fake NetInfo entries, then removes addresses matching restricted CIDR-like masks. `afsconf_ParseNetFiles` combines both by choosing successful results or intersecting both successful sets.

## State and Persistence
No durable state is stored in memory; persistent inputs are the NetInfo/NetRestrict text files. Outputs are caller-provided address, mask, and MTU arrays in network byte order plus a reason string.

## Dependencies and Integration Points
Integrates with RX interface discovery, `rx_IsLoopbackAddr`, OpenAFS dirpath names, and `cellconfig` APIs. Test code can override `rx_getAllAddrMaskMtu` to simulate interfaces.

## Risks and Test Signals
The parser is IPv4-only and uses fixed `MAXIPADDRS` arrays. `extract_Addr` does not reject octets above 255 before packing. `ParseNetInfoFile_int` checks `count > max`, which allows `count == max` writes and should be reviewed. Tests should cover blank/comment lines, subnet masks, fake addresses, duplicate matching, loopback removal, missing files, and combined NetInfo/NetRestrict outcomes.
