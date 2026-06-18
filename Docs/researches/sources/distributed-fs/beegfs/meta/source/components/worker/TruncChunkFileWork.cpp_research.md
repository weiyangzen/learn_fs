# sources/distributed-fs/beegfs/meta/source/components/worker/TruncChunkFileWork.cpp

## Purpose
Implements remote TruncLocalFileMsg execution for truncating a chunk on storage.

## Important APIs And Types
communicate sets mirror flags, disables dynamic attrs for mirror-second, optionally includes quota user/group data, sends request, copies response dynamic attrs, suppresses warning for TOOBIG, and returns the response result.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
Mutates remote chunk length and caller-provided result/dynamic attrs.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
filesize is already target-local size; callers must precompute stripe-local truncation correctly. TOOBIG is intentionally passed through to clients without warning.

## Test Signals
Test quota and non-quota truncation, TOOBIG, mirror primary/secondary, dynamic attrs, and communication failure.
