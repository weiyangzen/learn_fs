# sources/distributed-fs/openafs/src/vol/salvsync-server.c

## Purpose
Implements the server-side SALVSYNC scheduler and socket protocol for the demand-attach salvage server. It accepts client commands, maintains queued and pending salvage work, groups clone requests under parent volume groups, chooses work by partition/priority, tracks child completion, and notifies the fileserver on salvage failure.

## Important APIs, Types, And Functions
Public server entry points are `SALVSYNC_salvInit`, `SALVSYNC_getWork`, and `SALVSYNC_doneWorkByPid`. Important internal pieces include `SALVSYNC_syncThread`, `SALVSYNC_newconnection`, `SALVSYNC_com`, handler-array helpers, `AllocNode`, queue insert/remove helpers, `LookupNode`, `LookupNodeByCommand`, `LinkNode`, `HandlePrio`, `UpdateCommandPrio`, and command handlers for salvage, cancel, cancel-all, link, and query. Persistent in-memory structures are `salvageQueue`, `pendingQueue`, `SalvageHashTable`, `partition_salvaging`, and fixed handler arrays.

## Control Flow
`SALVSYNC_salvInit` initializes queues, hash buckets, locks, condition variables, and starts the detached sync thread. The sync thread binds the SALVSYNC endpoint, registers an atfork cleanup handler, accepts up to `MAXHANDLERS` sockets, and dispatches readable fds. `SALVSYNC_com` reads and validates one command, rejects malformed length or protocol version, dispatches under `VOL_LOCK`, fills queue lengths in the response, and drops channels flagged for shutdown. Workers call `SALVSYNC_getWork`, which waits for queued work, prefers partitions without active salvage, selects queued work, removes the node from the salvage queue, and appends it to pending. Reaper code calls `SALVSYNC_doneWorkByPid` to update state and force fileserver error state on child failure.

## State And Persistence
All scheduler state is in process memory: queued nodes, pending nodes, volume-group links, priorities, pid associations, and done/error state. It is not durable across salvageserver restart. The only external persistent effect is indirect: failed child status can force fileserver volume error state through FSSYNC. The SALVSYNC endpoint is a TCP or Unix-domain daemon-com endpoint on port/path declared in `salvsync.h`.

## Dependencies And Integration Points
This file requires `AFS_DEMAND_ATTACH_FS` and integrates with daemon-com transport, `partition.c` id lookup, `DiskPartitionList`, volume global locking, `rx_queue`, `salvaged.c` worker dispatch, and `fssync.h` for failure notification. It depends on command payload layout from `salvsync.h`.

## Risks And Test Signals
Risks include fixed `MAXHANDLERS` limiting concurrent clients, non-durable queue state, careful `VOL_LOCK` requirements around all queue/hash operations, priority ordering bugs, partition id validation, child pid reuse, and clone-parent state propagation. Test signals include malformed packet rejection, protocol mismatch, queue length responses, cancel/cancel-all, priority reordering, clone link scheduling, partition concurrency limits, child success/error completion, and fileserver force-error notification.
