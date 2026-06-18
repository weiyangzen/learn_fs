<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/chunk_health_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/chunk_health_command.cc

## Purpose
Implements `lizardfs-admin chunks-health`, reporting chunk availability, replication backlog, and deletion backlog by goal.

## Important APIs, Types, and Functions
Defines static goal caches `ChunksHealthCommand::goals` and `goalNames`, option strings `--availability`, `--replication`, and `--deletion`, plus methods `name`, `supportedOptions`, `usage`, `initializeGoals`, `run`, two `printState` overloads, and `print(uint64_t)`.

## Control Flow, State, and Persistence
`run` requires master host/port, sends `cltoma::chunksHealth::build(false)`, deserializes availability and replication state from `LIZ_MATOCL_CHUNKS_HEALTH`, rejects a regular-only response, then lazily loads goal IDs/names via `listGoals`. It prints all reports by default or a filtered subset when options are provided. State persists only in process-static goal caches, which can become stale if goal definitions change during a long-running process, although this CLI normally exits after one command.

## Dependencies and Integration Points
Depends on `ServerConnection`, `protocol/cltoma.h`, `protocol/matocl.h`, `ChunksAvailabilityState`, `ChunksReplicationState`, and goal serialization from the master.

## Risks and Test Signals
Risks include static goal cache reuse, output not escaping goal names in porcelain mode, implicit trust that all goal IDs in state exist in `goalNames`, and duplicate wording typos in option descriptions. Test signals are empty and nonempty availability/replication/deletion states, goal name lookup, all report filters, porcelain/non-porcelain output, incorrect response type handling, and connection/protocol errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/chunk_health_command.cc -->
