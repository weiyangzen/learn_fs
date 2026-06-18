# sources/distributed-fs/beegfs/meta/source/components/worker/LockEntryNotificationWork.h

## Purpose
Declares Work wrapper for notifying clients about granted entry or append locks.

## Important APIs And Types
Defines LockEntryNotifyList and stores lock type, parentEntryID, entryID, buddy-mirror flag, owned notifyList, static ack counter, and helper declarations.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
The work item owns the notification list by move and mutates inode lock state only when process runs.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
Caller must pass a list whose EntryLockDetails remain valid as list nodes. Static ackCounter is process-wide and mutex-protected but can wrap.

## Test Signals
Tests should cover move ownership and correct dispatch by LockEntryNotifyType.
