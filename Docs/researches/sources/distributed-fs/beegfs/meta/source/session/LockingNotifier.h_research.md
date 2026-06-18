## sources/distributed-fs/beegfs/meta/source/session/LockingNotifier.h

Purpose: declares a static utility for scheduling lock notification work when file locks become available.

Important APIs/types: `notifyWaitersEntryLock` takes lock type, parent entry ID, entry ID, buddy-mirror flag, and `LockEntryNotifyList`. `notifyWaitersRangeLock` takes parent entry ID, entry ID, buddy-mirror flag, and `LockRangeNotifyList`.

Control flow: callers do not instantiate `LockingNotifier`; the constructor is private and functions are static.

State and persistence behavior: no state or persistence.

Dependencies and integration points: includes storage locking definitions and worker work-package headers. The declarations document that notifier takes ownership of notify lists.

Risks: the ownership contract is important because lists are moved into asynchronous work in the implementation.

Test signals: compile tests around move-only/owned notification lists and call sites that should not reuse lists after notification.
