## sources/distributed-fs/openafs/src/libafscp/afscp_server.c

Purpose: Manages process-global cells and file servers for `libafscp`, including default cell/realm selection, VLDB address resolution, RX connection creation, and server lookup by UUID, address, or index.

Important APIs and functions: `afscp_FreeAllCells`, `afscp_FreeAllServers`, `afscp_CellById`, `afscp_CellByName`, `afscp_DefaultCell`, `afscp_SetDefaultRealm`, `afscp_SetDefaultCell`, `afscp_CellId`, `afscp_ServerById`, `afscp_ServerByAddr`, `afscp_AnyServerByAddr`, `afscp_ServerByIndex`, and `afscp_ServerConnection`.

Control flow: `afscp_CellByName` searches existing cells, grows the cell array, initializes security through `_GetSecurityObject`, initializes VLDB clients through `_GetVLservers`, then assigns the cell id. Default cell resolution reads local client configuration unless `defcell` is set. Server lookup grows per-cell and global server arrays, asks the VLDB for UUID or address mappings with `ubik_VL_GetAddrsU`, and creates one RX connection per returned address.

State and persistence: Uses global arrays `allcells` and `allservers`, global default cell/realm strings, and global `afscp_errno`. Cells own VLDB clients, security classes, server pointer arrays, and volume trees. Servers own RX connections. No on-disk persistence.

Dependencies and integration: Uses OpenAFS config directory APIs, ubik VLDB RPCs, RX connections, Kerberos realm routines for default realm, and volume lookup code that stores server indexes.

Risks: Free routines release arrays but not all nested allocations and connections. Error paths in `afscp_ServerById` can leave partially attached server entries in `fsservers`. `afscp_FreeAllServers` only frees the pointer array, not server objects or RX connections. There is no locking around global registries. Address byte order assumptions are subtle: public address lookup takes host order and stores network order.

Test signals: Exercise duplicate cell/server lookup, VLDB UUID and address resolution, fallback direct address connections when VLDB lookup fails, default cell configuration failures, realm replacement, global index bounds, and cleanup under valgrind or ASAN.
