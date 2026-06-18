# sources/control-plane/longhorn-engine/integration/common/cli.py

## Purpose
Defines pytest fixtures for process-manager clients used by integration tests.

## Important APIs, Types, and Functions
- `em_client` fixture connects to engine instance manager.
- `pm_client` fixture connects to replica instance manager.

## Control Flow
Each fixture constructs `ProcessManagerClient` for a configured address and registers `cleanup_process` as finalizer.

## State and Persistence Behavior
No persistent state. It ensures spawned processes are deleted after tests via process-manager cleanup.

## Dependencies and Integration Points
Depends on `common.core.cleanup_process`, `common.constants` instance-manager addresses, and generated `ProcessManagerClient`.

## Risks and Edge Cases
Default fixture arguments bind addresses at definition time. Cleanup asserts all processes are gone, so lingering process-manager failures fail tests.

## Test Signals
Used as shared fixture infrastructure; no direct assertions here beyond cleanup behavior in `common.core`.
