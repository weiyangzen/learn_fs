# sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSUserDefines.h

## Purpose
Defines user-visible constants for the Windows AFS redirector service interface: symbolic link/device names, request type numbers, request flags, trace subsystem bits, invalidation reasons, extent flags, file types, sysname constants, access modes, and reparse policy controls.

## Important APIs, Types, And Functions
Key constants include `AFS_SYMLINK(_W)`, `AFS_PIOCTL_FILE_INTERFACE_NAME`, `AFS_GLOBAL_ROOT_SHARE_NAME`, `AFS_PAYLOAD_BUFFER_SIZE`, request types for dir enum/create/open/extents/update/delete/rename/pioctl/pipe/cleanup/link/direct I/O, request flags for synchronous, case-sensitive, WOW64, fast, hold FID, cleanup, LocalSystem PAG, cache bypass, and last component, trace levels/subsystems, invalidation reasons, extent flags, file types, and reparse policy values.

## Control Flow
No code. The redirector sends `AFS_REQUEST_TYPE_*` work items to the service, which interprets matching structs and flags and replies through result IOCTLs.

## State And Persistence
No state, but constants govern operations that affect directory enumeration, file mutations, extent caching, pioctl/pipe operations, authgroups, invalidation, and reparse policy.

## Dependencies And Integration Points
Shared by kernel and user-mode builds. Conditional definitions fill in NT status and file attributes outside kernel mode. Integrates with `AFSUserIoctl.h`, `AFSUserStructs.h`, afsd_service, and afsredir.sys.

## Risks
Request/flag numbers are ABI. Renumbering breaks compatibility. Synchronous request contract violations can hang requests. Trace/invalidation flag misuse causes stale or noisy behavior.

## Test Signals
Cross-version service/driver tests, unknown request rejection, trace filtering, invalidation reason handling, extent flag combinations, cache-bypass reads/writes, and reparse policy IOCTL tests.
