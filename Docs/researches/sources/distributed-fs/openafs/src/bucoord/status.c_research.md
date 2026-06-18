# sources/distributed-fs/openafs/src/bucoord/status.c

## Purpose
Provides shared status-queue primitives for backup coordinator tasks. It initializes locks, creates/finds/deletes status nodes, and sets or clears task status flags under the queue lock.

## Important APIs, Types, And Functions
Public functions are `initStatus`, `lock_Status`, `unlock_Status`, `lock_cmdLine`, `unlock_cmdLine`, `clearStatus`, `createStatusNode`, `deleteStatusNode`, `findStatus`, and `setStatus`. It operates on external globals `statusHead`, `statusQueueLock`, and `cmdLineLock`.

## Control Flow
`initStatus` initializes the queue sentinel and locks. `createStatusNode` allocates a zeroed status object, links it at the back of `statusHead`, marks it `STARTING`, and returns it for caller population. `findStatus` linearly scans the queue by `taskId`. `setStatus` and `clearStatus` lock, find the node, update flags, and unlock. `deleteStatusNode` unlinks and frees a status node and its optional `cmdLine`.

## State And Persistence
State is transient in-memory status records linked through an intrusive `dlq` queue. There is no persistence. The queue is protected by `statusQueueLock`; command-line string access can be protected separately with `cmdLineLock`.

## Dependencies And Integration Points
Depends on `dlq.c`, OpenAFS lock primitives, `bc.h` status types, and com_err/command headers. Dump, restore, tape, database, job, kill, and status watcher code all coordinate through these helpers.

## Risks And Test Signals
`findStatus` does not lock internally, so callers must know whether they already hold the queue lock; some code intentionally does. `deleteStatusNode` assumes the node is currently linked and not concurrently observed. Test signals include create/find/set/clear/delete under lock, deleting nodes with `cmdLine`, concurrent status watcher updates, kill/abort flag propagation, and scheduled dump queue behavior.
