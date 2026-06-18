# sources/distributed-fs/beegfs/meta/source/components/worker/LockRangeNotificationWork.h

## Purpose
Declares Work wrapper for range-lock grant notifications.

## Important APIs And Types
Defines LockRangeNotifyList and stores parentEntryID, entryID, buddy-mirror flag, owned notifyList, static ack counter, and DatagramListener mutex helper.

## Control Flow
process() methods are scheduled on worker queues, call their private communicate() or barrier/notification body, store results for the caller, and signal completion through SynchronizedCounter or lock ack handling.

## State And Persistence
Runtime state is per-work notification data plus process-wide counter.

## Dependencies And Integration Points
Depends on Work/MultiWorkQueue scheduling, Program/App target mappers and node stores, MessagingTk RequestResponseTarget, storage message/response types, StripePattern/PathInfo, SynchronizedCounter result collection, and buddy-mirror header flags.

## Risks And Edge Cases
Caller must not use notifyList after moving it into the work item.

## Test Signals
Test construction ownership and process behavior through LockRangeNotificationWork.cpp integration.
