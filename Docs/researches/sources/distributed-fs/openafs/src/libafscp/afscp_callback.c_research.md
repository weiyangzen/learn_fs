<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_callback.c -->
# sources/distributed-fs/openafs/src/libafscp/afscp_callback.c

## Purpose
Implements libafscp callback tracking and the minimal Cache Manager callback RPC service that fileservers expect from an AFS client. It records callbacks for fetched FIDs, expires and invalidates stat cache entries, returns callbacks to servers, and responds to server callback RPCs such as break-callback, probe, who-are-you, and init-callback-state.

## Important APIs, Types, And Functions
Important globals are `afs_cb_inited`, `afs_cb_interface`, `afscp_maxcallbacks`, `afscp_cballoced`, and `allcallbacks`. Public helpers include `afscp_FindCallBack`, `afscp_AddCallBack`, `afscp_RemoveCallBack`, `afscp_ReturnCallBacks`, and `afscp_ReturnAllCallBacks`. Server-side RPC handlers include `SRXAFSCB_CallBack`, `SRXAFSCB_InitCallBackState`, `SRXAFSCB_Probe`, `SRXAFSCB_GetLock`, `SRXAFSCB_GetCE`, `SRXAFSCB_GetCE64`, `SRXAFSCB_XStatsVersion`, `SRXAFSCB_GetXStats`, `SRXAFSCB_InitCallBackState2`, `SRXAFSCB_TellMeAboutYourself`, `SRXAFSCB_WhoAreYou`, `SRXAFSCB_InitCallBackState3`, `SRXAFSCB_ProbeUuid`, `SRXAFSCB_GetServerPrefs`, `SRXAFSCB_GetCellServDB`, `SRXAFSCB_GetLocalCell`, `SRXAFSCB_GetCacheConfig`, and `SRXAFSCB_GetCellByNum`.

## Control Flow
`init_afs_cb` creates a client UUID and records interface addresses using Windows `syscfg_GetIFInfo` or Unix `rx_getAllAddr`. Callback lookup scans the global array for matching FID/server, expires old entries, and invalidates stats if necessary. Add scans for expired/free or matching slots, grows the array by doubling from four entries, stores callback metadata, and updates stat cache from fetch status. Remove and server break/init callbacks clear validity and invalidate stats. Return paths batch valid callbacks up to `AFSCBMAX`, mark them `CB_DROPPED`, call `RXAFS_GiveUpCallBacks` over server addresses, clear local entries, and free the global list on return-all. Most diagnostic callback RPCs return success with minimal data or `RXGEN_OPCODE` for unsupported queries.

## State And Persistence
State is memory-only: callback records, callback UUID/interface address, validity flags, expiration base times, and stat-cache side effects. `SRXAFSCB_TellMeAboutYourself` allocates capabilities data via `xdr_alloc` for the RPC response. No disk state is persisted.

## Dependencies And Integration Points
The file depends on Rx callback server stubs, fileserver RPCs, `afsutil`, `afscp_internal` stat cache helpers, server lookup by address/index, and platform network-interface discovery. It lets libafscp behave enough like a cache manager for fileservers to grant and revoke callbacks.

## Risks And Test Signals
Risks include unsynchronized global callback arrays in multithreaded callers, subtle expiration arithmetic, invalidation in nested loops, allocation ownership of capabilities buffers, minimal stub responses that may not satisfy newer server diagnostics, UUID/interface handling differences on Windows, and return-callback batching errors. Tests should cover callback add/find/expire/remove, server break callbacks, init-state invalidation, return-all cleanup, probe UUID mismatch, interface reporting, stat-cache invalidation, and concurrent access if libafscp is used from multiple threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_callback.c -->
