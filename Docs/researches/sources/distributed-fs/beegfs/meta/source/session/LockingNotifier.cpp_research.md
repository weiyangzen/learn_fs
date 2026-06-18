## sources/distributed-fs/beegfs/meta/source/session/LockingNotifier.cpp

Purpose: enqueues asynchronous notification work for clients/processes waiting on file entry locks or byte-range locks.

Important functions: `notifyWaitersEntryLock` creates `LockEntryNotificationWork`; `notifyWaitersRangeLock` creates `LockRangeNotificationWork`. Both accept ownership of their notification lists through move semantics and submit work to the communication slave queue.

Control flow: each method fetches `Program::getApp()->getCommSlaveQueue()`, allocates a `Work` object, and calls `addDirectWork`.

State and persistence behavior: no persistent state. Notification lists are transferred into work packages and processed asynchronously by worker infrastructure.

Dependencies and integration points: depends on `Program`, `MultiWorkQueue`, `Work`, `LockEntryNotificationWork`, and `LockRangeNotificationWork`. It is part of the lock-grant path in storage/session locking.

Risks: raw `new` assumes `addDirectWork` assumes ownership. `Program::getApp()` and `getCommSlaveQueue()` must be valid. If allocation fails, no notification is sent.

Test signals: tests should verify ownership transfer of notify lists, correct work type and fields, and queue submission for both entry and range locks.
