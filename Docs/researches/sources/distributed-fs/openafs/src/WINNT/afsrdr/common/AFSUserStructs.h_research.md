# sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSUserStructs.h

## Purpose
Defines the user/kernel ABI payloads for the Windows AFS redirector service channel: request/result framing, initialization, directory/volume data, file mutations, extents, pioctl and pipe I/O, invalidation, locks, FID hold/release, cleanup, trace, object status, authgroups, reparse tags, direct file I/O, and reparse policy.

## Important APIs, Types, And Functions
Foundational structs are `AFSFileID`, `AFSCommRequest`, and `AFSCommResult`. Initialization uses `AFSRedirectorInitInfo`. Directory/volume structs include `AFSDirQueryCB`, `AFSDirEnumEntry`, `AFSDirEnumResp`, `AFSVolumeInfoCB`, and `AFSVolumeSizeInfoCB`. File operation structs cover create/open/access-release, extent request/set/release/failure, update/delete/rename/hardlink/symlink/eval, cleanup, and direct `AFSFileIOCB`/result. Service interfaces include pioctl and pipe control blocks. Locking uses byte-range request/result structs. Status/auth/reparse structs include invalidation, network/volume status, sysname notification, driver status, object status, authgroup request, `AFSReparseTagInfo`, and policy get/set.

## Control Flow
The driver queues an `AFSCommRequest` with request type, flags, authgroup, file ID, name, and operation-specific data. The service reads it through `IOCTL_AFS_PROCESS_IRP_REQUEST`, performs work, and returns `AFSCommResult` or side-channel IOCTL payloads such as extent and lock results. Variable-length data uses trailing arrays and offsets/lengths.

## State And Persistence
Structs represent live redirector/cache state: FID identity, directory snapshots, data versions, extents and dirty ranges, file times/sizes/attributes, lock ownership, authgroups, sysnames, object status, cache invalidation, and reparse behavior. They encode changes that may affect server state or local cache persistence.

## Dependencies And Integration Points
Depends on Windows scalar types, `GUID`, `LARGE_INTEGER`, `BOOLEAN`, and constants from `AFSUserDefines.h`. Paired with IOCTLs in `AFSUserIoctl.h` and internal structs in `AFSRedirCommonStructs.h`.

## Risks
High ABI risk. Flexible arrays require exact size/alignment checks for names, targets, EAs, extents, locks, and reparse buffers. Mapped pointers are context-sensitive and not generally trustworthy. Authgroup and LocalSystem requests need strict authorization. Time/data-version errors can expose stale cache.

## Test Signals
Verify structure sizes/offsets for 32-bit, 64-bit, and WOW64; fuzz lengths/counts/offsets; run directory enumeration with links; create/update/delete/rename/hardlink/symlink files; request/release extents; exercise pioctl/pipe paths; validate byte-range locks, authgroups, and reparse policy.
