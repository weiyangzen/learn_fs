# sources/distributed-fs/openafs/src/venus/cacheout.c

## Purpose
`cacheout.c` implements a cell-wide utility for invalidating fileserver ACL/CPS cache entries for selected AFS user IDs and/or client IP addresses. It discovers fileservers through the VLDB, establishes RX connections to each fileserver, and calls `RXAFS_FlushCPS`. It also exposes a `listservers` command for the same VLDB-derived server list.

## Important APIs, Types, And Functions
`ListServers` queries `ubik_VL_GetAddrs` and, for multihomed entries, `ubik_VL_GetAddrsU`, filling the fixed `server_id[256]` array in network byte order. `InvalidateCache` parses `-id` and `-ip` lists into `ViceIds` and `IPAddrs`, then loops over discovered servers and calls `RXAFS_FlushCPS`. `GetServerList` prints resolved server names. `MyBeforeProc` initializes RX, opens client or server configuration, selects null/token/localauth security, initializes VLDB ubik connections, and stores the global `client`, `sc`, and `scindex` used by command handlers.

## Control Flow
`main` installs `MyBeforeProc` as the command prelude, registers the default invalidation syntax plus alias `ic`, registers `listservers` plus alias `ls`, dispatches, finalizes RX, and exits with the command result. The prelude chooses `/usr/vice/etc` or server configuration depending on `-localauth`, changes security level for `-encrypt`, reads VLDB server endpoints for the selected cell, optionally obtains RXKAD credentials, and creates a ubik client.

The invalidation command first refreshes the server list, rejects calls with neither user IDs nor IP addresses, converts up to 255 IDs and IPs, and sends the flush RPC to each fileserver. Individual server connection or RPC failures are reported as informational and summarized by a nonzero return, because the VLDB may contain down or non-fileserver hosts.

## State And Persistence
State is entirely runtime: discovered fileserver count and addresses, one ubik client, and one RX security object/index. Persistent effects occur remotely on fileservers by clearing authorization-related cache entries for the specified users or clients. The tool does not mutate VLDB, local configuration, or disk files.

## Dependencies And Integration Points
The file integrates OpenAFS auth, cell configuration, ubik/VLDB RPCs, RX/RXKAD, token cache lookup through `ktc_GetToken`, and the fileserver `RXAFS_FlushCPS` interface. It relies on client/server CellServDB configuration to find VLDB servers and on fileserver support for the flush RPC.

## Risks And Test Signals
Notable risks are fixed 256-entry arrays for servers, IDs, and IPs, minimal bounds feedback when more than 255 list items are provided, a duplicated `if (code)` line in the RX initialization error path, possible invalid address use in the multihomed error print when `bulkaddrs_len` is zero, and weak validation of `inet_addr` results. Test signals include `listservers` against single-homed and multihomed VLDB data, noauth/token/localauth/encrypt startup paths, invalid ID and IP inputs, partial server failures, and verifying that ACL/CPS changes become visible after a targeted flush.
