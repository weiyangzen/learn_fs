# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSShutdown.cpp

## Purpose
`AFSShutdown.cpp` handles `IRP_MJ_SHUTDOWN` and records clean shutdown state for configurations that require it. The actual filesystem shutdown hook is currently a no-op.

## Important APIs, Control Flow, And State
`AFSShutdown` retrieves the IRP stack, and if `AFS_DBG_REQUIRE_CLEAN_SHUTDOWN` is set in `AFSDebugFlags`, writes `AFS_REG_SHUTDOWN_STATUS` as `1` through `AFSUpdateRegistryParameter`. It calls `AFSShutdownFilesystem`, normalizes any failure back to success, completes the IRP, and returns success. `AFSShutdownFilesystem` currently just returns `STATUS_SUCCESS`.

## Dependencies And Integration Points
This file participates in the clean-shutdown contract enforced by `DriverEntry`, which rejects load if clean shutdown was required and the registry did not show a clean value. It depends on registry update helpers, tracing, exception filtering, dump support, and `AFSCompleteRequest`.

## Risks And Test Signals
Because `AFSShutdownFilesystem` is empty and failures are suppressed, shutdown persistence relies almost entirely on the registry marker. Tests should verify the shutdown marker transitions from dirty at load to clean at shutdown, behavior when registry writes fail, completion of shutdown IRPs, and that unload/redirector closure paths elsewhere handle real resource cleanup.
