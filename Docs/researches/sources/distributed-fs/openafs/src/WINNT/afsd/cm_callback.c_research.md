# sources/distributed-fs/openafs/src/WINNT/afsd/cm_callback.c

## Purpose
`cm_callback.c` implements the Windows OpenAFS cache manager callback service and local callback lifecycle. It receives file-server callback-break RPCs, tracks callback-grant races, exposes AFS callback/debug RPC entry points, renews or expires cached callback state, and optionally gives callbacks back to file servers during shutdown or network transitions. The core invariant is that a cached `cm_scache_t` may be trusted only while its callback server and expiration state are current, or while read-only volume callback rules deliberately preserve validity.

## Important APIs and Types
Key exported cache-manager routines are `cm_InitCallback`, `cm_HaveCallback`, `cm_StartCallbackGrantingCall`, `cm_EndCallbackGrantingCall`, `cm_GetCallback`, `cm_CheckCBExpiration`, `cm_CallbackNotifyChange`, `cm_GiveUpAllCallbacks*`, and the callback RPC server functions `SRXAFSCB_*`. The file owns `cm_callbackLock`, `cm_callbackCount`, `cm_activeCallbackGrantingCalls`, and `cm_racingRevokesp`; `cm_racingRevokes_t` records callback breaks that may race with outstanding callback-granting RPCs. Global flags include `cm_OfflineROIsValid`, `cm_giveUpAllCBs`, and `cm_shutdown`.

## Control Flow
Incoming `SRXAFSCB_CallBack` maps the Rx peer to a file server/cell, then dispatches per-FID breaks to `cm_RevokeCallback` or volume breaks to `cm_RevokeVolumeCallback`. Both record a racing revoke before scanning scache buckets, then discard matching callbacks, invalidate redirector objects, and issue SMB notify-change events. `SRXAFSCB_InitCallBackState*` handles server-wide callback loss by recording a cancel-all race marker and scanning all cached vnodes from that server. `cm_GetCallback` obtains `CM_SCACHESYNC_FETCHSTATUS | CM_SCACHESYNC_GETCALLBACK`, starts race tracking, drops the scache lock for `RXAFS_FetchStatus`, uses `cm_Analyze` for retry/failover, then merges status only if `cm_EndCallbackGrantingCall` did not detect a racing revoke.

## State and Persistence
Callback state lives in memory on `cm_scache_t` (`cbServerp`, `cbExpires`, `cbIssued`) and for pure read-only volumes on `cm_volume_t` (`cbExpiresRO`, `cbServerpRO`, `creationDateRO`, `volumeSizeRO`). No durable callback state is written. A registry setting, `CallBack Notify Change Delay`, is read dynamically to delay notifications by at most five seconds.

## Dependencies and Integration Points
This file integrates with Rx callback RPC stubs, `cm_scache`, `cm_volume`, `cm_server`, `cm_conn`, redirector invalidation (`RDR_InvalidateObject`, `RDR_InvalidateVolume`), SMB notifications, freelance root handling, event/logging helpers, and XDR allocation for debug RPC replies.

## Risks and Test Signals
Race safety depends on strict lock ordering and balanced active-callback counts; tests should force callback breaks while `FetchStatus` is in flight and verify stale callbacks are not installed. Expiration tests should cover pure RO volumes, offline/all-down volumes, server multihoming, redirector invalidation, and SMB change notifications. Risk areas include long global scache scans, registry reads on every notification, pointer truncation in debug RPCs, and callback-server reference ownership in `cm_EndCallbackGrantingCall`.
