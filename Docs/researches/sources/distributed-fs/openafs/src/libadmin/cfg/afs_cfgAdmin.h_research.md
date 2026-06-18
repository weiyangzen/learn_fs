# sources/distributed-fs/openafs/src/libadmin/cfg/afs_cfgAdmin.h

## Purpose
Declares the public server/client configuration API for libadmin. The header organizes operations for host configuration, client configuration, server CellServDB updates, BOS server control, database/file/update server setup, update clients, and deallocation utilities.

## Important APIs, Types, And Functions
Public data types include `cfg_partitionEntry_t`, `cfg_cellServDbStatus_t`, callback type `cfg_cellServDbUpdateCallBack_t`, and `cfg_dbServersStatus_t`. Exported string constants name standard BOS instances such as `cfg_kaserverBosName`, `cfg_ptserverBosName`, `cfg_vlserverBosName`, `cfg_buserverBosName`, `cfg_fileserverBosName`, `cfg_upserverBosName`, and update-client suffix/prefix constants.

Function groups include `cfg_Host*` for static server config and partition table operations; `cfg_Client*` for cache-manager/client CellServDB operations; `cfg_CellServDb*` for cell-wide server CellServDB updates; `cfg_BosServer*`; database server start/stop/status/quorum helpers; file server start/stop/status; update server/client start/stop/status; convenience `cfg_SysBinServerStart`, `cfg_SysControlClientStart`, and `cfg_BinDistClientStart`; and deallocators for returned strings, partition lists, and CellServDB callback status records.

## Control Flow
The header documents the intended sequence: set static server configuration through `cfg_Host*`, set static client configuration through `cfg_Client*`, then dynamically configure server processes by category. It also documents an idempotence goal for implemented functions.

## State And Persistence
No state is stored in the header. Its API mutates persistent host and cell configuration: ThisCell, CellServDB, KeyFile, UserList, BosConfig, service state, partition tables, server process definitions, and client registry/configuration depending on platform.

## Dependencies And Integration Points
It includes `afs_Admin.h` and relies on opaque host/cell handles created by other libadmin modules. Implementations integrate with BOS, KAS, PTS, VOS, Windows service/registry helpers, CellServDB parsers, and local filesystem configuration paths.

## Risks And Test Signals
Risks are API/implementation drift and platform support assumptions: many implementation paths are local-only and return `ADMCFGNOTSUPPORTED` on Unix or remote hosts. Tests should verify function availability, callback ownership rules, deallocator behavior, and idempotence for repeated configuration calls where supported.
