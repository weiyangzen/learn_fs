# sources/distributed-fs/ceph-client/include/uapi/linux/membarrier.h

## Purpose
Defines the `membarrier(2)` command and flag ABI for issuing process-wide, system-wide, expedited, sync-core, and restartable-sequence memory ordering operations.

## Important APIs, Types, And Functions
Exports `enum membarrier_cmd` with query, global, global expedited, private expedited, private expedited sync-core, private expedited rseq, registration commands, `MEMBARRIER_CMD_GET_REGISTRATIONS`, and compatibility alias `MEMBARRIER_CMD_SHARED`. `enum membarrier_cmd_flag` exports `MEMBARRIER_CMD_FLAG_CPU`.

## Control Flow
Userspace calls `membarrier(MEMBARRIER_CMD_QUERY, ...)` to discover support, registers for relevant expedited commands, then invokes barriers. Some commands require prior registration and return `-EPERM`; unsupported architecture features return `-EINVAL`. RSEQ command can target one CPU when the CPU flag is supplied.

## State, Persistence, And Dependencies
Registration state is per-process and visible through `MEMBARRIER_CMD_GET_REGISTRATIONS`. The header has no dependencies beyond standard C enum layout.

## Integration Points
Used by runtimes, JITs, RCU-like libraries, and restartable sequence users that need inter-thread ordering or instruction stream serialization.

## Risks
Commands are bit positions except query value zero; treating query as a bit is wrong. Missing registration, unsupported sync-core/rseq support, or assuming non-running threads execute barriers immediately can lead to subtle correctness bugs.

## Test Signals
Check query bitmasks, registration idempotence, `GET_REGISTRATIONS`, failure paths for unregistered expedited calls, CPU-targeted rseq behavior, and architecture-specific sync-core availability.
