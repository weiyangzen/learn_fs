# sources/distributed-fs/beegfs/meta/source/components/worker/CopyChunkFileWork.h

## Purpose
Declares Work wrapper for chunk-balancer CpChunkPathsMsg.

## Important APIs And Types
Constructor copies source/destination IDs, relative path, EntryInfo, mirrored flag, result pointer, counter, and FileEvent. Private isTargetIDMirrored validates group IDs.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
State is per-work-item and mostly by value except result/counter pointers.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
EntryInfo/FileEvent are copied, so caller mutations after construction are not reflected.

## Test Signals
Test constructor copy behavior and target mirror validation.
