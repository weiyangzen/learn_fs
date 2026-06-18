# sources/distributed-fs/beegfs/meta/source/components/worker/UnlinkChunkFileWork.h

## Purpose
Declares Work wrapper for unlinking a chunk file from one storage target.

## Important APIs And Types
Constructor captures entryID, StripePattern, targetID, PathInfo, result pointer, and counter; setters control message user ID and mirror-second mode.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
All referenced objects are non-owning; result/counter are caller synchronization outputs.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
Caller must preserve PathInfo and StripePattern lifetimes until completion.

## Test Signals
Compile/lifetime tests and unlink integration tests should exercise both mirror modes.
