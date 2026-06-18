# sources/distributed-fs/ceph-client/drivers/md/dm-ps-queue-length.c

## Purpose
Implements the `queue-length` multipath path selector. It chooses the valid path with the fewest in-flight I/Os and uses list rotation to spread ties across paths.

## Important APIs, Types, And Functions
`struct selector` holds valid and failed path lists protected by a spinlock. `struct path_info` stores the `dm_path`, repeat count, and atomic in-flight I/O count `qlen`. The registered selector callbacks are `ql_create()`, `ql_destroy()`, `ql_add_path()`, `ql_fail_path()`, `ql_reinstate_path()`, `ql_select_path()`, `ql_start_io()`, `ql_end_io()`, and `ql_status()`.

## Control Flow
Path addition parses an optional repeat count, deprecates values above one by forcing them to one, allocates path context, and appends the path to the valid list. Selection scans valid paths under lock, stops early when it finds a zero-queue path, moves the selected path to the tail, and returns the associated `dm_path`. `start_io` increments `qlen`; `end_io` decrements it. Failure and reinstate move path contexts between lists under lock.

## State And Persistence
The only dynamic metric is the atomic in-flight request count per path. Lists and counts are reset on table reload. There is no persistent state and no history of latency or throughput.

## Dependencies And Integration Points
The file integrates with DM multipath through the path-selector registration API. The multipath core is responsible for calling start/end hooks around I/O so `qlen` remains accurate. Status exposes the current `qlen` in `STATUSTYPE_INFO` and repeat count in `STATUSTYPE_TABLE`.

## Risks
If the multipath core or an error path misses `end_io`, a path can be permanently penalized. The metric counts requests, not bytes, so large and small bios are weighted equally. Atomic reads during selection can race completions but are acceptable for heuristic load balancing. Repeat-count compatibility remains in the table grammar but no longer changes behavior above one.

## Test Signals
Test balanced selection at equal queue depth, preference for lower queue depth, fail/reinstate list movement, and start/end balancing under errors. Status should show `qlen` rising under outstanding I/O and returning to zero after completion. Module load should register version `0.2.0`.
