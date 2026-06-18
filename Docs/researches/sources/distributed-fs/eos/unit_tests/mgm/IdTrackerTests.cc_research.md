# sources/distributed-fs/eos/unit_tests/mgm/IdTrackerTests.cc

## Purpose
Tests `IdTrackerWithValidity`, a time-based tracker for MGM ids such as drain candidates. It verifies insertion, lookup, expiration, removal, custom validity, and clearing.

## Important APIs, types, and functions
The test uses `IdTrackerWithValidity<uint64_t>`, `TrackerType::Drain`, `GetClock`, `AddEntry`, `HasEntry`, `DoCleanup`, `RemoveEntry`, and `Clear`.

## Control flow
It constructs a tracker with fake-clock mode, inserts ids at five-second intervals, advances time to expire the first and then all entries, removes an explicit entry, adds entries with custom expiration times based on the id, and clears all tracker state.

## State and persistence
State is in-memory id-to-expiration tracking. No durable state is written. The fake clock makes expiration deterministic.

## Dependencies and integration points
Depends on Google Test and MGM misc id tracker code. It integrates with background MGM workflows that need temporary suppression or validity windows.

## Risks and test signals
Good signals exist for cleanup boundaries. Missing coverage includes multiple `TrackerType` namespaces, duplicate inserts, non-fake real clock behavior, and concurrent access if the tracker is shared across threads.
