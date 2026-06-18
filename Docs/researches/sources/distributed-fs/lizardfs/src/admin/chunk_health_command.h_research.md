<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/chunk_health_command.h -->
# sources/distributed-fs/lizardfs/src/admin/chunk_health_command.h

## Purpose
Declares the `ChunksHealthCommand` admin command and its private printing/cache helpers.

## Important APIs, Types, and Functions
`ChunksHealthCommand` derives from `LizardFsProbeCommand` and overrides `name`, `supportedOptions`, `usage`, and `run`. Private members include option constants, `initializeGoals(ServerConnection&)`, `printState` helpers for `ChunksAvailabilityState` and `ChunksReplicationState`, `print(uint64_t)`, and static `goals`/`goalNames`.

## Control Flow, State, and Persistence
The header defines command object shape and process-static state but no logic. Static caches are shared by every instance in the process.

## Dependencies and Integration Points
Includes `common/chunks_availability_state.h`, `common/server_connection.h`, and `admin/lizardfs_admin_command.h`, tying this command to master protocol state and CLI dispatch.

## Risks and Test Signals
Risks include declaration drift with the `.cc` file, the unused declared `kOptionAll`, and static cache lifetime. Build coverage and CLI tests for all supported options are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/chunk_health_command.h -->
