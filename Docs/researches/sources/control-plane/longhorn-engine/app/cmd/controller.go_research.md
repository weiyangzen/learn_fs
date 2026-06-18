# sources/control-plane/longhorn-engine/app/cmd/controller.go

## Purpose
Defines the `controller` CLI command that starts a Longhorn engine controller process, configures backends/frontends/timeouts/snapshot limits, starts initial replicas when provided, exposes the controller gRPC server, and waits for shutdown.

## Important APIs, Types, and Functions
- `ControllerCmd()` declares all startup flags.
- `startController()` performs validation, constructs backend factories and frontend, creates `controller.Controller`, registers shutdown hooks, starts replicas and gRPC service, then waits.
- `getControllerClient()` creates `pkg/controller/client.ControllerClient` using global identity flags.

## Control Flow
The command requires a positional volume name and validates it with `util.ValidVolumeName`. It parses nominal and current sizes via `docker/go-units.RAMInBytes`, derives short/long engine-replica timeouts and iSCSI target timeout, validates rebuild sync concurrency, constructs requested backend factories (`file`, `tcp`), optionally creates a frontend, and attempts a best-effort filesystem unfreeze before controller construction. If initial replicas are supplied, `control.Start` runs before gRPC serving; no-backend startup errors map to `ENODATA`. The gRPC address and server are then assigned and `StartGRPCServer` is called before `WaitForShutdown`.

## State and Persistence Behavior
Persistent volume state is owned by controller/backends/replicas, not this file. Startup flags configure controller behavior that affects persisted replica chains, frontend device lifecycle, snapshot pruning limits, unmap marking, rebuild sync concurrency, and upgrade/salvage behavior. Shutdown uses a wait group so registered shutdown completion is observed before process exit.

## Dependencies and Integration Points
Depends on `pkg/backend/dynamic`, file/remote backend factories, `pkg/controller`, controller gRPC RPC package, `pkg/types`, and `pkg/util`. It is the process entry point used by integration helpers `create_engine_process` and by many tests that interact through generated controller clients.

## Risks and Edge Cases
Unsupported backend names call `logrus.Fatalf`, exiting instead of returning. Startup with replicas can exit directly with status 1 or ENODATA. Timeout derivation and filesystem unfreeze are safety-sensitive because they affect failure detection and crash recovery. Invalid snapshot max size or nonpositive rebuild sync limit aborts startup.

## Test Signals
`integration/core/conftest.py` and `integration/data/conftest.py` start controller processes. `test_controller.py` verifies replica list/create/delete/update, volume start/shutdown, and expansion. `test_cli.py` validates engine restart, bad replica startup, expansion, and snapshot behavior after reattachment.
