## sources/distributed-fs/beegfs/meta/tests/TestBuddyMirroring.cpp

Purpose: Provides concurrency smoke tests for metadata entry lock stores used by buddy mirroring and metadata operations.

Important APIs/types/functions: Defines `ParentNameLockTestThread`, `FileIDLockTestThread`, and `DirIDLockTestThread`, each deriving from `PThread`. Tests `BuddyMirroring.simpleEntryLocks` and `BuddyMirroring.rwEntryLocks` start multiple lock/unlock threads against `EntryLockStore`.

Control flow: Each thread logs, obtains a lock, sleeps up to one second, then unlocks. The tests allocate thread objects, start all, join all, and delete them.

State and persistence: No disk persistence. Shared state is `EntryLockStore` plus lock data returned by `lock()`.

Dependencies and integration: Uses BeeGFS `PThread`, `EntryLockStore`, `Random`, logging, and GoogleTest. It exercises parent/name locks, file ID locks, and directory read/write lock paths.

Risks and test signals: The tests are nondeterministic timing smoke tests and contain no explicit assertions beyond absence of deadlock/crash. They may miss fairness, exclusivity, and ordering regressions. Stronger tests would instrument concurrent critical sections and assert mutual exclusion/read-sharing invariants.
