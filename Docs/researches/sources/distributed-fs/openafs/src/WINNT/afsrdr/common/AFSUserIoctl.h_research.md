# sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSUserIoctl.h

## Purpose
Assigns buffered device IOCTL codes used between user-mode OpenAFS components and the Windows AFS redirector/library devices.

## Important APIs, Types, And Functions
Defines IOCTLs for control/redirector/library initialization, processing IRP requests/results, setting/releasing/failing extents, invalidating cache, network/volume status, shutdown, sysname notification, status request, byte-range locks, debug trace config/retrieval, force crash, object info, authgroup create/query/set/reset/SID/logon operations, library trace config, and reparse policy get/set.

## Control Flow
User-mode service code calls `DeviceIoControl` with `CTL_CODE(FILE_DEVICE_DISK_FILE_SYSTEM, function, METHOD_BUFFERED, FILE_ANY_ACCESS)` and matching structs from `AFSUserStructs.h`.

## State And Persistence
No local state. IOCTLs mutate driver/service initialization state, extent ownership, cache invalidation, online/offline state, sysnames, authgroups, trace settings, and reparse policy.

## Dependencies And Integration Points
Requires Windows `CTL_CODE` definitions and pairs with `AFSUserDefines.h` and `AFSUserStructs.h`. It is a service/driver ABI boundary.

## Risks
Function code collisions or method/access changes break compatibility. `FILE_ANY_ACCESS` requires strong driver-side authorization. Buffered variable-length payloads need strict size validation.

## Test Signals
DeviceIoControl tests for correct/malformed buffers, authorization for dangerous operations, and cross-version service/driver compatibility.
