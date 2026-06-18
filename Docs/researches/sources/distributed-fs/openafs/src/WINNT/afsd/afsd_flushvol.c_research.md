# sources/distributed-fs/openafs/src/WINNT/afsd/afsd_flushvol.c

## Purpose
`afsd_flushvol.c` handles flushing AFS volumes in response to Windows power notifications such as hibernate/resume coordination. It runs a helper thread, impersonates the logged-in shell user, enumerates connected network resources, identifies AFS volume UNC paths, issues `VIOC_FLUSHVOLUME` pioctls, logs timing/failure events, and coordinates completion with the service main thread.

## Important APIs, types, and functions
The pioctl wrapper is `afsd_ServicePerformFlushVolumeCmd`. The main flush routine is `afsd_ServicePerformFlushVolumes`. Thread and service integration functions are `PowerNotificationThreadCreate`, `PowerNotificationThreadNotify`, `PowerNotificationThreadExit`, and `afsd_ServiceFlushVolumesThreadProc`.

Security/session helpers are `GetUserToken` and `ImpersonateClient`. Resource helpers are `CheckAndCloseHandle` and `LogTimingEvent`. Static globals `gThreadInfo` and `gThreadHandle` hold event/thread handles.

## Control flow
`PowerNotificationThreadCreate` creates three named events for power notification, main-thread resume, and termination, then starts `afsd_ServiceFlushVolumesThreadProc`. The thread waits on terminate and power events. On terminate, it reverts impersonation, closes event handles, and exits. On power event, it impersonates the logged-in shell user, calls `afsd_ServicePerformFlushVolumes`, resets the power event, and signals the resume event.

`PowerNotificationThreadNotify` signals the power event and waits for resume, bounded by `HardDeadtimeout * 1000`. `PowerNotificationThreadExit` signals terminate and waits for the thread.

The flush routine obtains the AFS share name via `smb_GetSharename`, determines the server prefix, opens a connected-resource enumeration with `WNetOpenEnum`, scans each `NETRESOURCE`, filters resources whose remote name matches the AFS share prefix but is not the root share itself, and calls `pioctl(..., VIOC_FLUSHVOLUME, ...)` for each volume. It logs per-volume timing on success, warning on failure, and total volume count/time at the end.

## State and persistence behavior
State is in-memory thread/event state plus the current impersonation token. The routine does not persist configuration. It can change cache-manager state by flushing cached volume data. EventLog entries are persisted through `LogEvent`. The thread uses named kernel objects, so names can collide with existing objects in the session/global namespace.

## Dependencies and integration points
The file depends on AFSD cache-manager state (`cm_noIPAddr`, `HardDeadtimeout`), SMB share naming (`smb_GetSharename`), Windows network resource enumeration (`WNetOpenEnum`, `WNetEnumResource`, `WNetCloseEnum`), shell/window-station APIs for token discovery, impersonation APIs, `pioctl`/`VIOC_FLUSHVOLUME`, `fs_utils.h`, `lanahelper.h`, and AFSD event logging. It is called from service power-notification paths outside this file.

## Risks and edge cases
`cm_noIPAddr == 0` short-circuits flushing with a comment indicating loopback-only handling; that condition should be verified against the variable's actual semantics. `WNetOpenEnum` failure leaks `lpNetResBuf` because the buffer is allocated before opening enumeration and not freed on that path. `ImpersonateClient` does not close `hUserToken` after `ImpersonateLoggedOnUser`, leaking a token handle on success and failure after token acquisition. The flush thread impersonates once and does not call `RevertToSelf` after each flush cycle, only on termination. `PowerNotificationThreadCreate` logs `eventName` on existing events without initializing the buffer. Named events can collide with stale or maliciously created objects. `CheckAndCloseHandle` nulls only its local copy, leaving globals unchanged. `GetTickCount` elapsed math ignores wraparound for long intervals. The thread closes handles that are also stored globally, creating possible stale-handle use if exit paths race.

## Test signals
Tests should cover share-name null/bad/root-only cases, WNet enumeration success/failure/no-more-items, filtering of AFS root share versus child volume paths, pioctl success/failure, total/per-volume event logs, timeout behavior in `PowerNotificationThreadNotify`, clean thread termination, token acquisition with and without shell desktop access, handle leak detection for token and enumeration error paths, and duplicate named-event collision behavior.
