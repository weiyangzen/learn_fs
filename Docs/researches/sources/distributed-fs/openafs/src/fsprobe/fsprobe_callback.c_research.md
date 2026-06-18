# sources/distributed-fs/openafs/src/fsprobe/fsprobe_callback.c

## Purpose
Implements minimal AFS callback server procedures so FileServers can treat the probe process like a cache manager while statistics are collected.

## Important APIs, Types, And Functions
Defines callback globals `afs_cb_inited` and `afs_cb_interface`, private `init_afs_cb`, and many `SRXAFSCB_*` RPC handlers: `CallBack`, `InitCallBackState`, `Probe`, `GetCE64`, `GetCE`, `GetLock`, `XStatsVersion`, `GetXStats`, `InitCallBackState2`, `WhoAreYou`, `InitCallBackState3`, `ProbeUuid`, `GetServerPrefs`, `GetCellServDB`, `GetCellByNum`, `GetLocalCell`, `GetCacheConfig`, and `TellMeAboutYourself`.

## Control Flow
Most handlers are no-op stubs returning success because fsprobe does not maintain real cache-manager state. `InitCallBackState2` and several cache/cell query procedures return `RXGEN_OPCODE` to signal unsupported calls. `WhoAreYou` and `TellMeAboutYourself` lazily initialize interface addresses and UUIDs, then return them. `ProbeUuid` lazily initializes and compares the supplied UUID against the process callback UUID.

## State And Persistence
The only persistent state is the generated callback UUID and local interface address list in `afs_cb_interface`. It is process-local and initialized once.

## Dependencies And Integration Points
These functions satisfy symbols expected by generated `afscbint.ss.c` and are dispatched by `RXAFSCB_ExecuteRequest` from the callback service created in `fsprobe_Init`.

## Risks And Test Signals
Because most RPCs return success without filling outputs, callers must tolerate probe-only semantics. Verbose logging blocks reference stale macro names in disabled code paths, so enabling them may not compile. Tests should cover callback service startup, `WhoAreYou`, `TellMeAboutYourself`, `ProbeUuid` match/mismatch, unsupported opcode returns, and FileServer compatibility during fsprobe polling.
