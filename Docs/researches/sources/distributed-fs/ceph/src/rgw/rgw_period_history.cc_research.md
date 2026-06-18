# sources/distributed-fs/ceph/src/rgw/rgw_period_history.cc

## Purpose
`rgw_period_history.cc` implements an in-memory, thread-safe history manager for RGW realm periods. It tracks consecutive ranges of periods, detects forks, merges adjacent histories, and fetches missing predecessor periods through a pluggable `Puller`.

## Important APIs, Types, And Functions
Internal `History` stores a deque of consecutive `RGWPeriod` objects and exposes oldest/newest epoch, containment, indexed lookup, and predecessor id. `RGWPeriodHistory::Impl` owns a boost intrusive AVL set of disjoint histories. Public methods are `get_current()`, `attach()`, `insert()`, and `lookup()`. `Cursor` exposes period access and forward/backward navigation.

## Control Flow
Construction seeds the current history from the current period if available. `insert_locked()` places a period into an existing range, prepends/appends to adjacent ranges, creates a new disjoint range, updates an existing period if its period epoch is newer, or returns `-EEXIST` on same realm epoch with different period id. `attach()` inserts the requested period, then repeatedly pulls predecessor periods outside the mutex until the requested epoch connects to current history.

## State And Persistence
All state is in memory: intrusive set nodes own `History` allocations and deques. The destructor clears and deletes histories. Persistence is delegated to the `Puller` implementation, typically `RGWPeriodPuller`, which can read local config-store state or pull from the master zone.

## Dependencies And Integration Points
The implementation depends on `RGWPeriod`, `RGWPeriodHistory::Puller`, boost intrusive AVL set, mutex locking, Ceph logging, and config-store references passed to `attach()`. Multisite sync code can use cursors only when periods are connected to the current period.

## Risks And Test Signals
Risks include cursor invalidation for disjoint histories, fork detection, empty predecessor chains, locking mistakes around external pulls, and merge correctness when current history is the source or destination. Tests should cover insert before/after current, merging two ranges, duplicate epoch same/different id, attach with missing predecessors, current-period-empty construction, cursor traversal, and concurrent lookup/insert behavior.
