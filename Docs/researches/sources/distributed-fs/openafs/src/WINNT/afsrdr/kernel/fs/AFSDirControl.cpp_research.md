# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSDirControl.cpp

Purpose: handles `IRP_MJ_DIRECTORY_CONTROL` and forwards directory enumeration/change-notification work to the library device for redirector file objects.

Important APIs/types/functions: `AFSDirControl()` rejects the control device with `STATUS_INVALID_DEVICE_REQUEST`, gates redirector requests through `AFSCheckLibraryState()`, forwards with `IoCallDriver()`, and calls `AFSClearLibraryRequest()`.

Control flow: control-device requests complete locally as invalid. Redirector requests follow the common library-forwarding pattern: check state, complete locally on non-pending failure, leave pending alone, or skip the stack and call the library device.

State/persistence: no local persistent state. Directory state is owned by the library/redirector path.

Dependencies/integration: uses the control device extension's `LibraryDeviceObject`, shared completion and exception helpers, and the library request-state protocol.

Risks: pending library-state handling is the main correctness hazard. Directory control can be frequent and buffer-sensitive; this wrapper assumes the library validates detailed query parameters.

Test signals: control-device rejection, successful forwarding of query directory and notify change requests, library unavailable, pending queue behavior, and no local completion after `IoCallDriver()` ownership transfer.
