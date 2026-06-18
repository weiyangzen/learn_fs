<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/ready_chunkservers_count_command.h -->
# sources/distributed-fs/lizardfs/src/admin/ready_chunkservers_count_command.h

## Purpose
Declares the ready chunkserver count command.

## Important APIs, Types, and Functions
`ReadyChunkserversCountCommand` overrides `name`, `usage`, and `run`.

## Control Flow, State, and Persistence
No state is declared in the header.

## Dependencies and Integration Points
Includes the base admin command. Implementation integrates chunkserver listing.

## Risks and Test Signals
Risk is mostly semantic drift between "ready" and the count predicate. Build and helper-based tests are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/ready_chunkservers_count_command.h -->
