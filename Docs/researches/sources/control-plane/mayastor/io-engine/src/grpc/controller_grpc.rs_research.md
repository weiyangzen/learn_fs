# sources/control-plane/mayastor/io-engine/src/grpc/controller_grpc.rs

## Purpose
Provides gRPC-facing helper functions for listing NVMe controllers and fetching per-controller I/O statistics.

## Important APIs, Types, and Functions
- `NvmeControllerInfo` includes controller name, state, namespace size, and block size.
- `NvmeController::to_info()` converts controller runtime state into response data.
- `controller_stats(controller_name)` asynchronously obtains `BlockDeviceIoStats`.
- `list_controllers()` returns info for all names in `NVME_CONTROLLERS`.

## Control Flow and State
`controller_stats` looks up a controller by name, creates a oneshot, locks the controller, calls its callback-style `get_io_stats`, and awaits the result. If submission fails, it logs and returns the `CoreError`. If the controller name is absent, it returns `CoreError::BdevNotFound`. `list_controllers` iterates the controller registry names, re-lookups each controller, locks it, and converts it to info. Namespace absence yields zero size and block size.

State lives in `NVME_CONTROLLERS`; this file only reads it and bridges callback results to async.

## Dependencies and Integration Points
Used by gRPC v0/v1 host/controller services and io-engine client controller stats commands. Depends on `NvmeController`, `NvmeControllerState`, `NVME_CONTROLLERS`, `BlockDeviceIoStats`, `CoreError`, and callback helpers.

## Risks and Test Signals
Registry entries can disappear between name listing and lookup, so `filter_map` intentionally skips missing controllers. The stats oneshot expects a callback response; if callback is never invoked, callers await forever. Tests should cover missing controller error, namespace-less controller info, stats success/failure, and concurrent registry mutation during list.
