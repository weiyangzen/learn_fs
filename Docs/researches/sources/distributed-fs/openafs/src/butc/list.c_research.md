# sources/distributed-fs/openafs/src/butc/list.c

## Purpose
`list.c` maintains the volatile list of active `butc` task nodes (`struct dumpNode`) carrying dump/restore parameters from RPC handlers to worker threads.

## Important APIs, Types, and Functions
`InitNodeList(portOffset)` seeds task ids as `(portOffset * 1000) + 1` and initializes a dummy head. `allocTaskId()` returns monotonically increasing ids. `CreateNode()` allocates and prepends a zeroed node. `FreeNode(taskID)` unlinks and frees a node plus `dumpName`, `volumeSetName`, `restores`, and `dumps`. `GetNthNode()` and `GetNode()` provide lookup by list position or task id.

## Control Flow
`tcmain.c` initializes the list at startup. `tcprocs.c` creates nodes when starting asynchronous dump/restore work. `dump.c` and `lwps.c` free nodes when workers finish.

## State and Persistence Behavior
All state is process-local heap memory. Task ids are not reused until process restart. No BUDB or tape state is persisted here.

## Dependencies and Integration Points
Depends on `struct dumpNode` and backup RPC descriptor types from AFS headers. Integrates with `tcprocs.c`, `dump.c`, `lwps.c`, and status/task id reporting.

## Risks and Test Signals
The list is not internally locked, so pthread builds should be stress-tested for concurrent create/free/lookup. `CreateNode()` asserts on allocation failure. `FreeNode()` silently ignores unknown ids. Tests should verify port-offset id ranges, create/free memory ownership, cleanup after failed worker creation, and missing-node return codes.
