# sources/distributed-fs/beegfs/meta/source/components/worker/CopyChunkFileWork.cpp

## Purpose
Implements the storage request that starts a chunk copy for chunk balancing.

## Important APIs And Types
communicate builds CpChunkPathsMsg with event flag, validates mirrored source/destination as buddy group IDs, sets mirror routing, sends to the source target, and returns CpChunkPathsRespMsg result.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
It records only outResult/counter locally; remote storage begins copy work.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
Mirrored files with non-group IDs return INTERRUPTED. Communication failures are normalized to COMMUNICATION. The copy may only be started, not completed, by this response.

## Test Signals
Test mirrored ID validation, non-mirrored copy, storage queue full/AGAIN, communication failure, and file-event serialization.
