# sources/distributed-fs/beegfs/meta/source/components/worker/LockEntryNotificationWork.cpp

## Purpose
Implements UDP lock-grant notification and ack handling for entry/append locks.

## Important APIs And Types
process builds wait-ack IDs, registers them with AcknowledgmentStore, repeatedly sends LockGrantedMsg to clients through DatagramListener, waits for acks, unregisters waiters, and if acks are missing references the loaded inode, unlocks unacknowledged waiters, and cancels all waiters when multiple acks are missing. Helper methods unlock append/flock waiters and increment a static ack counter.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
State is transient waitAcks/receivedAcks plus the static ack counter. It mutates in-memory FileInode lock queues on missed acknowledgments.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
notifyList elements back waitAck privateData, so the list must not change during processing. Missing client nodes do not remove waiters until ack timeout. Multiple missing acks trigger broad cancellation.

## Test Signals
Test all acks received, unknown client, partial acks, no acks, append vs flock behavior, cancel-all threshold, and ack ID uniqueness.
