# sources/distributed-fs/openafs/src/sys/rmtsysnet.c

## Purpose
`rmtsysnet.c` converts selected pioctl input and output buffers between host byte order and network byte order for RMTSYS RPC transport.

## Important APIs, types, and functions
It defines local `struct Acl`, `struct AclEntry`, and `struct ClearToken`. Exported helpers are `RSkipLine`, `RParseAcl`, `RAclToString`, `RCleanAcl`, `RFetchVolumeStatus_conversion`, `RClearToken_convert`, `inparam_conversion`, and `outparam_conversion`.

## Control flow
ACL conversion parses textual ACLs into linked lists, writes them back, and frees temporary entries. Token conversions walk length-prefixed secret-ticket and clear-token regions and convert embedded integer fields. Volume-status conversion swaps fields in `AFSFetchVolumeStatus`. The in/out conversion switches inspect `cmd & 0xffff` and convert only older pioctls that were not already network-order clean.

## State and persistence behavior
No durable state is stored. It mutates the caller-provided buffer in place before or after an RX call.

## Dependencies and integration points
It depends on pioctl opcode definitions from `venus.h`, AFS volume/token structures, XDR/RX integer conventions, and is called by `rmtsysc.c` and `rmtsyss.c`.

## Risks
Parsing and serialization use fixed buffers, `sscanf`, `sprintf`, and `strcat` into pioctl-sized buffers, so malformed or oversized ACLs can overflow or truncate. Token conversion trusts embedded lengths and can walk outside the buffer if the caller supplies malformed data. New pioctls default to no conversion, which is correct only if their wire format is already network order.

## Test signals
Round-trip ACL, token, volume-status, cache-params, and scalar pioctl buffers through host-to-network and network-to-host conversion. Include malformed ACL counts, long names, bad token lengths, and unknown opcode behavior.
