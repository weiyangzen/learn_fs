# sources/distributed-fs/beegfs/meta/source/components/worker/LockRangeNotificationWork.cpp

## Purpose
Implements UDP lock-grant notification and ack handling for byte-range locks.

## Important APIs And Types
process mirrors the entry-lock workflow: register wait acks, resend LockGrantedMsg up to configured retries, unregister, then for missing acks reference the loaded file inode, set each RangeLockDetails to unlock, call flockRange, and cancel all waiters if multiple acks are missing.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
State is transient ack maps and static counter; missed notifications mutate in-memory range-lock queues.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
The code intentionally parallels LockEntryNotificationWork and can drift from it. Missing acks can revoke granted locks and cancel waiters, so timeout tuning affects client-visible lock behavior.

## Test Signals
Test full/partial/missing acks, disconnected clients, range unlock behavior, cancel-all path, retry timing, and ack ID uniqueness.
