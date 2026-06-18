# sources/distributed-fs/openafs/src/WINNT/afsd/afsd_flushvol.h

## Purpose
`afsd_flushvol.h` declares the AFSD power-notification volume-flush interface and the internal thread, impersonation, pioctl, and logging helpers used by `afsd_flushvol.c`.

## Important APIs, types, and functions
The header defines `FLUSHVOLTHREADINFO`, containing handles for the power-event, main-resume, and terminate events. Public functions are `PowerNotificationThreadCreate`, `PowerNotificationThreadNotify`, and `PowerNotificationThreadExit`.

It also declares file-local helpers as `static`: `afsd_ServicePerformFlushVolumeCmd`, `afsd_ServiceFlushVolumesThreadProc`, `CheckAndCloseHandle`, `GetUserToken`, `ImpersonateClient`, and `LogTimingEvent`.

## Control flow
There is no executable code in the header. It documents the thread lifecycle contract: create the notification thread, notify it when a power event requires flushing, and exit it during service shutdown.

## State and persistence behavior
The declared `FLUSHVOLTHREADINFO` carries kernel object handles that coordinate in-memory service/thread state. The public API can lead to cache flushes and EventLog writes, but the header itself does not persist anything.

## Dependencies and integration points
The header includes `Winnetwk.h` for network-resource enumeration types and `fs_utils.h` for pioctl-related definitions. It integrates AFSD service power handling with the flush implementation and Windows event/thread primitives.

## Risks and edge cases
Declaring implementation helpers as `static` in a header is unusual; each includer would get private declarations and could hide mismatches if definitions change. Public lifecycle functions have no explicit state object, so they rely on globals in `afsd_flushvol.c` and can be misordered by callers. The header exposes no timeout or error-detail reporting beyond Boolean success.

## Test signals
Build tests should ensure only the intended implementation includes the static helper declarations. Integration tests should call create/notify/exit in normal and repeated sequences, verify Boolean return behavior on timeout/failure, and check that handle lifecycle remains valid across service power events.
