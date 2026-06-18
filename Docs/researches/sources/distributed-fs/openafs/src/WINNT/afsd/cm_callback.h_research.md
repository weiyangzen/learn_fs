# sources/distributed-fs/openafs/src/WINNT/afsd/cm_callback.h

## Purpose
`cm_callback.h` defines the public interface for callback management in the Windows cache manager. It declares the request/race-tracking structures, callback acquisition flags, file notification filter constants, exported callback lifecycle APIs, and global callback flags shared by the daemon, connection, and scache layers.

## Important APIs and Types
`cm_callbackRequest_t` captures the callback counter at the start of a callback-granting RPC, the start time used to compute expiration, and the server that granted the callback. `cm_racingRevokes_t` is the queued record for revokes that arrive while callback-granting calls are active; it stores a queue node, FID, callback count, and cancellation flags. `CM_RACINGFLAG_CANCELALL`, `CM_RACINGFLAG_CANCELVOL`, and `CM_RACINGFLAG_ALL` describe revoke scope. `CM_CALLBACK_MAINTAINCOUNT` and `CM_CALLBACK_BULKSTAT` tune `cm_EndCallbackGrantingCall` behavior. `FILE_NOTIFY_GENERIC_DIRECTORY_FILTER` and `FILE_NOTIFY_GENERIC_FILE_FILTER` define notification masks used when callback loss must wake Windows consumers.

## Control Flow
Callers wrap callback-returning RPCs with `cm_StartCallbackGrantingCall` and `cm_EndCallbackGrantingCall`. They use `cm_HaveCallback` as a cheap validity predicate and `cm_GetCallback` to fetch status and install a callback if needed. The daemon calls `cm_CheckCBExpiration`, and server/network shutdown paths call `cm_GiveUpAllCallbacks*`.

## State and Persistence
The header exposes `cm_callbackLock`, `cm_OfflineROIsValid`, `cm_giveUpAllCBs`, and `cm_shutdown`; all are process-memory controls. Persistence is intentionally absent because callbacks are server leases, not cache-disk metadata.

## Dependencies and Integration Points
The header depends on `osi.h`, `cm_scache.h`, AFS callback protocol structures, server/user/request types declared elsewhere, and Windows `FILE_NOTIFY_CHANGE_*` constants. It is consumed by files that fetch status, process file-server callbacks, run background expiration, or drain callbacks before server teardown.

## Risks and Test Signals
Consumers must observe the locking and active-count contract implied by `cm_callbackRequest_t`; mismatched start/end calls can leak race records or underflow counts. Tests should verify build visibility of all callback APIs, correct flag propagation for bulk status, and no accidental persistence assumptions.
