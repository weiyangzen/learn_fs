# sources/distributed-fs/eos/unit_tests/mgm/CapsTests.cc

## Purpose
Tests FUSEX capability tracking in the MGM `Caps` class, including storage, updates, expiration, deletion, broadcast selection, implied capabilities, and concurrent delete/imply behavior.

## Important APIs, types, and functions
The fixture builds a fake `XrdMgmOfs`, configures environment variables to avoid service startup, and uses `Caps::Store`, `Get`, `HasCap`, `pop`, `expire`, `dropCaps`, `Remove`, `Delete`, `BroadcastCap`, `GetBroadcastCapsTS`, `GetAllCaps`, `GetInodeCapAuthIds`, and `Imply`. Helpers create `eos::fusex::cap` and `VirtualIdentity` values.

## Control flow
Tests insert capabilities keyed by auth id, update client id or inode id, inspect the three internal views (`GetCaps`, client caps, client/inode caps), expire time-ordered entries, drop by client UUID, remove by iterator, delete by inode, and select broadcast targets while excluding a caller's own UUID. The final test runs delete and imply loops concurrently.

## State and persistence
State is in-memory capability maps and time-ordered expiration structures. No durable data is written, but the fake global `gOFS` and environment are shared across the fixture suite.

## Dependencies and integration points
Depends on FUSE server capability code, XRootD MGM OFS, ZMQ teardown behavior, fusex protobuf messages, and Google Test.

## Risks and test signals
Signals are rich for index consistency and expiration semantics. Risks include static fixture global leakage, real-time sleeps making tests slow/flaky, and expected `ncaps()` divergence from `GetCaps().size()` after updates. Concurrency coverage is useful but nondeterministic and should be complemented with thread-sanitizer runs.
