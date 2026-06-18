# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSFlushBuffers.cpp

Purpose: handles flush-buffer IRPs and forwards redirector flushes to the library while rejecting the control device.

Important APIs/types/functions: `AFSFlushBuffers()` rejects `AFSDeviceObject` with `STATUS_INVALID_DEVICE_REQUEST`, calls `AFSCheckLibraryState()`, forwards to `LibraryDeviceObject`, and calls `AFSClearLibraryRequest()`.

Control flow: follows the common dispatch-wrapper pattern without a structured exception wrapper. Local invalid or library-state failure is completed immediately; pending or forwarded requests are left to the library/lower path.

State/persistence: local code persists no state. Flush semantics and cache durability are implemented by the library/redirector lower path.

Dependencies/integration: depends on `AFSDeviceObject`, `AFSDeviceExt`, library state management, and IRP completion helpers.

Risks: flush operations are durability-sensitive; this wrapper assumes `AFSCheckLibraryState()` and the library device will serialize correctly with cache manager callbacks. Unlike several sibling dispatchers, this function uses `__Enter` but no explicit `__try/__except`, so exception behavior depends on macro definitions.

Test signals: control-device rejection, forwarded flush on regular files, library unavailable/pending behavior, interaction with cache-manager flush callbacks, and shutdown-time flush handling.
