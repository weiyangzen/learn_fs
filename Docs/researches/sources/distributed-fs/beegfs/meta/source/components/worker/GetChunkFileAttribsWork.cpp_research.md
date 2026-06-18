# sources/distributed-fs/beegfs/meta/source/components/worker/GetChunkFileAttribsWork.cpp

## Purpose
Implements remote GetChunkFileAttribsMsg execution and dynamic attribute extraction.

## Important APIs And Types
communicate sets buddy mirror flags, routes through RequestResponseTarget, validates GetChunkFileAttribsRespMsg result, and fills DynamicFileAttribs with storage version, size, blocks, mtime, and atime.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
Writes caller-provided result and outDynAttribs; reads remote chunk file state.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
outDynAttribs is assumed non-null on success. Buddy mirror second routing must match target mapper state.

## Test Signals
Test successful stat, failed target communication, non-success storage response, buddy primary/secondary flags, and user-id propagation.
