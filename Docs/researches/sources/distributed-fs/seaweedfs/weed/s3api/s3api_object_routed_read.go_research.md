# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_routed_read.go

## Purpose

This file implements owner-routed object entry reads for multi-filer deployments so reads can observe just-written data on the write owner before replication converges.

## Important APIs, Types, and Functions

Functions include `getObjectEntryRoutedByKey`, `priorWriteOwner`, `markOwnerUnreachable`, `ownerRecentlyUnreachable`, and `lookupEntryOnFiler`. `unreachableOwnerTTL` is a two-second skip window.

## Control Flow

The read path resolves the write owner from the object route key, skips recently unreachable owners, calls `LookupEntry` through failover, and probes a prior owner once on `ErrNotFound` during ring rebalance windows.

## State and Persistence Behavior

No persistent state is written. In-memory state records owner addresses with expiry times in `unreachableOwners`.

## Dependencies and Integration Points

The file depends on route-key helpers, object write lock client ownership, `pb.WithFilerClient`, `filer_pb.LookupEntry`, failover helpers, and `util.FullPath`.

## Risks and Edge Cases

Risks include stale ring ownership, owner transport failures, prior-owner stale reads, and TTL tuning between avoiding failed dials and resuming owner reads quickly.

## Test Signals

The companion unit test covers owner marking isolation; integration tests should simulate owner failover and ring moves.
