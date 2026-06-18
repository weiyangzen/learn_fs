# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/DisabledNameserviceStore.java

## Purpose
`DisabledNameserviceStore` defines the cached state-store API for nameservices administratively disabled in the federation.

## Important APIs, Types, And Functions
The abstract methods are `disableNameservice`, `enableNameservice`, and `getDisabledNameservices`. It stores `DisabledNameservice` records through `CachedRecordStore`.

## Control Flow
Concrete implementations perform record insert/delete/query operations through the state-store driver and cache inherited from `CachedRecordStore`.

## State, Persistence, And Dependencies
Persistent state is a set of `DisabledNameservice` records in the configured state-store backend. In-memory cache state comes from the base class.

## Integration Points
Router admin and resolver paths use this store to avoid routing to disabled namespaces. `StateStoreService` registers `DisabledNameserviceStoreImpl` as one of the built-in record stores.

## Risks
As an abstract contract, correctness depends on implementations refreshing cache after enable/disable changes and handling unavailable state-store errors consistently.

## Test Signals
Tests should cover disable, enable, idempotence, cache refresh visibility, unavailable store exceptions, and integration with resolver routing decisions.
