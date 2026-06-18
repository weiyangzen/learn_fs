# sources/distributed-fs/openafs/src/afs/afs_callback.c

Purpose: Implements the RX callback service exported by the cache manager to fileservers and debugging clients. It breaks callbacks, reports cache/lock/server/cell state, returns xstats and cache configuration, and identifies the client to servers.

Important APIs and functions: Debug RPCs include `SRXAFSCB_GetCE`, `SRXAFSCB_GetCE64`, and `SRXAFSCB_GetLock`. Callback RPCs include `SRXAFSCB_CallBack`, `SRXAFSCB_Probe`, `SRXAFSCB_InitCallBackState`, `SRXAFSCB_InitCallBackState3`, and `SRXAFSCB_ProbeUuid`. Information RPCs include `SRXAFSCB_WhoAreYou`, `SRXAFSCB_TellMeAboutYourself`, `SRXAFSCB_GetServerPrefs`, `SRXAFSCB_GetCellServDB`, `SRXAFSCB_GetLocalCell`, `SRXAFSCB_GetCacheConfig`, and `SRXAFSCB_GetCellByNum`. `ClearCallBack` is the key invalidation helper, and `afs_RXCallBackServer` donates a daemon thread to RX.

Control flow: RPC entry points acquire the AFS GLOCK, gather stats, perform their operation, and release the GLOCK. `SRXAFSCB_CallBack` iterates incoming FIDs and calls `ClearCallBack`, which handles whole-volume callback breaks when vnode is zero or single-FID breaks otherwise. It scans vcache hash chains, clears callback pointers/hints, waits around initializing/dead vnodes, takes vnode references, stales cache flags, and resets volume info for volume breaks. Init-callback-state finds the calling server, stales every vcache callback from it, clears capability knowledge, resets affected volumes, and purges the DNLC.

State and persistence: Updates volatile counters (`afs_allCBs`, odd/even callback/zap counts, `afs_connectBacks`), callback pointers and expiration state in vcaches, server capability flags, volume info, DNLC entries, and interface identity in `afs_cb_interface`. Returned RPC buffers are allocated for the RX stub to free. No durable state is written.

Dependencies and integration points: Depends on generated callback RPC interfaces, RX call/peer APIs, vcache and volume hash tables, server lookup, cell management, interface-address tracking, cache init parameters, stats/xstats, lock tables, and platform vnode reference APIs.

Risks: Hash-chain scans deliberately drop and reacquire locks around vnode refs, so iterator restart logic must remain correct. Debug RPCs expose pointer-derived addresses and lock internals. Several callbacks allocate output buffers while holding global state. `InitCallBackState3` currently delegates to address-based lookup instead of UUID lookup, leaving multi-homed/server-identity ambiguity.

Test signals: Break one file callback, whole-volume callback, callback for initializing/dead vnodes, init callback state from a known and unknown server, probe UUID match/mismatch, xstats collections, cache-config marshalling, server preference enumeration, cell DB/local cell/cell-by-number results, callback server startup wait for `afs_server`, and shutdown counter reset.
