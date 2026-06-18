# sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSUserPrototypes.h

## Purpose
Declares user/cache-manager functions that notify or service the Windows AFS redirector. This is the call surface from afsd/cache-manager events into redirector coordination.

## Important APIs, Types, And Functions
Exports `RDR_Initialize`, shutdown notify/final, network status and address change notifications, volume status/invalidation, object invalidation, file status setting, sysname notification, background fetch, suspend/resume, and `RDR_RequestExtentRelease`.

## Control Flow
Cache-manager code calls these functions when redirector state must initialize, invalidate, update, or drain. Extent release sends file extent lists to the redirector; sysname and volume/network notifications update kernel-visible state.

## State And Persistence
No header state. Implementations affect redirector state, cache extents, object validity, volume state, and service lifecycle state.

## Dependencies And Integration Points
Depends on `cm_fid_t`, `cm_scache_t`, `cm_user_t`, `cm_req_t`, `AFSFileExtentCB`, `GUID`, and Windows scalar types. Integrates cache-manager events with afsredir.sys.

## Risks
Mixed `DWORD` and `afs_int32` return types require caller care. Stale FIDs/authgroups can invalidate wrong objects. Async background fetch must preserve scache/user lifetimes.

## Test Signals
Initialization, network up/down, volume online/offline, object invalidation, sysname changes, cache-pressure extent release, suspend/resume, and shutdown sequencing validate the API.
