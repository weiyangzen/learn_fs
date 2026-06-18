# sources/distributed-fs/openafs/src/rx/rx_server.h

## Purpose
Defines the server idle-queue entry used by RX server threads waiting for calls or listener duties.

## Important APIs, Types, And Functions
`struct rx_serverQueueEntry` contains an `opr_queue` entry, `newcall`, optional lock and condition variable, thread number `tno`, and `socketp` pointer. The comments define the handoff contract between listener and server roles.

## Control Flow
Server threads enqueue this structure when idle. When a call arrives, RX fills `newcall` and wakes the thread. If `socketp` is non-null, the sleeping server is willing to become a listener; it sleeps with `*socketp == -1` and wakes with a real socket when selected as listener.

## State And Persistence
State is transient per idle server thread. It records the call/socket assignment and synchronization primitive used for wakeup.

## Dependencies And Integration Points
The structure integrates `rx.c` server scheduling with pthread/LWP listener code and `rx_idleServerQueue`. It relies on `struct rx_call`, `opr_queue`, lock types, and `osi_socket`.

## Risks And Test Signals
Risks are missed wakeups, stale `socketp` values, and inconsistent lock use around queue entries. Server pool tests, hot-thread listener handoff, and high-concurrency incoming call tests are useful signals.
