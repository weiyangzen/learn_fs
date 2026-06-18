# sources/distributed-fs/beegfs/meta/source/components/worker/GetChunkFileAttribsWork.h

## Purpose
Declares Work wrapper for fetching chunk dynamic attributes from a storage target.

## Important APIs And Types
Constructor captures entryID, StripePattern, targetID, PathInfo, DynamicFileAttribs*, result pointer, and counter; setters control user ID and mirror second.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
All pointers are non-owning and must remain valid through processing.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
The implementation expects outDynAttribs to be valid when success occurs.

## Test Signals
Compile/lifetime tests plus mirror-second request tests are useful.
