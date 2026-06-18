# sources/distributed-fs/beegfs/meta/source/components/worker/TruncChunkFileWork.h

## Purpose
Declares Work wrapper for truncating a chunk file on one storage target.

## Important APIs And Types
Constructor captures entryID, local filesize, StripePattern, targetID, PathInfo, optional DynamicFileAttribs, result pointer, and counter. Setters configure quota user/group, message user ID, and mirror-second mode.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
Holds non-owning references and writes result outputs during process.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
Uninitialized userID/groupID are used only when useQuota is set. Caller lifetime for pattern/path/counter is critical.

## Test Signals
Tests should cover setter combinations and optional dynamic attribute output.
