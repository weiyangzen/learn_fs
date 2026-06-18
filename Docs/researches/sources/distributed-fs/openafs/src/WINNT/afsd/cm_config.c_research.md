# sources/distributed-fs/openafs/src/WINNT/afsd/cm_config.c

## Purpose
`cm_config.c` reads and writes Windows OpenAFS client configuration related to cells. It supports CellServDB file parsing/enumeration, registry CellServDB schema lookup/enumeration/update, DNS AFSDB/SRV lookup, root-cell and generic service parameter writes, and safe-ish CellServDB replacement helpers.

## Important APIs and Types
Public search APIs are `cm_SearchCellFile`, `cm_SearchCellFileEx`, `cm_SearchCellRegistry`, and `cm_SearchCellByDNS`; enumeration APIs are `cm_EnumerateCellFile` and `cm_EnumerateCellRegistry`. Persistence helpers include `cm_AddCellToRegistry`, `cm_WriteConfigString`, `cm_WriteConfigInt`, `cm_OpenCellFile`, `cm_AppendPrunedCellList`, `cm_AppendNewCell`, `cm_AppendNewCellLine`, `cm_CloseCellFile`, `cm_GetCellServDB`, `cm_GetRootCellName`, and `cm_GetConfigDir`. Local helpers parse key/value pairs and suppress lookups for probable Windows module names such as `.dll` and `.exe`.

## Control Flow
File lookup opens CellServDB, finds exact or unique partial cell matches, records linked-cell names, then parses server lines into hostnames or IPv4 literals and calls the supplied `cm_configProc_t`. Registry lookup opens `HKLM\...\OpenAFS\Client\CellServDB`, handles exact or unique prefix cell keys, reads `LinkedCell` and `ForceDNS`, then enumerates server keys, resolving `HostName`, `Rank`, `IPv4Address`, and optional VL port. DNS lookup calls `getAFSServer("afs3-vlserver", "udp", ...)` and emits configured server addresses and ranks.

## State and Persistence
This file is the persistence boundary for cell configuration. Registry writes are non-volatile under the OpenAFS client service key. CellServDB updates write `CellServDB.new`, prune old cell sections, append new content, then rename the new file over `CellServDB`. Root cell and generic config values are read/written under the service parameter registry subkey.

## Dependencies and Integration Points
It depends on Windows registry APIs, Shlwapi recursive key deletion, Winsock name resolution, StrSafe routines, `afssw_GetClientCellServDBDir`, OpenAFS DNS helpers, and callback function pointers consumed by `cm_cell.c`.

## Risks and Test Signals
Important tests should cover exact and ambiguous partial matches, linked-cell parsing, ForceDNS fallthrough, registry schema edge cases, DNS suppression for module-like names or no-TLD names, IPv4 literal fallback, long line/name boundaries, and CellServDB replacement behavior. Risks include mixed case-insensitive comparisons, legacy `gethostbyname`, partial failure cleanup, and `cm_CloseCellFile` unlink/rename ordering.
