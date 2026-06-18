# sources/distributed-fs/coda/coda-src/vice/srvproc2.cc

## Purpose

`sources/distributed-fs/coda/coda-src/vice/srvproc2.cc` implements secondary Coda file-server RPCs for connection lifecycle, volume discovery and status, root-volume configuration, server time probing, connection setup, and runtime statistics. It complements `srvproc.cc` by handling administrative and metadata/status operations rather than object data transfer.

## Important APIs, Types, and Functions

RPC handlers include `FS_ViceDisconnectFS`, `FS_TokenExpired`, `FS_ViceGetStatistics`, `FS_ViceGetVolumeInfo`, `FS_ViceGetVolumeLocation`, `FS_ViceGetVolumeStatus`, `FS_ViceSetVolumeStatus`, `FS_ViceGetRootVolume`, `FS_ViceSetRootVolume`, `FS_ViceGetTime`, `FS_ViceNewConnection`, and `FS_ViceNewConnectFS`. Helpers include `GetROOTVOLUME`, `SetVolumeStatus`, `PerformSetQuota`, `SetViceStats`, `SetRPCStats`, `SetVolumeStats`, `SetSystemStats`, platform-specific `SetSystemStats_linux`/`SetSystemStats_bsd44`, `GetEtherStats`, and `PrintVolumeStatus`.

## Control Flow

Connection RPCs map the `RPC2_Handle` to `ClientEntry`, lock the associated `HostTable`, and either delete the client, clean up an expired host, or build/validate callback connections. Volume info resolves root aliases through `db/ROOTVOLUME`, consults the VRDB for replicated volumes, falls back to `VGetVolumeInfo`, and normalizes type/group-id fields. Volume status fetches the root vnode, checks caller rights or system-user privilege, fills status/name/motd/offline buffers, and releases the vnode and volume. Set-volume-status validates buffers and client identity, obtains an exclusive volume lock, locks the root vnode, requires `SystemUser`, changes quota/name/motd/offline message fields, spools replicated quota log records, and commits through `PutObjects` with volume update enabled.

## State and Persistence Behavior

The file mutates client and host connection state, callback connection handles, volume header fields, and the `db/ROOTVOLUME` configuration file. `FS_ViceSetRootVolume` writes `ROOTVOLUME.new` and atomically renames it over `ROOTVOLUME`. `FS_ViceSetVolumeStatus` persists quota and text fields in the volume header and can add COP pending state for replicated quota updates. Statistics routines read transient counters, RPC2/SFTP packet counters, partition free-space lists, `getrusage`, and `/proc` or kernel memory depending on platform.

## Dependencies and Integration Points

It integrates with `CLIENT_Build`, `CLIENT_Delete`, `CLIENT_CleanUpHost`, `CLIENT_MakeCallBackConn`, RPC2 private pointers, VRDB/VLDB lookup, `VGetVolumeInfo`, `VGetVolumeLocation`, volume/vnode locking, ACL rights checks from `srvproc.cc`, `CodaBreakCallBack`, replicated update helpers (`NewCOP1Update`, `CopPendingMan`, `SpoolVMLogRecord`), `vice_config_path`, global server counters, partition lists, and RPC2/SFTP statistics globals.

## Risks and Edge Cases

`SetVolumeStatus` uses bounded byte-string buffers but some `strncpy` lengths are tied to the wrong bounded object in the offMsg/motd paths, so boundary tests are important. `FS_ViceSetRootVolume` leaves `ROOTVOLUME.new` behind on some write failures and uses `O_EXCL`, which can make retries fail until cleanup. `FS_ViceGetTime` performs callback-channel repair on a timing RPC, so callback connection failures can affect a low-level liveness path. Volume id translation and `IsReplicated` mismatches return generic errors. Statistics collection has wraparound comments and platform-specific parsers that can silently skip fields if `/proc` formats change.

## Test Signals

Exercise connection build/disconnect/token-expiry paths, callback reconnection through `ViceGetTime` and `ViceNewConnectFS`, root volume get/set including stale `.new` files and permission failures, volume info lookup by name/id/root alias/replicated id, volume status buffer-size checks, set-volume-status authorization and replicated quota logging, and statistics output under empty, multi-partition, and Linux `/proc` parser scenarios.
