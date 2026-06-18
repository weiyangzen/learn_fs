# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/TestNamenodeResolver.java

## Purpose
`TestNamenodeResolver` validates `MembershipNamenodeResolver`, the state-store-backed active NameNode resolver used by routers to choose NameNodes by nameservice and block pool.

## Important APIs, Types, and Functions
The test uses `StateStoreService`, `MembershipNamenodeResolver`, `NamenodeStatusReport`, `FederationNamenodeContext`, `FederationNamenodeServiceState`, `registerNamenode()`, `getNamenodesForNameserviceId()`, `getNamenodesForBlockPoolId()`, `updateActiveNamenode()`, and state-store expiration config `FEDERATION_STORE_MEMBERSHIP_EXPIRATION_MS`.

## Control Flow
Class setup creates a test state store with five-second membership expiration and a resolver with router id. Each test loads the driver and clears membership records. `testShuffleObserverNNs()` registers active, standby, then observer NameNodes, refreshes caches, asserts observer-first ordering when observer reads are requested, and loops until observer ordering is shuffled. `testStateStoreDisconnected()` closes the store driver, refreshes caches, verifies lookups return no cached data, and expects `StateStoreUnavailableException` on registration. `testRegistrationExpired()` verifies an active record disappears after expiration and reappears after heartbeat. `testRegistrationNamenodeSelection()` exercises active-vs-standby-vs-unavailable ordering, expiration, and newest-active/newest-standby selection. The final tests update a standby NameNode to active by RPC address, including an IP address case.

## State and Persistence
Membership records are persisted in the state-store test driver and loaded into resolver caches. Expiration is time-based and requires sleeps plus cache refreshes.

## Dependencies and Integration Points
The test integrates federation state-store utilities, resolver cache refresh, HA service states, RPC address parsing, and router membership selection policy. It protects router failover and observer-read behavior.

## Risks and Test Signals
Tests use real sleeps beyond the expiration interval, so they are slow and timing-sensitive. `verifyFirstRegistration()` expects null for zero results, documenting resolver behavior when caches are empty. Passing tests signal correct priority ordering, observer shuffling, state-store outage handling, expiry cleanup, and in-cache active-state promotion after successful RPC.
