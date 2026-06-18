# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSVolumeInfo.cpp

## Purpose
`AFSVolumeInfo.cpp` handles volume-information IRPs. Query requests are forwarded to the library driver; set requests are rejected as invalid.

## Important APIs, Control Flow, And State
`AFSQueryVolumeInfo` rejects control-device requests, gates on `AFSCheckLibraryState`, completes on errors unless queued, skips the current stack location, forwards to `LibraryDeviceObject`, and clears the in-flight guard. `AFSSetVolumeInfo` logs the file object and completes with `STATUS_INVALID_DEVICE_REQUEST` without forwarding. No local volume metadata is maintained.

## Dependencies And Integration Points
Volume query answers come from the library driver. This file depends on library state management, common completion/exception support, and the control device extension's `LibraryDeviceObject`.

## Risks And Test Signals
Set-volume operations always fail, so callers attempting label or filesystem metadata changes should receive a consistent invalid-device response. Query behavior depends on library readiness and can pend through the queue. Tests should cover query pass-through, set rejection, absent-library queuing, control-device rejection, and library failure propagation.
