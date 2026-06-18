# sources/distributed-fs/ceph-client/fs/dlm/requestqueue.h

## Purpose
`requestqueue.h` declares the API for saving, processing, waiting on, and purging DLM messages queued during recovery.

## Important APIs, Types, And Functions
It declares `dlm_add_requestqueue()`, `dlm_process_requestqueue()`, `dlm_wait_requestqueue()`, and `dlm_purge_requestqueue()`.

## Control Flow
Receive code adds messages while locking is stopped; recoverd processes and purges the queue as recovery completes. `dlm_wait_requestqueue()` is declared here and implemented elsewhere in the lock receive path.

## State And Persistence
No header-owned state. Implementations operate on lockspace requestqueue lists and flags.

## Dependencies And Integration Points
Used by recoverd, member stop/start code, and lock receive code.

## Risks
The declared wait helper is not implemented in `requestqueue.c`, so readers must look elsewhere for the wait behavior. Queue APIs require the caller to understand recovery stop/running flags.

## Test Signals
Compile/link coverage plus recovery replay tests validate the declarations.
