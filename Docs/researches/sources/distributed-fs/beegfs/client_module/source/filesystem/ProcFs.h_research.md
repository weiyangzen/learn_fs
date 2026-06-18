# sources/distributed-fs/beegfs/client_module/source/filesystem/ProcFs.h

## Purpose
Declares the BeeGFS procfs management and callback interface.

## Important APIs and Types
Exports global and per-mount create/remove functions, seq-file read callbacks for config/build/status/fs UUID/nodes/client info/target states/toggles/log levels, write callbacks for toggles/drop connections/log levels/remap failure, and proc data compatibility helpers.

## Control Flow
The declarations mirror the static proc entry tables in `ProcFs.c`. Open/write callbacks recover `App*` from proc metadata and delegate behavior to `ProcFsHelper`.

## State and Persistence
No owned state. It declares interfaces that operate on per-mount proc entries and `App` runtime state.

## Dependencies and Integration Points
Includes target state store, common types, `App`, Linux procfs, and seq_file. Used by superblock mount lifecycle and procfs implementation.

## Risks
The public surface includes internal-looking `__ProcFs_*` callbacks; external misuse could bypass expected procfs data setup. Declaration drift against `ProcFs.c` or helper tables can break builds.

## Test Signals
Compile with procfs API variants and run proc entry open/read/write smoke tests through the declared callbacks.
