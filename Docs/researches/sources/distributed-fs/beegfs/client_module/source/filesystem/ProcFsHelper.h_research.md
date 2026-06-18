# sources/distributed-fs/beegfs/client_module/source/filesystem/ProcFsHelper.h

## Purpose
Declares procfs formatting and write-control helpers used by `ProcFs.c`.

## Important APIs and Types
Declares V2 seq-file read helpers for config, build config, status, fs UUID, nodes, client info, target states, connection retries, netbench mode, and log levels. Also declares legacy buffer-style read helpers, write helpers for mutable proc entries, and node/root/connection formatting helpers.

## Control Flow
The header separates procfs wrapper mechanics from the actual read/write behavior. `ProcFs.c` calls these functions after resolving the per-mount `App`.

## State and Persistence
No owned state. Functions operate on live `App`, node, target, config, and logger state.

## Dependencies and Integration Points
Includes `App`, common definitions, `NodeStoreEx`, and seq_file. It is an integration boundary between procfs VFS callbacks and BeeGFS internal state.

## Risks
Several legacy buffer-style declarations appear not implemented in the current `ProcFsHelper.c` excerpt, so callers should prefer V2 seq helpers unless legacy implementation exists elsewhere. Declaration drift can hide dead APIs.

## Test Signals
Compile all procfs users, verify each declared V2 helper has a definition, and run proc read/write smoke tests with representative app state.
