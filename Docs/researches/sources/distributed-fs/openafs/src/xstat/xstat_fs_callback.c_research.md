# sources/distributed-fs/openafs/src/xstat/xstat_fs_callback.c

## Purpose
`xstat_fs_callback.c` supplies the AFSCB server-side callback routines required when the file-server xstat collector opens an Rx callback listener. The collector is not a real Cache Manager, so most callbacks are no-op compatibility stubs; identity-oriented calls return a generated UUID and interface address list.

## Important APIs, Types, And Functions
The file defines `afs_cb_inited`, `afs_cb_interface`, private `init_afs_cb`, and many `SRXAFSCB_*` RPC handlers including `CallBack`, `InitCallBackState`, `Probe`, `GetCE64`, `GetCE`, `GetLock`, `XStatsVersion`, `GetXStats`, `InitCallBackState2`, `WhoAreYou`, `InitCallBackState3`, `ProbeUuid`, `GetServerPrefs`, `GetCellServDB`, `GetCellByNum`, `GetLocalCell`, `GetCacheConfig`, and `TellMeAboutYourself`.

## Control Flow
The callback listener created in `xstat_fs_Init` dispatches AFSCB RPCs to these functions. Most simply return success or `RXGEN_OPCODE` for unsupported optional calls. `init_afs_cb` generates a UUID with platform-specific APIs and populates local addresses through `rx_getAllAddr`. `SRXAFSCB_WhoAreYou` and `SRXAFSCB_TellMeAboutYourself` lazily initialize and copy `afs_cb_interface`; `SRXAFSCB_ProbeUuid` compares the incoming UUID with the cached one; `SRXAFSCB_GetLocalCell` allocates and returns the string `"This is xstat_fs"`.

## State And Persistence
State is process-local: one generated callback UUID, address list, and initialization flag. No callback contents are cached, and no filesystem or registry state is changed. `GetLocalCell` allocates a string for the RPC output and relies on RPC/XDR cleanup by the caller/runtime.

## Dependencies And Integration Points
The stubs satisfy symbols expected by `RXAFSCB_ExecuteRequest` from `afs/afscbint.h`, and are explicitly sanity-called by `xstat_fs_CleanupInit`. They depend on Rx address discovery, UUID helpers, host utility logging when verbose mode is compiled on, and Windows UUID APIs on NT builds.

## Risks And Test Signals
Risks are mostly protocol-compatibility risks: unsupported callbacks return `RXGEN_OPCODE`, while a file server may expect identity callbacks to behave consistently. `afs_cb_inited` is not locked, so concurrent initial identity RPCs can race. Test signals include successful xstat polling against a file server, callback probes not causing disconnects, stable `WhoAreYou`/`ProbeUuid` behavior, and compile coverage across Windows and Unix UUID paths.
