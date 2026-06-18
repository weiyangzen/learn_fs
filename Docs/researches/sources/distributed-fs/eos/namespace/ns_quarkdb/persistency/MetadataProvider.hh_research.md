# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataProvider.hh

## Purpose
This header declares `MetadataProvider`, the sharded asynchronous metadata retrieval and cache coordinator for QuarkDB namespace services.

## Important APIs, Types, and Functions
The public API retrieves container and file metadata, drops cached ids, checks file existence, inserts newly created file/container objects into caches, changes file/container cache capacities, and returns cache statistics. Private `pickShard()` overloads map file and container identifiers to one of `kShards == 16`.

Important members are `mExecutor`, `mQcl`, and `mShards`. The comment documents a lifetime invariant: the folly executor must outlive qclient futures and therefore is declared before qclient storage.

## Control Flow
Users construct the provider with QDB contact details and service pointers, then call asynchronous retrieval APIs. All calls are forwarded to a selected `MetadataProviderShard`.

## State and Persistence Behavior
The provider owns cache shards and qclients but no durable metadata. It coordinates in-memory cache state for persistent protobuf objects fetched from QuarkDB.

## Dependencies and Integration Points
It depends on identifier types, metadata interfaces, `MetadataProviderShard`, namespace macros, folly futures and splitters, and QDB contact details. It integrates with `QuarkFileMDSvc` and `QuarkContainerMDSvc`.

## Risks and Test Signals
Service pointers are non-owning and passed down to shards for object construction, so their lifetimes must exceed provider operations. Tests should target pointer lifetime assumptions, shard selection consistency, and executor/qclient teardown while futures are pending.
