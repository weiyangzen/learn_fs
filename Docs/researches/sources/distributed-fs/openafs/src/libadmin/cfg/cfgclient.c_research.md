# sources/distributed-fs/openafs/src/libadmin/cfg/cfgclient.c

## Purpose
Implements the `cfg_Client*` portion of the configuration API. It queries local client/cache-manager installation and static configuration, sets the default client cell, edits the local client CellServDB, and starts/stops the cache manager service where supported.

## Important APIs, Types, And Functions
Exported functions are `cfg_ClientQueryStatus`, `cfg_ClientSetCell`, `cfg_ClientCellServDbAdd`, `cfg_ClientCellServDbRemove`, `cfg_ClientStop`, and `cfg_ClientStart`. Local helpers are `ClientCellServDbUpdate`, `CacheManagerStart`, and `CacheManagerStop`. Windows-only code uses `cfgutil_WindowsServiceQuery/Start/Stop`, `afssw_GetClientVersion`, `afssw_SetClientCellName`, and CellServDB parser/writer routines such as `CSDB_ReadFile`, `CSDB_FindCell`, `CSDB_AddCell`, `CSDB_AddCellServer`, `CSDB_RemoveLine`, and `CSDB_WriteFile`.

## Control Flow
`cfg_ClientQueryStatus` validates parameters, requires the target host to be local, checks whether the Windows AFS client service is installed, obtains version information from registry-backed software helpers, then opens client configuration through `afsconf_Open`. It verifies a local cell name, matching CellServDB entry, and at least one database server, returning an allocated cell name only when static configuration is valid.

`cfg_ClientSetCell` validates a local host handle, cell name, and multistring database host list. On Windows, it reads the client CellServDB, creates or replaces the cell entry, resolves each database host to an address string, writes the file, sets the default client cell in the registry, and calls `ka_CellConfig` so underlying packages observe the cell change. `cfg_ClientCellServDbAdd/Remove` call `ClientCellServDbUpdate`, which resolves the database host to a full name, finds matching server lines by address, adds or removes the server entry, and writes the CellServDB. `cfg_ClientStart/Stop` validate the host and delegate to Windows service helpers with a timeout.

## State And Persistence
Persistent state includes the client CellServDB file at `AFSDIR_CLIENT_CELLSERVDB_FILEPATH`, client configuration under `AFSDIR_CLIENT_ETC_DIRPATH`, and Windows registry/service state for the AFS cache manager and default client cell. Returned cell names are heap-allocated and must be released through `cfg_StringDeallocate`. On non-Windows builds most operations return `ADMCFGNOTSUPPORTED`.

## Dependencies And Integration Points
The file depends on OpenAFS cell configuration, KAuth cell configuration refresh, Windows registry/software helpers, CellServDB parsing code, `cfginternal` host utilities, and service-control wrappers. It is typically used during server setup to ensure the local client knows the cell being configured.

## Risks And Test Signals
Risks include local-only behavior despite remote-looking API parameters, Windows-only implementation paths, concurrent edits to CellServDB without explicit locking here, fixed maximum host/cell counts, and multi-string parsing assumptions. Tests should cover valid/invalid local host detection, missing/malformed client config, installed and uninstalled Windows service states, CellServDB add/remove idempotence, duplicate host aliases by address, registry write failures, and start/stop timeout behavior.
