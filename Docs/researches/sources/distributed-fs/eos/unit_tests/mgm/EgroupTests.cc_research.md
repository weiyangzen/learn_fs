# sources/distributed-fs/eos/unit_tests/mgm/EgroupTests.cc

## Purpose
Tests CERN e-group membership lookup and caching behavior used by MGM authorization. It covers both a live functional LDAP-style lookup and deterministic injected cache behavior.

## Important APIs, types, and functions
The tests use `eos::mgm::Egroup`, `SteadyClock`, `Egroup::Member`, `inject`, `DumpMember`, `DumpMembers`, `refresh`, and `getPendingQueueSize`.

## Control flow
The functional test calls real membership checks for known CERN users/groups. Cache tests inject membership statuses, advance a fake clock through lifetimes, wait for pending asynchronous refresh queues to drain, and verify stale-to-refreshed membership transitions. Explicit refresh bypasses normal expiration delay.

## State and persistence
State is in-memory membership cache with expiration lifetimes and asynchronous refresh queue. No durable state is persisted.

## Dependencies and integration points
Depends on MGM e-group code, common steady clock abstraction, and Google Test. The live test integrates with CERN external directory infrastructure.

## Risks and test signals
The live functional test is environment-dependent and may fail outside CERN network or when directory data changes. Deterministic tests strongly cover cache lifetime semantics but spin-wait on queue size. Additional tests should cover lookup failures, negative-cache expiration, and shutdown of pending refresh threads.
