# sources/distributed-fs/beegfs/meta/source/net/message/MirroredMessage.h

## Purpose
Defines the template base for metadata operations that may execute locally, forward to a metadata buddy, participate in sequence-number replay protection, and record changes for buddy resync.

## Important APIs And Types
Important virtual hooks are processSecondaryResponse(), mirrorLogContext(), executeLocally(), isMirrored(), lock(), forwardToSecondary(), and prepareMirrorRequestArgs(). Concrete helpers include processIncoming(), earlyComplete(), buddyResyncNotify(), finishOperation(), notifySecondaryOfACK(), sendToSecondary(), timestamp fixers, updateNodeOp(), and setBuddyNeedsResync().

## Control Flow
processIncoming optionally locks mirrored metadata, references a mirrored session, handles sequence-number zero by returning a new base, acquires/reuses MirrorStateSlot for duplicate request handling, registers a resync changeset and op when a resync is in progress, executes locally, and finishes or early-completes. finishOperation forwards observable changes to the secondary or sends AckNotify, records response state for replay, commits/abandons resync changesets, unregisters the resync op, sends the client response, and releases locks. sendToSecondary rejects forwarding during resync, validates secondary online/good state, sets needs-resync on unsuitable state or communication/result mismatch, copies sequence/requestor/user fields, and routes to the secondary mirror target.

## State And Persistence
State includes resyncJob pointer, lockState RAII object, shared MirrorStateSlot, mirrored sessions sequence stores, per-thread BuddyResyncer changesets, buddy needs-resync marker, operation counters, and optional timestamp mirroring updates on inodes.

## Dependencies And Integration Points
Depends on NetMessage base classes, Program/App service registries, MessagingTk, node/session/target stores, generated common message classes, and operation statistics counters.

## Risks And Edge Cases
This is a central correctness point. Lock ordering must be obeyed by every subclass. Response replay relies on memory barriers and one active request per client/sequence. If forwarding fails after local success, rollback is intentionally not attempted and needs-resync is set. resyncJob is reacquired in finishOperation and must remain valid long enough for unregisterOps. A typo in AckNotifiy names follows existing class names.

## Test Signals
Test duplicate sequence replay, sequence zero base negotiation, selective ack, local-only non-mutating operations, observable forwarding success/failure, secondary result mismatch, resync-in-progress changeset commit/abandon, earlyComplete socket release, timestamp mirroring, and lock-order deadlock scenarios.
